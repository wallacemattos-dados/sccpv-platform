import sys
import os
import streamlit as st

# Blindagem de PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.login import render_login
from src.ui.pages.admin_dashboard import render_admin_dashboard
from src.ui.pages.public_search import render_public_search

# --- IMPORTS NOVOS ---
from src.ui.pages.coordinator_dashboard import render_coordinator_dashboard
from src.ui.pages.researcher_dashboard import render_researcher_dashboard

st.set_page_config(page_title="SCCPV", layout="wide")

def main():
    if 'user' in st.session_state:
        # SIDEBAR LOGADO
        with st.sidebar:
            st.write(f"👤 {st.session_state['user'].name}")
            if st.button("Sair"):
                del st.session_state['user']
                st.rerun()
        
        # ROTEAMENTO POR PAPEL (O SEGREDO ESTÁ AQUI)
        role = st.session_state['user'].role.value
        
        if role == "admin":
            render_admin_dashboard()
        elif role == "coordenador":
            render_coordinator_dashboard()
        elif role == "pesquisador":
            render_researcher_dashboard()
        else:
            st.error(f"Sem tela para perfil: {role}")

    else:
        # NÃO LOGADO
        page = st.sidebar.radio("Menu", ["Consulta Pública", "Login"])
        if page == "Consulta Pública":
            render_public_search()
        else:
            render_login()

if __name__ == "__main__":
    main()