import argparse

from twisted.internet import reactor

__all__ = ['main']

# sub-command functions
def emitter(args):
    print(args.x * args.y)


def loopback(args):
    print('((%s))' % args.z)


def get_parser():
    """
    Creates an argument parser for collecting the available options.

    Currently has alot of duplicate calls. One day I will figure out
    how to get argparse to do my bidding. Just not today ...

    Returns:
     parser: The CLI argument parser.
    """
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the "emitter" command
    parser_emitter = subparsers.add_parser('emitter')
    parser_emitter.add_argument('-S', '--stream', type=str)
    parser_emitter.add_argument('-b', '--baud', type=int, default=9600)
    parser_emitter.add_argument('-p', '--parity', type=str, default='none')
    parser_emitter.add_argument('-d', '--databits', type=int, default=8)
    parser_emitter.add_argument('-s', '--stopbits', type=int, default=1)
    parser_emitter.set_defaults(func=emitter)

    # create the parser for the "bar" command
    parser_loopback = subparsers.add_parser('loopback')
    parser_loopback.add_argument('-t', '--turnaround', type=float, help="")
    parser_loopback.add_argument('device', type=str)
    parser_loopback.set_defaults(func=loopback)

    return parser


def main():
    """
    Main entry point for Bert.

    Really, just handles args, and kicks off twisted's event loop
    """
    parser = get_parser()
     # parse the args and call whatever function was selected
    args = parser.parse_args('foo 1 -x 2'.split())
    args.func(args)
    print parser.parse_args()


if __name__ == '__main__':
    main()

