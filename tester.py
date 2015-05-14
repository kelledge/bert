import threading
import serial
import time
import logging
import logging.handlers
from bert import framing
from bert import utils

logger = logging.getLogger('test_runner')
logger.setLevel('INFO')  # INFO, DEBUG, etc
handler = logging.handlers.SysLogHandler(address='/dev/log')


class SerialLoopBack(threading.Thread):
    def __init__(self, serial_name):
        self.frame = None
        self.on_frame = self.onFrame()
        self.unframer = framing.UnFramer(target=self.on_frame)
        self.serial_port = serial.Serial(serial_name)
        threading.Thread.__init__(self)
        return

    @utils.coroutine
    def onFrame(self):
        while True:
            self.frame = (yield)

    def run(self):
        while True:
            if self.serial_port.inWaiting() > 0:
                self.unframer.send(self.serial_port.read(size=1))

            if self.frame is not None:
                time.sleep(0.1)
                self.serial_port.write(self.frame.raw)
                self.frame = None


class SerialBroadcast(threading.Thread):
    def __init__(self, serial_name, test_name):
        self.frame = None
        self.on_frame = self.onFrame()
        self.unframer = framing.UnFramer(target=self.on_frame)
        self.serial_port = serial.Serial(serial_name)
        self.urandom = open('/dev/urandom', 'rb')
        self.test_name = test_name
        threading.Thread.__init__(self)
        return

    @utils.coroutine
    def onFrame(self):
        while True:
            self.frame = (yield)

    def resetUnframer(self):
        self.unframer = framing.UnFramer(target=self.on_frame)

    def run(self):
        frame_size = 32
        while True:
            framer = framing.Framer(self.urandom.read(frame_size))
            logger.debug('test="' + self.test_name + '" Made my frame')
            for frame_bytes in framer:
                self.serial_port.write(frame_bytes)
            self.frame = None
            self.serial_port.setTimeout(0)
            read_start = time.time()
            while self.frame is None:
                if self.serial_port.inWaiting() > 0:
                    self.unframer.send(self.serial_port.read(size=1))
                if (time.time() - read_start) > 1.1:
                    # Reset Unframer to discart any partial frames that may be
                    # lingering
                    self.resetUnframer()
                    # Break out of loop by setting frame to False which is not
                    # None
                    self.frame = False

            if self.frame is False:
                logger.info('test="' + self.test_name +
                            '" result="fail" reason="response timeout"')
            elif self.frame.valid is True:
                logger.info('test="' + self.test_name +
                            '" result="pass" reason="valid checksum"')

            else:
                logger.info('test="' + self.test_name +
                            '" result="fail" reason="invalid checksum"')
            time.sleep(59)


class SerialTest(object):
    def __init__(self, serial_number, serial_type):
        # These two lines set up the logger for syslog
        # They should be moved to whatever the managing class ends up being
        handler.setFormatter(logging.Formatter(fmt=(serial_number +
                                                    ': %(message)s')))
        logger.addHandler(handler)

        self.serial_number = serial_number
        self.serial_type = serial_type
        if self.serial_type is not 'FTDI':
            self.loop_back = SerialLoopBack('/dev/serial/by-id/' +
                                            self.serial_number + '/' +
                                            self.serial_type + 'r')
            self.broadcast = SerialBroadcast('/dev/serial/by-id/' +
                                             self.serial_number +
                                             '/' + self.serial_type +
                                             'l', self.serial_type)
        else:
            self.loop_back = SerialLoopBack('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A703X3A3-if00-port0')
            self.broadcast = SerialBroadcast('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A90BJ1LX-if00-port0', self.serial_type)

    def start_test(self):
        self.loop_back.start()
        self.broadcast.start()
        logger.info('test="' + self.serial_type + '" starting test')
