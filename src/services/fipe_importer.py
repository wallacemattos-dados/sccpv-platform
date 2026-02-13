import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import httpx
import time
from sqlmodel import Session, select
from src.database import engine
from src.models import Brand, Model, MonthlyAverage

# URLs da API Pública
BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"

# Top Marcas para o MVP (Evitar loop infinito de milhares de requisições)
TARGET_BRANDS = ["VW - VolksWagen", "Fiat", "Chevrolet", "Ford", "Toyota"]

class FipeImporter:
    def __init__(self):
        self.client = httpx.Client(timeout=10.0)

    def run_import(self):
        with Session(engine) as session:
            print("🚀 Iniciando importação da FIPE (Modo Rápido)...")
            
            # 1. Buscar Todas as Marcas
            print("📡 Baixando Marcas...")
            resp = self.client.get(f"{BASE_URL}/marcas")
            brands_data = resp.json()
            
            for b_data in brands_data:
                name = b_data['nome']
                code = b_data['codigo']
                
                # Filtro: Importar apenas as TOP marcas para teste rápido
                if name not in TARGET_BRANDS:
                    continue
                
                print(f"  -> Processando Marca: {name}")
                
                # Upsert Marca (Verifica se existe, se não, cria)
                brand = session.exec(select(Brand).where(Brand.name == name.upper())).first()
                if not brand:
                    brand = Brand(name=name.upper())
                    session.add(brand)
                    session.commit()
                    session.refresh(brand)
                
                # 2. Buscar Modelos da Marca
                self._import_models(session, brand, code)
            
            print("✅ Importação Concluída com Sucesso!")

    def _import_models(self, session: Session, brand: Brand, brand_code: str):
        # API retorna modelos e anos
        resp = self.client.get(f"{BASE_URL}/marcas/{brand_code}/modelos")
        models_data = resp.json()['modelos']
        
        # Limita a 5 modelos por marca para o teste ser rápido (Remova o [:5] em prod)
        for m_data in models_data[:5]: 
            model_name = m_data['nome'].upper()
            model_code = m_data['codigo']
            
            # Upsert Modelo
            model = session.exec(select(Model).where(Model.name == model_name)).first()
            if not model:
                model = Model(name=model_name, brand_id=brand.id, category="Indefinido")
                session.add(model)
                session.commit()
                session.refresh(model)
            
            # 3. Buscar Preço (Para popular a Média Inicial)
            # Pegamos o último ano disponível para dar um preço de referência
            self._import_price(session, brand_code, model_code, model)

    def _import_price(self, session: Session, brand_code: str, model_code: str, model: Model):
        # Pega lista de anos
        resp = self.client.get(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos")
        years_data = resp.json()
        
        if not years_data:
            return

        # Pega o primeiro ano da lista (geralmente o mais novo)
        year_obj = years_data[0] 
        year_code = year_obj['codigo']
        
        # Pega o detalhe do preço
        resp = self.client.get(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}")
        price_data = resp.json()
        
        # Tratamento de string "R$ 105.000,00" -> float 105000.00
        valor_str = price_data['Valor'].replace("R$ ", "").replace(".", "").replace(",", ".")
        try:
            valor = float(valor_str)
        except:
            valor = 0.0
            
        modelo_ano = price_data.get('AnoModelo', 2024)
        mes_ref = "2026-02" # Fixando o mês atual para o MVP
        
        # Inserir na tabela MonthlyAverage (Batch Pre-calculado)
        # Verifica se já tem média para este carro neste mês
        existing_avg = session.exec(
            select(MonthlyAverage)
            .where(MonthlyAverage.model_id == model.id)
            .where(MonthlyAverage.model_year == modelo_ano)
        ).first()
        
        if not existing_avg:
            avg = MonthlyAverage(
                reference_month=mes_ref,
                model_id=model.id,
                model_year=modelo_ano,
                avg_price=valor,
                min_price=valor, # Como só tem 1, min/max/avg são iguais
                max_price=valor,
                sample_size=1 # 1 amostra (FIPE)
            )
            session.add(avg)
            session.commit()
            print(f"     $ Preço Importado: {model.name} ({modelo_ano}) -> R$ {valor}")

# Bloco de Execução Direta
if __name__ == "__main__":
    importer = FipeImporter()
    importer.run_import()