import streamlit as st
import pandas as pd
from database.connection import run_query
from database.queries import (
    SELECT_ALL_DIAGNOSTICOS,
    INSERT_DIAGNOSTICO,
    UPDATE_DIAGNOSTICO,
    DELETE_DIAGNOSTICO,
    SELECT_ALL_FORNECEDORES,
)


def show():
    st.markdown("## 📋 Gestão de Diagnósticos ESG")
    st.markdown("---")

    tab_listar, tab_inserir, tab_editar, tab_deletar = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar Status", "🗑️ Deletar"]
    )

    # ── LISTAR ────────────────────────────────────────────────
    with tab_listar:
        st.markdown("### Todos os Diagnósticos")

        # filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_status = st.selectbox(
                "Filtrar por Status",
                ["Todos", "pendente", "em andamento", "concluido"],
            )
        with col_f2:
            filtro_forn = st.text_input("Filtrar por Fornecedor (nome)")

        data = run_query(SELECT_ALL_DIAGNOSTICOS)
        if data:
            df = pd.DataFrame(data)
            if filtro_status != "Todos":
                df = df[df["status"] == filtro_status]
            if filtro_forn:
                df = df[df["fornecedor"].str.contains(filtro_forn, case=False, na=False)]

            def colorir_status(val):
                cores = {
                    "concluido": "background-color: #1e4d2b; color: #2ecc71",
                    "pendente": "background-color: #4d3000; color: #e67e22",
                    "em andamento": "background-color: #1a2e4d; color: #3498db",
                }
                return cores.get(val, "")

            df_display = df.copy()
            df_display.columns = ["ID", "Fornecedor", "Status", "Data Início"]
            st.dataframe(
                df_display.style.map(colorir_status, subset=["Status"]),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"Mostrando {len(df_display)} diagnóstico(s)")
        else:
            st.info("Nenhum diagnóstico encontrado.")

    # ── INSERIR ───────────────────────────────────────────────
    with tab_inserir:
        st.markdown("### Novo Diagnóstico")
        fornecedores = run_query(SELECT_ALL_FORNECEDORES)
        if not fornecedores:
            st.error("Nenhum fornecedor cadastrado. Cadastre fornecedores primeiro.")
            return

        opcoes_forn = {r["nome_fantasia"]: r["cnpj"] for r in fornecedores}

        with st.form("form_insert_diag"):
            forn_sel = st.selectbox("Fornecedor", list(opcoes_forn.keys()))
            status_sel = st.selectbox("Status Inicial", ["pendente", "em andamento", "concluido"])
            submitted = st.form_submit_button("💾 Criar Diagnóstico")

        if submitted:
            cnpj_sel = opcoes_forn[forn_sel]
            rows = run_query(INSERT_DIAGNOSTICO, params=(status_sel, cnpj_sel), fetch=False)
            if rows:
                st.success(f"✅ Diagnóstico criado para '{forn_sel}'!")
            else:
                st.error("Erro ao criar diagnóstico.")

    # ── EDITAR ────────────────────────────────────────────────
    with tab_editar:
        st.markdown("### Alterar Status do Diagnóstico")
        data = run_query(SELECT_ALL_DIAGNOSTICOS)
        if data:
            opcoes_diag = {
                f"#{r['id_diagnostico']} — {r['fornecedor']} ({r['status']})": r
                for r in data
            }
            sel = st.selectbox("Selecione o diagnóstico", list(opcoes_diag.keys()))
            reg = opcoes_diag[sel]

            with st.form("form_edit_diag"):
                novo_status = st.selectbox(
                    "Novo Status",
                    ["pendente", "em andamento", "concluido"],
                    index=["pendente", "em andamento", "concluido"].index(reg["status"].lower()) if reg.get("status") and reg["status"].lower() in ["pendente", "em andamento", "concluido"] else 0,
                )
                submitted_edit = st.form_submit_button("💾 Salvar")

            if submitted_edit:
                rows = run_query(
                    UPDATE_DIAGNOSTICO,
                    params=(novo_status, reg["id_diagnostico"]),
                    fetch=False,
                )
                if rows:
                    st.success("✅ Status atualizado!")
                else:
                    st.warning("Nenhuma alteração realizada.")
        else:
            st.info("Nenhum diagnóstico disponível.")

    # ── DELETAR ───────────────────────────────────────────────
    with tab_deletar:
        st.markdown("### Deletar Diagnóstico")
        st.warning("⚠️ As respostas e evidências vinculadas serão removidas (CASCADE).")
        data = run_query(SELECT_ALL_DIAGNOSTICOS)
        if data:
            opcoes_del = {
                f"#{r['id_diagnostico']} — {r['fornecedor']} ({r['status']})": r["id_diagnostico"]
                for r in data
            }
            sel_del = st.selectbox("Selecione o diagnóstico para deletar", list(opcoes_del.keys()))
            id_del = opcoes_del[sel_del]
            confirmar = st.checkbox(f"Confirmo a exclusão do diagnóstico **{sel_del}**")
            if st.button("🗑️ Deletar", disabled=not confirmar):
                rows = run_query(DELETE_DIAGNOSTICO, params=(id_del,), fetch=False)
                if rows:
                    st.success("✅ Diagnóstico deletado!")
                else:
                    st.error("Erro ao deletar.")
        else:
            st.info("Nenhum diagnóstico disponível.")
