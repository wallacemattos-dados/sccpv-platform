import streamlit as st
from sqlmodel import select
from src.database import get_session
from src.services.catalog_service import CatalogService
from src.models import User, Brand, Model

def render_admin_dashboard():
    st.title("🛠️ Backoffice Administrativo")
    st.caption("Gerencie Usuários, Marcas e Modelos aqui.")
    
    # Abas para organizar a tela
    tab_users, tab_brands, tab_models = st.tabs(["👥 Usuários", "🏷️ Marcas", "🚗 Modelos"])
    
    # Inicializa sessão e serviço
    session = next(get_session())
    catalog_service = CatalogService(session)
    
    # --- ABA 1: USUÁRIOS ---
    with tab_users:
        st.subheader("Controle de Acesso")
        users = session.exec(select(User)).all()
        # Exibe tabela simples
        st.dataframe(
            [{"ID": u.id, "Nome": u.name, "Email": u.email, "Perfil": u.role.value} for u in users],
            use_container_width=True
        )
        st.info("Para adicionar usuários, utilize o script de bootstrap ou solicite ao suporte (MVP).")

    # --- ABA 2: MARCAS ---
    with tab_brands:
        st.subheader("Catálogo de Marcas")
        
        # Área de Cadastro Manual
        with st.expander("➕ Cadastrar Nova Marca"):
            with st.form("new_brand_form"):
                brand_name = st.text_input("Nome da Marca")
                if st.form_submit_button("Salvar"):
                    if brand_name:
                        catalog_service.create_brand(brand_name)
                        st.success(f"Marca '{brand_name}' salva!")
                        st.rerun()

        # Listagem (Grid)
        brands = catalog_service.get_all_brands()
        if brands:
            st.dataframe([{"ID": b.id, "Nome": b.name} for b in brands], use_container_width=True)
        else:
            st.warning("Nenhuma marca encontrada. Rode o importador da FIPE!")

    # --- ABA 3: MODELOS ---
    with tab_models:
        st.subheader("Catálogo de Modelos")
        
        brands = catalog_service.get_all_brands()
        if not brands:
            st.error("Cadastre ou importe marcas primeiro.")
        else:
            # Filtro para visualizar modelos
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_brand = st.selectbox("Filtrar por Marca:", brands, format_func=lambda x: x.name)
            
            # Cadastro de Modelo vinculado à marca selecionada
            with st.expander(f"➕ Novo Modelo para {selected_brand.name}"):
                with st.form("new_model_form"):
                    model_name = st.text_input("Nome do Modelo")
                    category = st.selectbox("Categoria", ["SUV", "Sedan", "Hatch", "Picape", "Luxo", "Indefinido"])
                    
                    if st.form_submit_button("Salvar Modelo"):
                        if model_name:
                            catalog_service.create_model(model_name, selected_brand.id, category)
                            st.success("Modelo salvo!")
                            st.rerun()

            # Listagem
            models = catalog_service.get_models_by_brand(selected_brand.id)
            if models:
                st.dataframe(
                    [{"ID": m.id, "Modelo": m.name, "Categoria": m.category} for m in models],
                    use_container_width=True
                )
            else:
                st.info(f"Nenhum modelo cadastrado para {selected_brand.name}.")