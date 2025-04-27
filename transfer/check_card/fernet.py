import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())


def encrypt_card(card_number) -> str:
    return cipher.encrypt(card_number.encode()).decode()


def decrypt_card(encrypted_card: str) -> str:
    return cipher.decrypt(encrypted_card.encode()).decode()
