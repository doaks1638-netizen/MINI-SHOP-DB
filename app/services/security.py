# security (pawdlib + hash password + virify passwrod)
from pwdlib import PasswordHash

password_context = PasswordHash.recommended()


def create_hash_password(password: str):
    return password_context.hash(password)


def verify_password(password, hash_password):
    return password_context.verify(password, hash_password)
