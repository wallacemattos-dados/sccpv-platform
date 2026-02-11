# src/services/auth_service.py
from sqlmodel import Session, select
from src.models import User
from src.security import verify_password

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Busca usuário pelo email e verifica a senha.
        Retorna o objeto User se sucesso, ou None se falhar.
        """
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).first()
        
        if not user:
            return None
            
        if not verify_password(password, user.password_hash):
            return None
            
        return user