import streamlit as st
from datetime import date
from sqlmodel import select
from src.database.connection import get_session
from src.models import User, Store, UserRole, ResearchAssignment, AssignmentStatus
from src.services.assignment_service import AssignmentService

def render_coordinator_dashboard():
    st.title("📅 Gestão de Visitas (Coordenador)")
    st.info("Distribua as visitas para os pesquisadores.")

    session = next(get_session())
    service = AssignmentService(session)

    # 1. Formulário de Agendamento
    with st.form("assign_form"):
        col1, col2, col3 = st.columns(3)
        
        # Select Pesquisadores
        researchers = session.exec(select(User).where(User.role == UserRole.PESQUISADOR)).all()
        r_selected = col1.selectbox("Pesquisador", researchers, format_func=lambda x: x.name)
        
        # Select Lojas
        stores = session.exec(select(Store)).all()
        s_selected = col2.selectbox("Loja Alvo", stores, format_func=lambda x: f"{x.name} ({x.region.name})")
        
        # Select Data
        d_selected = col3.date_input("Data da Visita", date.today())
        
        if st.form_submit_button("📅 Agendar Visita"):
            if r_selected and s_selected:
                service.create_assignment(r_selected.id, s_selected.id, d_selected)
                st.success(f"Visita agendada para {r_selected.name} na loja {s_selected.name}!")
                st.rerun()

    # 2. Lista de Agendamentos
    st.divider()
    st.subheader("Agenda da Semana")
    assignments = service.get_all_assignments()
    
    if assignments:
        # Tabela Simples
        data = []
        for a in assignments:
            data.append({
                "Data": a.week_start_date,
                "Pesquisador": a.researcher.name,
                "Loja": a.store.name,
                "Status": a.status.value
            })
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("Nenhuma visita agendada ainda.")