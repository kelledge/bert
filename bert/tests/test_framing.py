import mock

from twisted.trial import unittest
from .. import framing

class TestUnFramer(unittest.TestCase):
    def setUp(self):
        self.valid_frame1 = b'\x7e\x00\x04\x08\x52\x4e\x48\x0f'
        self.valid_frame2 = b'\x7e\x00\x05\x88\x01\x42\x44\x00\xf0'

        self.valid_frame_in_stream = (
            b'\x01\x02\x03' + 
            self.valid_frame1 + 
            b'\x03\x04\x05'
        )
        self.valid_frames = (
            self.valid_frame1 + 
            self.valid_frame2
        )
        self.valid_frames_in_stream = (
            b'\x01\x02\x03' +
            self.valid_frame1 +
            b'\x04\x05\x06' +
            self.valid_frame2 +
            b'\x07\x08\x09'
        )

    def tearDown(self):
        pass

    def runFixture(self, fixture):
        frame_receiver = mock.MagicMock()
        unframer = framing.UnFramer(target=frame_receiver)
        for b in fixture:
            unframer.send(b)

        return frame_receiver

    def test_detectValidFrame(self):
        frame_receiver = self.runFixture(self.valid_frame1)
        expected_calls = [mock.call(
            length=4,
            contents='\x08\x52\x4e\x48',
            bytesum=0xf0,
            checksum=0x0f
        )]

        actual_calls = frame_receiver.send.call_args_list
        self.assertEqual(actual_calls, expected_calls)        

    def test_detectValidFrameInStream(self):
        frame_receiver = self.runFixture(self.valid_frame_in_stream)
        expected_calls = [mock.call(
            length=4,
            contents='\x08\x52\x4e\x48',
            bytesum=0xf0,
            checksum=0x0f
        )]

        actual_calls = frame_receiver.send.call_args_list
        self.assertEqual(actual_calls, expected_calls)        

    def test_detectMultipleValidFrames(self): 
        frame_receiver = self.runFixture(self.valid_frames)
        expected_calls = [
            mock.call(
                length=4,
                contents='\x08\x52\x4e\x48',
                bytesum=0xf0,
                checksum=0x0f
            ),
            mock.call(
                bytesum=271, 
                checksum=240, 
                length=5, 
                contents='\x88\x01\x42\x44\x00'
            )
        ]

        actual_calls = frame_receiver.send.call_args_list
        self.assertEqual(actual_calls, expected_calls) 

    def test_detectMultipleValidFramesInStream(self): 
        frame_receiver = self.runFixture(self.valid_frames_in_stream)
        expected_calls = [
            mock.call(
                length=4,
                contents='\x08\x52\x4e\x48',
                bytesum=0xf0,
                checksum=0x0f
            ),
            mock.call(
                bytesum=271, 
                checksum=240, 
                length=5, 
                contents='\x88\x01\x42\x44\x00'
            )
        ]

        actual_calls = frame_receiver.send.call_args_list
        self.assertEqual(actual_calls, expected_calls) 


class TestFramer(unittest.TestCase):

    def setUp(self):
        self.data_short = '\x08\x52\x4e\x48'
        self.data_long = (
            '\x10\x01\x00\x14\xa2\x00\x40' +
            '\x0a\x01\x27\xff\xfe\x00\x00' +
            '\x54\x78\x44\x61\x74\x61\x30\x41'
        )

    def test_correctChecksum(self):
        expected_checksum = '\x0f'        

        framer_generator = framing.Framer(self.data_short)
        framer_list = list(framer_generator)
        actual_checksum = framer_list[-1]

        self.assertEqual(expected_checksum, actual_checksum)

    def test_correctLength(self):
        expected_length = '\x00\x16'        

        framer_generator = framing.Framer(self.data_long)
        framer_list = ''.join(list(framer_generator))
        actual_length = framer_list[1:3]

        self.assertEqual(expected_length, actual_length)

    def test_correctLongLength(self):
        pass

    def test_correctStartDelimiter(self):
        expected_start_delimiter = '\x7e'        

        framer_generator = framing.Framer(self.data_long)
        framer_list = list(framer_generator)
        actual_start_delimiter = framer_list[0]

        self.assertEqual(expected_start_delimiter, actual_start_delimiter)

