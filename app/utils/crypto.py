# app/utils/crypto.py
from cryptography.fernet import Fernet
import os

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(file_path + '.enc', 'wb') as file:
        file.write(encrypted_data)
    return file_path + '.enc'

def decrypt_file(encrypted_file_path, key):
    f = Fernet(key)
    with open(encrypted_file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    original_path = encrypted_file_path.replace('.enc', '')
    with open(original_path, 'wb') as file:
        file.write(decrypted_data)
    return original_path