# 🌿 ESG Audit System — Interface Web

**Banco de Dados II · 2025 · Etapa 06 — Versão Final**

Grupo: Felipe Salustiano, Helder Barros, Kevin Sales, Lucas Mendes e Lucas Rafael.

---

## Descrição

Aplicação web com **Streamlit + MySQL** para gestão e auditoria ESG (Environmental, Social & Governance) de fornecedores. Integra CRUD de 4 tabelas, funções/procedimentos armazenados, triggers com log automático, visualização de views e um dashboard estatístico com 8 gráficos dinâmicos.

---

## Pré-requisitos

- Python 3.10+
- MySQL 8.0+ com o banco `esg_audit` criado e populado
- Funções, procedimentos, triggers e views das Etapas 04/05 instalados no banco

---

## Instalação

```bash
# 1. Extraia o projeto e entre na pasta
cd CRUD-ESG-main

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o banco
mkdir .streamlit
```

Crie `.streamlit/secrets.toml`:

```toml
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_USER     = "root"
DB_PASSWORD = "sua_senha"
DB_NAME     = "esg_audit"
```

> ⚠️ O arquivo `secrets.toml` **nunca deve ser versionado** — já está no `.gitignore`.

---

## Execução

```bash
streamlit run app.py
```

Acesse em: `http://localhost:8501`

---

## Funcionalidades — Etapa 06

### CRUD (4 tabelas)

| Página | Tabela | Operações |
|--------|--------|-----------|
| 🏭 Fornecedores | `fornecedor` | Listar, Inserir, Editar, Deletar |
| 📋 Diagnósticos | `diagnostico` | Listar (filtros), Inserir, Editar status, Deletar |
| 📌 Planos de Ação | `plano_acao` | Listar (filtros), Inserir, Editar, Deletar |
| ⚖️ Avaliações de Risco | `avaliacao` | Listar (filtros + gráfico), Inserir, Editar, Deletar |

### Consultas SQL

5 consultas avançadas (JOINs, GROUP BY, CASE WHEN, DATEDIFF) com visualizações automáticas e exportação CSV.

### Views (Etapa 04)

- **`vw_painel_riscos_esg`** — consolida avaliações de IA por dimensão ESG com filtros e gráficos comparativos
- **`vw_auditoria_evidencias`** — rastreia evidências por questão/diagnóstico (4 JOINs), com filtros e histograma

### Funções & Procedimentos (Etapa 05)

| Objeto | Tipo | Ação na interface |
|--------|------|-------------------|
| `calcular_nivel_risco_fornecedor(cnpj)` | FUNCTION | Seleciona fornecedor e exibe nível de risco |
| `total_evidencias_por_diagnostico(id)` | FUNCTION | Seleciona diagnóstico e conta evidências |
| `atualizar_status_plano_acao()` | PROCEDURE | Botão executa e exibe planos atualizados |
| `relatorio_fornecedores_com_pendencias()` | PROCEDURE (CURSOR) | Botão gera relatório com tabela |
| `trg_log_avaliacao_ia` | TRIGGER | Log visualizado em tempo real na aba Triggers |
| `trg_validar_score_resposta` | TRIGGER | Descrição e comportamento documentados |

### Dashboard Estatístico (8 Gráficos)

| # | Tipo | Medida Estatística |
|---|------|--------------------|
| 1 | Pizza Donut | Distribuição de frequência — Status dos Diagnósticos |
| 2 | Pizza Donut | Distribuição de frequência — Criticidade dos Planos |
| 3 | Barras + Dispersão | Média, Mínimo e Máximo do risco por dimensão ESG |
| 4 | Histograma | Distribuição de frequência dos Scores de IA |
| 5 | Barras Horizontal | Ranking comparativo de score médio por fornecedor |
| 6 | Linha | Tendência temporal de diagnósticos por mês |
| 7 | Radar | Perfil multivariado de risco ESG (0–100%) |
| 8 | Barras Agrupadas | Comparativo de níveis de risco nas avaliações |

**Indicadores estatísticos exibidos:** Média, Mediana, Moda, Desvio Padrão, Variância do Score de IA.

---

## Estrutura do Projeto

```
CRUD-ESG-main/
├── app.py                    # Ponto de entrada + CSS + roteamento
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml          # Conexão MySQL (NÃO versionar)
├── database/
│   ├── __init__.py
│   ├── connection.py         # Conexão MySQL + run_query
│   └── queries.py            # Todas as queries SQL
└── pages/
    ├── __init__.py
    ├── dashboard.py          # Dashboard — 8 gráficos + estatísticas
    ├── fornecedores.py       # CRUD Fornecedores
    ├── diagnosticos.py       # CRUD Diagnósticos
    ├── planos.py             # CRUD Planos de Ação       [ETAPA 06]
    ├── avaliacoes.py         # CRUD Avaliações de Risco  [ETAPA 06]
    ├── consultas.py          # 5 consultas SQL com gráficos
    ├── views.py              # Views Etapas 03/04        [ETAPA 06]
    ├── funcoes_proc.py       # Funções, Procedures, Triggers [ETAPA 06]
    └── configuracoes.py      # Teste de conexão e schema
```

---

## Dependências

```
streamlit>=1.35.0
mysql-connector-python>=8.3.0
pandas>=2.0.0
plotly>=5.20.0
numpy>=1.24.0
```
