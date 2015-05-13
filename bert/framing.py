"""
Coroutine base data framing and unframing.
"""
import struct
import collections
import logging

from . import utils

__all__ = ['Frame', 'UnFramer', 'Framer']



logger = logging.getLogger()
class Frame(collections.namedtuple('Frame', ['content', 'length', 'valid', 'checksum'])):
    """
    Simple container for frames.
    """
    def __repr__(self):
        """
        Content can be quite large. Truncate it to something more easily
        represented. 
        """
        trunc_content = self.content[:10] + ' ...'
        return "Frame(content=%s, length=%r, valid=%r)" % (trunc_content, self.length, self.valid)
    @property
    def raw(self):
      return '\x7e'+ struct.pack('>H', self.length) + self.content + struct.pack('>B', self.checksum)


@utils.coroutine
def UnFramer(target=None):
    """
    Performs un-framing on a serial stream of data.
    """
    
    while True:
        byte = (yield)
        logger.debug('Start, or unframed byte: ' + byte + '\r\n')
        if byte == '\x7e':
            length_msb = (yield)
            length_lsb = (yield)
            frame_length, = struct.unpack('>H', length_msb + length_lsb)
            logger.debug('Received length: %d\r\n', frame_length)
            frame_bytesum = 0
            frame_contents = ''

            for _ in xrange(frame_length):
                byte = (yield)
                frame_bytesum += struct.unpack('>B', byte)[0]
                frame_contents += byte
	
            logger.debug('Finished retreiving contents.\r\n')
            frame_checksum, = struct.unpack('>B', (yield))
            logger.debug('Received checksum: ' + str(frame_checksum) + '\r\n')

            valid = True if ((0xff - (frame_bytesum & 0xff)) == frame_checksum) else False
            target.send(Frame(frame_contents, frame_length, valid, frame_checksum))
            logger.debug('Frame sent to target.\r\n')


def Framer(bytes):
    """
    Performs framing on a series of bytes. Currently does the following:
    * Start delimiter
    * Length as big-endiann word
    * Checksum calculation
    """
    
    unsigned_byte_struct = struct.Struct('>B')

    frame_length = len(bytes)
    logger.debug('New frame length = %d', frame_length)
    frame_bytesum = 0

    yield '\x7e'
    yield struct.pack('>H', frame_length)
    yield bytes

    for b in bytes:
        uint8_b, = unsigned_byte_struct.unpack(b)
        frame_bytesum += uint8_b

    frame_checksum = 0xff - (frame_bytesum & 0xff)
    logger.debug('Frame checksum = ' + str(frame_checksum) + '\r\n')
    yield unsigned_byte_struct.pack(frame_checksum)
    

