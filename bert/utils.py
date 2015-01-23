"""
Useful utilities.
"""
__all__ = ['coroutine', 'BlockRead']

def coroutine(func):
    """
    A coroutine decorator. Kicks off a generator by callings its
    next method.
    """
    def start(*args, **kwargs):
        coroutine = func(*args, **kwargs)
        coroutine.next()
        return coroutine
    return start

@coroutine
def Flatten(target):
    """
    Given a stream chunk of arbitrary length, delivers this chunk to a target
    coroutine byte-per-byte.

    'chunk' -> Flatten -> 'c', 'h', 'u', 'n', 'k' -> target

    Useful in data pipelines containing routines that depend on receiving
    data in a serial, byte-oriented fashion.
    """
    while True:
        for byte in itertools.chain( (yield) ):
            target.send(byte)

def BlockRead(file_handle, block_size):
    while True:
        block = file_handle.read(block_size)
        if not block:
            break
        yield block


