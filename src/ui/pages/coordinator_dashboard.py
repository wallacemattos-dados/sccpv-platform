# src/ui/pages/coordinator_dashboard.py
import streamlit as st
from datetime import date
from sqlmodel import select
from src.database.connection import get_session
from src.models import User, Store, UserRole, StoreStatus
from src.services.assignment_service import AssignmentService
from src.services.store_service import StoreService # <--- Novo Import

def render_coordinator_dashboard():
    st.title("📅 Painel do Coordenador")
    
    # Organização em Abas
    tab_agendas, tab_lojas = st.tabs(["📅 Gestão de Visitas", "✅ Aprovar Lojas"])

    session = next(get_session())
    assignment_service = AssignmentService(session)
    store_service = StoreService(session) # <--- Instância do Serviço

    # --- ABA 1: AGENDAMENTOS (O que já existia) ---
    with tab_agendas:
        st.subheader("Distribuir Tarefas")
        
        with st.form("assign_form"):
            col1, col2, col3 = st.columns(3)
            
            # Select Pesquisadores
            researchers = session.exec(select(User).where(User.role == UserRole.PESQUISADOR)).all()
            if not researchers:
                st.error("Nenhum pesquisador cadastrado.")
                r_selected = None
            else:
                r_selected = col1.selectbox("Pesquisador", researchers, format_func=lambda x: x.name)
            
            # Select Lojas (Apenas Aprovadas aparecem aqui)
            stores = store_service.get_stores_by_status(StoreStatus.APPROVED)
            if not stores:
                st.warning("Nenhuma loja aprovada disponível para visita.")
                s_selected = None
            else:
                s_selected = col2.selectbox("Loja Alvo", stores, format_func=lambda x: f"{x.name} ({x.region.name})")
            
            # Select Data
            d_selected = col3.date_input("Data da Visita", date.today())
            
            if st.form_submit_button("📅 Agendar Visita"):
                if r_selected and s_selected:
                    assignment_service.create_assignment(r_selected.id, s_selected.id, d_selected)
                    st.success(f"Visita agendada para {r_selected.name} na loja {s_selected.name}!")
                    st.rerun()

        st.divider()
        st.markdown("#### Agenda da Semana")
        assignments = assignment_service.get_all_assignments()
        
        if assignments:
            data = [
                {
                    "Data": a.week_start_date.strftime("%d/%m/%Y"),
                    "Pesquisador": a.researcher.name,
                    "Loja": a.store.name,
                    "Status": a.status.value.upper()
                }
                for a in assignments
            ]
            st.dataframe(data, use_container_width=True)
        else:
            st.info("Nenhuma visita agendada.")

    # --- ABA 2: APROVAÇÃO DE LOJAS (NOVO FLUXO) ---
    with tab_lojas:
        st.subheader("Solicitações de Cadastro de Lojas")
        st.caption("Lojistas aguardando validação para entrarem na rota de visitas.")
        
        pending_stores = store_service.get_stores_by_status(StoreStatus.PENDING)
        
        if not pending_stores:
            st.success("🎉 Nenhuma pendência! Todas as lojas foram processadas.")
        else:
            for store in pending_stores:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    
                    # Detalhes da Loja
                    c1.markdown(f"**🏪 {store.name}**")
                    c1.caption(f"📍 {store.address}")
                    
                    # Detalhes da Região/Dono
                    c2.markdown(f"**Região:** {store.region.name}")
                    c2.caption(f"Solicitante: {store.creator.name} ({store.creator.email})")
                    
                    # Ação
                    if c3.button("✅ Aprovar", key=f"appr_{store.id}", type="primary", use_container_width=True):
                        store_service.approve_store(store.id)
                        st.toast(f"Loja '{store.name}' aprovada com sucesso!")
                        st.rerun()