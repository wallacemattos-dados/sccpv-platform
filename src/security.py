from passlib.context import CryptContext

# Configura o contexto de hashing (usando bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Gera o hash seguro da senha."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto bate com o hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)