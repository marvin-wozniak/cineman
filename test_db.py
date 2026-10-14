from src.database import DatabaseManager
from src.tmdb import TMDBClient

db = DatabaseManager()  # Va recréer cineman.db proprement
tmdb = TMDBClient()

# Récupère Les Affranchis (ID 769)
details = tmdb.get_movie_details(769)
if details:
  details["tmdb_id"] = 769
  db.add_movie(details)
if db.add_movie(details):
    print("Film ajouté avec succès !")

movies = db.get_all_movies()
print("\n--- Contenu actuel de la base SQLite ---")
for movie in movies:
  print(movie)