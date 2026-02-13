# src/ui/pages/store_owner_dashboard.py
import streamlit as st
from sqlmodel import select
from src.database.connection import get_session
from src.services.store_service import StoreService
from src.models import Store, ResearchAssignment, VehicleCapture

def render_store_owner_dashboard():
    st.title("🏪 Portal do Lojista")
    
    if 'user' not in st.session_state:
        st.error("Sessão inválida. Faça login novamente.")
        return

    user = st.session_state['user']
    session = next(get_session())
    store_service = StoreService(session)

    # 1. Verifica se o usuário já tem loja cadastrada
    my_stores = session.exec(select(Store).where(Store.created_by_id == user.id)).all()

    if not my_stores:
        st.warning("Você ainda não possui lojas cadastradas.")
        
        with st.form("register_store"):
            st.subheader("Cadastrar Minha Loja")
            name = st.text_input("Nome Fantasia")
            address = st.text_input("Endereço Completo")
            
            # Busca regiões para o select
            regions = store_service.get_all_regions()
            
            if not regions:
                st.error("O sistema ainda não possui regiões cadastradas pelo Administrador.")
                region_selected = None
            else:
                region_selected = st.selectbox("Região", regions, format_func=lambda x: x.name)
            
            if st.form_submit_button("Solicitar Cadastro"):
                if region_selected and name and address:
                    store_service.create_store_request(name, address, region_selected.id, user.id)
                    st.success("Solicitação enviada! Aguarde aprovação do administrador.")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos e certifique-se de que há regiões disponíveis.")
    else:
        # Se tem loja, mostra os dados da primeira loja encontrada
        store = my_stores[0] 
        
        # Header da Loja
        st.subheader(f"🏠 {store.name}")
        st.caption(f"{store.address} | Status: {store.status.value.upper()}")
        
        if store.status.value == "pending":
            st.info("🕒 Sua loja está em análise. Em breve você receberá visitas.")
        else:
            st.divider()
            st.markdown("### 📋 Histórico de Coletas na Sua Loja")
            
            # Busca veículos coletados NESTA loja
            # Fazemos um Join para garantir que pegamos capturas -> assignments -> loja certa
            captures = session.exec(
                select(VehicleCapture)
                .join(ResearchAssignment)
                .where(ResearchAssignment.store_id == store.id)
                .order_by(VehicleCapture.capture_date.desc())
            ).all()
            
            if captures:
                data = [
                    {
                        "Data": c.capture_date.strftime("%d/%m/%Y"),
                        "Modelo": c.model.name,
                        "Ano": c.model_year,
                        "Preço Coletado": f"R$ {c.price:,.2f}"
                    }
                    for c in captures
                ]
                st.dataframe(data, use_container_width=True)
            else:
                st.info("Nenhuma visita realizada ainda nesta loja.")