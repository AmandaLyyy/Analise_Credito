# Sistema de Análise de Crédito — ECIL
Natureza: Aplicação web interna de gestão e concessão de crédito  
Desenvolvido por: Amanda G. — UNIP Marquês, Ciência da Computação

---

## Descrição

Sistema desenvolvido sob demanda para automatizar o processo de análise e concessão de crédito da empresa Ecil LTDA, substituindo controles manuais por uma plataforma web segura, auditável e com geração de relatórios oficiais.

O sistema realiza a pontuação de crédito de clientes (score 0–1000), sugere limites e taxas de juros, registra histórico de análises e emite relatórios em PDF e Excel — centralizando em banco de dados relacional todas as operações que antes eram realizadas de forma descentralizada.

---

## Funcionalidades

- Autenticação de usuários com sessão controlada
- Cadastro e gestão de clientes com CPF/CNPJ formatados
- Cálculo automatizado de score de crédito, taxa de juros e limite sugerido
- Aprovação, recusa ou pendência de crédito por cliente
- Cadastro e gestão de fornecedores vinculados a cada cliente
- Registro de notas fiscais por fornecedor com controle de vencimento
- Geração de relatórios exportáveis em **PDF** e **Excel** (geral ou por cliente)
- Dashboard com indicadores: aprovados, pendentes, recusados e distribuição de score
- Filtro de fornecedores por cliente no dashboard
- Importação em massa de clientes e fornecedores via script Python
- Observações de Serasa por cliente

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3 · Flask |
| Banco de Dados | MySQL 8 · InnoDB |
| Front-end | HTML5 · CSS3 · Bootstrap 5 · Bootstrap Icons · Jinja2 |
| Relatórios | ReportLab (PDF) · OpenPyXL (Excel) |
| Gráficos | Chart.js |
| Implantação | Railway |
| Versionamento | Git · GitHub |

---

## Como executar

**Pré-requisitos:** Python 3.10+, MySQL 8, pip

```bash
# 1. Clone o repositório
git clone https://github.com/AmandaLyyy/Analise_Credito.git
cd Analise_Credito/CreditoProjeto/CreditoProjetoI

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais do banco

# 4. Execute a aplicação
python app.py

# Acesse: http://localhost:5000
```

---

## Variáveis de ambiente

```env
DB_HOST=seu_host
DB_PORT=3306
DB_NAME=nome_do_banco
DB_USER=usuario
DB_PASSWORD=senha
SECRET_KEY=sua_chave_secreta
```

---

## Estrutura do projeto

```
CreditoProjeto/
└── CreditoProjetoI/
    ├── app.py              # Aplicação principal
    ├── requirements.txt    # Dependências
    ├── Procfile            # Configuração Railway
    ├── .env.example        # Exemplo de variáveis de ambiente
    └── templates/          # Templates HTML
```
