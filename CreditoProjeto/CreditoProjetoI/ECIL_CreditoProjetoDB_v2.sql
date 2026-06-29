
--  ECIL - Empreendimento Comercial Industrial Ecil LTDA
--  Sistema de Análise de Crédito | Vila Olímpia - SP

-- ── 1. CRIAR / SELECIONAR O BANCO ───────────────────────────
CREATE DATABASE IF NOT EXISTS ECIL_CreditoProjetoDB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ECIL_CreditoProjetoDB;

-- ── 2. TABELA: Clientes ─────────────────────────────────────
--  Armazena os dados cadastrais de cada cliente analisado.
CREATE TABLE IF NOT EXISTS Clientes (
    ClienteID         INT AUTO_INCREMENT PRIMARY KEY,
    Nome              VARCHAR(255)   NOT NULL,
    CPF               VARCHAR(18)    NOT NULL UNIQUE   -- CPF ou CNPJ (com pontuação)
                                     COMMENT 'Aceita CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00)',
    RendaMensal       DECIMAL(15,2)  NOT NULL           COMMENT 'Sugestão de limite de crédito',
    HistoricoPagamento ENUM('Excelente','Bom','Regular','Ruim') NOT NULL DEFAULT 'Bom',
    DividasAtuais     DECIMAL(15,2)  NOT NULL DEFAULT 0.00,
    IdadeCredito      INT            NOT NULL DEFAULT 0  COMMENT 'Usado internamente pelo score',
    MixCredito        INT            NOT NULL DEFAULT 3   COMMENT 'Diversidade de crédito (1-5)',
    ConsultasRecentes INT            NOT NULL DEFAULT 0   COMMENT 'Consultas nos últimos 6 meses',
    SetorAtuacao      ENUM('Pescados','Ingredientes','Nutrição Animal','Outros')
                                     NOT NULL DEFAULT 'Pescados',
    TempoEmprego      INT            NOT NULL DEFAULT 12  COMMENT 'Meses — usado internamente',
    Situacao          ENUM('Aprovado','Recusado','Pendente') NOT NULL DEFAULT 'Pendente',
    SerasaObservacao  TEXT           COMMENT 'Campo livre — até 10.000 caracteres',
    DataCadastro      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    DataAtualizacao   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_cpf    (CPF),
    INDEX idx_setor  (SetorAtuacao),
    INDEX idx_situacao (Situacao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Clientes analisados pelo sistema ECIL';


-- ── 3. TABELA: AnalisesCredito ──────────────────────────────
--  Cada análise de score gerada pelo sistema para um cliente.
CREATE TABLE IF NOT EXISTS AnalisesCredito (
    AnaliseID         INT AUTO_INCREMENT PRIMARY KEY,
    ClienteID         INT            NOT NULL,
    DataAnalise       TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    PontuacaoCredito  INT            NOT NULL COMMENT 'Score 300-850',
    DecisaoCredito    ENUM('Aprovado','Pendente','Negado') NOT NULL,
    LimiteSugerido    DECIMAL(15,2)  DEFAULT 0.00,
    TaxaJuros         DECIMAL(5,2)   DEFAULT 0.00 COMMENT 'Taxa mensal em %',
    DetalhesScore     TEXT           COMMENT 'JSON com detalhamento do score',

    FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID) ON DELETE CASCADE,
    INDEX idx_cliente  (ClienteID),
    INDEX idx_data     (DataAnalise),
    INDEX idx_decisao  (DecisaoCredito)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Histórico de análises de crédito por cliente';

USE ECIL_CreditoProjetoDB;

CREATE TABLE IF NOT EXISTS NotasFiscais (
    NFID              INT AUTO_INCREMENT PRIMARY KEY,
    FornecedorID      INT NOT NULL,
    NumeroNF          VARCHAR(50) NOT NULL COMMENT 'Número da nota fiscal',
    DataEmissao       DATE NOT NULL COMMENT 'Data de emissão da NF',
    ValorNF           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    DataVencimento    DATE NOT NULL COMMENT 'Data de vencimento',
    DataCriacao       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (FornecedorID) REFERENCES Fornecedores(FornecedorID) ON DELETE CASCADE,
    INDEX idx_fornecedor (FornecedorID),
    INDEX idx_vencimento (DataVencimento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── 4. TABELA: Fornecedores ─────────────────────────────────
--  Cada cliente pode ter N fornecedores cadastrados.
--  Esta tabela é o coração da novidade da versão 2.
CREATE TABLE IF NOT EXISTS Fornecedores (
    FornecedorID      INT AUTO_INCREMENT PRIMARY KEY,
    ClienteID         INT            NOT NULL            COMMENT 'Vínculo com o cliente',

    -- Identificação do fornecedor
    NomeFornecedor    VARCHAR(255)   NOT NULL DEFAULT '' COMMENT 'Nome/razão social do fornecedor',
    Email             VARCHAR(255)   DEFAULT ''          COMMENT 'E-mail do fornecedor',
    Telefone          VARCHAR(20)    DEFAULT ''          COMMENT 'Telefone do fornecedor',

    -- Referência e contato interno
    ForneceReferencia ENUM('Sim','Não') NOT NULL DEFAULT 'Sim',
    NomeContato       VARCHAR(255)   DEFAULT ''          COMMENT 'Pessoa de contato no fornecedor',

    -- Histórico de compras
    PrimeiraCompraData  DATE         DEFAULT NULL        COMMENT 'Data da 1ª compra',
    PrimeiraCompraValor DECIMAL(15,2) DEFAULT 0.00      COMMENT 'Valor da 1ª compra',
    UltimaCompraData    DATE         DEFAULT NULL        COMMENT 'Data da última compra',
    UltimaCompraValor   DECIMAL(15,2) DEFAULT 0.00      COMMENT 'Valor da última compra',

    -- Crédito e cadastro
    LimiteCredito     DECIMAL(15,2)  DEFAULT 0.00       COMMENT 'Limite concedido pelo fornecedor',
    DataCadastroFornecedor DATE      DEFAULT NULL        COMMENT 'Data de cadastro no fornecedor',

    -- Controle interno
    DataCriacao       TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    DataAtualizacao   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID) ON DELETE CASCADE,
    INDEX idx_cliente_forn (ClienteID),
    INDEX idx_referencia   (ForneceReferencia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Fornecedores vinculados a cada cliente';

-- ── 5. VIEW: vw_analise_credito_ecil ───────────────────────
--  Visão completa unindo cliente + última análise.
--  Útil para relatórios e exportação CSV.
CREATE OR REPLACE VIEW vw_analise_credito_ecil AS
SELECT
    C.ClienteID,
    C.Nome,
    C.CPF,
    C.RendaMensal                              AS SugestaoLimite,
    C.HistoricoPagamento,
    C.Situacao,
    C.SerasaObservacao,
    C.SetorAtuacao,
    C.MixCredito,
    C.ConsultasRecentes,
    AC.AnaliseID,
    DATE_FORMAT(AC.DataAnalise, '%Y-%m-%d %H:%i:%s') AS DataAnalise,
    AC.PontuacaoCredito,
    AC.DecisaoCredito,
    CAST(AC.LimiteSugerido AS DECIMAL(15,2))   AS LimiteSugerido,
    CAST(AC.TaxaJuros      AS DECIMAL(5,2))    AS TaxaJuros
FROM AnalisesCredito AC
INNER JOIN Clientes C ON AC.ClienteID = C.ClienteID;


-- ── 6. VIEW: vw_fornecedores_por_cliente ───────────────────
--  Lista todos os fornecedores com o nome do cliente.
--  É esta view que alimenta a listbox lateral da tela.
CREATE OR REPLACE VIEW vw_fornecedores_por_cliente AS
SELECT
    F.FornecedorID,
    C.ClienteID,
    C.Nome                                      AS NomeCliente,
    C.CPF,
    F.NomeFornecedor,
    F.Email,
    F.Telefone,
    F.ForneceReferencia,
    F.NomeContato,
    F.PrimeiraCompraData,
    F.PrimeiraCompraValor,
    F.UltimaCompraData,
    F.UltimaCompraValor,
    F.LimiteCredito,
    F.DataCadastroFornecedor,
    F.DataCriacao
FROM Fornecedores F
INNER JOIN Clientes C ON F.ClienteID = C.ClienteID
ORDER BY C.Nome, F.NomeFornecedor;

-- Aumenta o campo CPF
ALTER TABLE Clientes
    MODIFY COLUMN CPF VARCHAR(18) NOT NULL
    COMMENT 'CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00)';

select * from Clientes;

SELECT * FROM vw_analise_credito_ecil;

SELECT * FROM vw_fornecedores_por_cliente WHERE CPF = '47873113876';

USE ecil_creditoprojetodb;
ALTER TABLE Clientes 
    MODIFY COLUMN RendaMensal DECIMAL(15,2) DEFAULT 0.00;

-- Ver análises com dados do cliente
-- SELECT * FROM vw_analise_credito_ecil;
-- Ver fornecedores de um cliente específico (pelo nome)
-- SELECT * FROM vw_fornecedores_por_cliente WHERE NomeCliente LIKE '%PEIXARIA%';
-- Ver fornecedores de um cliente pelo CPF/CNPJ
-- SELECT * FROM vw_fornecedores_por_cliente WHERE CPF = '47873113876';

-- Quantos fornecedores cada cliente tem
-- SELECT NomeCliente, CPF, COUNT(*) AS TotalFornecedores
-- FROM vw_fornecedores_por_cliente
-- GROUP BY ClienteID, NomeCliente, CPF
-- ORDER BY TotalFornecedores DESC;

-- Fornecedores que dão referência
-- SELECT NomeCliente, NomeFornecedor, Email, Telefone
-- FROM vw_fornecedores_por_cliente
-- WHERE ForneceReferencia = 'Sim';
