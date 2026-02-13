import streamlit as st
from sqlmodel import select
from src.database.connection import get_session
from src.services.catalog_service import CatalogService
from src.services.store_service import StoreService
from src.models import User, StoreStatus

def render_admin_dashboard():
    st.title("🛠️ Backoffice Administrativo")
    
    # NOVAS ABAS ADICIONADAS
    tab_users, tab_brands, tab_models, tab_regions, tab_stores = st.tabs(
        ["👥 Usuários", "🏷️ Marcas", "🚗 Modelos", "🌍 Regiões", "🏪 Lojas"]
    )
    
    session = next(get_session())
    catalog_service = CatalogService(session)
    store_service = StoreService(session) # Instancia o novo serviço
    
    # --- ABA 1: USUÁRIOS ---
    with tab_users:
        st.subheader("Controle de Acesso")
        users = session.exec(select(User)).all()
        st.dataframe([{"ID": u.id, "Nome": u.name, "Email": u.email, "Perfil": u.role.value} for u in users], use_container_width=True)

    # --- ABA 2: MARCAS ---
    with tab_brands:
        st.subheader("Catálogo de Marcas")
        with st.expander("➕ Nova Marca"):
            with st.form("new_brand"):
                if st.form_submit_button("Salvar") and (nome := st.text_input("Nome")):
                    catalog_service.create_brand(nome)
                    st.rerun()
        st.dataframe([{"Nome": b.name} for b in catalog_service.get_all_brands()], use_container_width=True)

    # --- ABA 3: MODELOS ---
    with tab_models:
        st.subheader("Catálogo de Modelos")
        brands = catalog_service.get_all_brands()
        if brands:
            brand = st.selectbox("Marca", brands, format_func=lambda x: x.name)
            with st.expander("➕ Novo Modelo"):
                with st.form("new_model"):
                    nome = st.text_input("Nome")
                    cat = st.selectbox("Categoria", ["SUV", "Sedan", "Hatch"])
                    if st.form_submit_button("Salvar") and nome:
                        catalog_service.create_model(nome, brand.id, cat)
                        st.rerun()
            models = catalog_service.get_models_by_brand(brand.id)
            st.dataframe([{"Modelo": m.name, "Categoria": m.category} for m in models], use_container_width=True)

    # --- ABA 4: REGIÕES (NOVO) ---
    with tab_regions:
        st.subheader("Gestão Geográfica")
        
        with st.form("region_form"):
            col1, col2 = st.columns([3, 1])
            reg_name = col1.text_input("Nome da Região (ex: Zona Sul)")
            if col2.form_submit_button("Criar Região") and reg_name:
                store_service.create_region(reg_name)
                st.success("Região criada!")
                st.rerun()
                
        regions = store_service.get_all_regions()
        if regions:
            st.dataframe([{"ID": r.id, "Nome": r.name} for r in regions], use_container_width=True)
        else:
            st.info("Nenhuma região cadastrada.")

    # --- ABA 5: LOJAS (NOVO) ---
    with tab_stores:
        st.subheader("Aprovação de Lojas")
        
        # 1. Simulação de Cadastro (Normalmente seria o Lojista fazendo isso)
        with st.expander("📝 Simular Cadastro de Loja (Lojista)"):
            regions = store_service.get_all_regions()
            if not regions:
                st.warning("Crie regiões antes de cadastrar lojas.")
            else:
                with st.form("store_form"):
                    s_name = st.text_input("Nome da Loja")
                    s_addr = st.text_input("Endereço")
                    s_region = st.selectbox("Região", regions, format_func=lambda x: x.name)
                    
                    if st.form_submit_button("Enviar Solicitação"):
                        # Usa o ID do admin logado como 'dono' apenas para teste
                        owner_id = st.session_state['user'].id 
                        store_service.create_store_request(s_name, s_addr, s_region.id, owner_id)
                        st.success("Solicitação enviada!")
                        st.rerun()

        st.divider()
        
        # 2. Área de Aprovação (Workflow)
        st.markdown("#### ⏳ Solicitações Pendentes")
        pending_stores = store_service.get_stores_by_status(StoreStatus.PENDING)
        
        if not pending_stores:
            st.info("Nenhuma solicitação pendente.")
        else:
            for store in pending_stores:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.markdown(f"**{store.name}**")
                    c2.caption(f"{store.address} ({store.region.name})")
                    if c3.button("✅ Aprovar", key=f"btn_{store.id}"):
                        store_service.approve_store(store.id)
                        st.toast(f"Loja {store.name} aprovada!")
                        st.rerun()

        # 3. Lista de Aprovadas
        st.markdown("#### ✅ Lojas Ativas")
        active_stores = store_service.get_stores_by_status(StoreStatus.APPROVED)
        st.dataframe(
            [{"Loja": s.name, "Região": s.region.name, "Status": s.status.value} for s in active_stores],
            use_container_width=True
        )