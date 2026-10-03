import sys
from pathlib import Path

# Fix du chemin d'import
src_path = Path(__file__).resolve().parent / "src"
sys.path.append(str(src_path))

from tmdb import TMDBClient

client = TMDBClient()

print("--- Recherche ---")
results = client.search_movies("Les Affranchis")
for movie in results:
  print(
      f"{movie['title']} ({movie.get('release_date', '')[:4]}) - ID:"
      f" {movie['id']}"
  )

if results:
  first_id = results[0]["id"]
  print("\n--- Détails du premier résultat ---")
  details = client.get_movie_details(first_id)
  print(details)