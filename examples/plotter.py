"""Plot chat activity over time using Matplotlib."""

from slasher import Slasher
import matplotlib.pyplot as plt

s = Slasher.from_url("https://www.twitch.tv/videos/1080642970")
average_messages_per_interval = s.average()

fig, ax = plt.subplots()
ax.plot(s.intervals.keys(), s.intervals.values())

keys = list(s.intervals.keys())

ax.hlines(
	average_messages_per_interval,
	keys[0],
	keys[-1],
	color="red",
	linestyles="dashed",
	label="Average messages per interval"
)

ax.set(xlabel='Invervals (s)', ylabel='Messages', title=f'Messages from "{s.chat.title}" Over Time')
ax.grid()

plt.show()
