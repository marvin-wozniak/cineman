from datetime import datetime, time, timedelta
import sqlite3
from typing import List, Optional

from src.models import Cinema, Movie, Screening


class DatabaseManager:

    def __init__(self, db_path: str = "cineman.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Crée et retourne une connexion à la base SQL."""
        conn = sqlite3.connect(self.db_path)
        # Active le support des clés étrangères dans SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Crée les tables si elles n'existent pas encore."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Table des films
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    director TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    runtime INTEGER NOT NULL
                );
            """)

            # Table des cinémas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cinemas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    address TEXT,
                    google_maps_url TEXT
                );
            """)

            # Table des séances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_id INTEGER NOT NULL,
                    cinema_id INTEGER NOT NULL,
                    date_time TEXT NOT NULL,
                    is_projected BOOLEAN NOT NULL DEFAULT 0,
                    end_time TEXT,
                    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
                    FOREIGN KEY (cinema_id) REFERENCES cinemas (id) ON DELETE CASCADE
                );
            """)
            conn.commit()

    # --- CRUD MOVIES ---

    def add_movie(self, movie: Movie) -> Movie:
        """Insère un film en base de données et retourne l'objet avec son ID généré."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO movies (title, director, year, runtime)
                VALUES (?, ?, ?, ?)
                """,
                (movie.title, movie.director, movie.year, movie.runtime),
            )
            conn.commit()
            movie.id = cursor.lastrowid
            return movie

    def get_all_movies(self) -> List[Movie]:
        """Récupère tous les films sous forme d'objets Movie."""
        movies = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, director, year, runtime FROM movies ORDER BY title"
            )
            rows = cursor.fetchall()

            for row in rows:
                movie = Movie(
                    id=row[0],
                    title=row[1],
                    director=row[2],
                    year=row[3],
                    runtime=row[4],
                )
                movies.append(movie)
        return movies

    def delete_movie(self, movie_id: int) -> None:
        """Supprime un film (et ses séances associées via ON DELETE CASCADE)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
            conn.commit()

        self.cleanup_old_projected_screenings()

    # --- NETTOYAGE AUTOMATIQUE (-5 JOURS) ---
    def cleanup_old_projected_screenings(self, days: int = 5) -> int:
        """"Supprime les séances vues dont la date remonte à plus de 'days' jours """
        cutoff_date = datetime.now() - timedelta(days=days)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM screenings
                WHERE is_projected = 1 AND date_time < ?
                """,
                (cutoff_date.isoformat(),),
            )
            deleted_count = cursor.rowcount
            conn.commit()
            if deleted_count > 0:
                print(f"[BDD] Nettoyage automatique : {deleted_count} ancienne(s) séance(s) vue(s) supprimée(s).")

   # --- ANTI-CHEVAUCHEMENT / CONCURRENCE ---

    def check_screenings_conflict(self, new_screening: Screening) -> Optional[Screening]:
        """
        Vérifie si la nouvelle séance chevauche une séance existante.
        Retourne la seéance en conflit si trouvée, sinon None.
        """
        ads_margin = 15

        start_a = new_screening.date_time
        if isinstance(start_a, str):
            start_a = datetime.fromisoformat(start_a)

        duration_a = new_screening.movie.runtime + ads_margin
        end_a = start_a + timedelta(minutes=duration_a)

        print("\n=== [DEBUG LOG] NOUVELLE SÉANCE ===")
        print(f"Film : {new_screening.movie.title}")
        print(f"Début A : {start_a} | Fin A : {end_a}")

        existing_screenings = self.get_all_screenings()
        print(f"Séances en BDD trouvées : {len(existing_screenings)}")

        for s in existing_screenings:
            start_b = s.date_time
            if isinstance(start_b, str):
                start_b = datetime.fromisoformat(start_b)

            duration_b = s.movie.runtime + ads_margin
            end_b = start_b + timedelta(minutes=duration_b)

            is_overlap = (start_a < end_b) and (end_a > start_b)

            print(f"--- Comparaison avec ID {s.id} ({s.movie.title}) ---")
            print(f"  Début B : {start_b} | Fin B : {end_b}")
            print(f"  {start_a} < {end_b} ? -> {start_a < end_b}")
            print(f"  {end_a} > {start_b} ? -> {end_a > start_b}")
            print(f"  CONFLIT DÉTECTÉ ? -> {is_overlap}")

            if is_overlap:
                print("===================================\n")
                return s

        print("===================================\n")
        return None
    

        
        
   
   
    # --- CRUD CINEMAS ---

    def add_cinema(self, cinema: Cinema) -> Cinema:
        """Insère un cinéma en base de données."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO cinemas (name, address, google_maps_url)
                VALUES (?, ?, ?)
                """,
                (cinema.name, cinema.address, cinema.google_maps_url),
            )
            conn.commit()
            cinema.id = cursor.lastrowid
            return cinema

    def get_all_cinemas(self) -> List[Cinema]:
        """Récupère tous les cinémas sous forme d'objets Cinema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, address, google_maps_url FROM cinemas ORDER BY name"
            )
            rows = cursor.fetchall()

        return [
            Cinema(
                id=row[0], name=row[1], address=row[2], google_maps_url=row[3]
            )
            for row in rows
        ]

    # --- CRUD SCREENINGS ---

    def add_screening(self, screening: Screening) -> Screening:
        """Insère une séance en base de données."""
        if screening.movie.id is None:
            raise ValueError(
                "Le film associé doit posséder un ID avant d'ajouter une séance."
            )

        if screening.cinema.id is None:
            raise ValueError("Le cinéma associé doit posséder un ID.")

        #Vérification des conflits d'horaires
        conflict = self.check_screenings_conflict(screening)
        if conflict:
            c_start = conflict.date_time.strftime("%Hh%M") if isinstance(conflict.date_time, datetime) else conflict.date_time
            c_end = (conflict.calculate_end_time()).strftime("%Hh%M")
            raise ValueError(
                f"Conflit d'horaire : la séance chevauche '{conflict.movie.title}'"
                f"au {conflict.cinema.name} ({c_start} - {c_end})"
            )

        screening.end_time = screening.calculate_end_time()





    

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO screenings (movie_id, cinema_id, date_time, is_projected, end_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    screening.movie.id,
                    screening.cinema.id,
                    screening.date_time.isoformat(),
                    1 if screening.is_projected else 0,
                    screening.end_time.isoformat(),
                ),
            )
            conn.commit()
            screening.id = cursor.lastrowid
            return screening

    def get_all_screenings(self) -> List[Screening]:
        """Récupère toutes les séances enregistrées avec leur film et cinéma associés."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id, s.date_time, s.is_projected, s.end_time,
                    m.id, m.title, m.director, m.year, m.runtime,
                    c.id, c.name, c.address, c.google_maps_url
                FROM screenings s
                JOIN movies m ON s.movie_id = m.id
                JOIN cinemas c ON s.cinema_id = c.id
                ORDER BY s.date_time ASC
            """)
            rows = cursor.fetchall()

        screenings = []
        for row in rows:
            movie = Movie(
                id=row[4],
                title=row[5],
                director=row[6],
                year=row[7],
                runtime=row[8],
            )

            cinema = Cinema(
                id=row[9], name=row[10], address=row[11], google_maps_url=row[12]
            )
            date_time_obj = datetime.fromisoformat(row[1])

            screening = Screening(
                id=row[0],
                movie=movie,
                cinema=cinema,
                date_time=date_time_obj,
                is_projected=bool(row[2]),
                end_time=datetime.strptime(row[3], "%H:%M:%S").time()
                if row[3]
                else None,
            )
            screenings.append(screening)

        return screenings

    def mark_screening_as_projected(
        self, screening_id: int, is_projected: bool = True
    ) -> None:
        """Met à jour le statut de visionnage d'une séance."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE screenings SET is_projected = ? WHERE id = ?",
                (1 if is_projected else 0, screening_id),
            )
            conn.commit()

    def delete_screening(self, screening_id: int) -> None:
        """Supprime une séance de la base de données."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM screenings WHERE id = ?", (screening_id,)
            )
            conn.commit()