import streamlit as st
import pandas as pd
from database.connection import run_query
from database.queries import SELECT_ALL_FORNECEDORES, DELETE_FORNECEDOR


SELECT_FULL = """
SELECT cnpj, nome_fantasia, razao_social, cep, logradouro, numero, cidade, estado
FROM fornecedor ORDER BY nome_fantasia;
"""

INSERT_FORN = """
INSERT INTO fornecedor (cnpj, nome_fantasia, razao_social, cep, logradouro, numero, cidade, estado)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

UPDATE_FORN = """
UPDATE fornecedor
SET nome_fantasia = %s, razao_social = %s, logradouro = %s,
    numero = %s, cep = %s, cidade = %s, estado = %s
WHERE cnpj = %s;
"""

ESTADOS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
           "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]


def show():
    st.markdown("## 🏭 Gestão de Fornecedores")
    st.markdown("---")

    tab_listar, tab_inserir, tab_editar, tab_deletar = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"]
    )

    # ── LISTAR ────────────────────────────────────────────────
    with tab_listar:
        st.markdown("### Todos os Fornecedores")
        data = run_query(SELECT_FULL)
        if data:
            df = pd.DataFrame(data)
            df.columns = ["CNPJ", "Nome Fantasia", "Razão Social", "CEP",
                          "Logradouro", "Número", "Cidade", "Estado"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(df)} fornecedor(es)")
        else:
            st.info("Nenhum fornecedor encontrado.")

    # ── INSERIR ───────────────────────────────────────────────
    with tab_inserir:
        st.markdown("### Novo Fornecedor")
        with st.form("form_insert_forn"):
            col1, col2 = st.columns(2)
            with col1:
                cnpj     = st.text_input("CNPJ (14 dígitos)", max_chars=14)
                nome     = st.text_input("Nome Fantasia")
                razao    = st.text_input("Razão Social")
                cep      = st.text_input("CEP (8 dígitos)", max_chars=8)
            with col2:
                logradouro = st.text_input("Logradouro / Rua")
                numero     = st.text_input("Número")
                cidade     = st.text_input("Cidade")
                estado     = st.selectbox("Estado", ESTADOS)
            submitted = st.form_submit_button("💾 Inserir")

        if submitted:
            erros = []
            if not cnpj or len(cnpj) != 14 or not cnpj.isdigit():
                erros.append("CNPJ deve ter exatamente 14 dígitos numéricos.")
            if not nome:
                erros.append("Nome Fantasia é obrigatório.")
            if not razao:
                erros.append("Razão Social é obrigatória.")
            if not cep or len(cep) != 8 or not cep.isdigit():
                erros.append("CEP deve ter 8 dígitos numéricos.")
            if erros:
                for e in erros:
                    st.error(e)
            else:
                rows = run_query(
                    INSERT_FORN,
                    params=(cnpj, nome, razao, cep, logradouro, numero, cidade, estado),
                    fetch=False,
                )
                if rows:
                    st.success(f"✅ Fornecedor '{nome}' inserido com sucesso!")
                else:
                    st.error("Erro ao inserir. Verifique se o CNPJ já existe.")

    # ── EDITAR ────────────────────────────────────────────────
    with tab_editar:
        st.markdown("### Editar Fornecedor")
        data = run_query(SELECT_FULL)
        if data:
            opcoes = {f"{r['nome_fantasia']} ({r['cnpj']})": r for r in data}
            selecionado = st.selectbox("Selecione o fornecedor", list(opcoes.keys()))
            reg = opcoes[selecionado]

            with st.form("form_edit_forn"):
                col1, col2 = st.columns(2)
                with col1:
                    novo_nome  = st.text_input("Nome Fantasia", value=reg.get("nome_fantasia") or "")
                    nova_razao = st.text_input("Razão Social",  value=reg.get("razao_social")  or "")
                    novo_log   = st.text_input("Logradouro",    value=reg.get("logradouro")    or "")
                    novo_num   = st.text_input("Número",        value=reg.get("numero")        or "")
                with col2:
                    novo_cep    = st.text_input("CEP", value=reg.get("cep") or "", max_chars=8)
                    nova_cidade = st.text_input("Cidade", value=reg.get("cidade") or "")
                    idx_estado  = ESTADOS.index(reg["estado"]) if reg.get("estado") in ESTADOS else 0
                    novo_estado = st.selectbox("Estado", ESTADOS, index=idx_estado)
                submitted_edit = st.form_submit_button("💾 Salvar Alterações")

            if submitted_edit:
                rows = run_query(
                    UPDATE_FORN,
                    params=(novo_nome, nova_razao, novo_log, novo_num,
                            novo_cep, nova_cidade, novo_estado, reg["cnpj"]),
                    fetch=False,
                )
                if rows:
                    st.success("✅ Fornecedor atualizado com sucesso!")
                else:
                    st.warning("Nenhuma alteração realizada.")
        else:
            st.info("Nenhum fornecedor disponível para editar.")

    # ── DELETAR ───────────────────────────────────────────────
    with tab_deletar:
        st.markdown("### Deletar Fornecedor")
        st.warning("⚠️ Esta ação é irreversível e pode afetar diagnósticos e avaliações.")
        data = run_query(SELECT_FULL)
        if data:
            opcoes_del = {f"{r['nome_fantasia']} ({r['cnpj']})": r["cnpj"] for r in data}
            selecionado_del = st.selectbox("Selecione o fornecedor para deletar", list(opcoes_del.keys()))
            cnpj_del = opcoes_del[selecionado_del]
            confirmar = st.checkbox(f"Confirmo que desejo deletar **{selecionado_del}**")
            if st.button("🗑️ Deletar", disabled=not confirmar):
                rows = run_query(DELETE_FORNECEDOR, params=(cnpj_del,), fetch=False)
                if rows:
                    st.success("✅ Fornecedor deletado com sucesso!")
                else:
                    st.error("Erro ao deletar fornecedor.")
        else:
            st.info("Nenhum fornecedor disponível.")
