import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import run_query
from database.queries import (
    QUERY_VIEW_RISCOS_ESG,
    QUERY_VIEW_AUDITORIA_EVIDENCIAS,
)

CORES_RISCO = {"Baixo": "#2ecc71", "Médio": "#e67e22", "Alto": "#e74c3c", "Crítico": "#8e1a1a"}
CORES_DIM   = {"Ambiental": "#2ecc71", "Social": "#3498db", "Governança": "#9b59b6"}


def show():
    st.markdown("## 👁️ Views — Consultas Pré-definidas")
    st.markdown("---")
    st.info("As views abaixo foram criadas na **Etapa 04** e consolidam JOINs complexos em consultas reutilizáveis.")

    tab_v1, tab_v2 = st.tabs([
        "📊 vw_painel_riscos_esg",
        "🔍 vw_auditoria_evidencias",
    ])

    # ════════════════════════════════════════════════════════════
    # VIEW 1 — vw_painel_riscos_esg
    # ════════════════════════════════════════════════════════════
    with tab_v1:
        st.markdown("### 📊 View: `vw_painel_riscos_esg`")
        st.markdown("""
        **Objetivo:** Consolida o histórico de análises do motor de IA.
        Une dados cadastrais do fornecedor com a classificação de risco gerada pelas
        diferentes dimensões ESG (Ambiental, Social, Governança).

        Permite relatórios executivos instantâneos sem remontar JOINs complexos.
        """)

        with st.expander("🧾 Ver SQL da View"):
            st.code("""
CREATE OR REPLACE VIEW vw_painel_riscos_esg AS
SELECT
    f.cnpj,
    f.nome_fantasia,
    m.versao          AS versao_modelo,
    m.dimensao_foco,
    a.risco
FROM fornecedor f
JOIN avaliacao a  ON f.cnpj       = a.cnpj_fornecedor
JOIN ia_modelo m  ON a.id_modelo  = m.id_modelo;
            """, language="sql")

        st.markdown("#### Filtros")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_dim_v1 = st.selectbox(
                "Dimensão ESG", ["Todas", "Ambiental", "Social", "Governança"], key="v1_dim"
            )
        with col_f2:
            filtro_risco_v1 = st.selectbox(
                "Nível de Risco", ["Todos", "Baixo", "Médio", "Alto", "Crítico"], key="v1_risco"
            )

        if st.button("▶️ Executar View", key="btn_v1"):
            with st.spinner("Consultando..."):
                data = run_query(QUERY_VIEW_RISCOS_ESG)

            if data:
                df = pd.DataFrame(data)
                if filtro_dim_v1 != "Todas":
                    df = df[df["dimensao_foco"] == filtro_dim_v1]
                if filtro_risco_v1 != "Todos":
                    df = df[df["risco"] == filtro_risco_v1]

                st.success(f"✅ {len(df)} registro(s) retornado(s)")
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Gráficos
                if len(df) > 0:
                    col_g1, col_g2 = st.columns(2)

                    with col_g1:
                        st.markdown("**Distribuição de Risco por Dimensão**")
                        cross = df.groupby(["dimensao_foco", "risco"]).size().reset_index(name="total")
                        fig = px.bar(
                            cross, x="dimensao_foco", y="total", color="risco",
                            barmode="group",
                            color_discrete_map=CORES_RISCO,
                            labels={"dimensao_foco": "Dimensão", "total": "Qtd", "risco": "Risco"},
                        )
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#e0e0e0", margin=dict(t=10, b=20),
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col_g2:
                        st.markdown("**Proporção de Risco (geral)**")
                        dist_risco = df["risco"].value_counts().reset_index()
                        dist_risco.columns = ["risco", "total"]
                        fig2 = px.pie(
                            dist_risco, names="risco", values="total",
                            color="risco", color_discrete_map=CORES_RISCO,
                            hole=0.4,
                        )
                        fig2.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0",
                            margin=dict(t=10, b=10),
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                    # Exportar
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Exportar CSV", data=csv, file_name="vw_painel_riscos_esg.csv", mime="text/csv")
            else:
                st.warning("View sem dados ou não encontrada no banco.")

    # ════════════════════════════════════════════════════════════
    # VIEW 2 — vw_auditoria_evidencias
    # ════════════════════════════════════════════════════════════
    with tab_v2:
        st.markdown("### 🔍 View: `vw_auditoria_evidencias`")
        st.markdown("""
        **Objetivo:** Focada no perfil operacional de Auditores.
        Varre as tabelas de respostas de ponta a ponta e entrega o link do arquivo
        físico anexado (`url_storage`) para cada questão respondida.

        Exige 4 JOINs encadeados: `fornecedor → diagnostico → resposta → resposta_evidencia → evidencia`.
        """)

        with st.expander("🧾 Ver SQL da View"):
            st.code("""
CREATE OR REPLACE VIEW vw_auditoria_evidencias AS
SELECT
    f.nome_fantasia       AS fornecedor,
    d.id_diagnostico,
    d.status              AS status_diagnostico,
    r.num_questao,
    r.score_ia,
    e.tipo_arquivo,
    e.url_storage
FROM fornecedor f
JOIN diagnostico      d  ON f.cnpj            = d.cnpj_fornecedor
JOIN resposta         r  ON d.id_diagnostico  = r.id_diagnostico
JOIN resposta_evidencia re ON r.id_diagnostico = re.id_diagnostico
                          AND r.num_questao    = re.num_questao
JOIN evidencia        e  ON re.id_arquivo     = e.id_arquivo;
            """, language="sql")

        st.markdown("#### Filtros")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_forn_v2 = st.text_input("Fornecedor (nome)", key="v2_forn")
        with col_f2:
            filtro_status_v2 = st.selectbox(
                "Status Diagnóstico",
                ["Todos", "Finalizado", "Em Andamento", "pendente", "concluido"],
                key="v2_status",
            )
        with col_f3:
            filtro_tipo_v2 = st.selectbox(
                "Tipo de Arquivo", ["Todos", "pdf", "png", "jpg", "xlsx", "docx"], key="v2_tipo"
            )

        if st.button("▶️ Executar View", key="btn_v2"):
            with st.spinner("Consultando..."):
                data = run_query(QUERY_VIEW_AUDITORIA_EVIDENCIAS)

            if data:
                df = pd.DataFrame(data)
                if filtro_forn_v2:
                    df = df[df["fornecedor"].str.contains(filtro_forn_v2, case=False, na=False)]
                if filtro_status_v2 != "Todos":
                    df = df[df["status_diagnostico"] == filtro_status_v2]
                if filtro_tipo_v2 != "Todos":
                    df = df[df["tipo_arquivo"] == filtro_tipo_v2]

                st.success(f"✅ {len(df)} evidência(s) encontrada(s)")
                st.dataframe(df, use_container_width=True, hide_index=True)

                if len(df) > 0:
                    # Distribuição de scores
                    if "score_ia" in df.columns:
                        scores_validos = df["score_ia"].dropna()
                        if len(scores_validos) > 0:
                            st.markdown("**Score de IA por Questão (nas evidências filtradas)**")
                            fig3 = px.histogram(
                                df.dropna(subset=["score_ia"]),
                                x="score_ia",
                                nbins=10,
                                color_discrete_sequence=["#3498db"],
                                labels={"score_ia": "Score IA", "count": "Frequência"},
                            )
                            fig3.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font_color="#e0e0e0", margin=dict(t=10, b=20),
                            )
                            st.plotly_chart(fig3, use_container_width=True)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Exportar CSV", data=csv,
                                       file_name="vw_auditoria_evidencias.csv", mime="text/csv")
            else:
                st.warning("View sem dados ou não encontrada no banco.")
