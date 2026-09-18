from datetime import date, datetime, time
import streamlit as st

from src.database import DatabaseManager
from src.models import Movie, Screening

# Configuration de la page Streamlit
st.set_page_config(page_title="Cineman", page_icon="🎬", layout="wide")

# Initialisation du gestionnaire de BDD
db = DatabaseManager("cineman.db")

st.title("🎬 Cineman — Programmation Répertoire")

# Navigation par onglets
tab_planning, tab_add_screening, tab_add_movie = st.tabs(
    ["📅 Planning", "➕ Ajouter une séance", "🎥 Ajouter un film"]
)

# -------------------------------------------------------------------
# ONGLET 1 : Planning des séances
# -------------------------------------------------------------------
with tab_planning:
    st.header("Séances à venir")

    screenings = db.get_all_screenings()

    if not screenings:
        st.info("Aucune séance programmée pour le moment.")
    else:
        for s in screenings:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    # Correction ici : s.movie.title sans parenthèses
                    st.subheader(s.movie.title)
                    st.caption(
                        f"De {s.movie.director} ({s.movie.year}) — {s.movie.runtime} min"
                    )
                with col2:
                    formatted_date = s.date_time.strftime("%d/%m/%Y à %Hh%M")
                    st.write(f"📍 **{s.cinema}**")
                    st.write(f"🕒 {formatted_date}")
                with col3:
                    if s.is_projected:
                        st.success("Vu ✅")
                    else:
                        st.warning("À voir 🍿")
                st.divider()

# -------------------------------------------------------------------
# ONGLET 2 : Ajouter une séance
# -------------------------------------------------------------------
with tab_add_screening:
    st.header("Programmer une séance")

    movies = db.get_all_movies()

    if not movies:
        st.warning(
            "Veuillez d'abord ajouter au moins un film dans l'onglet 'Ajouter un film'."
        )
    else:
        movie_options = {f"{m.title} ({m.director})": m for m in movies}

        with st.form("add_screening_form"):
            selected_movie_label = st.selectbox(
                "Film", list(movie_options.keys())
            )
            cinema = st.text_input(
                "Cinéma", placeholder="ex: Le Champo, Reflet Médicis..."
            )

            col_date, col_time = st.columns(2)
            with col_date:
                # Utilisation explicite de date.today()
                screening_date = st.date_input("Date", value=date.today())
            with col_time:
                # Utilisation explicite d'un objet time
                screening_time = st.time_input("Heure", value=time(20, 0))

            submit_screening = st.form_submit_button("Enregistrer la séance")

            if submit_screening:
                if not cinema.strip():
                    st.error("Le nom du cinéma est obligatoire.")
                else:
                    selected_movie = movie_options[selected_movie_label]

                    # Combinaison sécurisée de la date et de l'heure
                    full_datetime = datetime.combine(
                        screening_date, screening_time
                    )

                    new_screening = Screening(
                        movie=selected_movie,
                        cinema=cinema.strip(),
                        date_time=full_datetime,
                    )
                    db.add_screening(new_screening)
                    st.success(
                        f"Séance pour '{selected_movie.title}' au {cinema} ajoutée avec succès !"
                    )
                    st.rerun()

# -------------------------------------------------------------------
# ONGLET 3 : Ajouter un film
# -------------------------------------------------------------------
with tab_add_movie:
    st.header("Ajouter un nouveau film")

    with st.form("add_movie_form"):
        title = st.text_input("Titre du film")
        director = st.text_input("Réalisateur")

        col_year, col_runtime = st.columns(2)
        with col_year:
            year = st.number_input(
                "Année de sortie", min_value=1895, max_value=2030, value=2024
            )
        with col_runtime:
            runtime = st.number_input(
                "Durée (en minutes)", min_value=1, max_value=600, value=100
            )

        submit_movie = st.form_submit_button("Enregistrer le film")

        if submit_movie:
            if not title.strip() or not director.strip():
                st.error("Le titre et le réalisateur sont obligatoires.")
            else:
                new_movie = Movie(
                    title=title.strip(),
                    director=director.strip(),
                    year=int(year),
                    runtime=int(runtime),
                )
                db.add_movie(new_movie)
                st.success(f"Film '{title}' enregistré avec succès !")
                st.rerun()