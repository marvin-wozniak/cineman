import os
from pathlib import Path
import requests
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, encoding="utf-8")


class TMDBClient:
  BASE_URL = "https://api.themoviedb.org/3"

  def __init__(self):
    self.api_key = os.getenv("TMDB_API_KEY")
    self.base_url = self.BASE_URL

  def _extract_year(self, date_str: str) -> str:
    """Extrait l'année (4 chiffres) d'une chaîne de date TMDB."""
    if date_str and isinstance(date_str, str) and len(date_str) >= 4:
      return date_str[:4]
    return "N/A"

  def search_movies(self, query: str) -> list:
    url = f"{self.base_url}/search/movie"
    params = {"api_key": self.api_key, "query": query, "language": "fr-FR"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
      results = response.json().get("results", [])
      formatted_results = []

      for m in results[:5]:
        movie_id = m.get("id")
        title = m.get("title")
        raw_date = m.get("release_date") or m.get("first_air_date", "")

        year = self._extract_year(raw_date)

        formatted_results.append({
          "id": movie_id,
          "title": title,
          "year": year,
        })
      return formatted_results
    return []

  def get_movie_details(self, movie_id: int) -> dict:
    url = f"{self.base_url}/movie/{movie_id}"
    params = {
      "api_key": self.api_key,
      "language": "fr-FR",
      "append_to_response": "credits",
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
      data = response.json()
      raw_date = data.get("release_date", "")
      year_str = self._extract_year(raw_date)
      year = int(year_str) if year_str.isdigit() else None

      director = "Inconnu"
      credits = data.get("credits", {})
      crew = credits.get("crew", [])
      for member in crew:
        if member.get("job") == "Director":
          director = member.get("name")
          break

      return {
        "tmdb_id": data.get("id"),
        "title": data.get("title"),
        "director": director,
        "year": year,
        "runtime": data.get("runtime"),
        "poster_path": data.get("poster_path"),
      }
    return {}