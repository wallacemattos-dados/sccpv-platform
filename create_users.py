# create_users.py
from sqlmodel import Session, select
from src.database.connection import engine
from src.models import User, UserRole
from src.security import get_password_hash

def create_all_roles():
    with Session(engine) as session:
        # Lista de usuários para criar
        users_to_create = [
            # (Nome, Email, Role)
            ("Roberto Coordenador", "roberto@sccpv.com", UserRole.COORDENADOR),
            ("Ana Pesquisadora", "ana@sccpv.com", UserRole.PESQUISADOR),
            ("Carlos Gerente", "carlos@sccpv.com", UserRole.GERENTE),
            ("Fernanda Lojista", "fernanda@sccpv.com", UserRole.LOJISTA),
        ]

        print("🚀 Criando/Atualizando usuários...")
        
        for name, email, role in users_to_create:
            existing = session.exec(select(User).where(User.email == email)).first()
            if not existing:
                user = User(
                    name=name,
                    email=email,
                    password_hash=get_password_hash("123456"), # Senha padrão
                    role=role,
                    is_active=True
                )
                session.add(user)
                print(f"✅ Criado: {name} ({role.value})")
            else:
                print(f"ℹ️ Já existe: {name}")
        
        session.commit()

if __name__ == "__main__":
    create_all_roles()