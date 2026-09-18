from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional


@dataclass
class Movie:
    title: str
    director: str
    year: int
    runtime: int #durée en minute
    id:Optional[int] = None

@dataclass
class Cinema:
    name: str
    address: Optional[str] = None
    google_maps_url: Optional[str] = None
    id: Optional[int] = None 

@dataclass
class Screening:
    movie: Movie
    cinema: Cinema
    date_time: datetime
    is_projected: bool = False
    end_time: Optional[time] = None
    id:Optional[int] = None

    def calculate_end_time(self, ads_duration_minutes: int = 15) -> time:
        """Calcule l'heure de fin théorique de la séance en comptant la durée du film + les publicités"""
        total_duration = self.movie.runtime + ads_duration_minutes
        end_datetime = self.date_time + timedelta(minutes=total_duration)
        return end_datetime.time()