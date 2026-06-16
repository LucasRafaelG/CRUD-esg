import streamlit as st

st.set_page_config(
    page_title="ESG Audit System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Importar páginas ──────────────────────────────────────────
from _pages import (
    dashboard, fornecedores, diagnosticos,
    consultas, configuracoes
)
from _pages import planos, avaliacoes, funcoes_proc, views

# ── CSS customizado ───────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: -0.03em;
    }
    .stApp {
        background: linear-gradient(135deg, #0a0f0a 0%, #0d1a12 50%, #0a0f1a 100%);
        color: #e0e0e0;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1a12 0%, #0a1020 100%);
        border-right: 1px solid #1a3a2a;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #a0c8a8 !important;
    }
    div[data-testid="metric-container"] {
        background: rgba(20, 60, 35, 0.4);
        border: 1px solid #1e5c3a;
        border-radius: 10px;
        padding: 12px 16px;
    }
    div[data-testid="metric-container"] label {
        color: #7ec8a0 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'IBM Plex Mono', monospace;
    }
    .stDataFrame {
        border: 1px solid #1e3a2a !important;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(10, 25, 15, 0.8);
        border-radius: 8px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #7ec8a0;
        border-radius: 6px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(30, 90, 55, 0.6) !important;
        color: #ffffff !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e5c3a, #1a3a5c);
        color: white;
        border: 1px solid #2ecc71;
        border-radius: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #27ae60, #2980b9);
        border-color: #3498db;
        transform: translateY(-1px);
    }
    .stSelectbox > div > div {
        background: rgba(15, 35, 20, 0.8);
        border-color: #2d5a3d;
        color: #e0e0e0;
    }
    .stTextInput > div > div > input {
        background: rgba(15, 35, 20, 0.8);
        border-color: #2d5a3d;
        color: #e0e0e0;
    }
    .stNumberInput > div > div > input {
        background: rgba(15, 35, 20, 0.8);
        color: #e0e0e0;
    }
    .stTextArea > div > div > textarea {
        background: rgba(15, 35, 20, 0.8);
        border-color: #2d5a3d;
        color: #e0e0e0;
    }
    .stAlert {
        border-radius: 8px;
    }
    hr {
        border-color: #1e3a2a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 16px 0 8px 0;'>
            <span style='font-size:2.5rem'>🌿</span><br>
            <span style='font-family: IBM Plex Mono, monospace; font-size:1.1rem;
                         color:#7ec8a0; letter-spacing:-0.02em;'>
                ESG Audit
            </span><br>
            <span style='font-size:0.75rem; color:#4a7a5a;'>Sistema de Auditoria ESG</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown(
        "<div style='font-size:0.7rem; color:#7ec8a0; padding-bottom:4px;'>📂 CRUD — Gestão de Dados</div>",
        unsafe_allow_html=True,
    )
    pagina = st.selectbox(
        "Navegação",
        [
            "🏠  Dashboard",
            "─── CRUD ───────────────",
            "🏭  Fornecedores",
            "📋  Diagnósticos",
            "📌  Planos de Ação",
            "⚖️   Avaliações de Risco",
            "─── ANÁLISE ────────────",
            "🔍  Consultas SQL",
            "👁️   Views (Etapa 04)",
            "─── BANCO ──────────────",
            "🧩  Funções & Procedimentos",
            "⚙️   Configurações",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.7rem; color:#4a7a5a; text-align:center;'>"
        "Banco de Dados II · 2025<br>Auditoria ESG de Fornecedores<br>"
        "<br>Etapa 06 — Versão Final"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Roteamento ────────────────────────────────────────────────
if "Dashboard" in pagina:
    dashboard.show()
elif "Fornecedores" in pagina:
    fornecedores.show()
elif "Diagnósticos" in pagina:
    diagnosticos.show()
elif "Planos de Ação" in pagina:
    planos.show()
elif "Avaliações" in pagina:
    avaliacoes.show()
elif "Consultas" in pagina:
    consultas.show()
elif "Views" in pagina:
    views.show()
elif "Funções" in pagina:
    funcoes_proc.show()
elif "Configurações" in pagina:
    configuracoes.show()
elif "───" in pagina:
    st.info("Selecione uma opção no menu acima.")
