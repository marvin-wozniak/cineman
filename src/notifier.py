import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler

from src.models import Screening

# Configuration SMTP (ex: Gmail ou serveur local SMTP)
# En production, ces identifiants sont lus depuis des variables d'environnement (.env)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "ton.email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "ton_mot_de_passe_app")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "ton.email@gmail.com")

# Initialisation du planificateur de tâches en arrière-plan
scheduler = BackgroundScheduler()
scheduler.start()


def send_email(subject: str, body: str, recipient: str = NOTIFICATION_EMAIL) -> bool:
    """Envoie un e-mail via le serveur SMTP configuré."""
    # Si aucun identifiant n'est configuré, on simule l'envoi dans la console
    if SMTP_USER == "ton.email@gmail.com":
        print(f"\n[SIMULATION EMAIL] ----------------------------------")
        print(f"À : {recipient}")
        print(f"Sujet : {subject}")
        print(f"Corps :\n{body}")
        print(f"-----------------------------------------------------\n")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoie de l'e-mail : {e}")
        return False


def notify_screening_created(screening: Screening) -> None:
    """Envoie un e-mail de confirmation immédiat lors de la création d'une séance."""
    formatted_date = screening.date_time.strftime("%d/%m/%Y à %Hh%M")
    end_time_str = screening.calculate_end_time().strftime("%Hh%M")

    subject = f"🎬 Séance confirmée : {screening.movie.title}"
    body = (
        f"Bonjour,\n\n"
        f"Votre séance a bien été programmée :\n\n"
        f"🎞️ Film : {screening.movie.title} ({screening.movie.year})\n"
        f"🎬 Réalisateur : {screening.movie.director}\n"
        f"📍 Cinéma : {screening.cinema.name}\n"
        f"🕒 Horaires : {formatted_date} (Fin estimée : {end_time_str})\n\n"
        f"Bon film !"
    )

    send_email(subject, body)
    
    # Programmer également le rappel 2h avant la séance
    schedule_screening_reminder(screening)


def send_screening_reminder(screening: Screening) -> None:
    """Rappel envoyé 2 heures avant la séance."""
    subject = f"⏰ Rappel (2h avant) : {screening.movie.title} au {screening.cinema.name}"
    body = (
        f"Rappel : Votre séance pour '{screening.movie.title}' commence dans 2 heures !\n\n"
        f"📍 Cinéma : {screening.cinema.name}\n"
        f"🕒 Heure de début : {screening.date_time.strftime('%Hh%M')}\n\n"
        f"N'oubliez pas d'arriver un peu en avance !"
    )
    send_email(subject, body)


def schedule_screening_reminder(screening: Screening) -> None:
    """Calcule l'heure du rappel (-2h) et l'ajoute au planificateur de tâches."""
    reminder_time = screening.date_time - timedelta(hours=2)

    # On ne planifie le rappel que si l'heure calculée est dans le futur
    if reminder_time > datetime.now():
        job_id = f"reminder_screening_{screening.id}"
        scheduler.add_job(
            send_screening_reminder,
            "date",
            run_date=reminder_time,
            args=[screening],
            id=job_id,
            replace_existing=True,
        )
        print(f"Rappel planifié pour le {reminder_time.strftime('%d/%m/%Y à %Hh%M')}")