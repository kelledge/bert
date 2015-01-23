"""
Coroutine base data framing and unframing.
"""
import struct
import collections

from . import utils

__all__ = ['Frame', 'UnFramer', 'Framer']

class Frame(collections.namedtuple('Frame', ['content', 'length', 'valid'])):
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


@utils.coroutine
def UnFramer(target=None):
    """
    Performs un-framing on a serial stream of data.
    """
    
    while True:
        byte = (yield)

        if byte == '\x7e':
            length_msb = (yield)
            length_lsb = (yield)
            frame_length, = struct.unpack('>H', length_msb + length_lsb)
            frame_bytesum = 0
            frame_contents = ''

            for _ in xrange(frame_length):
                byte = (yield)
                frame_bytesum += struct.unpack('>B', byte)[0]
                frame_contents += byte
	
            frame_checksum, = struct.unpack('>B', (yield))

            valid = True if ((0xff - (frame_bytesum & 0xff)) == frame_checksum) else False
            target.send(
                length=frame_length,
                contents=frame_contents,
                bytesum=frame_bytesum,
                checksum=frame_checksum
            )


def Framer(bytes):
    """
    Performs framing on a series of bytes. Currently does the following:
    * Start delimiter
    * Length as big-endiann word
    * Checksum calculation
    """
    unsigned_byte_struct = struct.Struct('>B')

    frame_length = len(bytes)
    frame_bytesum = 0

    yield '\x7e'
    yield struct.pack('>H', frame_length)
    yield bytes

    for b in bytes:
        uint8_b, = unsigned_byte_struct.unpack(b)
        frame_bytesum += uint8_b

    frame_checksum = 0xff - (frame_bytesum & 0xff)
    yield unsigned_byte_struct.pack(frame_checksum)

