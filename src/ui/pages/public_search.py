import streamlit as st

def render_public_search():
    st.title("🚗 Consulta de Preços (SCCPV)")
    st.markdown("Consulte a média de mercado baseada em pesquisas reais.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        marca = st.selectbox("1. Marca", ["Fiat", "Volkswagen", "Toyota"])
    
    with col2:
        # Mock de lógica condicional visual
        modelos = ["Uno", "Palio", "Toro"] if marca == "Fiat" else ["Corolla", "Hilux"]
        modelo = st.selectbox("2. Modelo", modelos)
        
    with col3:
        ano = st.selectbox("3. Ano Modelo", [2024, 2023, 2022, 2021])
        
    if st.button("🔍 Consultar Preço Médio", type="primary"):
        st.divider()
        st.subheader(f"Resultado para: {marca} {modelo} {ano}")
        
        # Simulação de resultado (Fake Data por enquanto)
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Preço Médio", "R$ 45.200,00", "1.2%")
        col_res2.metric("Mínimo", "R$ 42.000,00")
        col_res3.metric("Máximo", "R$ 48.500,00")
        
        st.info("Dados baseados no fechamento mensal de Fevereiro/2026.")