import streamlit as st
from src.database.connection import get_session
from src.services.assignment_service import AssignmentService
from src.services.catalog_service import CatalogService

def render_researcher_dashboard():
    st.title("📱 Coleta de Preços (Pesquisador)")
    
    user = st.session_state['user']
    session = next(get_session())
    service = AssignmentService(session)
    catalog = CatalogService(session)
    
    # 1. Minhas Tarefas
    my_tasks = service.get_my_pending_assignments(user.id)
    
    if not my_tasks:
        st.success("🎉 Nenhuma tarefa pendente! Bom descanso.")
        return

    # Seleciona qual loja estou visitando agora
    task_options = {t.id: f"{t.store.name} - {t.week_start_date}" for t in my_tasks}
    selected_task_id = st.selectbox("📍 Visita Atual:", options=task_options.keys(), format_func=lambda x: task_options[x])
    
    current_task = next(t for t in my_tasks if t.id == selected_task_id)
    
    st.divider()
    st.markdown(f"### Loja: {current_task.store.name}")

    # 2. Coleta
    with st.container(border=True):
        col1, col2 = st.columns(2)
        brands = catalog.get_all_brands()
        brand = col1.selectbox("Marca", brands, format_func=lambda x: x.name)
        
        if brand:
            models = catalog.get_models_by_brand(brand.id)
            model = col2.selectbox("Modelo", models, format_func=lambda x: x.name)
            
            c1, c2 = st.columns(2)
            ano = c1.number_input("Ano", value=2024)
            price = c2.number_input("Preço (R$)", min_value=0.0)
            
            if st.button("💾 Salvar Preço"):
                service.capture_price(current_task.id, model.id, price, ano)
                st.toast("Preço salvo!")

    # 3. Finalizar
    if st.button("✅ Finalizar Visita"):
        service.complete_assignment(current_task.id)
        st.balloons()
        st.rerun()