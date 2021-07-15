from argparse import ArgumentParser, FileType
from datetime import timedelta
from sys import stdout
from typing import Any

from slasher import Slasher, TEN_SECONDS, ZERO_SECONDS

FORMATS = ('ffmpeg', 'ffsilencer', 'mlt')

def parse_timedelta(string: str) -> timedelta:
    return eval(string, {"timedelta":  timedelta})

parser = ArgumentParser(prog="slasher", description="Leave the noise of VODs on the cutting room floor.")

def add_url(parser: ArgumentParser):
    parser.add_argument("url", type=str, help="a chat-downloader-compatible URL")

def is_timedelta(delta: Any) -> bool:
    return isinstance(delta, timedelta)

# Global arguments
parser.add_argument("--format", "-f", choices=FORMATS, default="mlt", help="what output you want (default: mlt)")
parser.add_argument('--output', '-o',  help="where the format will be written to (default: stdout)", type=FileType('w'), default=stdout)
parser.add_argument("--duration", type=str, default=None, help="how long an interval should be, uses Python's timedelta syntax (default: ten seconds)")
parser.add_argument("--delay", type=str, default=None, help="how far back messages should be pushed back, used to sync chat with stream, uses Python's timedelta syntax (default: zero seconds)")
parser.add_argument("--start", type=str, default=None, help="capture messages from this time, uses Python's timedelta syntax (default: zero seconds)")
parser.add_argument("--end", type=str, default=None, help="capture messages to this time, uses Python's timedelta syntax (default: timedelta.max)")
parser.add_argument('--resource', "-r", help="The name of your resource, only works with `-f mlt` (default: 'vod.mp4')", type=str, default="vod.mp4")

# Sub-commands
subparsers = parser.add_subparsers(dest='subparser')

filter_parser = subparsers.add_parser("filter", help="remove intervals of a stream that don't meet a certain comment threshold")
add_url(filter_parser)
filter_parser.add_argument("--multiplier", "-m", type=float, default=2.0, help="intervals must have a number of messages greater than the average times this (default: 2)")

top_parser = subparsers.add_parser("top", help="pick the top intervals from a stream sorted by messages")
add_url(top_parser)
top_parser.add_argument("--amount", "-a", type=int, default=5, help="number of intervals you want to keep")

# Execution
args = parser.parse_args()

duration = parse_timedelta(args.duration) if args.duration else TEN_SECONDS
delay = parse_timedelta(args.delay) if args.delay else ZERO_SECONDS
assert is_timedelta(duration)
assert is_timedelta(delay)

s = Slasher.from_url(args.url, duration=duration, delay=delay)

if args.start or args.end:
    start = parse_timedelta(args.start) if args.start else ZERO_SECONDS
    end = parse_timedelta(args.end) if args.start else timedelta.max
    assert is_timedelta(start)
    assert is_timedelta(end)
    s = s.clip(start=start, end=end)

if args.subparser == "filter":
    s = s.filter(args.multiplier)
elif args.subparser == "top":
    s = s.top(args.amount)

if args.format == "mlt":
    with args.output as f:
	    s.to_mlt(f, resource=args.resource)
elif args.format == "ffmpeg":
    with args.output as f:
	    s.to_ffmpeg_filter_complex(f)
elif args.format == "ffsilencer":
    with args.output as f:
	    s.to_ffsilencer(f)
