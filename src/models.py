from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional
import streamlit as st
import streamlit.components.v1 as components

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


MOIS_FR = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril",
    5: "mai", 6: "juin", 7: "juillet", 8: "août",
    9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

JOURS_FR = {
    0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
    4: "Vendredi", 5: "Samedi", 6: "Dimanche"
}

def format_date_fr(dt: datetime) -> str:
    """
    Formate un objet datetime au format français : 'Jeudi 1er octobre à 20h00'
    """
    jour_nom = JOURS_FR[dt.weekday()]
    
    # Gestion du '1er' pour le premier jour du mois
    jour_num = "1er" if dt.day == 1 else str(dt.day)
    
    mois_nom = MOIS_FR[dt.month]
    heure = dt.strftime("%HH%M").replace("H00", "h00").replace("H", "h")
    
    return f"{jour_nom} {jour_num} {mois_nom} à {heure}"




