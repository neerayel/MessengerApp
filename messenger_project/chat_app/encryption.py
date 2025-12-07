from cryptography.fernet import Fernet
from django.conf import settings
import base64

class MessageEncryptor:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        encrypted = self.cipher_suite.encrypt(message)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_message):
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_message.encode('utf-8'))
            decrypted = self.cipher_suite.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Ошибка дешифрования: {str(e)}")

# Создаем глобальный экземпляр шифратора
_encryptor = MessageEncryptor()

def encrypt_message(message):
    return _encryptor.encrypt(message)

def decrypt_message(encrypted_message):
    return _encryptor.decrypt(encrypted_message)