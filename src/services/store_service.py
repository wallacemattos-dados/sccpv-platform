from typing import List, Optional
from sqlmodel import Session, select
from src.models import Store, Region, StoreStatus, User

class StoreService:
    def __init__(self, session: Session):
        self.session = session

    # --- REGIÕES ---
    def create_region(self, name: str, coordinator_id: Optional[int] = None) -> Region:
        """Cria uma região (ex: Zona Sul, Centro)."""
        region = Region(name=name, coordinator_id=coordinator_id)
        self.session.add(region)
        self.session.commit()
        self.session.refresh(region)
        return region

    def get_all_regions(self) -> List[Region]:
        return self.session.exec(select(Region)).all()

    # --- LOJAS ---
    def create_store_request(self, name: str, address: str, region_id: int, owner_id: int) -> Store:
        """Lojista solicita cadastro (Nasce como PENDING)."""
        store = Store(
            name=name,
            address=address,
            region_id=region_id,
            created_by_id=owner_id,
            status=StoreStatus.PENDING # Fluxo de aprovação
        )
        self.session.add(store)
        self.session.commit()
        self.session.refresh(store)
        return store

    def approve_store(self, store_id: int) -> Store:
        """Coordenador/Admin aprova a loja."""
        store = self.session.get(Store, store_id)
        if not store:
            raise ValueError("Loja não encontrada.")
        
        store.status = StoreStatus.APPROVED
        self.session.add(store)
        self.session.commit()
        self.session.refresh(store)
        return store

    def get_stores_by_status(self, status: StoreStatus = None) -> List[Store]:
        """Filtra lojas (ex: Mostra só as pendentes para o Admin)."""
        query = select(Store)
        if status:
            query = query.where(Store.status == status)
        return self.session.exec(query).all()