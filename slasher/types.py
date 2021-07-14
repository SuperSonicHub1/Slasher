from typing import Dict, Protocol, Generator, Optional, TypedDict

class Message(TypedDict):
    """Partial typing of `chat-downloader`'s chat item dictionary.'"""
    time_in_seconds: Optional[float]


class Chat(Protocol):
    """Basic typing of `chat-downloader`'s unexported `Chat` class.
    TODO: How do I also mark this as being a genrator?"""
    chat: Optional[Generator[Message, None, None]]
    title: Optional[str]
    duration: Optional[float]
    is_live: Optional[bool]
    start_time: Optional[float]


# Key is a number of seconds, value is number of messages
TimeDict = Dict[int, int]
