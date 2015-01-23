"""
Twisted protocols implementing Bert logic/state.
"""
import itertools

from twisted.internet import protocol, reactor
from . import framing

__all__ = ['BertProtocol', 'BertEmitter', 'BertLoopback']

class BertProtocol(protocol.Protocol, object):
    """
    Base protocol. Allows sending and receiving structured frames of data.
    """
    def __init__(self, unframer=framing.UnFramer):
        super(BertProtocol, self).__init__()

    def connectionMade(self):
        """
        Called when Twisted connects this protocol to a transport. Left
        unimplemented to remind subclasses they need to handle this event.
        """
        raise NotImplemented()

    def dataReceived(self, data):
        """
        Called when Twisted has data for us. Send it straight through to
        the unframer coroutine.
        """

    def frameSend(self, data):
        """
        Assemble a frame from the data, and place this frame on the wire.
        """
        frame = framing.Framer(data)      
        self.transport.write(''.join(frame))



    def frameReceived(self, frame):
        """
        Called when the the unframer successfully collects a frame from the wire.
        """
        raise NotImplemented()


class BertEmitter(BertProtocol):
    """
    Collects data from a byte stream, and sends this data to a loopback while
    keeping track of errors.

    :param stream: data stream to to read bytes from and place on the wire
    :param block_size: number of bytes to send on the wire in a single frame
    :param timeout: time (seconds) to wait before giving up on a sent frame

    """
    def __init__(self, stream, block_size, timeout):
        super(BertEmitter, self).__init__()
        
        self.stream = stream
        self.block_size = block_size
        self.timeout = timeout

        self.valid_count = 0
        self.invalid_count = 0
        self.timeout_count = 0
        self.timer = None
       
    def connectionMade(self):
        """
        Kick off the test. Start sending frames and tracking errors.
        """
    
    def frameSend(self, data):
        """
        Override base implementation to keep track of timeouts.
        """
        self.timeoutStart()
        super(BertEmitter, self).frameSend(data)

    def frameReceived(self, frame):
        """
        Check validity of frame. Cancle timeous. Update error tracking.
        """
        self.timeoutCancel()
        if frame.valid:
            self.valid_count += 1
        else:
            self.invalid_count += 1

    def frameTimeout(self):
        self.timeout_count += 1

    def timeoutStart(self):
        if self.timer is None:
            self.timer = reactor.callLater(self.timeout, self.frameTimeout)

    def timeoutCancel(self):
        if self.timer is not None and self.timer.active():
            self.timer.cancel()
            self.timer = None


class BertLoopback(BertProtocol):
    """
    Simply receives frames, and echos them back after the configured turnaround
    time has passed.

    :param turnaround: time (seconds) to wait before echoing frame back
    """
    def __init__(self, turnaround):
        """

        """
        super(BertLoopback, self).__init__()
        self.turnaround = turnaround

    def connectionMade(self):
        """
        Nothing to do here.
        """
        pass

    def frameReceived(self, frame):
        """
        Echo back frames received, after waiting the configured turnaround time.
        """
        reactor.callLater(self.turnaround, self.frameSend, frame.content)

