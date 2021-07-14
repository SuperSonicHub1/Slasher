# Slasher
A commmand-line tool and Python library for autonomous editing of livestreams via live chat activity.

Through *Slasher*, __you__ (the chat member, not the creator) are the editor of the livestream! Through an
ultra-simple algorithm, portions of a livestream where chat is unusually active are kept and concatenated
together. This allows for the speedy (we are just downloading, processing, and creating text afterall)
creation of highlights that your audience directly finds enjoying. Personally, I think that the highlights
that my tool creates are quite fun to watch, and I at times forgot that they were created via a computer
program!

Because of the nature of *Slasher*, the algorithm can occasionally cut off speech, take out chunks of 
long-running moments (singing), leave intervals without context. Luckily, *Slasher* can output project files
compatible with video editors so that the editor is fully in control and can quickly integrate the tool
into their workflow. *Slasher* will not be appropriate for all livestreams and editors,
but it does what it can do really well and attempts to give the end-user as much control as they please!

With default settings (2x multiplier, 10-second intervals, zero delay), *Slasher*'s filter mode can turn
about one hour of content into seven minutes, making it easy to watch a two-or-three hour live stream during
a lunch break, and quickly consume an 8-hour live stream in under an hour. Can't justify watching or editing
a 24-hour livestream? Now you can! Don't care about occasionally awkward edits and just want a half-hour
highlight half an hour after your livestream ends to get those sweet views? Be my guest!
The possibilites with my tool should be quite endless, so go crazy!

## Installation
As a developer, clone the project and run `poetry install`. Instructions for normal users coming soon!

## Usage

### Command-Line Interface
```
usage: slasher [-h] [--format {ffmpeg,ffsilencer,mlt}] [--output OUTPUT]
               [--duration DURATION] [--delay DELAY] [--start START]
               [--end END]
               {filter,top} ...

Leave the noise of VODs on the cutting room floor.

positional arguments:
  {filter,top}
    filter              remove intervals of a stream that don't meet a certain
                        comment threshold
        positional arguments:
          url                   a chat-downloader-compatible URL

        optional arguments:
          --multiplier MULTIPLIER, -m MULTIPLIER
                                intervals must have a number of messages greater than
                                the average times this (default: 2)

    top                 pick the top intervals from a stream sorted by
                        messages
        positional arguments:
          url                   a chat-downloader-compatible URL

        optional arguments:
          --amount AMOUNT, -a AMOUNT
                                 number of intervals you want to keep

optional arguments:
  -h, --help            show this help message and exit
  --format {ffmpeg,ffsilencer,mlt}, -f {ffmpeg,ffsilencer,mlt}
                        what output you want (default: mlt)
  --output OUTPUT, -o OUTPUT
                        where the format will be written to (default: stdout)
  --duration DURATION   how long an interval should be, uses Python's
                        timedelta syntax (default: ten seconds)
  --delay DELAY         how far back messages should be pushed back, used to
                        sync chat with stream, uses Python's timedelta syntax
                        (default: zero seconds)
  --start START         capture messages from this time, uses Python's
                        timedelta syntax (default: zero seconds)
  --end END             capture messages to this time, uses Python's timedelta
                        syntax (default: timedelta.max)
```

### Python Library
The entirety of Slasher sans the command line app is less than 150 lines,
is fully typed, and has docstrings that give you the gist of what each function does,
so just [read it](./slasher/slasher.py)!

## Examples
Slasher comes with sensible defaults, so usage is as basic as:
```bash
python -m slasher filter https://www.twitch.tv/videos/1080642970
python -m slasher top https://www.twitch.tv/videos/1080642970
```
```python
from slasher import Slasher
s = Slasher.from_url("https://www.twitch.tv/videos/1080642970")
s = s.filter()
```

If you want to write your results to a file:
```bash
python -m slasher --output intervals.mlt filter https://www.twitch.tv/videos/1080642970
```
```python
with open("intervals.mlt", "w") as f:
    s.to_mlt(f)
```

For more examples of Python lib usage, see [examples/](./examples/)

## Formats
### [MLT XML](https://www.mltframework.org/docs/mltxml/)
CLI: `--format mlt`

Python: `Slasher.to_mlt`

This is an [XML document](https://en.wikipedia.org/wiki/XML) format compatible with the open-source
multimedia framework MLT, and can be opened in 
[compatible video editors](https://www.mltframework.org/projects/) such as [Shotcut](https://shotcut.com/).
I have no plans to support other video editors as most are expensive or are exclusive to macOS. 

## [FFsilencer](https://github.com/supersonichub1/ffsilencer)
CLI: `--format ffsilencer`

Python: `Slasher.to_ffsilencer`

This is a basic plain-text format with a timesecond in seconds on the left and a duration in seconds on the
right, like `2550 10`. This is inspired by a Bash script I wrote to remove silence from videos with FFmpeg.
Until I add some sort of "custom" option to FFsilencer, advanced users can feel free to download and use
[a modified version of FFsilencer](./slasher.bash) I made for this project.

## [FFmpeg Filter Complex](https://ffmpeg.org/ffmpeg-filters.html)
__!FOR ADVANCED USERS!__

CLI: `--format ffmpeg`

Python: `Slasher.to_ffmpeg_filter_complex`

This is an implementation of FFsilencer's filter complex creator in Python. The video and audio streams
used are `[outv]` and `[outa]` respectively. With FFmpeg, use it like this:
```bash
ffmpeg -hide_banner -i $IN -filter_complex_script $SCRIPT -map [outv] -map [outa] $OUT
```

## Resources
For info on how `timedelta` works, see [the Python docs](https://docs.python.org/3/library/datetime.html#datetime.timedelta).
To see what sites *Slasher* supports, see [Chat Downloader](https://github.com/xenova/chat-downloader/#supported-sites)

## License
https://unlicense.org/
