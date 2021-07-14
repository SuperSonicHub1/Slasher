from slasher import Slasher
from datetime import timedelta

# Works with Twitch, YouTube, Facebook...
# In this case, we use a Nyanners VOD
s = Slasher.from_url("https://www.twitch.tv/videos/1080642970")

# Let's not keep any intervals that as 3 times
# as active as other ones  
s = s.filter(3)

# Finally, we can write some MLT-compatible XML
# to a file
with open("intervals.mlt", "w") as f:
	s.to_mlt(f)
