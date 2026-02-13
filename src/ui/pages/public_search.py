import streamlit as st
from sqlmodel import select
from src.database import get_session
from src.models import Brand, Model, MonthlyAverage
from src.services.catalog_service import CatalogService

def render_public_search():
    st.title("🚗 Consulta de Preços (SCCPV)")
    st.markdown("Consulte a média de mercado (Base Inicial: Tabela FIPE).")
    
    session = next(get_session())
    catalog_service = CatalogService(session)

    # 1. Seleção de Marca (Do Banco)
    brands = catalog_service.get_all_brands()
    marca = st.selectbox("1. Marca", brands, format_func=lambda x: x.name, index=None, placeholder="Selecione...")
    
    if marca:
        # 2. Seleção de Modelo (Do Banco)
        models = catalog_service.get_models_by_brand(marca.id)
        modelo = st.selectbox("2. Modelo", models, format_func=lambda x: x.name, index=None, placeholder="Selecione...")
        
        if modelo:
            # 3. Busca Anos disponíveis na tabela de Médias
            years_query = select(MonthlyAverage.model_year).where(MonthlyAverage.model_id == modelo.id).distinct()
            years = session.exec(years_query).all()
            
            if years:
                ano = st.selectbox("3. Ano Modelo", sorted(years, reverse=True))
                
                if st.button("🔍 Consultar Preço", type="primary"):
                    # Busca a média calculada (ou importada)
                    avg_data = session.exec(
                        select(MonthlyAverage)
                        .where(MonthlyAverage.model_id == modelo.id)
                        .where(MonthlyAverage.model_year == ano)
                        .order_by(MonthlyAverage.reference_month.desc())
                    ).first()
                    
                    if avg_data:
                        st.divider()
                        st.subheader(f"{marca.name} {modelo.name} {ano}")
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Preço Médio", f"R$ {avg_data.avg_price:,.2f}")
                        c2.metric("Mínimo", f"R$ {avg_data.min_price:,.2f}")
                        c3.metric("Máximo", f"R$ {avg_data.max_price:,.2f}")
                        
                        st.caption(f"Referência: {avg_data.reference_month} | Amostra: {avg_data.sample_size} veículo(s)")
                    else:
                        st.warning("Dados não consolidados para este período.")
            else:
                st.info("Nenhum dado de preço disponível para este modelo ainda.")