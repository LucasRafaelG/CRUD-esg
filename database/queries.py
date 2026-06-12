# ============================================================
# CONSULTAS SQL — Sistema de Auditoria ESG de Fornecedores
# ============================================================

# -----------------------------------------------------------
# CONSULTA 1 — Ranking de risco médio por fornecedor (JOIN)
# -----------------------------------------------------------
QUERY_RISCO_FORNECEDOR = """
SELECT
    f.nome_fantasia AS fornecedor,
    f.cnpj,
    ROUND(AVG(
        CASE a.risco
            WHEN 'Baixo'    THEN 1
            WHEN 'Médio'    THEN 2
            WHEN 'Alto'     THEN 3
            WHEN 'Crítico'  THEN 4
            ELSE 2
        END
    ), 2) AS risco_medio,
    COUNT(a.id_modelo) AS qtd_avaliacoes
FROM fornecedor f
JOIN avaliacao a ON f.cnpj = a.cnpj_fornecedor
GROUP BY f.cnpj, f.nome_fantasia
ORDER BY risco_medio DESC;
"""

# -----------------------------------------------------------
# CONSULTA 2 — Diagnósticos por status com score médio de IA
# -----------------------------------------------------------
QUERY_DIAGNOSTICO_STATUS = """
SELECT
    f.nome_fantasia AS fornecedor,
    d.id_diagnostico,
    d.status,
    d.data_inicio,
    ROUND(AVG(r.score_ia), 2) AS score_medio_ia,
    COUNT(r.num_questao) AS qtd_respostas
FROM diagnostico d
JOIN fornecedor f ON d.cnpj_fornecedor = f.cnpj
LEFT JOIN resposta r ON d.id_diagnostico = r.id_diagnostico
GROUP BY d.id_diagnostico, f.nome_fantasia, d.status, d.data_inicio
ORDER BY d.data_inicio DESC;
"""

# -----------------------------------------------------------
# CONSULTA 3 — Distribuição de risco por dimensão da IA
# -----------------------------------------------------------
QUERY_RISCO_POR_DIMENSAO = """
SELECT
    m.dimensao_foco AS dimensao,
    COUNT(a.cnpj_fornecedor) AS qtd_fornecedores,
    ROUND(AVG(
        CASE a.risco
            WHEN 'Baixo'   THEN 1
            WHEN 'Médio'   THEN 2
            WHEN 'Alto'    THEN 3
            WHEN 'Crítico' THEN 4
            ELSE 2
        END
    ), 2) AS risco_medio,
    ROUND(MIN(
        CASE a.risco
            WHEN 'Baixo'   THEN 1
            WHEN 'Médio'   THEN 2
            WHEN 'Alto'    THEN 3
            WHEN 'Crítico' THEN 4
            ELSE 2
        END
    ), 2) AS risco_minimo,
    ROUND(MAX(
        CASE a.risco
            WHEN 'Baixo'   THEN 1
            WHEN 'Médio'   THEN 2
            WHEN 'Alto'    THEN 3
            WHEN 'Crítico' THEN 4
            ELSE 2
        END
    ), 2) AS risco_maximo
FROM avaliacao a
JOIN ia_modelo m ON a.id_modelo = m.id_modelo
JOIN fornecedor f ON a.cnpj_fornecedor = f.cnpj
GROUP BY m.dimensao_foco
ORDER BY risco_medio DESC;
"""

# -----------------------------------------------------------
# CONSULTA 4 — Planos de ação críticos com tarefas pendentes
# -----------------------------------------------------------
QUERY_PLANOS_CRITICOS = """
SELECT
    p.id_plano,
    f.nome_fantasia AS fornecedor,
    p.criticidade,
    p.prazo_final,
    p.status,
    DATEDIFF(p.prazo_final, CURRENT_DATE) AS dias_restantes
FROM plano_acao p
JOIN fornecedor f ON p.cnpj_fornecedor = f.cnpj
WHERE p.criticidade = 'alta'
ORDER BY dias_restantes ASC;
"""

# -----------------------------------------------------------
# CONSULTA 5 — Fornecedores sem diagnóstico
# -----------------------------------------------------------
QUERY_FORNECEDORES_SEM_DIAGNOSTICO = """
SELECT
    f.cnpj,
    f.nome_fantasia
FROM fornecedor f
LEFT JOIN diagnostico d ON f.cnpj = d.cnpj_fornecedor
WHERE d.id_diagnostico IS NULL;
"""

# -----------------------------------------------------------
# CONSULTA 6 — Score IA médio por fornecedor
# -----------------------------------------------------------
QUERY_SCORE_IA_POR_FORNECEDOR = """
SELECT
    f.nome_fantasia AS fornecedor,
    ROUND(AVG(r.score_ia), 2) AS score_medio
FROM resposta r
JOIN diagnostico d ON r.id_diagnostico = d.id_diagnostico
JOIN fornecedor f ON d.cnpj_fornecedor = f.cnpj
GROUP BY f.nome_fantasia
ORDER BY score_medio DESC
LIMIT 15;
"""

# -----------------------------------------------------------
# CONSULTA 7 — Distribuição de status dos diagnósticos
# -----------------------------------------------------------
QUERY_STATUS_DIAGNOSTICOS = """
SELECT status, COUNT(*) AS total
FROM diagnostico
GROUP BY status;
"""

# -----------------------------------------------------------
# CONSULTA 8 — Distribuição de criticidade dos planos
# -----------------------------------------------------------
QUERY_CRITICIDADE_PLANOS = """
SELECT criticidade, COUNT(*) AS total
FROM plano_acao
GROUP BY criticidade;
"""

# -----------------------------------------------------------
# CONSULTA 9 — Distribuição dos níveis de risco
# -----------------------------------------------------------
QUERY_DISTRIBUICAO_RISCO = """
SELECT risco, COUNT(*) AS total
FROM avaliacao
GROUP BY risco
ORDER BY FIELD(risco, 'Baixo', 'Médio', 'Alto', 'Crítico');
"""

# -----------------------------------------------------------
# CONSULTA 10 — Diagnósticos por mês (tendência temporal)
# -----------------------------------------------------------
QUERY_DIAGNOSTICOS_POR_MES = """
SELECT
    DATE_FORMAT(data_inicio, '%Y-%m') AS mes,
    COUNT(*) AS total
FROM diagnostico
GROUP BY mes
ORDER BY mes;
"""

# -----------------------------------------------------------
# CONSULTA 11 — Estatísticas dos Scores de IA
# -----------------------------------------------------------
QUERY_SCORE_IA_STATS = """
SELECT
    COUNT(*)                        AS total_respostas,
    ROUND(AVG(score_ia), 2)         AS media,
    ROUND(STDDEV(score_ia), 2)      AS desvio_padrao,
    ROUND(VARIANCE(score_ia), 2)    AS variancia,
    ROUND(MIN(score_ia), 2)         AS minimo,
    ROUND(MAX(score_ia), 2)         AS maximo
FROM resposta
WHERE score_ia IS NOT NULL;
"""

# -----------------------------------------------------------
# CONSULTA 12 — Distribuição dos Scores IA por faixa (histograma)
# -----------------------------------------------------------
QUERY_SCORE_IA_DISTRIBUICAO = """
SELECT
    CASE
        WHEN score_ia < 2  THEN '0–2 (Crítico)'
        WHEN score_ia < 4  THEN '2–4 (Baixo)'
        WHEN score_ia < 6  THEN '4–6 (Regular)'
        WHEN score_ia < 8  THEN '6–8 (Bom)'
        ELSE                    '8–10 (Ótimo)'
    END AS faixa,
    COUNT(*) AS frequencia
FROM resposta
WHERE score_ia IS NOT NULL
GROUP BY faixa
ORDER BY MIN(score_ia);
"""

# -----------------------------------------------------------
# CONSULTA 13 — Risco numérico médio por dimensão (para radar)
# -----------------------------------------------------------
QUERY_RADAR_DIMENSAO = """
SELECT
    m.dimensao_foco AS dimensao,
    ROUND(AVG(
        CASE a.risco
            WHEN 'Baixo'   THEN 25
            WHEN 'Médio'   THEN 50
            WHEN 'Alto'    THEN 75
            WHEN 'Crítico' THEN 100
            ELSE 50
        END
    ), 1) AS nivel_risco_pct
FROM avaliacao a
JOIN ia_modelo m ON a.id_modelo = m.id_modelo
GROUP BY m.dimensao_foco;
"""

# -----------------------------------------------------------
# CONSULTA 14 — Todos os scores para cálculo de mediana (Python)
# -----------------------------------------------------------
QUERY_TODOS_SCORES = """
SELECT score_ia FROM resposta WHERE score_ia IS NOT NULL ORDER BY score_ia;
"""

# -----------------------------------------------------------
# CONSULTA 15 — Status dos planos por mês de criação
# -----------------------------------------------------------
QUERY_PLANOS_POR_STATUS = """
SELECT status, COUNT(*) AS total
FROM plano_acao
GROUP BY status
ORDER BY total DESC;
"""

# -----------------------------------------------------------
# CRUD — Fornecedor
# -----------------------------------------------------------
INSERT_FORNECEDOR = """
INSERT INTO fornecedor (cnpj, nome_fantasia, razao_social, cep, logradouro, numero)
VALUES (%s, %s, %s, %s, %s, %s);
"""

UPDATE_FORNECEDOR = """
UPDATE fornecedor
SET nome_fantasia = %s, logradouro = %s, numero = %s, cep = %s
WHERE cnpj = %s;
"""

DELETE_FORNECEDOR = """
DELETE FROM fornecedor WHERE cnpj = %s;
"""

SELECT_ALL_FORNECEDORES = """
SELECT cnpj, nome_fantasia, cep FROM fornecedor ORDER BY nome_fantasia;
"""

SELECT_FORNECEDOR_FULL = """
SELECT cnpj, nome_fantasia, razao_social, cep, logradouro, numero, complemento, bairro, cidade, estado
FROM fornecedor ORDER BY nome_fantasia;
"""

# -----------------------------------------------------------
# CRUD — Diagnóstico
# -----------------------------------------------------------
INSERT_DIAGNOSTICO = """
INSERT INTO diagnostico (status, data_inicio, cnpj_fornecedor)
VALUES (%s, CURRENT_DATE, %s);
"""

UPDATE_DIAGNOSTICO = """
UPDATE diagnostico
SET status = %s
WHERE id_diagnostico = %s;
"""

DELETE_DIAGNOSTICO = """
DELETE FROM diagnostico WHERE id_diagnostico = %s;
"""

SELECT_ALL_DIAGNOSTICOS = """
SELECT d.id_diagnostico, f.nome_fantasia AS fornecedor, d.status, d.data_inicio
FROM diagnostico d
JOIN fornecedor f ON d.cnpj_fornecedor = f.cnpj
ORDER BY d.data_inicio DESC;
"""

# -----------------------------------------------------------
# CRUD — Plano de Ação
# -----------------------------------------------------------
SELECT_ALL_PLANOS = """
SELECT
    p.id_plano,
    f.nome_fantasia AS fornecedor,
    p.descricao,
    p.criticidade,
    p.data_criacao,
    p.prazo_final,
    p.status
FROM plano_acao p
JOIN fornecedor f ON p.cnpj_fornecedor = f.cnpj
ORDER BY p.data_criacao DESC;
"""

INSERT_PLANO = """
INSERT INTO plano_acao (descricao, criticidade, data_criacao, prazo_final, status, cnpj_fornecedor)
VALUES (%s, %s, CURRENT_DATE, %s, %s, %s);
"""

UPDATE_PLANO = """
UPDATE plano_acao
SET descricao = %s, criticidade = %s, prazo_final = %s, status = %s
WHERE id_plano = %s;
"""

DELETE_PLANO = """
DELETE FROM plano_acao WHERE id_plano = %s;
"""

# -----------------------------------------------------------
# CRUD — Avaliação de Risco
# -----------------------------------------------------------
SELECT_ALL_AVALIACOES = """
SELECT
    a.cnpj_fornecedor,
    f.nome_fantasia AS fornecedor,
    a.id_modelo,
    m.nome AS modelo_ia,
    m.dimensao_foco,
    a.risco,
    a.data_avaliacao
FROM avaliacao a
JOIN fornecedor f ON a.cnpj_fornecedor = f.cnpj
JOIN ia_modelo m ON a.id_modelo = m.id_modelo
ORDER BY a.data_avaliacao DESC;
"""

SELECT_ALL_MODELOS_IA = """
SELECT id_modelo, nome, versao, dimensao_foco FROM ia_modelo ORDER BY nome;
"""

INSERT_AVALIACAO = """
INSERT INTO avaliacao (cnpj_fornecedor, id_modelo, risco)
VALUES (%s, %s, %s);
"""

UPDATE_AVALIACAO = """
UPDATE avaliacao SET risco = %s
WHERE cnpj_fornecedor = %s AND id_modelo = %s;
"""

DELETE_AVALIACAO = """
DELETE FROM avaliacao WHERE cnpj_fornecedor = %s AND id_modelo = %s;
"""

# -----------------------------------------------------------
# VIEWS — Etapa 04
# -----------------------------------------------------------
QUERY_VIEW_RISCOS_ESG = """
SELECT * FROM vw_painel_riscos_esg ORDER BY nome_fantasia, dimensao_foco;
"""

QUERY_VIEW_AUDITORIA_EVIDENCIAS = """
SELECT * FROM vw_auditoria_evidencias ORDER BY fornecedor, id_diagnostico;
"""

# -----------------------------------------------------------
# FUNÇÕES — Etapa 05
# -----------------------------------------------------------
QUERY_NIVEL_RISCO_FORNECEDOR = """
SELECT calcular_nivel_risco_fornecedor(%s) AS nivel_risco;
"""

QUERY_TOTAL_EVIDENCIAS_DIAGNOSTICO = """
SELECT total_evidencias_por_diagnostico(%s) AS total_evidencias;
"""

QUERY_NIVEL_RISCO_TODOS = """
SELECT
    f.cnpj,
    f.nome_fantasia,
    calcular_nivel_risco_fornecedor(f.cnpj) AS nivel_risco
FROM fornecedor f
ORDER BY f.nome_fantasia;
"""

# -----------------------------------------------------------
# TRIGGERS — Log de Avaliações (efeito do trg_log_avaliacao_ia)
# -----------------------------------------------------------
SELECT_LOG_AVALIACOES = """
SELECT
    l.cnpj_fornecedor,
    f.nome_fantasia AS fornecedor,
    l.id_modelo,
    m.nome           AS modelo_ia,
    l.risco_avaliado,
    l.data_avaliacao
FROM log_avaliacoes l
LEFT JOIN fornecedor f  ON l.cnpj_fornecedor = f.cnpj
LEFT JOIN ia_modelo  m  ON l.id_modelo = m.id_modelo
ORDER BY l.data_avaliacao DESC
LIMIT 100;
"""
