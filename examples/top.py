from slasher import Slasher
from datetime import timedelta

# Let's have each interval be a minute long
s = Slasher.from_url("https://www.twitch.tv/videos/1080642970", duration=timedelta(minutes=1))

# Inclusively keep intervals between 3 and 4 hours
s = s.clip(start=timedelta(hours=3), end=timedelta(hours=4)) 

# Let's just take the ten best clips and keep them in chronological order
# 10 intervals * 60 seconds = 10-minute edit
s = s.top(10)

with open("intervals.mlt", "w") as f:
	s.to_mlt(f)
