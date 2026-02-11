# create_admin.py
from sqlmodel import select
from src.database import get_session, engine # Import engine para session manual
from src.models import User, UserRole
from src.security import get_password_hash
from sqlmodel import Session

def create_super_admin():
    # Abre uma sessão manual
    with Session(engine) as session:
        # 1. Verifica se já existe
        statement = select(User).where(User.email == "admin@sccpv.com")
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print("⚠️ Usuário Admin já existe!")
            return

        # 2. Cria o objeto
        admin_user = User(
            name="Administrador Sistema",
            email="admin@sccpv.com",
            password_hash=get_password_hash("admin123"), # Senha inicial
            role=UserRole.ADMIN,
            is_active=True
        )

        # 3. Salva no banco
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print(f"✅ Admin criado com sucesso! ID: {admin_user.id}")
        print("📧 Email: admin@sccpv.com")
        print("🔑 Senha: admin123")

if __name__ == "__main__":
    create_super_admin()