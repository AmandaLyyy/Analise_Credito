# CréditoEcil — Sistema de Análise de Crédito

Sistema web para análise e gestão de crédito de clientes, desenvolvido com **Flask** e **MySQL**, implantado no **Railway**.

---

## Funcionalidades

- Cadastro e gestão de clientes com score de crédito
- Cadastro de fornecedores vinculados a cada cliente
- Registro de notas fiscais por fornecedor
- Dashboard com gráficos de situação e distribuição de score
- Relatórios exportáveis em **PDF** e **Excel** (geral ou por cliente)
- Filtro de fornecedores por cliente no dashboard
- Importação de clientes via script Python

---

## Tecnologias

- Python 3 + Flask
- MySQL (Railway)
- Bootstrap 5 + Bootstrap Icons
- ReportLab (PDF)
- OpenPyXL (Excel)

---

## Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/AmandaLyyy/ecil-credito.git
cd ecil-credito/CreditoProjeto/CreditoProjetoI
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

Edite o `.env` com as credenciais do seu banco MySQL.

### 5. Rode a aplicação

```bash
python app.py
```

Acesse em: [http://localhost:5000](http://localhost:5000)

---

## Variáveis de ambiente necessárias

| Variável | Descrição |
|---|---|
| `DB_HOST` | Host do banco de dados |
| `DB_PORT` | Porta do banco (padrão: 3306) |
| `DB_NAME` | Nome do banco de dados |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |
| `SECRET_KEY` | Chave secreta da aplicação Flask |

---

## Deploy no Railway

O projeto está configurado para deploy automático via GitHub. Basta conectar o repositório ao Railway e configurar as variáveis de ambiente no painel.

---

## Acesso

| Usuário | Senha |
|---|---|
| Admin | *(definida internamente)* |

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
