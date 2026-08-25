from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import settings

Password_hash = PasswordHash.recommended()


def verify_pass(hash_password: str, password: str):
    return Password_hash.verify(password, hash_password)


postgres_pass = settings.database_password
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
