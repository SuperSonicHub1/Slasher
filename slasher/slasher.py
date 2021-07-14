from dataclasses import dataclass
from datetime import timedelta
from functools import reduce
from math import floor
from operator import itemgetter
from typing import TextIO, List
from xml.dom import minidom

from chat_downloader import ChatDownloader

from .types import Chat, TimeDict

ZERO_SECONDS = timedelta(seconds=0)
TEN_SECONDS = timedelta(seconds=10)

chat_dl = ChatDownloader()
impl = minidom.getDOMImplementation()

@dataclass
class Slasher:
    url: str
    chat: Chat
    intervals: TimeDict
    duration: timedelta = TEN_SECONDS
    delay: timedelta = ZERO_SECONDS

    @staticmethod
    def from_url(url: str,
                 duration: timedelta = TEN_SECONDS,
                 delay: timedelta = ZERO_SECONDS) -> 'Slasher':
        """Generate a Slasher from a `chat-downloader`-compatible URL."""

        chat = chat_dl.get_chat(url)

        intervals: TimeDict = {}

        for item in chat:
            temp_time_in_seconds = item.get('time_in_seconds')

            if temp_time_in_seconds == None:
                continue

            floored_time_in_seconds = floor(temp_time_in_seconds)

            # If the delay causes the message to go under 0, drop it
            if floored_time_in_seconds - delay.seconds <= 0:
                continue

            # Now its a mulitple of {duration}!
            time_in_seconds = floored_time_in_seconds - (
                (floored_time_in_seconds - delay.seconds) % duration.seconds)

            if time_in_seconds in intervals:
                intervals[time_in_seconds] += 1
            else:
                intervals[time_in_seconds] = 1

        return Slasher(url, chat, intervals, duration, delay)

    def average(self) -> int:
        """Get the floored average number of messages in an interval."""
        return reduce(
            lambda x, y: x + y,
            self.intervals.values(),
        ) // len(self.intervals)

    def filter(self, multiplier: float = 2.0) -> 'Slasher':
        """Remove intervals whose number of messages are smaller than the average times {multiplier}."""
        average = self.average()

        filtered_intervals = {
            interval: messages
            for interval, messages in self.intervals.items()
            if messages >= floor(average * multiplier)
        }

        return Slasher(self.url, self.chat, filtered_intervals, self.duration,
                       self.delay)

    def top(self, amount: int = 5) -> 'Slasher':
        """Sort all intervals by message intensity, save the top {amount}, and then resort chronologically."""
        sorted_by_number_of_messages = sorted(self.intervals.items(), key=itemgetter(1), reverse=True)
        truncated_sorted_by_number_of_messages = sorted_by_number_of_messages[:amount]
        chronologically_sorted_items = sorted(truncated_sorted_by_number_of_messages, key=itemgetter(0))
        return Slasher(self.url, self.chat, dict(chronologically_sorted_items), self.duration, self.delay)

    def clip(self, start: timedelta = ZERO_SECONDS, end: timedelta = timedelta.max):
        """Remove intervals outside of a certain time period."""
        clipped_intervals = {
            interval: messages
            for interval, messages in self.intervals.items()
            if interval >= start.seconds and interval <= end.seconds
        }
        return Slasher(self.url, self.chat, clipped_intervals, self.duration,
                       self.delay)

    def to_ffmpeg_filter_complex(self, f: TextIO):
        """Write a FFmpeg filter complex: https://ffmpeg.org/ffmpeg-filters.html.
        Use something like: `ffmpeg -hide_banner -i $IN -filter_complex_script $SCRIPT -map [outv] -map [outa] $OUT`."""
        pairs: List[str] = []
        for index, interval in enumerate(self.intervals.keys()):
            f.write(f"[0:v]trim=start={interval}:end={interval + self.duration.seconds},setpts=PTS-STARTPTS,format=yuv420p[{index}v];\n")
            pairs.append(f"[{index}v]")
            f.write(f"[0:a]atrim=start={interval}:end={interval + self.duration.seconds},asetpts=PTS-STARTPTS[{index}a];\n")
            pairs.append(f"[{index}a]")
        f.write(f"{''.join(pairs)}concat=n={len(self.intervals)}:v=1:a=1[outv][outa]\n")

    def to_ffsilencer(self, f: TextIO):
        """Write a space-separated time and duration format to a text file 
		semi-compatible with FFsilencer: https://github.com/supersonichub1/ffsilencer."""
        for interval in self.intervals.keys():
            f.write(f"{interval} {self.duration.seconds}\n")

    def to_mlt(self, f: TextIO, resource: str = "vod.mp4"):
        """Write an XML document compatible with the MLT Framework and 
		associated editors: https://www.mltframework.org/docs/mltxml/."""
        document = impl.createDocument(None, "mlt", None)

        def create_producer(id_: str = "producer0"):
            producer = document.createElement("producer")
            producer.setAttribute("id", id_)
            property_el = document.createElement("property")
            property_el.setAttribute("name", "resource")
            property_el.appendChild(document.createTextNode(resource))
            producer.appendChild(property_el)
            return producer

        def create_entry(in_: timedelta,
                            out: timedelta,
                            producer: str):
            # print("in create_entry:", producer)
            entry = document.createElement("entry")
            entry.setAttribute("in", str(in_) + ".000")
            entry.setAttribute("out", str(out) + ".000")
            entry.setAttribute("producer", producer)
            return entry

        def intervals_to_entries(producer: str = "producer0") -> list:
            entries = []
            for interval in self.intervals.keys():
                in_ = timedelta(seconds=interval)
                out = in_ + self.duration
                entries.append(create_entry(in_, out, producer))

            return entries

        def create_playlist(entries: list, id_: str = "playlist0"):
            playlist = document.createElement("playlist")
            playlist.setAttribute("id", id_)
            for entry in entries:
                playlist.appendChild(entry)
            return playlist

        entries = intervals_to_entries()
        playlist = create_playlist(entries)

        mlt = document.documentElement
        mlt.setAttribute("title", "VODinator verson 2021.07.14")

        mlt.appendChild(create_producer())
        mlt.appendChild(playlist)

        document.writexml(f)


# Extra guffins from when this was a script
"""
# Duration for Twitch extractor is in seconds
print(chat.duration)

messages = list(chat)
number_of_messages = len(messages)
message_rate = number_of_messages / (chat.duration or 1)

# About 1.7 messages a second! That's crazy!
print(f"Number of messages: {number_of_messages} || Rate: {message_rate} messages per second")
"""
