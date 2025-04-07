from cryptography.fernet import Fernet

class Crypto:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt(self, text: str) -> str:
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        return self.cipher.decrypt(encrypted_text.encode()).decode()