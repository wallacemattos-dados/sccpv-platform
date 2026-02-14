import sys
import os

# --- CORREÇÃO DE PATH (Para rodar como script isolado) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)
# ---------------------------------------------------------

import requests
import time
from datetime import datetime
from sqlmodel import Session, select
from src.database.connection import engine
from src.models import Brand, Model, MonthlyAverage

class FipeImporter:
    BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"
    
    # Headers para simular um navegador real (Evita bloqueio imediato)
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Configurações de Segurança e Performance
    DELAY = 1.0       # Tempo de espera entre requisições (segundos)
    MAX_RETRIES = 5   # Quantas vezes insistir se a API falhar
    YEAR_LIMIT = 4    # Pega apenas os últimos 4 anos (Foco em carros novos/seminovos)
    CURRENT_YEAR = datetime.now().year
    MIN_YEAR = CURRENT_YEAR - YEAR_LIMIT

    # IDs das marcas principais para a apresentação (Chevrolet, VW, Fiat, Ford, Honda, Toyota, Hyundai)
    TOP_BRANDS_IDS = ['23', '59', '21', '22', '25', '56', '26']

    def _request(self, endpoint):
        """Faz a requisição com sistema de 'Retry' (Insistência) caso a API bloqueie."""
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, headers=self.HEADERS, timeout=15)
                
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 429:
                    # Cálculo de espera progressiva (5s, 10s, 15s...)
                    wait_time = (attempt + 1) * 5  
                    print(f"⏳ API ocupada (429) em {endpoint}. Tentativa {attempt+1}/{self.MAX_RETRIES}. Esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue # Tenta de novo na próxima iteração do loop
                
                else:
                    print(f"⚠️ Erro {response.status_code} em {endpoint}")
                    return None
                    
            except Exception as e:
                print(f"⚠️ Erro de conexão: {e}. Tentando de novo...")
                time.sleep(2)
        
        print(f"❌ Falha definitiva em {endpoint} após {self.MAX_RETRIES} tentativas.")
        return None

    def run_import(self):
        print("🚀 Iniciando Importação Robusta (Top Marcas)...")
        print("ℹ️  Isso vai popular seu banco com dados reais. Se a API bloquear, o script aguardará automaticamente.")
        
        marcas = self._request("/marcas")
        if not marcas:
            print("❌ Não foi possível baixar a lista inicial de marcas.")
            return

        # Filtra apenas as principais para a apresentação ser rápida
        marcas_filtradas = [m for m in marcas if m['codigo'] in self.TOP_BRANDS_IDS]
        print(f"📡 {len(marcas_filtradas)} marcas principais identificadas.")

        with Session(engine) as session:
            for m_data in marcas_filtradas:
                brand_code = m_data['codigo']
                brand_name = m_data['nome'].upper()

                print(f"\n🏢 PROCESSANDO MARCA: {brand_name}")
                
                # 1. Salva Marca
                brand = session.exec(select(Brand).where(Brand.name == brand_name)).first()
                if not brand:
                    brand = Brand(name=brand_name)
                    session.add(brand)
                    session.commit()
                    session.refresh(brand)

                # Pausa para não sobrecarregar a API
                time.sleep(self.DELAY)
                
                # 2. Busca Modelos
                self._process_models(session, brand, brand_code)
            
            print("\n🏁 IMPORTAÇÃO FINALIZADA COM SUCESSO!")

    def _process_models(self, session, brand, brand_code):
        data = self._request(f"/marcas/{brand_code}/modelos")
        if not data or 'modelos' not in data:
            return

        modelos = data['modelos']
        print(f"   -> {len(modelos)} modelos encontrados. Baixando anos dos top 15...")
        
        # Limita a 15 modelos por marca para a demo não demorar uma eternidade
        # (Pega os primeiros 15, que geralmente são os mais populares)
        for m_data in modelos[:15]: 
            model_code = m_data['codigo']
            model_name = m_data['nome'].upper()

            model = session.exec(select(Model).where(Model.name == model_name)).first()
            if not model:
                model = Model(name=model_name, brand_id=brand.id, category="Indefinido")
                session.add(model)
                session.commit()
                session.refresh(model)

            self._process_years(session, brand_code, model_code, model)

    def _process_years(self, session, brand_code, model_code, model):
        anos = self._request(f"/marcas/{brand_code}/modelos/{model_code}/anos")
        if not anos:
            return

        for ano_data in anos:
            year_code = ano_data['codigo']
            year_label = ano_data['nome']
            
            try:
                # Extrai o ano numérico (Ex: "2022 Gasolina" -> 2022)
                year_num = int(year_label.split(' ')[0])
                # Ajuste para anos "Zero KM" que a Fipe manda como 32000
                if year_num > self.CURRENT_YEAR + 1: year_num = self.CURRENT_YEAR
            except ValueError:
                continue

            # Filtro de Ano (apenas recentes)
            if year_num < self.MIN_YEAR:
                continue

            self._fetch_and_save_price(session, brand_code, model_code, year_code, model, year_num)

    def _fetch_and_save_price(self, session, brand_code, model_code, year_code, model, year_num):
        price_data = self._request(f"/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}")
        
        if not price_data:
            return

        try:
            # Converte "R$ 80.000,00" para float 80000.00
            valor_str = price_data['Valor'].replace("R$ ", "").replace(".", "").replace(",", ".")
            valor = float(valor_str)
            ref_month_code = datetime.now().strftime("%Y-%m")

            # Verifica se já existe para não duplicar
            existing = session.exec(
                select(MonthlyAverage)
                .where(MonthlyAverage.model_id == model.id)
                .where(MonthlyAverage.model_year == year_num)
                .where(MonthlyAverage.reference_month == ref_month_code)
            ).first()

            if not existing:
                avg = MonthlyAverage(
                    reference_month=ref_month_code,
                    model_id=model.id,
                    model_year=year_num,
                    avg_price=valor,
                    min_price=valor,
                    max_price=valor,
                    sample_size=1
                )
                session.add(avg)
                session.commit()
                print(f"      ✅ {model.name} {year_num}: R$ {valor:,.2f}") 

        except Exception as e:
            pass # Ignora erros pontuais de conversão para não parar o script

if __name__ == "__main__":
    importer = FipeImporter()
    importer.run_import()