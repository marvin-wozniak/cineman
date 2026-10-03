import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

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