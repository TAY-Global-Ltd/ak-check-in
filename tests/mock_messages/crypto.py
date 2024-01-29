from cryptography.fernet import Fernet
import os

CRYPTO_KEY = 'iuuDj2_K-wY_4TJOa7f1wv2joj_peFdH8VBT8ZPQTik='

fernet = Fernet(CRYPTO_KEY)


def encrypt(s):
    return fernet.encrypt(s.encode())


def descript(s):
    return fernet.decrypt(s).decode()


def get_secret(env_var_name):
    return descript(os.environ[env_var_name])
