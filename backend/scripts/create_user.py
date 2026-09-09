"""Create a local Pstral demo account without exposing the password in shell history."""

from getpass import getpass
import os
import sys

from app.core.auth import UserCreate, create_user, init_users_db
from app.core.config import settings


def main() -> int:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        print("Configurez SECRET_KEY avant de créer un compte.", file=sys.stderr)
        return 2
    init_users_db()
    username = input("Identifiant : ").strip()
    email = input("Email : ").strip()
    full_name = input("Nom complet : ").strip()
    password = getpass("Mot de passe (12 caractères minimum) : ")
    confirmation = getpass("Confirmer le mot de passe : ")
    if password != confirmation:
        print("Les mots de passe ne correspondent pas.", file=sys.stderr)
        return 2
    try:
        user = create_user(UserCreate(username=username, email=email, full_name=full_name, password=password))
    except Exception as exc:
        print(f"Création impossible : {exc}", file=sys.stderr)
        return 1
    print(f"Compte créé : {user.username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
