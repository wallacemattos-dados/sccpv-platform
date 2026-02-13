# src/services/auth_service.py
from typing import Optional
from sqlmodel import Session, select
from src.models import User
# Importa a verificação de senha (certifique-se que src/security.py existe)
from src.security import verify_password 

class AuthService:
    def __init__(self, session: Session):
        """Inicializa o serviço com uma sessão de banco de dados."""
        self.session = session

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Busca usuário pelo email e verifica a senha hash.
        Retorna o objeto User se sucesso, ou None se falhar.
        """
        # 1. Busca o usuário no banco pelo email
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).first()
        
        # 2. Se não achar usuário, falha
        if not user:
            return None
            
        # 3. Se achar, verifica se a senha bate com o hash
        if not verify_password(password, user.password_hash):
            return None
            
        # 4. Retorna o usuário autenticado
        return user