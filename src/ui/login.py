import streamlit as st
from src.database import get_session
from src.services.auth_service import AuthService

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Acesso Restrito SCCPV")
        
        email = st.text_input("E-mail", placeholder="admin@sccpv.com")
        password = st.text_input("Senha", type="password", placeholder="admin123")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            # Injeção de dependência manual para a sessão
            session = next(get_session())
            auth_service = AuthService(session)
            
            user = auth_service.authenticate_user(email, password)
            
            if user:
                # Salva o usuário na sessão (Cookie criptografado do Streamlit)
                st.session_state['user'] = user
                st.success(f"Bem-vindo, {user.name}!")
                st.rerun() # Recarrega a página para atualizar o menu
            else:
                st.error("Credenciais inválidas. Tente novamente.")

        st.markdown("---")
        st.info("Para acesso público à tabela de preços, use o menu lateral.")