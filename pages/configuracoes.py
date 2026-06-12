import streamlit as st
from database.connection import run_query


def show():
    st.markdown("## ⚙️ Configuração do Banco de Dados")
    st.markdown("---")

    st.markdown("""
    ### Como configurar a conexão

    Crie um arquivo `.streamlit/secrets.toml` na raiz do projeto com o seguinte conteúdo:

    ```toml
    DB_HOST     = "localhost"
    DB_PORT     = 3306
    DB_USER     = "root"
    DB_PASSWORD = "sua_senha"
    DB_NAME     = "esg_audit"
    ```

    > 💡 O arquivo `secrets.toml` **nunca** deve ser versionado no Git. Já está no `.gitignore`.
    """)

    st.markdown("---")
    st.markdown("### Testar Conexão")

    if st.button("🔌 Testar conexão com o banco"):
        with st.spinner("Conectando..."):
            result = run_query("SELECT 1 AS ok;")
        if result:
            st.success("✅ Conexão estabelecida com sucesso!")
        else:
            st.error("❌ Falha na conexão. Verifique suas configurações em `.streamlit/secrets.toml`.")

    st.markdown("---")
    st.markdown("### Informações do Schema")

    if st.button("📐 Listar tabelas do banco"):
        tabelas = run_query("SHOW TABLES;")
        if tabelas:
            nomes = [list(t.values())[0] for t in tabelas]
            for t in nomes:
                count = run_query(f"SELECT COUNT(*) AS total FROM `{t}`;")
                total = count[0]["total"] if count else "?"
                st.markdown(f"- **{t}** — {total} registro(s)")
        else:
            st.warning("Não foi possível listar as tabelas.")
