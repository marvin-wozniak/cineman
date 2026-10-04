import os
from pathlib import Path
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"


load_dotenv(dotenv_path=env_path, encoding="utf-8")



class TMDBClient:
  BASE_URL = "https://api.themoviedb.org/3"

  def __init__(self):
    self.api_key = os.getenv("TMDB_API_KEY")

  def search_movies(self, query: str) -> List[Dict]:
    """ Cherche des films par titre et renvoie les 5 premiers résultats"""
    if not query:
      return []

    url = f"{self.BASE_URL}/search/movie"
    params = {
      "api_key": self.api_key,
      "query": query,
      "language": "fr-FR"
    }

    try:
      response = requests.get(url, params=params)
      if response.status_code == 200:
        return response.json().get("results", [])[:5]
    except Exception as e:
      print(f"Erreur lors de la recherche TMDB : {e}")
    return []

  def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
    """ Récupère les détails d'un film (durée, réal, affiche, année)."""
    params = {
      "api_key": self.api_key,
      "language": "fr-FR"

    }

    try:
      res_details = requests.get(f"{self.BASE_URL}/movie/{tmdb_id}", params=params).json()

      res_credits = requests.get(f"{self.BASE_URL}/movie/{tmdb_id}/credits", params=params).json()

      director = "Inconnu"
      for crew in res_credits.get("crew", []):
        if crew.get("job") == "Director":
          director = crew.get("name")
          break

      release_date = res_details.get("release_date", "")
      year = int(release_date[:4]) if release_date else None

      return {
        "title": res_details.get("title"),
        "director":director,
        "year": year,
        "runtime": res_details.get("runtime", 0),
        "poster_path": res_details.get("poster_path")
      }
    except Exception as e:
      print(f"Erreur lors de la récupération des détails TMDB: {e}")
      return None 