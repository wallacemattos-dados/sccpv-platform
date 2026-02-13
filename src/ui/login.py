import streamlit as st
from src.database import get_session
from src.services.auth_service import AuthService

def render_login():
    # Layout: Usamos colunas para centralizar o formulário na tela
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🔐 Acesso Restrito SCCPV")
        st.caption("Acesso exclusivo para administradores, gerentes e pesquisadores.")
        
        # Formulário visual (não usamos st.form para permitir feedback imediato)
        email = st.text_input("E-mail", placeholder="admin@sccpv.com")
        password = st.text_input("Senha", type="password", placeholder="••••••")
        
        login_clicked = st.button("Entrar", type="primary", use_container_width=True)

        if login_clicked:
            if not email or not password:
                st.warning("Por favor, preencha todos os campos.")
            else:
                try:
                    # 1. Obtém a sessão do banco de dados
                    session = next(get_session())
                    
                    # 2. Instancia o serviço de autenticação
                    auth_service = AuthService(session)
                    
                    # 3. Tenta autenticar
                    user = auth_service.authenticate_user(email, password)
                    
                    if user:
                        # SUCESSO: Salva o usuário na sessão do Streamlit
                        st.session_state['user'] = user
                        st.toast(f"Bem-vindo de volta, {user.name}!", icon="✅")
                        
                        # Recarrega a página para o app.py redirecionar para o Dashboard
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")
                except Exception as e:
                    st.error(f"Erro ao tentar login: {e}")

        st.markdown("---")
        st.info("💡 Dica: Se você é um visitante, use o menu lateral para acessar a **Consulta Pública** sem necessidade de login.")