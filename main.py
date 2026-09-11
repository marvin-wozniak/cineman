from datetime import datetime
from src.database import DatabaseManager
from src.models import Screening

# 1. Connexion à la base Cineman
db = DatabaseManager("cineman.db")

# 2. Récupération du film existant
movies = db.get_all_movies()
if movies:
    movie = movies[0]  # On prend le premier film (ex: Pusher)

    # 3. Création et enregistrement d'une séance au Quartier Latin
    screening = Screening(
        movie=movie,
        cinema="La Filmothèque du Quartier Latin",
        date_time=datetime(2026, 9, 18, 20, 0),
    )

    saved_screening = db.add_screening(screening)
    print(f"-> Séance ajoutée avec l'ID : {saved_screening.id}")

# 4. Affichage de toutes les séances programmées
all_screenings = db.get_all_screenings()
print("\n--- Planning des Séances ---")
for s in all_screenings:
    formatted_date = s.date_time.strftime("%d/%m/%Y à %Hh%M")
    print(
        f"[{s.id}] {s.movie.title} - {s.cinema} le {formatted_date} (Vu : {s.is_projected})"
    )