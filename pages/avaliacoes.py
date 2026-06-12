import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import run_query
from database.queries import (
    SELECT_ALL_AVALIACOES,
    INSERT_AVALIACAO,
    UPDATE_AVALIACAO,
    DELETE_AVALIACAO,
    SELECT_ALL_FORNECEDORES,
    SELECT_ALL_MODELOS_IA,
)

NIVEIS_RISCO = ["Baixo", "Médio", "Alto", "Crítico"]

CORES_RISCO = {
    "Baixo":   "background-color: #1e4d2b; color: #2ecc71",
    "Médio":   "background-color: #4d3000; color: #e67e22",
    "Alto":    "background-color: #4d2500; color: #e67e22",
    "Crítico": "background-color: #4d1a1a; color: #e74c3c",
}

CORES_DIM = {
    "Ambiental":  "#2ecc71",
    "Social":     "#3498db",
    "Governança": "#9b59b6",
}


def show():
    st.markdown("## ⚖️ Gestão de Avaliações de Risco (IA)")
    st.markdown("---")

    tab_listar, tab_inserir, tab_editar, tab_deletar = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"]
    )

    # ── LISTAR ────────────────────────────────────────────────
    with tab_listar:
        st.markdown("### Todas as Avaliações de Risco")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_risco = st.selectbox("Filtrar por Risco", ["Todos"] + NIVEIS_RISCO, key="av_f_risco")
        with col_f2:
            filtro_dim = st.selectbox("Filtrar por Dimensão", ["Todos", "Ambiental", "Social", "Governança"], key="av_f_dim")

        data = run_query(SELECT_ALL_AVALIACOES)
        if data:
            df = pd.DataFrame(data)
            if filtro_risco != "Todos":
                df = df[df["risco"] == filtro_risco]
            if filtro_dim != "Todos":
                df = df[df["dimensao_foco"] == filtro_dim]

            def estilo_risco(val):
                return CORES_RISCO.get(val, "")

            df_display = df[["fornecedor", "modelo_ia", "dimensao_foco", "risco", "data_avaliacao"]].copy()
            df_display.columns = ["Fornecedor", "Modelo IA", "Dimensão", "Risco", "Data Avaliação"]

            st.dataframe(
                df_display.style.map(estilo_risco, subset=["Risco"]),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"Total: {len(df_display)} avaliação(ões)")

            # Mini-gráfico de distribuição
            if len(df) > 0:
                st.markdown("#### Distribuição de Risco nas Avaliações Filtradas")
                dist = df["risco"].value_counts().reset_index()
                dist.columns = ["risco", "total"]
                fig = px.bar(
                    dist, x="risco", y="total",
                    color="risco",
                    color_discrete_map={"Baixo": "#2ecc71", "Médio": "#e67e22",
                                        "Alto": "#e74c3c", "Crítico": "#8e1a1a"},
                    labels={"risco": "Nível de Risco", "total": "Quantidade"},
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e0e0e0", showlegend=False, margin=dict(t=10, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma avaliação encontrada.")

    # ── INSERIR ───────────────────────────────────────────────
    with tab_inserir:
        st.markdown("### Nova Avaliação de Risco")
        st.info("💡 Ao inserir uma avaliação, o trigger **trg_log_avaliacao_ia** registra automaticamente no log.")

        fornecedores = run_query(SELECT_ALL_FORNECEDORES)
        modelos = run_query(SELECT_ALL_MODELOS_IA)

        if not fornecedores or not modelos:
            st.error("Cadastre fornecedores e modelos de IA antes de inserir avaliações.")
        else:
            opcoes_forn = {r["nome_fantasia"]: r["cnpj"] for r in fornecedores}
            opcoes_mod = {f"{r['nome']} ({r['dimensao_foco']}) — v{r['versao']}": r["id_modelo"] for r in modelos}

            with st.form("form_insert_aval"):
                col1, col2 = st.columns(2)
                with col1:
                    forn_sel = st.selectbox("Fornecedor", list(opcoes_forn.keys()))
                with col2:
                    mod_sel = st.selectbox("Modelo de IA", list(opcoes_mod.keys()))
                risco_sel = st.select_slider(
                    "Nível de Risco",
                    options=NIVEIS_RISCO,
                    value="Médio",
                )
                submitted = st.form_submit_button("💾 Registrar Avaliação")

            if submitted:
                cnpj = opcoes_forn[forn_sel]
                id_mod = opcoes_mod[mod_sel]
                rows = run_query(INSERT_AVALIACAO, params=(cnpj, id_mod, risco_sel), fetch=False)
                if rows:
                    st.success(f"✅ Avaliação registrada! Risco '{risco_sel}' para '{forn_sel}'.")
                    st.info("🔔 O trigger `trg_log_avaliacao_ia` gravou automaticamente no log.")
                else:
                    st.error("Erro ao registrar avaliação. Verifique se já existe uma avaliação para este par (fornecedor, modelo).")

    # ── EDITAR ────────────────────────────────────────────────
    with tab_editar:
        st.markdown("### Alterar Nível de Risco")
        data = run_query(SELECT_ALL_AVALIACOES)
        if data:
            opcoes = {
                f"{r['fornecedor']} × {r['modelo_ia']} — atual: {r['risco']}": r
                for r in data
            }
            sel = st.selectbox("Selecione a avaliação", list(opcoes.keys()), key="av_edit_sel")
            reg = opcoes[sel]

            with st.form("form_edit_aval"):
                novo_risco = st.select_slider(
                    "Novo Nível de Risco",
                    options=NIVEIS_RISCO,
                    value=reg["risco"] if reg["risco"] in NIVEIS_RISCO else "Médio",
                )
                submitted_edit = st.form_submit_button("💾 Salvar")

            if submitted_edit:
                rows = run_query(
                    UPDATE_AVALIACAO,
                    params=(novo_risco, reg["cnpj_fornecedor"], reg["id_modelo"]),
                    fetch=False,
                )
                if rows:
                    st.success(f"✅ Risco atualizado para '{novo_risco}'!")
                else:
                    st.warning("Nenhuma alteração realizada.")
        else:
            st.info("Nenhuma avaliação disponível.")

    # ── DELETAR ───────────────────────────────────────────────
    with tab_deletar:
        st.markdown("### Remover Avaliação")
        st.warning("⚠️ Esta ação remove a avaliação de risco do par fornecedor × modelo.")
        data = run_query(SELECT_ALL_AVALIACOES)
        if data:
            opcoes_del = {
                f"{r['fornecedor']} × {r['modelo_ia']} ({r['risco']})": (r["cnpj_fornecedor"], r["id_modelo"])
                for r in data
            }
            sel_del = st.selectbox("Selecione a avaliação", list(opcoes_del.keys()), key="av_del_sel")
            cnpj_del, id_mod_del = opcoes_del[sel_del]
            confirmar = st.checkbox(f"Confirmo a exclusão de **{sel_del}**")
            if st.button("🗑️ Deletar", disabled=not confirmar, key="av_del_btn"):
                rows = run_query(DELETE_AVALIACAO, params=(cnpj_del, id_mod_del), fetch=False)
                if rows:
                    st.success("✅ Avaliação removida!")
                else:
                    st.error("Erro ao deletar.")
        else:
            st.info("Nenhuma avaliação disponível.")
