from sqlmodel import Session, select
from src.database.connection import engine, init_db
from src.models import User, UserRole
from src.security import get_password_hash

def create_fake_users():
    with Session(engine) as session:
        # 1. Coordenador
        coord_email = "roberto@sccpv.com"
        if not session.exec(select(User).where(User.email == coord_email)).first():
            coord = User(
                name="Roberto Coordenador",
                email=coord_email,
                password_hash=get_password_hash("123456"),
                role=UserRole.COORDENADOR,
                is_active=True
            )
            session.add(coord)
            print("✅ Usuário Coordenador criado: roberto@sccpv.com / 123456")

        # 2. Pesquisador
        pesq_email = "ana@sccpv.com"
        if not session.exec(select(User).where(User.email == pesq_email)).first():
            pesq = User(
                name="Ana Pesquisadora",
                email=pesq_email,
                password_hash=get_password_hash("123456"),
                role=UserRole.PESQUISADOR,
                is_active=True
            )
            session.add(pesq)
            print("✅ Usuário Pesquisador criado: ana@sccpv.com / 123456")
        
        session.commit()

if __name__ == "__main__":
    create_fake_users()