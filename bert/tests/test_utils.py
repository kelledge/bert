import mock
import StringIO

from twisted.trial import unittest
from .. import utils

class TestCoroutine(unittest.TestCase):

    def runDecorate(self, function, decorator):
        deco_function = utils.coroutine(function)
        return deco_function()

    def test_createsGenerator(self):
        mock_generator = mock.MagicMock()
        self.runDecorate(mock_generator, utils.coroutine)
        self.assertTrue(mock_generator.called)

    def test_startsGenerator(self):
        mock_generator = mock.MagicMock()
        mock_coroutine = self.runDecorate(mock_generator, utils.coroutine)
        self.assertTrue(mock_coroutine.next.called)
    

class TestBlockRead(unittest.TestCase):

    def runRead(self, length, block_size):
        buf = StringIO.StringIO(' ' * length)
        reads = list(utils.BlockRead(buf, block_size))
        return reads

    def test_blockSizeSmallerThanFile(self):
        expected_read = ['   ', '   ', '   ', '   ']
        actual_read = self.runRead(12, 3)
        self.assertEqual(actual_read, expected_read)

    def test_blockSizeLargerThanFile(self):
        expected_read = ['            ']
        actual_read = self.runRead(12, 13)
        self.assertEqual(actual_read, expected_read)

    def test_blockSizeUnevenBlockSize(self):
        expected_read = ['          ', '  ']
        actual_read = self.runRead(12,10)
        self.assertEqual(actual_read, expected_read)




