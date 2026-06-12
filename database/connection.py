import mysql.connector
from mysql.connector import Error
import streamlit as st


def get_connection():
    """Retorna uma conexão com o banco MySQL usando os dados de st.secrets ou config padrão."""
    try:
        conn = mysql.connector.connect(
            host=st.secrets.get("DB_HOST", "localhost"),
            port=int(st.secrets.get("DB_PORT", 3306)),
            user=st.secrets.get("DB_USER", "root"),
            password=st.secrets.get("DB_PASSWORD", ""),
            database=st.secrets.get("DB_NAME", "esg_audit"),
        )
        return conn
    except Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None


def run_query(sql: str, params=None, fetch=True):
    """Executa uma query e retorna os resultados (se fetch=True) ou None."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except Error as e:
        st.error(f"Erro na query: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
