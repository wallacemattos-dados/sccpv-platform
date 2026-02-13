import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from src.ui.login import render_login
from src.ui.pages.admin_dashboard import render_admin_dashboard
from src.ui.pages.public_search import render_public_search

# Configuração da Página (Deve ser a primeira linha do Streamlit)
st.set_page_config(page_title="SCCPV - Sistema Fipe", layout="wide")

def main():
    # Sidebar de Navegação
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/car--v1.png", width=50)
        st.title("SCCPV Platform")
        
        # Menu de Navegação
        page = st.radio("Navegação", ["Consulta Pública", "Área Restrita"])
        
        st.divider()
        
        # Se estiver logado, mostra botão de sair e infos
        if 'user' in st.session_state:
            user = st.session_state['user']
            st.write(f"👤 **{user.name}**")
            st.caption(f"Perfil: {user.role.value}")
            
            if st.button("Sair (Logout)"):
                del st.session_state['user']
                st.rerun()

    # Roteamento de Páginas
    if page == "Consulta Pública":
        render_public_search()
        
    elif page == "Área Restrita":
        if 'user' not in st.session_state:
            render_login()
        else:
            # Roteamento por Perfil (RBAC)
            user_role = st.session_state['user'].role
            
            if user_role == "admin":
                render_admin_dashboard()
            elif user_role == "gerente":
                st.info("Dashboard do Gerente (Em construção)")
            elif user_role == "pesquisador":
                st.info("Área de Coleta Mobile (Em construção)")
            else:
                st.warning("Perfil sem dashboard definido.")

if __name__ == "__main__":
    main()