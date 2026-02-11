from src.database import init_db
from src.models import *

if __name__ == "__main__":
    print("Criando tabelas...")
    init_db()
    print("Tabelas criadas com sucesso em sccpv.db!")