# src/ui/pages/manager_dashboard.py
import streamlit as st
import pandas as pd
from sqlmodel import select, func
from src.database.connection import get_session
from src.models import VehicleCapture, ResearchAssignment, Store, AssignmentStatus

def render_manager_dashboard():
    st.title("💼 Visão Tática (Gerência)")
    st.markdown("Indicadores de performance da operação de coleta.")

    session = next(get_session())

    # --- KPI: VISITAS ---
    try:
        # Total de visitas agendadas
        total_assignments = session.exec(select(func.count(ResearchAssignment.id))).one()
        
        # Total de visitas concluídas
        completed_assignments = session.exec(
            select(func.count(ResearchAssignment.id))
            .where(ResearchAssignment.status == AssignmentStatus.COMPLETED)
        ).one()
        
        # Total de preços coletados
        total_captures = session.exec(select(func.count(VehicleCapture.id))).one()
    except Exception:
        total_assignments = 0
        completed_assignments = 0
        total_captures = 0

    # Exibe KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Visitas Totais", total_assignments)
    
    delta_val = f"{(completed_assignments/total_assignments*100):.1f}%" if total_assignments > 0 else "0%"
    col2.metric("Concluídas", completed_assignments, delta=delta_val)
    
    col3.metric("Preços Coletados", total_captures)

    st.divider()

    # --- GRÁFICO 1: VOLUME POR LOJA ---
    st.subheader("📊 Coletas por Loja")
    
    query = (
        select(Store.name, func.count(VehicleCapture.id))
        .join(ResearchAssignment, ResearchAssignment.store_id == Store.id)
        .join(VehicleCapture, VehicleCapture.assignment_id == ResearchAssignment.id)
        .group_by(Store.name)
    )
    results = session.exec(query).all()
    
    if results:
        df_stores = pd.DataFrame(results, columns=["Loja", "Coletas"])
        st.bar_chart(df_stores.set_index("Loja"))
    else:
        st.info("Ainda não há dados suficientes para gerar gráficos.")