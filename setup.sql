-- ============================================================
-- ESG AUDIT SYSTEM — Setup Completo do Banco de Dados
-- Banco de Dados II · 2025 · Grupo: Felipe, Helder, Kevin,
--   Lucas Mendes e Lucas Rafael
-- ============================================================
-- Execute este script no MySQL Workbench ou via phpMyAdmin
-- (XAMPP) para criar e popular todo o banco de uma vez.
-- ============================================================

DROP DATABASE IF EXISTS esg_audit;
CREATE DATABASE esg_audit
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE esg_audit;

-- ============================================================
-- TABELAS
-- ============================================================

-- 1. Usuário e especializações
CREATE TABLE usuario (
    cpf   VARCHAR(11)  PRIMARY KEY,
    nome  VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE administrador (
    cpf          VARCHAR(11) PRIMARY KEY,
    nivel_acesso VARCHAR(30) DEFAULT 'Geral',
    FOREIGN KEY (cpf) REFERENCES usuario(cpf) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE auditor (
    cpf          VARCHAR(11)  PRIMARY KEY,
    certificacao VARCHAR(100) NOT NULL,
    FOREIGN KEY (cpf) REFERENCES usuario(cpf) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 2. Fornecedor
CREATE TABLE fornecedor (
    cnpj         VARCHAR(14)  PRIMARY KEY,
    nome_fantasia VARCHAR(100) NOT NULL,
    razao_social  VARCHAR(150) NOT NULL,
    cep          VARCHAR(8)   NOT NULL,
    logradouro   VARCHAR(100),
    numero       VARCHAR(10),
    complemento  VARCHAR(50),
    bairro       VARCHAR(50),
    cidade       VARCHAR(50),
    estado       CHAR(2)
);

-- 3. Diagnóstico e Respostas
CREATE TABLE diagnostico (
    id_diagnostico  INT AUTO_INCREMENT PRIMARY KEY,
    status          VARCHAR(30) NOT NULL,
    data_inicio     DATE        NOT NULL DEFAULT (CURRENT_DATE),
    data_fim        DATE,
    cnpj_fornecedor VARCHAR(14) NOT NULL,
    FOREIGN KEY (cnpj_fornecedor) REFERENCES fornecedor(cnpj)
);

CREATE TABLE resposta (
    id_diagnostico  INT,
    num_questao     INT,
    resposta_texto  TEXT        NOT NULL,
    score_ia        DECIMAL(4,2),
    justificativa_ia TEXT,
    PRIMARY KEY (id_diagnostico, num_questao),
    FOREIGN KEY (id_diagnostico) REFERENCES diagnostico(id_diagnostico) ON DELETE CASCADE
);

-- 4. Evidências
CREATE TABLE evidencia (
    id_arquivo    INT AUTO_INCREMENT PRIMARY KEY,
    nome_arquivo  VARCHAR(100) NOT NULL,
    tipo_arquivo  VARCHAR(10)  NOT NULL,
    url_storage   VARCHAR(255) NOT NULL,
    data_upload   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resposta_evidencia (
    id_diagnostico INT,
    num_questao    INT,
    id_arquivo     INT,
    PRIMARY KEY (id_diagnostico, num_questao, id_arquivo),
    FOREIGN KEY (id_diagnostico, num_questao) REFERENCES resposta(id_diagnostico, num_questao) ON DELETE CASCADE,
    FOREIGN KEY (id_arquivo) REFERENCES evidencia(id_arquivo) ON DELETE CASCADE
);

-- 5. Modelos de IA e Avaliação de Risco
CREATE TABLE ia_modelo (
    id_modelo     INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(50)  NOT NULL,
    versao        VARCHAR(10)  NOT NULL,
    dimensao_foco VARCHAR(15)  NOT NULL
);

CREATE TABLE avaliacao (
    cnpj_fornecedor VARCHAR(14),
    id_modelo       INT,
    risco           VARCHAR(10) NOT NULL,
    data_avaliacao  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cnpj_fornecedor, id_modelo),
    FOREIGN KEY (cnpj_fornecedor) REFERENCES fornecedor(cnpj),
    FOREIGN KEY (id_modelo)       REFERENCES ia_modelo(id_modelo)
);

-- 6. Planos de Ação e Tarefas
CREATE TABLE plano_acao (
    id_plano        INT AUTO_INCREMENT PRIMARY KEY,
    descricao       TEXT        NOT NULL,
    criticidade     VARCHAR(10) NOT NULL,
    data_criacao    DATE        NOT NULL DEFAULT (CURRENT_DATE),
    prazo_final     DATE        NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'Pendente',
    cnpj_fornecedor VARCHAR(14) NOT NULL,
    FOREIGN KEY (cnpj_fornecedor) REFERENCES fornecedor(cnpj)
);

CREATE TABLE tarefa (
    id_tarefa INT AUTO_INCREMENT PRIMARY KEY,
    descricao TEXT        NOT NULL,
    status    VARCHAR(20) NOT NULL DEFAULT 'Pendente',
    prazo     DATE
);

CREATE TABLE plano_tarefa (
    id_plano  INT,
    id_tarefa INT,
    PRIMARY KEY (id_plano, id_tarefa),
    FOREIGN KEY (id_plano)  REFERENCES plano_acao(id_plano)  ON DELETE CASCADE,
    FOREIGN KEY (id_tarefa) REFERENCES tarefa(id_tarefa)     ON DELETE CASCADE
);

-- 7. Log de Avaliações (alimentado por trigger)
CREATE TABLE log_avaliacoes (
    id_log          INT AUTO_INCREMENT PRIMARY KEY,
    cnpj_fornecedor VARCHAR(14),
    id_modelo       INT,
    risco_avaliado  VARCHAR(10),
    data_avaliacao  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- DADOS
-- ============================================================

-- Usuários
INSERT INTO usuario (cpf, nome, email, senha) VALUES
('11122233344', 'Ana Lima',      'ana.lima@esg.com',      'hash_admin_123'),
('55566677788', 'Carlos Rocha',  'carlos@auditoria.com',  'hash_auditor_456'),
('99900011122', 'Mariana Souza', 'mariana@esg.com',       'hash_admin_789');

INSERT INTO administrador (cpf, nivel_acesso) VALUES
('11122233344', 'Total'),
('99900011122', 'Relatórios');

INSERT INTO auditor (cpf, certificacao) VALUES
('55566677788', 'ISO 14001 Lead Auditor');

-- Fornecedores
INSERT INTO fornecedor (cnpj, nome_fantasia, razao_social, cep, logradouro, numero, cidade, estado) VALUES
('12345678000199', 'Tech Clean Energy',    'Tech Clean Solucoes Sustentaveis LTDA', '01001000', 'Praça da Sé',         '1',   'São Paulo',     'SP'),
('98765432000188', 'EcoLog Transportes',   'EcoLog Transportes e Logistica SA',     '20040002', 'Av. Rio Branco',      '100', 'Rio de Janeiro','RJ'),
('55544433000122', 'Papelaria Verde',      'Distribuidora de Papeis Reciclados LTDA','30140001', 'Av. Afonso Pena',    '500', 'Belo Horizonte','MG'),
('33322211000155', 'SolarBrasil Energia',  'SolarBrasil Energia Renovavel SA',      '40000000', 'Av. Sete de Setembro','200','Salvador',       'BA'),
('77788899000144', 'AgroSust Consultoria', 'AgroSust Consultoria Ambiental LTDA',   '80000000', 'Rua XV de Novembro',  '300','Curitiba',       'PR'),
('44455566000177', 'BioPack Embalagens',   'BioPack Embalagens Sustentaveis EIRELI', '01310100', 'Av. Paulista',       '1000','São Paulo',     'SP');

-- Modelos de IA
INSERT INTO ia_modelo (nome, versao, dimensao_foco) VALUES
('Edenred-EcoGPT',     'v2.1', 'Ambiental'),
('Edenred-SocialMatch','v1.0', 'Social'),
('Edenred-GovShield',  'v1.5', 'Governança');

-- Diagnósticos (datas variadas para gráfico temporal)
INSERT INTO diagnostico (id_diagnostico, status, data_inicio, cnpj_fornecedor) VALUES
(1,  'Finalizado',    '2025-08-10', '12345678000199'),
(2,  'Em Andamento',  '2025-09-15', '98765432000188'),
(3,  'Finalizado',    '2025-09-20', '33322211000155'),
(4,  'pendente',      '2025-10-05', '77788899000144'),
(5,  'Em Andamento',  '2025-10-18', '44455566000177'),
(6,  'Finalizado',    '2025-11-02', '12345678000199'),
(7,  'concluido',     '2025-11-15', '98765432000188'),
(8,  'pendente',      '2025-12-01', '55544433000122'),
(9,  'Em Andamento',  '2026-01-10', '33322211000155'),
(10, 'Finalizado',    '2026-02-05', '44455566000177'),
(11, 'pendente',      '2026-03-12', '77788899000144'),
(12, 'Em Andamento',  '2026-04-08', '12345678000199');

-- Respostas com scores variados
INSERT INTO resposta (id_diagnostico, num_questao, resposta_texto, score_ia, justificativa_ia) VALUES
(1, 1, 'Utilizamos 100% de energia solar nas operações fabris.',             9.50, 'Evidências fotovoltaicas consistentes.'),
(1, 2, 'Toda a cadeia possui contratos formais anti-trabalho escravo.',      10.00,'Cláusulas de compliance presentes.'),
(1, 3, 'Governança certificada ISO 37001 desde 2023.',                       8.75, 'Certificação verificada e vigente.'),
(2, 1, 'Frota movida parcialmente a biodiesel, transição em andamento.',     6.50, 'Necessário acelerar conversão da frota pesada.'),
(2, 2, 'Programa de treinamento de diversidade em implantação.',             7.00, 'Iniciativa válida, mas sem métricas definidas.'),
(3, 1, 'Painéis solares cobrem 80% da demanda energética.',                  8.20, 'Documentação técnica aprovada.'),
(3, 2, 'Relação trabalhista formalizada para 100% dos colaboradores.',       9.00, 'Contratos e RAIS conferidos.'),
(5, 1, 'Emissões de CO2 reduzidas 30% em 2024 vs. 2023.',                   8.50, 'Relatório GRI verificado.'),
(5, 2, 'Programa de equidade salarial implantado em 2024.',                  7.80, 'Dados verificados internamente.'),
(6, 1, 'Certificação LEED Gold obtida para nova planta industrial.',         9.20, 'Certificado válido até 2027.'),
(7, 1, 'Metas ESG integradas ao BSC corporativo.',                           8.00, 'Documentação do BSC analisada.'),
(9, 1, 'Uso de energia renovável chegou a 65% em 2025.',                    7.50, 'Dados de concessionária confirmados.'),
(10,1, 'Política de privacidade atualizada conforme LGPD.',                  8.90, 'Conformidade jurídica verificada.');

-- Evidências
INSERT INTO evidencia (id_arquivo, nome_arquivo, tipo_arquivo, url_storage) VALUES
(1, 'certificado_solar_2025.pdf',    'pdf', 'https://storage.esg.com/ev1'),
(2, 'contratos_fornecedores.pdf',    'pdf', 'https://storage.esg.com/ev2'),
(3, 'iso37001_certificado.pdf',      'pdf', 'https://storage.esg.com/ev3'),
(4, 'relatorio_gri_2024.pdf',        'pdf', 'https://storage.esg.com/ev4'),
(5, 'leed_gold_certificate.pdf',     'pdf', 'https://storage.esg.com/ev5');

INSERT INTO resposta_evidencia (id_diagnostico, num_questao, id_arquivo) VALUES
(1, 1, 1),
(1, 2, 2),
(1, 3, 3),
(5, 1, 4),
(6, 1, 5);

-- Avaliações de Risco
INSERT INTO avaliacao (cnpj_fornecedor, id_modelo, risco) VALUES
('12345678000199', 1, 'Baixo'),
('12345678000199', 2, 'Baixo'),
('12345678000199', 3, 'Baixo'),
('98765432000188', 1, 'Médio'),
('98765432000188', 2, 'Alto'),
('55544433000122', 1, 'Médio'),
('55544433000122', 3, 'Médio'),
('33322211000155', 1, 'Baixo'),
('33322211000155', 2, 'Médio'),
('77788899000144', 2, 'Alto'),
('77788899000144', 3, 'Crítico'),
('44455566000177', 1, 'Médio'),
('44455566000177', 2, 'Baixo');

-- Planos de Ação
INSERT INTO plano_acao (descricao, criticidade, data_criacao, prazo_final, status, cnpj_fornecedor) VALUES
('Substituir lâmpadas antigas por LED de alta eficiência.',                  'baixa', '2025-10-01', '2026-06-15', 'Pendente',     '12345678000199'),
('Apresentar plano de mitigação de emissões de CO2 da frota terceirizada.',  'alta',  '2025-11-01', '2026-03-20', 'Atrasado',     '98765432000188'),
('Implementar programa de reciclagem de resíduos sólidos industriais.',      'media', '2025-12-01', '2026-07-01', 'Em Andamento', '55544433000122'),
('Certificar cadeia de fornecimento conforme ISO 14001.',                    'alta',  '2025-09-15', '2026-02-28', 'Atrasado',     '77788899000144'),
('Criar política formal de diversidade e inclusão.',                         'media', '2026-01-10', '2026-08-01', 'Pendente',     '44455566000177'),
('Reduzir consumo de água em 20% até o final do ano.',                       'media', '2026-02-01', '2026-12-01', 'Em Andamento', '33322211000155'),
('Treinar 100% dos fornecedores em práticas ESG.',                           'alta',  '2026-03-01', '2026-09-01', 'Pendente',     '12345678000199'),
('Auditar conformidade trabalhista de todos os terceirizados.',              'alta',  '2025-08-01', '2025-12-31', 'Atrasado',     '98765432000188');

-- Tarefas
INSERT INTO tarefa (descricao, status, prazo) VALUES
('Levantar inventário de lâmpadas existentes.',           'Concluída', '2026-01-15'),
('Solicitar orçamentos para fornecedores de LED.',         'Pendente',  '2026-03-01'),
('Contratar consultora de emissões de carbono.',           'Pendente',  '2026-02-01'),
('Coletar dados de consumo da frota 2024.',                'Concluída', '2025-12-31'),
('Elaborar relatório de diagnóstico de resíduos.',         'Pendente',  '2026-04-01');

INSERT INTO plano_tarefa (id_plano, id_tarefa) VALUES
(1, 1), (1, 2),
(2, 3), (2, 4),
(3, 5);

-- ============================================================
-- VIEWS — Etapa 04
-- ============================================================

CREATE OR REPLACE VIEW vw_painel_riscos_esg AS
SELECT
    f.cnpj,
    f.nome_fantasia,
    m.versao          AS versao_modelo,
    m.dimensao_foco,
    a.risco
FROM fornecedor f
JOIN avaliacao a ON f.cnpj      = a.cnpj_fornecedor
JOIN ia_modelo m ON a.id_modelo = m.id_modelo;


CREATE OR REPLACE VIEW vw_auditoria_evidencias AS
SELECT
    f.nome_fantasia     AS fornecedor,
    d.id_diagnostico,
    d.status            AS status_diagnostico,
    r.num_questao,
    r.score_ia,
    e.tipo_arquivo,
    e.url_storage
FROM fornecedor f
JOIN diagnostico       d  ON f.cnpj           = d.cnpj_fornecedor
JOIN resposta          r  ON d.id_diagnostico = r.id_diagnostico
JOIN resposta_evidencia re ON r.id_diagnostico = re.id_diagnostico
                           AND r.num_questao   = re.num_questao
JOIN evidencia         e  ON re.id_arquivo    = e.id_arquivo;

-- ============================================================
-- FUNÇÕES — Etapa 05
-- ============================================================

DELIMITER //

CREATE FUNCTION calcular_nivel_risco_fornecedor(p_cnpj VARCHAR(14))
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE v_media DECIMAL(5,2);
    DECLARE v_nivel VARCHAR(20);

    SELECT AVG(
        CASE risco
            WHEN 'Baixo'   THEN 1
            WHEN 'Médio'   THEN 2
            WHEN 'Alto'    THEN 3
            WHEN 'Crítico' THEN 4
            ELSE 2
        END
    ) INTO v_media
    FROM avaliacao
    WHERE cnpj_fornecedor = p_cnpj;

    IF v_media IS NULL THEN
        RETURN 'Sem Avaliação';
    ELSEIF v_media < 1.5 THEN
        SET v_nivel = 'Baixo';
    ELSEIF v_media < 2.5 THEN
        SET v_nivel = 'Médio';
    ELSEIF v_media < 3.5 THEN
        SET v_nivel = 'Alto';
    ELSE
        SET v_nivel = 'Crítico';
    END IF;

    RETURN v_nivel;
END //


CREATE FUNCTION total_evidencias_por_diagnostico(p_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_total INT;

    SELECT COUNT(DISTINCT e.id_arquivo) INTO v_total
    FROM resposta r
    JOIN resposta_evidencia re ON r.id_diagnostico = re.id_diagnostico
                               AND r.num_questao   = re.num_questao
    JOIN evidencia e           ON re.id_arquivo    = e.id_arquivo
    WHERE r.id_diagnostico = p_id;

    RETURN IFNULL(v_total, 0);
END //

-- ============================================================
-- PROCEDIMENTOS — Etapa 05
-- ============================================================

CREATE PROCEDURE atualizar_status_plano_acao()
BEGIN
    UPDATE plano_acao
    SET status = 'Atrasado'
    WHERE prazo_final < CURDATE()
      AND status NOT IN ('Concluído', 'Cancelado');
END //


CREATE PROCEDURE relatorio_fornecedores_com_pendencias()
BEGIN
    DECLARE v_cnpj              VARCHAR(14);
    DECLARE v_nome              VARCHAR(100);
    DECLARE v_planos_atrasados  INT;
    DECLARE v_tarefas_pendentes INT;
    DECLARE v_fim               BOOLEAN DEFAULT FALSE;

    DECLARE cur CURSOR FOR
        SELECT DISTINCT f.cnpj, f.nome_fantasia
        FROM fornecedor f
        JOIN plano_acao p ON f.cnpj = p.cnpj_fornecedor
        WHERE p.status = 'Atrasado';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fim = TRUE;

    DROP TEMPORARY TABLE IF EXISTS temp_pendencias;
    CREATE TEMPORARY TABLE temp_pendencias (
        cnpj                VARCHAR(14),
        fornecedor          VARCHAR(100),
        planos_atrasados    INT,
        tarefas_pendentes   INT,
        mensagem_notificacao TEXT
    );

    OPEN cur;
    loop_cur: LOOP
        FETCH cur INTO v_cnpj, v_nome;
        IF v_fim THEN LEAVE loop_cur; END IF;

        SELECT COUNT(*) INTO v_planos_atrasados
        FROM plano_acao
        WHERE cnpj_fornecedor = v_cnpj AND status = 'Atrasado';

        SELECT COUNT(*) INTO v_tarefas_pendentes
        FROM tarefa t
        JOIN plano_tarefa pt ON t.id_tarefa = pt.id_tarefa
        JOIN plano_acao   p  ON pt.id_plano = p.id_plano
        WHERE p.cnpj_fornecedor = v_cnpj AND t.status = 'Pendente';

        INSERT INTO temp_pendencias VALUES (
            v_cnpj, v_nome,
            v_planos_atrasados,
            v_tarefas_pendentes,
            CONCAT('Notificação para ', v_nome, ': ',
                   v_planos_atrasados, ' plano(s) atrasado(s), ',
                   v_tarefas_pendentes, ' tarefa(s) pendente(s).')
        );
    END LOOP;
    CLOSE cur;

    SELECT * FROM temp_pendencias;
    DROP TEMPORARY TABLE IF EXISTS temp_pendencias;
END //

-- ============================================================
-- TRIGGERS — Etapa 05
-- ============================================================

CREATE TRIGGER trg_log_avaliacao_ia
AFTER INSERT ON avaliacao
FOR EACH ROW
BEGIN
    INSERT INTO log_avaliacoes (cnpj_fornecedor, id_modelo, risco_avaliado, data_avaliacao)
    VALUES (NEW.cnpj_fornecedor, NEW.id_modelo, NEW.risco, NEW.data_avaliacao);
END //


CREATE TRIGGER trg_validar_score_resposta
BEFORE INSERT ON resposta
FOR EACH ROW
BEGIN
    IF NEW.score_ia IS NOT NULL AND (NEW.score_ia < 0 OR NEW.score_ia > 10) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'score_ia deve estar entre 0 e 10.';
    END IF;
END //


CREATE TRIGGER trg_validar_score_resposta_update
BEFORE UPDATE ON resposta
FOR EACH ROW
BEGIN
    IF NEW.score_ia IS NOT NULL AND (NEW.score_ia < 0 OR NEW.score_ia > 10) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'score_ia deve estar entre 0 e 10.';
    END IF;
END //

DELIMITER ;

-- ============================================================
-- FIM DO SETUP
-- ============================================================
SELECT 'Banco esg_audit criado e populado com sucesso!' AS status;
