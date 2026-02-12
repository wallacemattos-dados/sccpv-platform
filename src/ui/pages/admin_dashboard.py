import streamlit as st
from sqlmodel import select
from src.database import get_session
from src.models import User, UserRole

def render_admin_dashboard():
    st.title("🛠️ Painel Administrativo")
    st.markdown("Gestão de Usuários e Permissões")
    
    # Abas para organizar
    tab1, tab2 = st.tabs(["Listar Usuários", "Novo Usuário"])
    
    session = next(get_session())
    
    with tab1:
        users = session.exec(select(User)).all()
        
        # Exibe dados em uma tabela limpa (removendo senha hash)
        user_data = [
            {"ID": u.id, "Nome": u.name, "Email": u.email, "Role": u.role.value, "Ativo": u.is_active}
            for u in users
        ]
        st.dataframe(user_data, use_container_width=True)
    
    with tab2:
        st.warning("Funcionalidade de cadastro em desenvolvimento (DEV-02)")