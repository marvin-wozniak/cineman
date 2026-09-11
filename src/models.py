from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass
class Movie:
    title: str
    director: str
    year: int
    runtime: int #durée en minute
    id:Optional[int] = None

@dataclass
class Screening:
    movie: Movie
    cinema: str
    date_time: datetime
    is_projected: bool = False
    end_time: Optional[time] = None
    id:Optional[int] = None