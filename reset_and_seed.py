import sys
import os
import requests
import time
from datetime import datetime
from sqlmodel import Session, select, delete
from src.database.connection import engine
from src.models import Brand, Model, MonthlyAverage, VehicleCapture, ResearchAssignment

# --- CONFIGURAÇÕES DA DEMO ---
# IDs: Chevrolet(23), VW(59), Fiat(21), Ford(22), Honda(25)
TOP_BRANDS_IDS = ['23', '59', '21', '22', '25'] 
LIMIT_MODELS = 8   # Reduzi para 8 para ser mais rápido
LIMIT_YEARS = 3    # Reduzi para 3 anos (foca nos novos) para evitar bloqueio
DELAY = 1.0        # Pausa obrigatória entre requisições
# -----------------------------

BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"
# Headers para simular um navegador real e evitar bloqueio
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

def clean_database():
    print("🧹 Limpando banco de dados...")
    with Session(engine) as session:
        # Ordem de deleção importa (filhos primeiro)
        session.exec(delete(VehicleCapture))
        session.exec(delete(ResearchAssignment))
        session.exec(delete(MonthlyAverage))
        session.exec(delete(Model))
        session.exec(delete(Brand))
        session.commit()
    print("✨ Banco limpo com sucesso!")

def request_with_retry(url):
    """Tenta a requisição até 3 vezes com espera progressiva."""
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait = (attempt + 1) * 5 # Espera 5s, 10s, 15s...
                print(f"⏳ API ocupada. Tentativa {attempt+1}/3. Aguardando {wait}s...")
                time.sleep(wait)
            else:
                return None
        except Exception as e:
            print(f"⚠️ Erro de conexão: {e}")
            time.sleep(2)
    return None

def seed_database():
    clean_database()
    print(f"🚀 Iniciando Carga Controlada ({len(TOP_BRANDS_IDS)} Marcas)...")
    
    current_year = datetime.now().year
    min_year = current_year - LIMIT_YEARS
    
    with Session(engine) as session:
        # 1. Busca Todas as Marcas (uma única requisição)
        all_brands = request_with_retry(f"{BASE_URL}/marcas")
        if not all_brands:
            print("❌ Falha crítica: Não foi possível baixar marcas.")
            return

        # Filtra apenas as 5 desejadas
        target_brands = [b for b in all_brands if b['codigo'] in TOP_BRANDS_IDS]

        for b_data in target_brands:
            brand_code = b_data['codigo']
            brand_name = b_data['nome'].upper()
            
            print(f"\n🏢 Processando Marca: {brand_name}")
            
            # Cria Marca
            brand = Brand(name=brand_name)
            session.add(brand)
            session.commit()
            session.refresh(brand)

            # Pausa para respirar antes de pedir modelos
            time.sleep(DELAY) 

            # 2. Busca Modelos
            models_data = request_with_retry(f"{BASE_URL}/marcas/{brand_code}/modelos")
            if not models_data: continue

            # Pega apenas os primeiros X modelos
            target_models = models_data['modelos'][:LIMIT_MODELS]

            for m_data in target_models:
                model_code = m_data['codigo']
                model_name = m_data['nome'].upper()
                
                # Cria Modelo
                model = Model(name=model_name, brand_id=brand.id, category="Indefinido")
                session.add(model)
                session.commit()
                session.refresh(model)
                
                print(f"   🚗 {model_name}...", end="", flush=True)

                # Pausa antes de pedir anos
                time.sleep(DELAY)

                # 3. Busca Anos
                years_data = request_with_retry(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos")
                if not years_data: 
                    print(" (Sem anos)")
                    continue

                count_years = 0
                for y_data in years_data:
                    if count_years >= LIMIT_YEARS: break 
                    
                    year_code = y_data['codigo']
                    year_label = y_data['nome']
                    
                    # Filtro de Ano
                    try:
                        year_num = int(year_label.split(' ')[0])
                        if year_num > current_year + 1: year_num = current_year
                    except: continue

                    if year_num < min_year: continue

                    # Pausa antes de pedir preço (ponto crítico de bloqueio)
                    time.sleep(DELAY)

                    # 4. Busca Preço
                    price_data = request_with_retry(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}")
                    if price_data:
                        val_str = price_data['Valor'].replace("R$ ", "").replace(".", "").replace(",", ".")
                        val = float(val_str)
                        
                        avg = MonthlyAverage(
                            reference_month=datetime.now().strftime("%Y-%m"),
                            model_id=model.id,
                            model_year=year_num,
                            avg_price=val,
                            min_price=val,
                            max_price=val,
                            sample_size=1
                        )
                        session.add(avg)
                        session.commit()
                        count_years += 1
                        print(".", end="", flush=True) # Feedback visual de progresso
                
                print(" OK") # Fim do modelo

    print("\n🏁 Carga Finalizada! O sistema está pronto para a apresentação.")

if __name__ == "__main__":
    seed_database()