import streamlit as st
import pandas as pd
from sqlmodel import select, func
from src.database.connection import get_session
from src.models import VehicleCapture, ResearchAssignment, Store, AssignmentStatus
from src.services.catalog_service import CatalogService # <--- Novo Import

def render_manager_dashboard():
    st.title("💼 Painel Gerencial")
    
    # Organiza em Abas para cumprir o Requisito 2
    tab_kpi, tab_marcas, tab_modelos = st.tabs(["📊 Indicadores", "🏷️ Gestão Marcas", "🚗 Gestão Modelos"])

    session = next(get_session())
    catalog_service = CatalogService(session) # <--- Serviço de Catálogo

    # --- ABA 1: INDICADORES (O que já tínhamos) ---
    with tab_kpi:
        # ... (CÓDIGO DOS KPIS E GRÁFICOS QUE JÁ FIZEMOS NO PASSO ANTERIOR) ...
        # (Copie aqui a lógica de KPIs e Gráficos do arquivo anterior manager_dashboard.py)
        # Para facilitar, vou resumir a lógica dos KPIs aqui:
        total_assignments = session.exec(select(func.count(ResearchAssignment.id))).one()
        total_captures = session.exec(select(func.count(VehicleCapture.id))).one()
        
        c1, c2 = st.columns(2)
        c1.metric("Visitas Totais", total_assignments)
        c2.metric("Preços Coletados", total_captures)
        
        st.caption("Dados em tempo real.")

    # --- ABA 2: MARCAS (Requisito do Gerente) ---
    with tab_marcas:
        st.subheader("Catálogo de Marcas")
        with st.form("mgr_new_brand"):
            if st.form_submit_button("Salvar Nova Marca") and (nome := st.text_input("Nome")):
                catalog_service.create_brand(nome)
                st.success("Marca criada!")
                st.rerun()
        st.dataframe([{"Nome": b.name} for b in catalog_service.get_all_brands()], use_container_width=True)

    # --- ABA 3: MODELOS (Requisito do Gerente) ---
    with tab_modelos:
        st.subheader("Catálogo de Modelos")
        brands = catalog_service.get_all_brands()
        if brands:
            brand = st.selectbox("Selecione a Marca", brands, format_func=lambda x: x.name)
            with st.form("mgr_new_model"):
                nome = st.text_input("Nome Modelo")
                cat = st.selectbox("Categoria", ["SUV", "Sedan", "Hatch", "Picape"])
                if st.form_submit_button("Salvar Modelo") and nome:
                    catalog_service.create_model(nome, brand.id, cat)
                    st.success("Modelo criado!")
                    st.rerun()
            
            models = catalog_service.get_models_by_brand(brand.id)
            st.dataframe([{"Modelo": m.name, "Categoria": m.category} for m in models], use_container_width=True)