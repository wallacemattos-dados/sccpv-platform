# app.py (ATUALIZADO FINAL)
import sys
import os
import streamlit as st

# Blindagem de PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.login import render_login
from src.ui.pages.admin_dashboard import render_admin_dashboard
from src.ui.pages.public_search import render_public_search

# IMPORTS DOS DASHBOARDS
from src.ui.pages.coordinator_dashboard import render_coordinator_dashboard
from src.ui.pages.researcher_dashboard import render_researcher_dashboard
from src.ui.pages.manager_dashboard import render_manager_dashboard       # <--- NOVO
from src.ui.pages.store_owner_dashboard import render_store_owner_dashboard # <--- NOVO

st.set_page_config(page_title="SCCPV Platform", layout="wide", page_icon="🚗")

def main():
    if 'user' in st.session_state:
        # SIDEBAR LOGADO
        with st.sidebar:
            user = st.session_state['user']
            st.markdown(f"### 👤 {user.name}")
            st.caption(f"Cargo: {user.role.value.title()}")
            
            if st.button("🚪 Sair", use_container_width=True):
                del st.session_state['user']
                st.rerun()
        
        # ROTEAMENTO POR PAPEL
        role = st.session_state['user'].role.value
        
        if role == "admin":
            render_admin_dashboard()
        elif role == "coordenador":
            render_coordinator_dashboard()
        elif role == "pesquisador":
            render_researcher_dashboard()
        elif role == "gerente":
            render_manager_dashboard()     # <--- NOVO
        elif role == "lojista":
            render_store_owner_dashboard() # <--- NOVO
        else:
            st.error(f"Erro de permissão: Perfil '{role}' desconhecido.")

    else:
        # AREA PÚBLICA (NÃO LOGADO)
        with st.sidebar:
            st.title("SCCPV")
            st.info("Bem-vindo ao Sistema de Coleta e Pesquisa Veicular.")
            nav = st.radio("Menu", ["Consulta Pública", "Área Restrita"])
            
        if nav == "Consulta Pública":
            render_public_search()
        else:
            render_login()

if __name__ == "__main__":
    main()