from datetime import datetime
from sqlmodel import Session, select, func
from src.database.connection import engine
from src.models import VehicleCapture, MonthlyAverage

def process_monthly_averages():
    print("🔄 Iniciando processamento Batch de médias mensais...")
    
    current_month = datetime.now().strftime("%Y-%m")
    
    with Session(engine) as session:
        # 1. Agrupa as capturas por Modelo e Ano
        # SQL: SELECT model_id, model_year, AVG(price), MIN(price), MAX(price), COUNT(*) ...
        statement = (
            select(
                VehicleCapture.model_id,
                VehicleCapture.model_year,
                func.avg(VehicleCapture.price),
                func.min(VehicleCapture.price),
                func.max(VehicleCapture.price),
                func.count(VehicleCapture.id)
            )
            .group_by(VehicleCapture.model_id, VehicleCapture.model_year)
        )
        
        results = session.exec(statement).all()
        
        if not results:
            print("⚠️ Nenhuma coleta encontrada para calcular.")
            return

        print(f"📊 Processando {len(results)} grupos de modelos...")

        count_updated = 0
        for row in results:
            model_id, model_year, avg_val, min_val, max_val, count_val = row
            
            # 2. Verifica se já existe média para este mês/modelo
            existing_avg = session.exec(
                select(MonthlyAverage)
                .where(MonthlyAverage.reference_month == current_month)
                .where(MonthlyAverage.model_id == model_id)
                .where(MonthlyAverage.model_year == model_year)
            ).first()

            if existing_avg:
                # Atualiza existente
                existing_avg.avg_price = avg_val
                existing_avg.min_price = min_val
                existing_avg.max_price = max_val
                existing_avg.sample_size = count_val
                session.add(existing_avg)
            else:
                # Cria novo registro de média
                new_avg = MonthlyAverage(
                    reference_month=current_month,
                    model_id=model_id,
                    model_year=model_year,
                    avg_price=avg_val,
                    min_val=min_val,
                    max_price=max_val,
                    sample_size=count_val
                )
                session.add(new_avg)
            
            count_updated += 1

        session.commit()
        print(f"✅ Sucesso! {count_updated} registros de média atualizados para {current_month}.")

if __name__ == "__main__":
    process_monthly_averages()