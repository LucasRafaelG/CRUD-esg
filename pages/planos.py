import streamlit as st
import pandas as pd
from datetime import date, timedelta
from database.connection import run_query
from database.queries import (
    SELECT_ALL_PLANOS,
    INSERT_PLANO,
    UPDATE_PLANO,
    DELETE_PLANO,
    SELECT_ALL_FORNECEDORES,
)

STATUS_OPCOES = ["Pendente", "Em Andamento", "Concluído", "Atrasado", "Cancelado"]
CRITICIDADE_OPCOES = ["baixa", "media", "alta"]

CORES_STATUS = {
    "Pendente":     "background-color: #4d3000; color: #e67e22",
    "Em Andamento": "background-color: #1a2e4d; color: #3498db",
    "Concluído":    "background-color: #1e4d2b; color: #2ecc71",
    "Atrasado":     "background-color: #4d1a1a; color: #e74c3c",
    "Cancelado":    "background-color: #2a2a2a; color: #95a5a6",
}

CORES_CRIT = {
    "alta":  "background-color: #4d1a1a; color: #e74c3c",
    "media": "background-color: #4d3000; color: #e67e22",
    "baixa": "background-color: #1e4d2b; color: #2ecc71",
}


def show():
    st.markdown("## 📌 Gestão de Planos de Ação")
    st.markdown("---")

    tab_listar, tab_inserir, tab_editar, tab_deletar = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"]
    )

    # ── LISTAR ────────────────────────────────────────────────
    with tab_listar:
        st.markdown("### Todos os Planos de Ação")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_status = st.selectbox("Status", ["Todos"] + STATUS_OPCOES, key="pl_f_status")
        with col_f2:
            filtro_crit = st.selectbox("Criticidade", ["Todos"] + CRITICIDADE_OPCOES, key="pl_f_crit")
        with col_f3:
            filtro_forn = st.text_input("Fornecedor (nome)", key="pl_f_forn")

        data = run_query(SELECT_ALL_PLANOS)
        if data:
            df = pd.DataFrame(data)
            if filtro_status != "Todos":
                df = df[df["status"] == filtro_status]
            if filtro_crit != "Todos":
                df = df[df["criticidade"] == filtro_crit]
            if filtro_forn:
                df = df[df["fornecedor"].str.contains(filtro_forn, case=False, na=False)]

            # Dias restantes
            df["dias_restantes"] = pd.to_datetime(df["prazo_final"]).apply(
                lambda d: (d.date() - date.today()).days
            )

            def estilo_status(val):
                return CORES_STATUS.get(val, "")

            def estilo_crit(val):
                return CORES_CRIT.get(val, "")

            df_display = df[["id_plano", "fornecedor", "criticidade", "status",
                              "data_criacao", "prazo_final", "dias_restantes"]].copy()
            df_display.columns = ["ID", "Fornecedor", "Criticidade", "Status",
                                   "Criado em", "Prazo Final", "Dias Restantes"]

            st.dataframe(
                df_display.style
                    .map(estilo_status, subset=["Status"])
                    .map(estilo_crit, subset=["Criticidade"]),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"Mostrando {len(df_display)} plano(s)")
        else:
            st.info("Nenhum plano de ação encontrado.")

    # ── INSERIR ───────────────────────────────────────────────
    with tab_inserir:
        st.markdown("### Novo Plano de Ação")
        fornecedores = run_query(SELECT_ALL_FORNECEDORES)
        if not fornecedores:
            st.error("Cadastre fornecedores antes de criar planos.")
        else:
            opcoes_forn = {r["nome_fantasia"]: r["cnpj"] for r in fornecedores}

            with st.form("form_insert_plano"):
                forn_sel = st.selectbox("Fornecedor", list(opcoes_forn.keys()))
                descricao = st.text_area("Descrição do Plano", height=100)
                col1, col2, col3 = st.columns(3)
                with col1:
                    criticidade = st.selectbox("Criticidade", CRITICIDADE_OPCOES)
                with col2:
                    prazo = st.date_input("Prazo Final", value=date.today() + timedelta(days=30))
                with col3:
                    status = st.selectbox("Status Inicial", STATUS_OPCOES)
                submitted = st.form_submit_button("💾 Criar Plano")

            if submitted:
                if not descricao.strip():
                    st.error("Descrição é obrigatória.")
                elif prazo <= date.today():
                    st.warning("⚠️ Prazo final já passou — o plano pode ser marcado como Atrasado.")
                    cnpj = opcoes_forn[forn_sel]
                    rows = run_query(INSERT_PLANO, params=(descricao, criticidade, str(prazo), status, cnpj), fetch=False)
                    if rows:
                        st.success(f"✅ Plano criado para '{forn_sel}'!")
                else:
                    cnpj = opcoes_forn[forn_sel]
                    rows = run_query(INSERT_PLANO, params=(descricao, criticidade, str(prazo), status, cnpj), fetch=False)
                    if rows:
                        st.success(f"✅ Plano criado para '{forn_sel}'!")
                    else:
                        st.error("Erro ao criar o plano.")

    # ── EDITAR ────────────────────────────────────────────────
    with tab_editar:
        st.markdown("### Editar Plano de Ação")
        data = run_query(SELECT_ALL_PLANOS)
        if data:
            opcoes = {
                f"#{r['id_plano']} — {r['fornecedor']} [{r['criticidade'].upper()}] ({r['status']})": r
                for r in data
            }
            sel = st.selectbox("Selecione o plano", list(opcoes.keys()), key="pl_edit_sel")
            reg = opcoes[sel]

            with st.form("form_edit_plano"):
                nova_desc = st.text_area("Descrição", value=reg["descricao"] or "", height=100)
                col1, col2, col3 = st.columns(3)
                with col1:
                    nova_crit = st.selectbox(
                        "Criticidade", CRITICIDADE_OPCOES,
                        index=CRITICIDADE_OPCOES.index(reg["criticidade"]) if reg["criticidade"] in CRITICIDADE_OPCOES else 0,
                    )
                with col2:
                    novo_prazo = st.date_input(
                        "Prazo Final",
                        value=pd.to_datetime(reg["prazo_final"]).date() if reg["prazo_final"] else date.today(),
                    )
                with col3:
                    novo_status = st.selectbox(
                        "Status", STATUS_OPCOES,
                        index=STATUS_OPCOES.index(reg["status"]) if reg["status"] in STATUS_OPCOES else 0,
                    )
                submitted_edit = st.form_submit_button("💾 Salvar Alterações")

            if submitted_edit:
                rows = run_query(
                    UPDATE_PLANO,
                    params=(nova_desc, nova_crit, str(novo_prazo), novo_status, reg["id_plano"]),
                    fetch=False,
                )
                if rows:
                    st.success("✅ Plano atualizado com sucesso!")
                else:
                    st.warning("Nenhuma alteração realizada.")
        else:
            st.info("Nenhum plano disponível para editar.")

    # ── DELETAR ───────────────────────────────────────────────
    with tab_deletar:
        st.markdown("### Deletar Plano de Ação")
        st.warning("⚠️ Esta ação é irreversível.")
        data = run_query(SELECT_ALL_PLANOS)
        if data:
            opcoes_del = {
                f"#{r['id_plano']} — {r['fornecedor']} ({r['status']})": r["id_plano"]
                for r in data
            }
            sel_del = st.selectbox("Selecione o plano para deletar", list(opcoes_del.keys()), key="pl_del_sel")
            id_del = opcoes_del[sel_del]
            confirmar = st.checkbox(f"Confirmo a exclusão do plano **{sel_del}**")
            if st.button("🗑️ Deletar", disabled=not confirmar, key="pl_del_btn"):
                rows = run_query(DELETE_PLANO, params=(id_del,), fetch=False)
                if rows:
                    st.success("✅ Plano deletado com sucesso!")
                else:
                    st.error("Erro ao deletar.")
        else:
            st.info("Nenhum plano disponível.")
