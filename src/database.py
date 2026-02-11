from sqlmodel import SQLModel, create_engine, Session
from src.config import settings

# check_same_thread=False é necessário para SQLite trabalhar com FastAPI/Streamlit
# echo=True mostra o SQL no terminal (útil para debug no War Room)
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread": False}
)

def init_db():
    """Cria todas as tabelas definidas nos Models"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency Injection para Sessões de Banco"""
    with Session(engine) as session:
        yield session