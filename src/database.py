import sqlite3
from typing import Optional
from src.models import Movie, Screening
from datetime import datetime, time

class DatabaseManager:
    def __init__(self, db_path: str = "cineman.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Crée et retourne une connection à la base SQL"""
        conn = sqlite3.Connection(self.db_path)
        # Permet d'acriver le support des clés étranger dans SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        """Créee les tables si elles n'existent pas encore."""
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

            # Table des séances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_id INTEGER NOT NULL,
                    cinema TEXT NOT NULL,
                    date_time TEXT NOT NULL,
                    is_projected BOOLEAN NOT NULL DEFAULT 0,
                    end_time TEXT,
                    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
                );
            """)
            conn.commit()

    def add_movie(self, movie: Movie) -> Movie:
        """Insère un film en base de données et retourne l'objet avec son ID généré"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO movies (title, director, year, runtime)
                VALUES (?,?,?,?)
                """,
                (movie.title, movie.director, movie.year, movie.runtime)
            )
            conn.commit()
            movie.id = cursor.lastrowid
            return movie

    def get_all_movies(self) -> list[Movie]:
      """Récupère tous les films de la base de donnée sous forme d'objet Movie"""
      movies = []
    
      with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, director, year, runtime FROM movies")
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

    def add_screening(self, screening: Screening) -> Screening:
        """Insère une séance en base de données."""
        if screening.movie.id is None:
            raise ValueError("Le film associé doit posséder un ID avant d'ajouter une séance.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO screenings (movie_id, cinema, date_time, is_projected, end_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                  screening.movie.id,
                  screening.cinema,
                  screening.date_time.isoformat(),
                  1 if screening.is_projected else 0,
                  screening.end_time.isoformat() if screening.end_time else None,  
                ),
            )
            conn.commit()
            screening.id =cursor.lastrowid
            return screening



    #fonction qui sert à enregister les séances / et à les afficher 
    def get_all_screenings(self) -> list[Screening]:
        """Récupère toutes les séances enregistrées avec leur film associé"""
        #on crée une liste pour la remplir plus tard
        screenings = []
        #je ne serais pas excatement dire ce que cela fait mais je pense que dans la base de donnée nous lion la table screening à la table movie, à partir du film movie 
        query = """
            SELECT 
            s.id, s.cinema, s.date_time, s.is_projected, s.end_time,
            m.id, m.title, m.director, m.year, m.runtime
        FROM screenings s
        JOIN movies m ON s.movie_id = m.id
        ORDER BY s.date_time ASC
        """
        # j'aimerai bien que tu m'explique étape par étape ce que fais ce "with" en m'expliquant bien ce qu'est le "cursor"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
            # Reconstitution de l'objet Movie à partir de la jointure
                movie = Movie(
                    id=row[5],
                    title=row[6],
                    director=row[7],
                    year=row[8],
                    runtime=row[9],
                )

                # Conversion du texte ISO en objets Python datetime et time
                date_time_obj = datetime.fromisoformat(row[2])
                end_time_obj= time.fromisoformat(row[4]) if row[4] else None

                # Reconstituttion de la séance

                screening = Screening(
                    id=row[0],
                    cinema=row[1],
                    date_time=date_time_obj,
                    is_projected=bool(row[3]),
                    end_time=end_time_obj,
                    movie=movie,
            )
            screenings.append(screening)
        return screenings
 