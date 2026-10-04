import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from src.tmdb import TMDBClient

client = TMDBClient()
print("Clé détectée :", client.api_key)

print("--- Test Recherche TMDB ---")
results =client.search_movies("Les Affranchis")
for movie in results:
  print(
    f"- {movie['title']} ({movie.get('release_date', '')[:4]} | ID:)"
    f" {movie['id']}"
  )

if results:
  first_id = results[0]["id"]
  print("\n--- Test Détails du premier résultat ---")
  details = client.get_movie_details(first_id)
  print(details)