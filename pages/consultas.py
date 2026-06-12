import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import run_query
from database.queries import (
    QUERY_RISCO_FORNECEDOR,
    QUERY_DIAGNOSTICO_STATUS,
    QUERY_RISCO_POR_DIMENSAO,
    QUERY_PLANOS_CRITICOS,
    QUERY_FORNECEDORES_SEM_DIAGNOSTICO,
)


CONSULTAS = {
    "1 — Ranking de Risco por Fornecedor (JOIN)": {
        "sql": QUERY_RISCO_FORNECEDOR,
        "descricao": "Calcula o risco médio de cada fornecedor cruzando as tabelas `avaliacao` e `fornecedor`. Ordena do mais arriscado ao menos arriscado.",
        "nivel": "⭐⭐ Médio",
    },
    "2 — Diagnósticos com Score de IA (JOIN múltiplo)": {
        "sql": QUERY_DIAGNOSTICO_STATUS,
        "descricao": "Lista todos os diagnósticos com o score médio atribuído pela IA, cruzando `diagnostico`, `fornecedor` e `resposta`.",
        "nivel": "⭐⭐ Médio",
    },
    "3 — Risco por Dimensão ESG (JOIN triplo + GROUP BY)": {
        "sql": QUERY_RISCO_POR_DIMENSAO,
        "descricao": "Agrupa o risco por dimensão ESG (ambiental, social, governança), cruzando `avaliacao`, `ia_modelo` e `fornecedor`. Calcula min, max e média.",
        "nivel": "⭐⭐⭐ Alto",
    },
    "4 — Planos Críticos com Tarefas Pendentes (JOIN + CASE + DATEDIFF)": {
        "sql": QUERY_PLANOS_CRITICOS,
        "descricao": "Lista planos de ação de criticidade ALTA com contagem de tarefas pendentes e dias restantes até o prazo. Usa CASE WHEN e DATEDIFF.",
        "nivel": "⭐⭐⭐ Alto",
    },
    "5 — Fornecedores sem Diagnóstico (LEFT JOIN + IS NULL)": {
        "sql": QUERY_FORNECEDORES_SEM_DIAGNOSTICO,
        "descricao": "Identifica fornecedores que ainda não possuem nenhum diagnóstico ESG associado. Usa LEFT JOIN para detectar ausência de relação.",
        "nivel": "⭐⭐ Médio",
    },
}


def show():
    st.markdown("## 🔍 Consultas SQL")
    st.markdown("---")

    consulta_sel = st.selectbox("Selecione uma consulta", list(CONSULTAS.keys()))
    info = CONSULTAS[consulta_sel]

    col_desc, col_nivel = st.columns([4, 1])
    with col_desc:
        st.info(f"📌 {info['descricao']}")
    with col_nivel:
        st.markdown(f"**Nível:** {info['nivel']}")

    with st.expander("🧾 Ver SQL da consulta"):
        st.code(info["sql"], language="sql")

    if st.button("▶️ Executar Consulta"):
        with st.spinner("Executando..."):
            data = run_query(info["sql"])

        if data:
            df = pd.DataFrame(data)
            st.success(f"✅ {len(df)} resultado(s) encontrado(s)")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Gráfico automático para consultas específicas
            if "1 —" in consulta_sel and "risco_medio" in df.columns:
                st.markdown("#### 📊 Visualização — Risco Médio por Fornecedor")
                fig = px.bar(
                    df.head(15),
                    x="fornecedor",
                    y="risco_medio",
                    color="risco_medio",
                    color_continuous_scale=["#2ecc71", "#e67e22", "#e74c3c"],
                    range_color=[0, 10],
                    labels={"risco_medio": "Risco Médio", "fornecedor": "Fornecedor"},
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e0e0e0",
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig, use_container_width=True)

            elif "3 —" in consulta_sel and "dimensao" in df.columns:
                st.markdown("#### 📊 Visualização — Risco por Dimensão ESG")
                CORES_ESG = {"ambiental": "#2ecc71", "social": "#3498db", "governanca": "#9b59b6"}
                fig = px.bar(
                    df,
                    x="dimensao",
                    y="risco_medio",
                    color="dimensao",
                    color_discrete_map=CORES_ESG,
                    error_y=None,
                    labels={"risco_medio": "Risco Médio", "dimensao": "Dimensão ESG"},
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e0e0e0",
                )
                st.plotly_chart(fig, use_container_width=True)

            elif "4 —" in consulta_sel and "dias_restantes" in df.columns:
                st.markdown("#### 📊 Visualização — Dias Restantes por Plano")
                fig = px.bar(
                    df,
                    x="id_plano",
                    y="dias_restantes",
                    color="tarefas_pendentes",
                    color_continuous_scale="Reds",
                    labels={
                        "dias_restantes": "Dias Restantes",
                        "id_plano": "ID Plano",
                        "tarefas_pendentes": "Tarefas Pendentes",
                    },
                    text="fornecedor",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e0e0e0",
                )
                st.plotly_chart(fig, use_container_width=True)

            # Exportar CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Exportar resultado (.csv)",
                data=csv,
                file_name=f"resultado_consulta.csv",
                mime="text/csv",
            )
        else:
            st.warning("Nenhum resultado encontrado.")
