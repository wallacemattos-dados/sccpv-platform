from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship

# --- ENUMS ---
class UserRole(str, Enum):
    ADMIN = "admin"
    GERENTE = "gerente"
    COORDENADOR = "coordenador"
    PESQUISADOR = "pesquisador"
    LOJISTA = "lojista"

class StoreStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AssignmentStatus(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"

# --- TABELAS ---

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: UserRole
    is_active: bool = Field(default=True)

    # Relacionamentos
    regions: List["Region"] = Relationship(back_populates="coordinator")
    assignments: List["ResearchAssignment"] = Relationship(back_populates="researcher")
    created_stores: List["Store"] = Relationship(back_populates="creator")

class Region(SQLModel, table=True):
    __tablename__ = "regions"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    coordinator_id: Optional[int] = Field(default=None, foreign_key="users.id")

    coordinator: Optional[User] = Relationship(back_populates="regions")
    stores: List["Store"] = Relationship(back_populates="region")

class Brand(SQLModel, table=True):
    __tablename__ = "brands"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    models: List["Model"] = Relationship(back_populates="brand")

class Model(SQLModel, table=True):
    __tablename__ = "models"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str  # Ex: SUV, Sedan
    brand_id: int = Field(foreign_key="brands.id")

    brand: Brand = Relationship(back_populates="models")
    captures: List["VehicleCapture"] = Relationship(back_populates="model")

class Store(SQLModel, table=True):
    __tablename__ = "stores"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str
    region_id: int = Field(foreign_key="regions.id")
    created_by_id: int = Field(foreign_key="users.id")
    status: StoreStatus = Field(default=StoreStatus.PENDING)

    region: Region = Relationship(back_populates="stores")
    creator: User = Relationship(back_populates="created_stores")
    assignments: List["ResearchAssignment"] = Relationship(back_populates="store")

class ResearchAssignment(SQLModel, table=True):
    __tablename__ = "research_assignments"
    id: Optional[int] = Field(default=None, primary_key=True)
    week_start_date: date
    researcher_id: int = Field(foreign_key="users.id")
    store_id: int = Field(foreign_key="stores.id")
    status: AssignmentStatus = Field(default=AssignmentStatus.OPEN)

    researcher: User = Relationship(back_populates="assignments")
    store: Store = Relationship(back_populates="assignments")
    captures: List["VehicleCapture"] = Relationship(back_populates="assignment")

class VehicleCapture(SQLModel, table=True):
    __tablename__ = "vehicle_captures"
    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: int = Field(foreign_key="research_assignments.id")
    model_id: int = Field(foreign_key="models.id")
    
    price: float
    model_year: int
    manufacture_year: int
    options: List[str] = Field(default=[], sa_column=Column(JSON))
    capture_date: datetime = Field(default_factory=datetime.now)

    assignment: ResearchAssignment = Relationship(back_populates="captures")
    model: Model = Relationship(back_populates="captures")

class MonthlyAverage(SQLModel, table=True):
    __tablename__ = "monthly_averages"
    id: Optional[int] = Field(default=None, primary_key=True)
    reference_month: str  # Format: YYYY-MM
    model_id: int = Field(foreign_key="models.id")
    model_year: int
    
    avg_price: float
    min_price: float
    max_price: float
    sample_size: int

class UserQuery(SQLModel, table=True):
    __tablename__ = "user_queries"
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    brand_queried: str
    model_queried: str
    year_queried: Optional[int] = None
    ip_address: Optional[str] = None