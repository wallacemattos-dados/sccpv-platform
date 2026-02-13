from sqlmodel import Session, select
from src.database.connection import engine
from src.models import Store, Region, StoreStatus, User

def create_store_data():
    with Session(engine) as session:
        # 1. Cria uma Região
        region = session.exec(select(Region).where(Region.name == "Centro SP")).first()
        if not region:
            region = Region(name="Centro SP")
            session.add(region)
            session.commit()
            session.refresh(region)
            print(f"✅ Região criada: {region.name}")

        # 2. Busca um usuário para ser o 'dono' (pega o primeiro admin ou user)
        owner = session.exec(select(User)).first()
        
        # 3. Cria uma Loja já APROVADA
        store = session.exec(select(Store).where(Store.name == "Loja Matriz")).first()
        if not store:
            store = Store(
                name="Loja Matriz",
                address="Av. Paulista, 1000",
                region_id=region.id,
                created_by_id=owner.id,
                status=StoreStatus.APPROVED  # <--- O segredo está aqui
            )
            session.add(store)
            session.commit()
            print(f"✅ Loja criada e APROVADA: {store.name}")
        else:
            print("ℹ️ Loja já existe.")

if __name__ == "__main__":
    create_store_data()