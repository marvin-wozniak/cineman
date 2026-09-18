from datetime import date, datetime, time
import urllib.parse
import streamlit as st

from src.database import DatabaseManager
from src.models import Cinema, Movie, Screening
from src.notifier import notify_screening_created

# Configuration de la page Streamlit
st.set_page_config(page_title="Cineman", page_icon="🎬", layout="wide")

# Initialisation du gestionnaire BDD
db = DatabaseManager("cineman.db")

st.title("🎬 Cineman — Programmation Répertoire")

# Navigation par onglets
tab_planning, tab_add_screening, tab_add_movie, tab_add_cinema = st.tabs([
    "📅 Planning",
    "➕ Programmer une séance",
    "🎥 Gestion des films",
    "🏛️ Gestion des cinémas",
])

# -------------------------------------------------------------------
# ONGLET 1 : Planning des séances
# -------------------------------------------------------------------
with tab_planning:
    st.header("Planning des séances")

    screenings = db.get_all_screenings()
    cinemas = db.get_all_cinemas()

    if not screenings:
        st.info("Aucune séance programmée pour le moment.")
    else:
        # --- Barre de filtres ---
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cinema_filter = st.selectbox(
                "Filtrer par cinéma",
                ["Tous"] + [c.name for c in cinemas],
                key="filter_cinema",
            )
        with col_f2:
            status_filter = st.selectbox(
                "Filtrer par statut",
                ["Toutes", "À voir 🍿", "Vues ✅"],
                key="filter_status",
            )

        # Application des filtres
        filtered_screenings = screenings
        if cinema_filter != "Tous":
            filtered_screenings = [
                s for s in filtered_screenings if s.cinema.name == cinema_filter
            ]
        if status_filter == "À voir 🍿":
            filtered_screenings = [
                s for s in filtered_screenings if not s.is_projected
            ]
        elif status_filter == "Vues ✅":
            filtered_screenings = [
                s for s in filtered_screenings if s.is_projected
            ]

        st.divider()

        # Affichage de la liste
        for s in filtered_screenings:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                # Infos Film
                with col1:
                    st.subheader(s.movie.title)
                    st.caption(
                        f"De **{s.movie.director}** ({s.movie.year}) — {s.movie.runtime} min"
                    )

                # Infos Lieu & Horaire
                with col2:
                    start_str = s.date_time.strftime("%d/%m/%Y à %Hh%M")
                    end_str = (
                        s.end_time.strftime("%Hh%M") if s.end_time else "N/A"
                    )

                    st.write(f"📍 **{s.cinema.name}**")
                    st.write(f"🕒 **{start_str}** *(Fin ~ {end_str})*")

                    # Lien Google Maps
                    if s.cinema.google_maps_url:
                        url = s.cinema.google_maps_url.strip()
                        if not url.startswith(("http://","https://")):
                            url = f"https://{url}"

                            st.markdown(
                            f"[🗺️ Voir sur Google Maps]({url})",
                            unsafe_allow_html=True,
                        )
                    else:
                        maps_query = urllib.parse.quote(
                            f"{s.cinema.name} {s.cinema.address or ''}"
                        )
                        st.markdown(
                            f"[🗺️ Chercher sur Maps](https://www.google.com/maps/search/?api=1&query={maps_query})",
                            unsafe_allow_html=True,
                        )

                # Statut & Action Vu
                with col3:
                    if s.is_projected:
                        st.success("Vu ✅")
                        if st.button("Marquer comme à voir", key=f"unsee_{s.id}"):
                            db.mark_screening_as_projected(s.id, False)
                            st.rerun()
                    else:
                        st.warning("À voir 🍿")
                        if st.button("Marquer comme vu ✅", key=f"see_{s.id}"):
                            db.mark_screening_as_projected(s.id, True)
                            st.rerun()

                # Action Supprimer
                with col4:
                    if st.button("🗑️", key=f"del_scr_{s.id}", help="Supprimer la séance"):
                        db.delete_screening(s.id)
                        st.success("Séance supprimée.")
                        st.rerun()

                st.divider()

# -------------------------------------------------------------------
# ONGLET 2 : Programmer une séance
# -------------------------------------------------------------------
with tab_add_screening:
    st.header("Programmer une nouvelle séance")

    movies = db.get_all_movies()
    cinemas = db.get_all_cinemas()

    if not movies:
        st.warning(
            "Veuillez d'abord ajouter au moins un film dans l'onglet 'Gestion des films'."
        )
    elif not cinemas:
        st.warning(
            "Veuillez d'abord ajouter au moins un cinéma dans l'onglet 'Gestion des cinémas'."
        )
    else:
        movie_options = {f"{m.title} ({m.director})": m for m in movies}
        cinema_options = {c.name: c for c in cinemas}

        with st.form("add_screening_form"):
            selected_movie_label = st.selectbox("Film", list(movie_options.keys()))
            selected_cinema_name = st.selectbox("Cinéma", list(cinema_options.keys()))

            col_date, col_time = st.columns(2)
            with col_date:
                screening_date = st.date_input("Date", value=date.today())
            with col_time:
                screening_time = st.time_input("Heure de début", value=time(20, 0))

            submit_screening = st.form_submit_button("Enregistrer la séance")

            if submit_screening:
                selected_movie = movie_options[selected_movie_label]
                selected_cinema = cinema_options[selected_cinema_name]

                full_datetime = datetime.combine(screening_date, screening_time)

                new_screening = Screening(
                    movie=selected_movie,
                    cinema=selected_cinema,
                    date_time=full_datetime,
                )

                # Sauvegarde en base de données
                saved_screening = db.add_screening(new_screening)

                # Envoi immédiat de la notification (et planification du rappel)
                notify_screening_created(saved_screening)

                st.success(
                    f"Séance pour '{selected_movie.title}' au {selected_cinema.name} programmée avec succès !"
                )
                st.rerun()

# -------------------------------------------------------------------
# ONGLET 3 : Gestion des films
# -------------------------------------------------------------------
with tab_add_movie:
    st.header("Gestion de la vidéothèque")

    col_form, col_list = st.columns([1, 1])

    with col_form:
        st.subheader("Ajouter un film")
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
                    "Durée (minutes)", min_value=1, max_value=600, value=100
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
                    st.success(f"Film '{title}' ajouté avec succès !")
                    st.rerun()

    with col_list:
        st.subheader("Films enregistrés")
        movies_list = db.get_all_movies()
        if not movies_list:
            st.info("Aucun film en base.")
        else:
            for m in movies_list:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"🎬 **{m.title}** — {m.director} ({m.year}) [{m.runtime} min]")
                with c2:
                    if st.button("🗑️", key=f"del_mov_{m.id}", help="Supprimer ce film"):
                        db.delete_movie(m.id)
                        st.rerun()

# -------------------------------------------------------------------
# ONGLET 4 : Gestion des cinémas
# -------------------------------------------------------------------
with tab_add_cinema:
    st.header("Gestion des salles de cinéma")

    col_cform, col_clist = st.columns([1, 1])

    with col_cform:
        st.subheader("Ajouter un cinéma")
        with st.form("add_cinema_form"):
            name = st.text_input("Nom du cinéma", placeholder="ex: Reflet Médicis")
            address = st.text_input("Adresse", placeholder="ex: 3 Rue Champollion, 75005 Paris")
            maps_url = st.text_input(
                "Lien Google Maps (optionnel)",
                placeholder="https://maps.google.com/...",
            )

            submit_cinema = st.form_submit_button("Enregistrer le cinéma")

            if submit_cinema:
                if not name.strip():
                    st.error("Le nom du cinéma est obligatoire.")
                else:
                    new_cinema = Cinema(
                        name=name.strip(),
                        address=address.strip() if address else None,
                        google_maps_url=maps_url.strip() if maps_url else None,
                    )
                    try:
                        db.add_cinema(new_cinema)
                        st.success(f"Cinéma '{name}' enregistré !")
                        st.rerun()
                    except Exception:
                        st.error("Ce cinéma existe déjà en base.")

    with col_clist:
        st.subheader("Cinémas enregistrés")
        cinemas_list = db.get_all_cinemas()
        if not cinemas_list:
            st.info("Aucun cinéma enregistré.")
        else:
            for c in cinemas_list:
                st.write(f"📍 **{c.name}**")
                if c.address:
                    st.caption(c.address)
                st.divider()