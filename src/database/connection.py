from sqlmodel import SQLModel, create_engine, Session
# Se der erro no config, verifique se src/config.py existe
from src.config import settings 

# Cria a engine de conexão com o SQLite
engine = create_engine(
    settings.DATABASE_URL, 
    echo=False,  # Mude para True para ver logs de SQL
    connect_args={"check_same_thread": False} # Necessário para Streamlit + SQLite
)

def init_db():
    """Função auxiliar para criar tabelas (usada no script de init)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Generator para Injeção de Dependência de Sessão"""
    with Session(engine) as session:
        yield session