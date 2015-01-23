import mock
import StringIO

from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from .. import protocol
from .. import framing

class TestBertProtocol(unittest.TestCase):
    pass

class TestBertEmitter(unittest.TestCase):

    def setUp(self):
        self.clock = task.Clock()
        self.tr = proto_helpers.StringTransport()
        self.valid_frame = framing.Frame(' ', 1, True)
        self.invalid_frame = framing.Frame(' ', 1, False)

        self.test_stream = StringIO.StringIO()
        self.test_block_size = 64
        self.test_timeout = 1.0

        self.bert_emitter = protocol.BertEmitter(self.test_stream, self.test_block_size, self.test_timeout)
        self.bert_emitter.transport = self.tr

    def test_receivedValidFrameIncreasesValidCount(self):
        expected_count = self.bert_emitter.valid_count + 1
        self.bert_emitter.frameReceived(self.valid_frame)
        self.assertEqual(self.bert_emitter.valid_count, expected_count)

    def test_receivedInalidFrameIncreasesInvalidCount(self):
        expected_count = self.bert_emitter.invalid_count + 1
        self.bert_emitter.frameReceived(self.invalid_frame)
        self.assertEqual(self.bert_emitter.invalid_count, expected_count)

    def test_timeoutExpiresIncreasesTimeoutCount(self):
         with mock.patch('twisted.internet.reactor.callLater', new=self.clock.callLater):
            expected_count = self.bert_emitter.timeout_count + 1
            self.bert_emitter.frameSend(' ')
            self.clock.advance(self.test_timeout + 0.1)
            self.assertEqual(self.bert_emitter.timeout_count, expected_count)

    def test_sendFrameCreatesTimeoutTimer(self):
        self.bert_emitter.frameSend(' ')
        self.assertTrue(self.bert_emitter.timer is not None)
        self.bert_emitter.timeoutCancel()

    def test_receiveFrameCancelsTimeoutTimer(self):
        with mock.patch('twisted.internet.reactor.callLater', new=self.clock.callLater):
            self.bert_emitter.frameSend(' ')
            self.clock.advance(self.test_timeout - 0.1)
            self.bert_emitter.frameReceived(self.valid_frame)
            self.assertTrue(self.bert_emitter.timer is None)


class TestBertLoopback(unittest.TestCase):
    
    def setUp(self):
        self.clock = task.Clock()
        self.tr = proto_helpers.StringTransport()
        self.valid_frame = '~\x00\x01 \xdf'

        self.bert_loopback = protocol.BertLoopback(.01)
        self.bert_loopback.transport = self.tr

    def test_noEchoBeforeTurnaroundTime(self):
        with mock.patch('twisted.internet.reactor.callLater', new=self.clock.callLater):
            self.bert_loopback.frameReceived(self.valid_frame)
            self.clock.advance(0.0099)
            self.assertEqual(self.tr.value(), '')
            self.tr.clear()
             
    def test_echoAfterTurnaroundTime(self):
        with mock.patch('twisted.internet.reactor.callLater', new=self.clock.callLater):
            self.bert_loopback.frameReceived(self.valid_frame)
            self.clock.advance(0.011)
            self.assertEqual(self.tr.value(), self.valid_frame)
            self.tr.clear()

