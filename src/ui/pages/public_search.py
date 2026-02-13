import streamlit as st
from sqlmodel import select, desc
from src.database.connection import get_session
from src.models import Brand, Model, MonthlyAverage, UserQuery

def render_public_search():
    st.title("🚗 Consulta de Preços (SCCPV)")
    st.markdown("Consulte a média de mercado baseada na Tabela FIPE e coletas regionais.")
    
    # Inicia sessão com o banco
    session = next(get_session())

    # --- FILTRO 1: MARCA ---
    # Busca todas as marcas ordenadas por nome
    brands = session.exec(select(Brand).order_by(Brand.name)).all()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        marca_selecionada = st.selectbox(
            "1. Marca",
            options=brands,
            format_func=lambda x: x.name, # Mostra o nome, mas o objeto é o valor
            index=None,
            placeholder="Selecione a marca..."
        )

    # --- FILTRO 2: MODELO (Depende da Marca) ---
    modelo_selecionado = None
    with col2:
        if marca_selecionada:
            models = session.exec(
                select(Model)
                .where(Model.brand_id == marca_selecionada.id)
                .order_by(Model.name)
            ).all()
            
            modelo_selecionado = st.selectbox(
                "2. Modelo",
                options=models,
                format_func=lambda x: x.name,
                index=None,
                placeholder="Selecione o modelo..."
            )
        else:
            st.selectbox("2. Modelo", [], disabled=True, placeholder="Aguardando marca...")

    # --- FILTRO 3: ANO (Depende do Modelo e se existe preço cadastrado) ---
    ano_selecionado = None
    with col3:
        if modelo_selecionado:
            # Busca apenas os anos que possuem registro na tabela de médias
            query_anos = (
                select(MonthlyAverage.model_year)
                .where(MonthlyAverage.model_id == modelo_selecionado.id)
                .distinct()
                .order_by(desc(MonthlyAverage.model_year))
            )
            anos_disponiveis = session.exec(query_anos).all()
            
            if anos_disponiveis:
                ano_selecionado = st.selectbox(
                    "3. Ano Modelo",
                    options=anos_disponiveis,
                    placeholder="Selecione o ano..."
                )
            else:
                st.warning("Sem dados para este modelo.")
        else:
            st.selectbox("3. Ano Modelo", [], disabled=True, placeholder="Aguardando modelo...")

    # --- AÇÃO: BUSCAR PREÇO ---
    if st.button("🔍 Consultar Preço", type="primary", disabled=not (marca_selecionada and modelo_selecionado and ano_selecionado)):
        
        # 1. Busca os dados de preço (Pega o mês de referência mais recente)
        query_price = (
            select(MonthlyAverage)
            .where(MonthlyAverage.model_id == modelo_selecionado.id)
            .where(MonthlyAverage.model_year == ano_selecionado)
            .order_by(desc(MonthlyAverage.reference_month)) # Pega o mais recente
        )
        resultado = session.exec(query_price).first()
        
        if resultado:
            st.divider()
            st.subheader(f"Resultado: {marca_selecionada.name} {modelo_selecionado.name} {ano_selecionado}")
            
            # Exibe Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric("Preço Médio", f"R$ {resultado.avg_price:,.2f}", help="Média de mercado")
            c2.metric("Mínimo Encontrado", f"R$ {resultado.min_price:,.2f}")
            c3.metric("Máximo Encontrado", f"R$ {resultado.max_price:,.2f}")
            
            st.caption(f"📅 Mês de Referência: {resultado.reference_month} | 📊 Amostra: {resultado.sample_size} registros")
            
            # 2. LOG DE ANALYTICS (Requisito de Negócio)
            # Salva que alguém pesquisou isso, para o Admin ver quais carros são mais buscados
            try:
                log_query = UserQuery(
                    brand_queried=marca_selecionada.name,
                    model_queried=modelo_selecionado.name,
                    year_queried=ano_selecionado,
                    ip_address="127.0.0.1" # Em prod pegaria do request headers
                )
                session.add(log_query)
                session.commit()
            except Exception as e:
                print(f"Erro ao salvar analytics: {e}") # Não trava a tela do usuário
                
        else:
            st.error("Erro: Dados não encontrados, embora o ano estivesse listado.")