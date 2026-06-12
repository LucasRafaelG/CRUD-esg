import streamlit as st
import pandas as pd
from database.connection import run_query, get_connection
from database.queries import (
    SELECT_ALL_FORNECEDORES,
    SELECT_ALL_DIAGNOSTICOS,
    QUERY_NIVEL_RISCO_FORNECEDOR,
    QUERY_TOTAL_EVIDENCIAS_DIAGNOSTICO,
    QUERY_NIVEL_RISCO_TODOS,
    SELECT_LOG_AVALIACOES,
)
from mysql.connector import Error


def call_procedure(proc_name: str):
    """Chama um stored procedure sem parâmetros e retorna os result sets."""
    conn = get_connection()
    if conn is None:
        return None, "Falha na conexão."
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"CALL {proc_name}()")
        results = []
        while True:
            rows = cursor.fetchall()
            if rows:
                results.append(rows)
            if not cursor.nextset():
                break
        conn.commit()
        return results, None
    except Error as e:
        return None, str(e)
    finally:
        cursor.close()
        conn.close()


def show():
    st.markdown("## 🧩 Funções, Procedimentos e Triggers")
    st.markdown("---")

    tab_func, tab_proc, tab_trig = st.tabs(
        ["⚙️ Funções", "🔄 Procedimentos", "🔔 Triggers & Log"]
    )

    # ════════════════════════════════════════════════════════════
    # FUNÇÕES
    # ════════════════════════════════════════════════════════════
    with tab_func:
        st.markdown("### Funções Armazenadas no Banco")

        # ── Função 1: calcular_nivel_risco_fornecedor ──────────
        with st.expander("📌 Função 1 — `calcular_nivel_risco_fornecedor(cnpj)`", expanded=True):
            st.markdown("""
            **Descrição:** Classifica automaticamente o nível de risco de um fornecedor
            com base na média ponderada das avaliações de IA (Baixo=1, Médio=2, Alto=3, Crítico=4).
            Retorna: `Baixo`, `Médio`, `Alto`, `Crítico` ou `Sem Avaliação`.
            """)
            st.code("""
SELECT calcular_nivel_risco_fornecedor('12345678000199');
            """, language="sql")

            col_a, col_b = st.columns([3, 1])
            with col_a:
                fornecedores = run_query(SELECT_ALL_FORNECEDORES)
                if fornecedores:
                    opcoes_forn = {r["nome_fantasia"]: r["cnpj"] for r in fornecedores}
                    forn_sel_f1 = st.selectbox("Selecione o Fornecedor", list(opcoes_forn.keys()), key="f1_sel")
                else:
                    st.warning("Nenhum fornecedor cadastrado.")
                    forn_sel_f1 = None

            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                executar_f1 = st.button("▶️ Executar", key="btn_f1")

            if executar_f1 and forn_sel_f1:
                cnpj = opcoes_forn[forn_sel_f1]
                result = run_query(QUERY_NIVEL_RISCO_FORNECEDOR, params=(cnpj,))
                if result:
                    nivel = result[0]["nivel_risco"]
                    cores = {"Baixo": "🟢", "Médio": "🟡", "Alto": "🟠", "Crítico": "🔴", "Sem Avaliação": "⚪"}
                    icone = cores.get(nivel, "⚪")
                    st.success(f"**{icone} Nível de Risco para '{forn_sel_f1}':** {nivel}")

            st.markdown("**Executar para todos os fornecedores:**")
            if st.button("▶️ Calcular Nível de Risco — Todos", key="btn_f1_todos"):
                result_todos = run_query(QUERY_NIVEL_RISCO_TODOS)
                if result_todos:
                    df = pd.DataFrame(result_todos)
                    df.columns = ["CNPJ", "Fornecedor", "Nível de Risco"]

                    def colorir_nivel(val):
                        cores_map = {
                            "Baixo":   "background-color:#1e4d2b; color:#2ecc71",
                            "Médio":   "background-color:#4d3000; color:#e67e22",
                            "Alto":    "background-color:#4d2500; color:#e74c3c",
                            "Crítico": "background-color:#4d1a1a; color:#e74c3c",
                        }
                        return cores_map.get(val, "")

                    st.dataframe(
                        df.style.map(colorir_nivel, subset=["Nível de Risco"]),
                        use_container_width=True, hide_index=True,
                    )

        # ── Função 2: total_evidencias_por_diagnostico ─────────
        with st.expander("📌 Função 2 — `total_evidencias_por_diagnostico(id)`"):
            st.markdown("""
            **Descrição:** Conta quantas evidências distintas (arquivos) estão vinculadas
            a um diagnóstico específico, percorrendo as tabelas `resposta`, `resposta_evidencia` e `evidencia`.
            """)
            st.code("""
SELECT total_evidencias_por_diagnostico(1);
            """, language="sql")

            diagnosticos = run_query(SELECT_ALL_DIAGNOSTICOS)
            if diagnosticos:
                opcoes_diag = {
                    f"#{r['id_diagnostico']} — {r['fornecedor']} ({r['status']})": r["id_diagnostico"]
                    for r in diagnosticos
                }
                col_a2, col_b2 = st.columns([3, 1])
                with col_a2:
                    diag_sel_f2 = st.selectbox("Selecione o Diagnóstico", list(opcoes_diag.keys()), key="f2_sel")
                with col_b2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    executar_f2 = st.button("▶️ Executar", key="btn_f2")

                if executar_f2:
                    id_diag = opcoes_diag[diag_sel_f2]
                    result = run_query(QUERY_TOTAL_EVIDENCIAS_DIAGNOSTICO, params=(id_diag,))
                    if result:
                        total = result[0]["total_evidencias"]
                        st.success(f"**Total de evidências no diagnóstico {id_diag}:** {total} arquivo(s)")
            else:
                st.info("Nenhum diagnóstico disponível.")

    # ════════════════════════════════════════════════════════════
    # PROCEDIMENTOS
    # ════════════════════════════════════════════════════════════
    with tab_proc:
        st.markdown("### Procedimentos Armazenados no Banco")

        # ── Proc 1: atualizar_status_plano_acao ───────────────
        with st.expander("🔄 Procedimento 1 — `atualizar_status_plano_acao()`", expanded=True):
            st.markdown("""
            **Descrição:** Verifica todos os planos de ação com `prazo_final < CURDATE()` e
            que **não** estejam com status `Concluído` ou `Cancelado`, atualizando-os para `Atrasado`.
            Útil para executar periodicamente e manter os dados sincronizados.
            """)
            st.code("""
CALL atualizar_status_plano_acao();
            """, language="sql")

            if st.button("▶️ Executar Procedimento", key="btn_proc1"):
                with st.spinner("Executando..."):
                    result, erro = call_procedure("atualizar_status_plano_acao")
                if erro:
                    st.error(f"Erro: {erro}")
                else:
                    st.success("✅ Procedimento executado! Planos com prazo vencido foram marcados como **Atrasado**.")
                    # Mostra planos após execução
                    planos = run_query("""
                        SELECT p.id_plano, f.nome_fantasia AS fornecedor,
                               p.criticidade, p.prazo_final, p.status
                        FROM plano_acao p
                        JOIN fornecedor f ON p.cnpj_fornecedor = f.cnpj
                        WHERE p.status = 'Atrasado'
                        ORDER BY p.prazo_final;
                    """)
                    if planos:
                        st.markdown("**Planos marcados como Atrasado:**")
                        st.dataframe(pd.DataFrame(planos), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum plano atrasado encontrado.")

        # ── Proc 2: relatorio_fornecedores_com_pendencias ─────
        with st.expander("🔄 Procedimento 2 — `relatorio_fornecedores_com_pendencias()` (com CURSOR)"):
            st.markdown("""
            **Descrição:** Utiliza um **CURSOR** para percorrer todos os fornecedores com planos
            atrasados. Para cada fornecedor, conta planos atrasados e tarefas pendentes,
            gerando um relatório com mensagem de notificação personalizada.
            """)
            st.code("""
CALL relatorio_fornecedores_com_pendencias();
            """, language="sql")

            if st.button("▶️ Gerar Relatório de Pendências", key="btn_proc2"):
                with st.spinner("Executando cursor e gerando relatório..."):
                    result, erro = call_procedure("relatorio_fornecedores_com_pendencias")
                if erro:
                    st.error(f"Erro: {erro}")
                elif result and len(result) > 0 and result[0]:
                    df_rel = pd.DataFrame(result[0])
                    st.success(f"✅ Relatório gerado: {len(df_rel)} fornecedor(es) com pendências.")
                    st.dataframe(df_rel, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum fornecedor com pendências encontrado (nenhum plano com status 'Atrasado').")

    # ════════════════════════════════════════════════════════════
    # TRIGGERS & LOG
    # ════════════════════════════════════════════════════════════
    with tab_trig:
        st.markdown("### Triggers — Descrição e Efeitos")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            #### 🔔 Trigger 1 — `trg_log_avaliacao_ia`
            **Evento:** `AFTER INSERT ON avaliacao`
            **Efeito:** Toda vez que uma nova avaliação é inserida, este trigger
            registra automaticamente um log na tabela `log_avaliacoes` com:
            - CNPJ do fornecedor avaliado
            - ID e versão do modelo de IA
            - Nível de risco atribuído
            - Data/hora da avaliação

            > 💡 Veja na aba **Avaliações** o botão de inserção para acionar este trigger.
            """)

        with col2:
            st.markdown("""
            #### 🔔 Trigger 2 — `trg_validar_score_resposta`
            **Evento:** `BEFORE INSERT / BEFORE UPDATE ON resposta`
            **Efeito:** Valida que o `score_ia` esteja dentro do intervalo [0, 10].
            Caso o valor seja inválido, lança um erro `SQLSTATE '45000'`
            impedindo a inserção ou atualização inválida.

            > 💡 Protege a integridade dos dados antes de qualquer escrita.
            """)

        st.markdown("---")
        st.markdown("### 📋 Log de Avaliações — Efeito do `trg_log_avaliacao_ia`")
        st.info("Abaixo estão os registros gravados automaticamente pelo trigger a cada nova avaliação inserida.")

        col_btn, col_lim = st.columns([1, 3])
        with col_lim:
            limite = st.slider("Mostrar últimos N registros", 5, 100, 20, key="log_lim")

        if st.button("🔄 Carregar Log", key="btn_log"):
            log_data = run_query(SELECT_LOG_AVALIACOES)
            if log_data:
                df_log = pd.DataFrame(log_data).head(limite)
                df_log.columns = ["CNPJ", "Fornecedor", "ID Modelo", "Modelo IA", "Risco Avaliado", "Data Avaliação"]
                st.success(f"✅ {len(log_data)} registro(s) no log. Exibindo {min(len(log_data), limite)}.")
                st.dataframe(df_log, use_container_width=True, hide_index=True)
            else:
                st.warning("Log vazio — nenhuma avaliação foi registrada ainda, ou a tabela `log_avaliacoes` não existe.")
