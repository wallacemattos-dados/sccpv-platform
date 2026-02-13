from typing import List, Optional
from sqlmodel import Session, select
from src.models import Brand, Model

class CatalogService:
    def __init__(self, session: Session):
        self.session = session

    def create_brand(self, name: str) -> Brand:
        """Cria uma nova marca, normalizando o nome para maiúsculas."""
        name = name.strip().upper()
        
        # Validação de Unicidade (Idempotência)
        existing = self.session.exec(select(Brand).where(Brand.name == name)).first()
        if existing:
            return existing
            
        brand = Brand(name=name)
        self.session.add(brand)
        self.session.commit()
        self.session.refresh(brand)
        return brand

    def get_all_brands(self) -> List[Brand]:
        """Retorna todas as marcas ordenadas por nome."""
        return self.session.exec(select(Brand).order_by(Brand.name)).all()

    def create_model(self, name: str, brand_id: int, category: str = "Indefinido") -> Model:
        """Cria um modelo vinculado a uma marca."""
        name = name.strip().upper()
        
        # Verifica se a marca existe
        brand = self.session.get(Brand, brand_id)
        if not brand:
            raise ValueError("Marca não encontrada.")

        # Verifica duplicidade do modelo
        existing = self.session.exec(select(Model).where(Model.name == name)).first()
        if existing:
             return existing

        model = Model(name=name, brand_id=brand_id, category=category)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def get_models_by_brand(self, brand_id: int) -> List[Model]:
        """Retorna modelos de uma marca específica."""
        return self.session.exec(select(Model).where(Model.brand_id == brand_id).order_by(Model.name)).all()