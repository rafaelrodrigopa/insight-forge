from dataclasses import dataclass


@dataclass
class CollectedContent:

    title: str
    content: str
    source: str
    url: str