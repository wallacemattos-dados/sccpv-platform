import sys
import os
from datetime import date, datetime
from sqlmodel import Session, select, delete
from src.database.connection import engine
from src.models import (
    User, UserRole, Brand, Model, Region, Store, StoreStatus,
    ResearchAssignment, AssignmentStatus, VehicleCapture, MonthlyAverage
)
from src.security import get_password_hash

def clean_database(session: Session):
    print("🧹 Limpando banco de dados...")
    # Ordem importa para respeitar Foreign Keys
    session.exec(delete(VehicleCapture))
    session.exec(delete(ResearchAssignment))
    session.exec(delete(MonthlyAverage))
    session.exec(delete(Store))
    session.exec(delete(Model))
    session.exec(delete(Brand))
    session.exec(delete(Region))
    session.exec(delete(User))
    session.commit()
    print("✨ Banco limpo.")

def create_mock_data():
    print("🚀 Iniciando carga de Dados Mockados (Cenário de Apresentação)...")
    
    with Session(engine) as session:
        clean_database(session)

        # 1. USUÁRIOS [cite: 51, 153]
        # Senha padrão: 123456
        pwd = get_password_hash("123456")
        
        users = [
            User(name="Admin Sistema", email="admin@sccpv.com", password_hash=pwd, role=UserRole.ADMIN),
            User(name="Roberto Coordenador", email="roberto@sccpv.com", password_hash=pwd, role=UserRole.COORDENADOR),
            User(name="Ana Pesquisadora", email="ana@sccpv.com", password_hash=pwd, role=UserRole.PESQUISADOR),
            User(name="Carlos Gerente", email="carlos@sccpv.com", password_hash=pwd, role=UserRole.GERENTE),
            User(name="Fernanda Lojista", email="fernanda@sccpv.com", password_hash=pwd, role=UserRole.LOJISTA),
        ]
        for u in users: session.add(u)
        session.commit()
        
        # Recupera IDs para relacionamentos
        coord = session.exec(select(User).where(User.role == UserRole.COORDENADOR)).first()
        pesq = session.exec(select(User).where(User.role == UserRole.PESQUISADOR)).first()
        lojista = session.exec(select(User).where(User.role == UserRole.LOJISTA)).first()

        print("✅ Usuários criados (Senha: 123456)")

        # 2. CATÁLOGO (Marcas e Modelos) [cite: 168, 169]
        # Toyota
        toyota = Brand(name="TOYOTA")
        session.add(toyota)
        session.commit()
        session.refresh(toyota)
        
        corolla = Model(name="COROLLA XEI", brand_id=toyota.id, category="Sedan")
        hilux = Model(name="HILUX CD", brand_id=toyota.id, category="Picape")
        session.add(corolla)
        session.add(hilux)

        # Fiat
        fiat = Brand(name="FIAT")
        session.add(fiat)
        session.commit()
        session.refresh(fiat)
        
        uno = Model(name="UNO MILLE", brand_id=fiat.id, category="Hatch")
        toro = Model(name="TORO VOLCANO", brand_id=fiat.id, category="Picape")
        session.add(uno)
        session.add(toro)
        
        session.commit()
        session.refresh(corolla)
        session.refresh(uno)
        print("✅ Catálogo criado (Toyota, Fiat)")

        # 3. REGIÕES E LOJAS [cite: 165, 166]
        region = Region(name="Centro SP", coordinator_id=coord.id)
        session.add(region)
        session.commit()
        session.refresh(region)

        # Loja 1: Aprovada e Ativa (Para visita)
        store_ok = Store(
            name="Garagem Central", 
            address="Av Paulista, 1000", 
            region_id=region.id, 
            created_by_id=coord.id, # Criada pelo sistema
            status=StoreStatus.APPROVED
        )
        
        # Loja 2: Pendente (Para demo de aprovação) 
        store_pending = Store(
            name="Loja da Fernanda", 
            address="Rua Augusta, 500", 
            region_id=region.id, 
            created_by_id=lojista.id, # Criada pela lojista
            status=StoreStatus.PENDING
        )
        
        session.add(store_ok)
        session.add(store_pending)
        session.commit()
        session.refresh(store_ok)
        print("✅ Lojas criadas (1 Aprovada, 1 Pendente)")

        # 4. OPERAÇÃO (Agendamento e Coleta Passada) [cite: 175, 176]
        # Visita Agendada para HOJE (Para Ana ver no mobile)
        assignment = ResearchAssignment(
            researcher_id=pesq.id,
            store_id=store_ok.id,
            week_start_date=date.today(),
            status=AssignmentStatus.OPEN
        )
        session.add(assignment)
        session.commit()
        
        # Simula uma coleta já realizada (Para Analytics)
        capture = VehicleCapture(
            assignment_id=assignment.id,
            model_id=corolla.id,
            model_year=2022,
            manufacture_year=2022,
            price=125000.00,
            capture_date=datetime.now()
        )
        session.add(capture)
        session.commit()
        print("✅ Operação criada (Visita agendada + 1 Coleta realizada)")

        # 5. DADOS PÚBLICOS (Médias Mensais para Consulta) [cite: 55, 306]
        # Isso garante que a consulta pública funcione sem precisar rodar o Batch agora
        ref_month = datetime.now().strftime("%Y-%m")
        
        # Dados "FIPE" simulados para o gráfico ficar bonito
        averages = [
            # Corolla desvalorizando levemente
            MonthlyAverage(reference_month=ref_month, model_id=corolla.id, model_year=2024, avg_price=150000.0, min_price=148000.0, max_price=155000.0, sample_size=10),
            MonthlyAverage(reference_month=ref_month, model_id=corolla.id, model_year=2023, avg_price=135000.0, min_price=130000.0, max_price=140000.0, sample_size=15),
            MonthlyAverage(reference_month=ref_month, model_id=corolla.id, model_year=2022, avg_price=120000.0, min_price=115000.0, max_price=125000.0, sample_size=20),
            
            # Uno estável
            MonthlyAverage(reference_month=ref_month, model_id=uno.id, model_year=2013, avg_price=35000.0, min_price=30000.0, max_price=40000.0, sample_size=50),
        ]
        
        for avg in averages: session.add(avg)
        session.commit()
        print("✅ Dados Públicos gerados (Médias de Mercado)")

    print("\n🏁 TUDO PRONTO! Pode iniciar a apresentação.")

if __name__ == "__main__":
    create_mock_data()