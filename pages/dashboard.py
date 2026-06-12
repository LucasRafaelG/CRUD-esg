import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from database.connection import run_query
from database.queries import (
    QUERY_RISCO_POR_DIMENSAO,
    QUERY_STATUS_DIAGNOSTICOS,
    QUERY_CRITICIDADE_PLANOS,
    QUERY_SCORE_IA_POR_FORNECEDOR,
    QUERY_SCORE_IA_STATS,
    QUERY_SCORE_IA_DISTRIBUICAO,
    QUERY_DIAGNOSTICOS_POR_MES,
    QUERY_DISTRIBUICAO_RISCO,
    QUERY_RADAR_DIMENSAO,
    QUERY_TODOS_SCORES,
    QUERY_PLANOS_POR_STATUS,
    SELECT_ALL_FORNECEDORES,
    SELECT_ALL_DIAGNOSTICOS,
)

# ─── Paleta de cores ESG ─────────────────────────────────────
CORES = {
    "Ambiental":    "#2ecc71",
    "Social":       "#3498db",
    "Governança":   "#9b59b6",
    "Finalizado":   "#2ecc71",
    "concluido":    "#2ecc71",
    "Em Andamento": "#3498db",
    "em andamento": "#3498db",
    "pendente":     "#e67e22",
    "Pendente":     "#e67e22",
    "Atrasado":     "#e74c3c",
    "Cancelado":    "#95a5a6",
    "alta":         "#e74c3c",
    "media":        "#e67e22",
    "baixa":        "#2ecc71",
    "Baixo":        "#2ecc71",
    "Médio":        "#e67e22",
    "Alto":         "#e74c3c",
    "Crítico":      "#8e1a1a",
}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e0e0e0",
)


def _badge(label: str, value, color: str = "#2ecc71") -> str:
    return (
        f"<div style='background:rgba(20,50,30,0.45);border:1px solid {color};"
        f"border-radius:10px;padding:14px 18px;margin:4px 0;text-align:center;'>"
        f"<div style='font-size:0.78rem;color:#9ecfb0;'>{label}</div>"
        f"<div style='font-size:1.55rem;font-weight:700;color:{color};font-family:IBM Plex Mono,monospace;'>{value}</div>"
        f"</div>"
    )


def show():
    st.markdown("## 🌿 Dashboard ESG — Versão Final")

    # ── Filtro global de período ──────────────────────────────
    with st.expander("🎛️ Filtros do Dashboard", expanded=False):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            periodo = st.selectbox(
                "Período de diagnósticos",
                ["Todos os períodos", "Últimos 3 meses", "Últimos 6 meses", "Último ano"],
                key="dash_periodo",
            )
        with col_d2:
            dim_filtro = st.multiselect(
                "Dimensões ESG",
                ["Ambiental", "Social", "Governança"],
                default=["Ambiental", "Social", "Governança"],
                key="dash_dim",
            )

    st.markdown("---")

    # ════════════════════════════════════════════════════════
    # SEÇÃO 1 — KPIs RESUMIDOS
    # ════════════════════════════════════════════════════════
    st.markdown("### 📊 Indicadores Resumidos")

    # Busca dados base
    fornecedores = run_query(SELECT_ALL_FORNECEDORES) or []
    diagnosticos = run_query(SELECT_ALL_DIAGNOSTICOS) or []
    planos_raw   = run_query("SELECT status FROM plano_acao;") or []
    aval_raw     = run_query("SELECT risco FROM avaliacao;") or []
    stats_raw    = run_query(QUERY_SCORE_IA_STATS) or [{}]
    scores_raw   = run_query(QUERY_TODOS_SCORES) or []

    total_forn    = len(fornecedores)
    total_diag    = len(diagnosticos)
    total_planos  = len(planos_raw)
    total_aval    = len(aval_raw)

    stats         = stats_raw[0] if stats_raw else {}
    media_score   = stats.get("media") or 0.0
    dp_score      = stats.get("desvio_padrao") or 0.0
    var_score     = stats.get("variancia") or 0.0

    # Mediana em Python
    scores_list = [float(s["score_ia"]) for s in scores_raw if s["score_ia"] is not None]
    mediana_score = round(float(np.median(scores_list)), 2) if scores_list else 0.0

    # Moda do status dos diagnósticos (mais frequente)
    if diagnosticos:
        df_diag_tmp = pd.DataFrame(diagnosticos)
        moda_status = df_diag_tmp["status"].mode()[0] if not df_diag_tmp["status"].empty else "—"
    else:
        moda_status = "—"

    # % diagnósticos finalizados/concluídos
    diag_concluidos = sum(1 for d in diagnosticos if d.get("status") in ("Finalizado", "concluido", "Concluído"))
    pct_concluidos  = round(diag_concluidos / total_diag * 100, 1) if total_diag > 0 else 0

    # % planos atrasados
    planos_atrasados = sum(1 for p in planos_raw if p.get("status") == "Atrasado")
    pct_atrasados    = round(planos_atrasados / total_planos * 100, 1) if total_planos > 0 else 0

    # KPI row 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏭 Fornecedores", total_forn)
    c2.metric("📋 Diagnósticos", total_diag, f"{pct_concluidos}% concluídos")
    c3.metric("📌 Planos de Ação", total_planos, f"{pct_atrasados}% atrasados" if pct_atrasados else None)
    c4.metric("⚖️ Avaliações de Risco", total_aval)

    st.markdown("")

    # KPI row 2 — Estatísticas de Score IA
    st.markdown("#### 🤖 Estatísticas do Score de IA (Respostas)")
    cols_stat = st.columns(5)
    labels_vals = [
        ("Média",          f"{media_score:.2f}",  "#3498db"),
        ("Mediana",        f"{mediana_score:.2f}", "#2ecc71"),
        ("Desvio Padrão",  f"{dp_score:.2f}",      "#e67e22"),
        ("Variância",      f"{var_score:.2f}",      "#9b59b6"),
        ("Moda (status)",  moda_status,             "#7ec8a0"),
    ]
    for col, (lbl, val, cor) in zip(cols_stat, labels_vals):
        col.markdown(_badge(lbl, val, cor), unsafe_allow_html=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════
    # SEÇÃO 2 — GRÁFICOS
    # ════════════════════════════════════════════════════════
    st.markdown("### 📈 Gráficos Dinâmicos")

    # ── Linha A: Pizza Status + Pizza Criticidade ────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🥧 Gráfico 1 — Distribuição de Status dos Diagnósticos")
        st.caption("*Distribuição de frequência — Moda: maior fatia*")
        data_status = run_query(QUERY_STATUS_DIAGNOSTICOS)
        if data_status:
            df_s = pd.DataFrame(data_status)
            fig1 = px.pie(
                df_s, names="status", values="total",
                color="status", color_discrete_map=CORES, hole=0.45,
            )
            fig1.update_traces(textposition="inside", textinfo="percent+label")
            fig1.update_layout(**LAYOUT_BASE, showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Sem dados de diagnósticos.")

    with col_b:
        st.markdown("#### 🥧 Gráfico 2 — Criticidade dos Planos de Ação")
        st.caption("*Distribuição de frequência por categoria de criticidade*")
        data_crit = run_query(QUERY_CRITICIDADE_PLANOS)
        if data_crit:
            df_c = pd.DataFrame(data_crit)
            fig2 = px.pie(
                df_c, names="criticidade", values="total",
                color="criticidade", color_discrete_map=CORES, hole=0.45,
            )
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            fig2.update_layout(**LAYOUT_BASE, showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados de planos.")

    # ── Linha B: Risco por Dimensão (barras + desvio) ────────
    st.markdown("#### 📊 Gráfico 3 — Risco Médio por Dimensão ESG (com Mínimo, Máximo e Desvio Padrão)")
    st.caption("*Médias comparativas + amplitude de variação — inspirado em análise de dispersão*")
    data_dim = run_query(QUERY_RISCO_POR_DIMENSAO)
    if data_dim:
        df_dim = pd.DataFrame(data_dim)
        if dim_filtro:
            df_dim = df_dim[df_dim["dimensao"].isin(dim_filtro)]

        if not df_dim.empty:
            cores_dim = [CORES.get(d, "#95a5a6") for d in df_dim["dimensao"]]
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=df_dim["dimensao"], y=df_dim["risco_medio"],
                marker_color=cores_dim,
                text=[f"Média: {v}" for v in df_dim["risco_medio"]],
                textposition="outside", name="Risco Médio",
            ))
            fig3.add_trace(go.Scatter(
                x=df_dim["dimensao"], y=df_dim["risco_maximo"],
                mode="markers", marker=dict(symbol="triangle-up", size=14, color="#e74c3c"),
                name="Máximo",
            ))
            fig3.add_trace(go.Scatter(
                x=df_dim["dimensao"], y=df_dim["risco_minimo"],
                mode="markers", marker=dict(symbol="triangle-down", size=14, color="#2ecc71"),
                name="Mínimo",
            ))
            fig3.update_layout(
                **LAYOUT_BASE,
                yaxis_title="Nível de Risco (1=Baixo … 4=Crítico)",
                xaxis_title="Dimensão ESG",
                margin=dict(t=20, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sem dados de avaliação por dimensão.")

    # ── Linha C: Histograma Score IA + Ranking ───────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### 📉 Gráfico 4 — Distribuição dos Scores de IA (Histograma)")
        st.caption("*Frequência por faixa de score — análise de distribuição*")
        data_hist = run_query(QUERY_SCORE_IA_DISTRIBUICAO)
        if data_hist:
            df_hist = pd.DataFrame(data_hist)
            fig4 = px.bar(
                df_hist, x="faixa", y="frequencia",
                color="frequencia",
                color_continuous_scale=["#e74c3c", "#e67e22", "#2ecc71"],
                text="frequencia",
                labels={"faixa": "Faixa de Score", "frequencia": "Frequência"},
            )
            fig4.update_traces(textposition="outside")
            # Linha de média
            if media_score:
                # Adicionar anotação de média
                fig4.add_annotation(
                    text=f"Média: {media_score}", showarrow=False,
                    xref="paper", yref="paper", x=0.98, y=0.95,
                    font=dict(color="#3498db", size=13),
                )
            fig4.update_layout(**LAYOUT_BASE, coloraxis_showscale=False, margin=dict(t=30, b=40))
            st.plotly_chart(fig4, use_container_width=True)

            # Métricas abaixo do gráfico
            st.markdown(
                f"<small style='color:#7ec8a0'>Média: **{media_score}** | "
                f"Mediana: **{mediana_score}** | "
                f"Desvio Padrão: **{dp_score}** | "
                f"Variância: **{var_score}**</small>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Sem dados de score de IA.")

    with col_d:
        st.markdown("#### 🏆 Gráfico 5 — Ranking de Score IA por Fornecedor")
        st.caption("*Comparativo de desempenho — Top 15 por score médio*")
        data_score = run_query(QUERY_SCORE_IA_POR_FORNECEDOR)
        if data_score:
            df_score = pd.DataFrame(data_score)
            fig5 = px.bar(
                df_score, x="score_medio", y="fornecedor",
                orientation="h",
                color="score_medio",
                color_continuous_scale=["#e74c3c", "#e67e22", "#2ecc71"],
                range_color=[0, 10],
                text="score_medio",
                labels={"score_medio": "Score Médio", "fornecedor": ""},
            )
            fig5.update_traces(textposition="outside")
            fig5.update_layout(
                **LAYOUT_BASE,
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                margin=dict(t=10, b=20),
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Sem dados de respostas com score.")

    # ── Linha D: Linha temporal + Radar ─────────────────────
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("#### 📅 Gráfico 6 — Tendência Temporal de Diagnósticos por Mês")
        st.caption("*Análise de tendência ao longo do tempo*")
        data_mes = run_query(QUERY_DIAGNOSTICOS_POR_MES)
        if data_mes:
            df_mes = pd.DataFrame(data_mes)
            fig6 = px.line(
                df_mes, x="mes", y="total",
                markers=True,
                color_discrete_sequence=["#2ecc71"],
                labels={"mes": "Mês", "total": "Diagnósticos"},
            )
            fig6.update_traces(
                line=dict(width=3),
                marker=dict(size=10, color="#2ecc71", line=dict(width=2, color="#0a3a1a")),
            )
            # Linha de média
            media_mensal = df_mes["total"].mean()
            fig6.add_hline(
                y=media_mensal, line_dash="dash", line_color="#e67e22",
                annotation_text=f"Média mensal: {media_mensal:.1f}",
                annotation_position="top right",
            )
            fig6.update_layout(**LAYOUT_BASE, margin=dict(t=20, b=40))
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("Sem dados temporais de diagnósticos.")

    with col_f:
        st.markdown("#### 🕸️ Gráfico 7 — Radar: Perfil de Risco ESG por Dimensão")
        st.caption("*Visualização multivariada do nível de risco (0–100%)*")
        data_radar = run_query(QUERY_RADAR_DIMENSAO)
        if data_radar:
            df_radar = pd.DataFrame(data_radar)
            if dim_filtro:
                df_radar = df_radar[df_radar["dimensao"].isin(dim_filtro)]

            if not df_radar.empty:
                categorias = df_radar["dimensao"].tolist()
                valores    = df_radar["nivel_risco_pct"].tolist()
                # Fechar o radar
                categorias_loop = categorias + [categorias[0]]
                valores_loop    = valores    + [valores[0]]

                fig7 = go.Figure()
                fig7.add_trace(go.Scatterpolar(
                    r=valores_loop,
                    theta=categorias_loop,
                    fill="toself",
                    fillcolor="rgba(46,204,113,0.2)",
                    line=dict(color="#2ecc71", width=2),
                    marker=dict(size=8, color="#2ecc71"),
                    name="Risco ESG",
                ))
                fig7.update_layout(
                    **LAYOUT_BASE,
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100],
                                        tickfont=dict(color="#9ecfb0"),
                                        gridcolor="#1e3a2a"),
                        angularaxis=dict(tickfont=dict(color="#e0e0e0"),
                                         gridcolor="#1e3a2a"),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                    showlegend=False,
                    margin=dict(t=20, b=20, l=40, r=40),
                )
                st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("Sem dados de dimensão ESG.")

    # ── Linha E: Distribuição de risco (barras agrupadas) ────
    st.markdown("#### 📊 Gráfico 8 — Distribuição dos Níveis de Risco nas Avaliações")
    st.caption("*Frequência absoluta de cada nível de risco — comparativo de distribuição*")
    data_dist_risco = run_query(QUERY_DISTRIBUICAO_RISCO)
    if data_dist_risco:
        df_dr = pd.DataFrame(data_dist_risco)
        # Ordem definida
        ordem = ["Baixo", "Médio", "Alto", "Crítico"]
        df_dr["risco"] = pd.Categorical(df_dr["risco"], categories=ordem, ordered=True)
        df_dr = df_dr.sort_values("risco")

        fig8 = go.Figure()
        for _, row in df_dr.iterrows():
            fig8.add_trace(go.Bar(
                x=[row["risco"]], y=[row["total"]],
                name=str(row["risco"]),
                marker_color=CORES.get(str(row["risco"]), "#95a5a6"),
                text=[row["total"]],
                textposition="outside",
            ))
        fig8.update_layout(
            **LAYOUT_BASE,
            barmode="group",
            showlegend=True,
            xaxis_title="Nível de Risco",
            yaxis_title="Quantidade de Avaliações",
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("Sem dados de avaliação de risco.")

    st.markdown("---")

    # ════════════════════════════════════════════════════════
    # SEÇÃO 3 — TABELA DE RESUMO EXECUTIVO
    # ════════════════════════════════════════════════════════
    st.markdown("### 📋 Resumo Executivo Consolidado")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("**Status dos Diagnósticos**")
        data_status2 = run_query(QUERY_STATUS_DIAGNOSTICOS)
        if data_status2:
            df_s2 = pd.DataFrame(data_status2)
            df_s2["pct"] = (df_s2["total"] / df_s2["total"].sum() * 100).round(1).astype(str) + "%"
            df_s2.columns = ["Status", "Total", "Percentual"]
            st.dataframe(df_s2, use_container_width=True, hide_index=True)

    with col_r2:
        st.markdown("**Status dos Planos de Ação**")
        data_planos_s = run_query(QUERY_PLANOS_POR_STATUS)
        if data_planos_s:
            df_ps = pd.DataFrame(data_planos_s)
            df_ps["pct"] = (df_ps["total"] / df_ps["total"].sum() * 100).round(1).astype(str) + "%"
            df_ps.columns = ["Status", "Total", "Percentual"]
            st.dataframe(df_ps, use_container_width=True, hide_index=True)

    st.markdown("")
    st.markdown(
        "<div style='font-size:0.72rem;color:#4a7a5a;text-align:center;'>"
        "ESG Audit System · Banco de Dados II · 2025 · Todos os dados refletem o banco em tempo real."
        "</div>",
        unsafe_allow_html=True,
    )
