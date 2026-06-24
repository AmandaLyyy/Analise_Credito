"""
Script de importação — clientes selecionados da planilha Referencia_Comercial_2026.xlsx
Execute na pasta do projeto: python importar_clientes.py
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(override=False)

def conectar():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 3306)),
        database=os.environ.get('DB_NAME', 'analisecredito_db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', '')
    )

CLIENTES = [
    {
        "nome": "Fundação Arthur Bernardes",
        "cnpj": "20.320.503/0001-51",
        "serasa": "",
        "situacao": "Pendente",
        "setor": "Outros",
        "fornecedores": [
            {
                "nome": "Certa Viagens",
                "contato": "",
                "telefone": "(31) 2515-4815",
                "email": "atendimento@rotacertaviagens.com.br",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": None
            },
            {
                "nome": "Gouvea Store",
                "contato": "",
                "telefone": "(31) 98955-4980",
                "email": "gouveastore01@gmail.com",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": None
            },
            {
                "nome": "Sigma Aldrich",
                "contato": "Ana Paula",
                "telefone": "(11) 2170-8028",
                "email": "",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": None
            },
            {
                "nome": "Sistema Informática",
                "contato": "Rita",
                "telefone": "(35) 3722-1444",
                "email": "financeiro@sistemainformatica.com.br",
                "referencia": "Sim",
                "limite": 0.0,
                "ultima_compra": "2025-12-01"
            }
        ]
    },
    {
        "nome": "CEAMAR COMERCIO ATACADISTA DE SALMAO LTDA",
        "cnpj": "40.851.202/0001-61",
        "serasa": "",
        "situacao": "Pendente",
        "setor": "Pescados",
        "fornecedores": [
            {
                "nome": "OPERGEL COML.INDL.DE PROD.ALIM.LTDA",
                "contato": "",
                "telefone": "(11) 3021-8988",
                "email": "",
                "referencia": "Sim",
                "limite": 1700000.0,
                "ultima_compra": "2026-06-04"
            }
        ]
    },
    {
        "nome": "ALEXSANDER DOS SANTOS BOLONHA - MAR AZUL",
        "cnpj": "35.936.550/0001-00",
        "serasa": "",
        "situacao": "Pendente",
        "setor": "Pescados",
        "fornecedores": [
            {
                "nome": "PISCARE IMPORT. DISTRIB. DE ALIM. LTDA",
                "contato": "Financeiro",
                "telefone": "(11) 3021-9726",
                "email": "",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": "2026-07-05"
            },
            {
                "nome": "BELA PESCA DIST. DE PESCADOS LTDA",
                "contato": "",
                "telefone": "(47) 98465-2800",
                "email": "",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": "2026-05-12"
            },
            {
                "nome": "MULT SP PESCADOS",
                "contato": "Financeiro MULT SP",
                "telefone": "",
                "email": "",
                "referencia": "Sim",
                "limite": 5000.0,
                "ultima_compra": "2026-05-28"
            }
        ]
    },
    {
        "nome": "MERCEARIA PARA LTDA",
        "cnpj": "40.262.413/0001-69",
        "serasa": "",
        "situacao": "Aprovado",
        "setor": "Pescados",
        "fornecedores": [
            {
                "nome": "AMAZONAS INDUSTRIAS ALIMENTICIAS S A AMASA",
                "contato": "",
                "telefone": "(91) 3258-6900",
                "email": "comercial@amasa.com.br",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": "2026-07-03"
            },
            {
                "nome": "FRIGORIFICO JAHU LTDA - FILIAL PINA (FRESCATO)",
                "contato": "",
                "telefone": "(81) 3771-5851",
                "email": "ana.luiza@frescatto.com",
                "referencia": "Não",
                "limite": 0.0,
                "ultima_compra": "2026-06-25"
            },
            {
                "nome": "MANIOCA COMERCIO DE ALIMENTOS DA AMAZONIA",
                "contato": "Carla Souza",
                "telefone": "(91) 3212-5589",
                "email": "",
                "referencia": "Sim",
                "limite": 5000.0,
                "ultima_compra": "2026-06-11"
            }
        ]
    }
]

def importar():
    conn   = conectar()
    cursor = conn.cursor()

    clientes_importados    = 0
    fornecedores_importados = 0

    for cliente in CLIENTES:
        cursor.execute("SELECT ClienteID FROM Clientes WHERE CPF = %s", (cliente["cnpj"],))
        existente = cursor.fetchone()

        if existente:
            cliente_id = existente[0]
            print(f"⚠  Cliente já existe: {cliente['nome']} (ID {cliente_id})")
        else:
            cursor.execute("""
                INSERT INTO Clientes
                    (Nome, CPF, Situacao, SerasaObservacao, SetorAtuacao,
                     HistoricoPagamento, DividasAtuais, RendaMensal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente["nome"],
                cliente["cnpj"],
                cliente["situacao"],
                cliente["serasa"],
                cliente["setor"],
                "Bom",
                0.0,
                0.0
            ))
            cliente_id = cursor.lastrowid
            clientes_importados += 1
            print(f"✅ Cliente criado: {cliente['nome']} (ID {cliente_id})")

        for f in cliente["fornecedores"]:
            cursor.execute("""
                SELECT FornecedorID FROM Fornecedores
                WHERE ClienteID = %s AND NomeFornecedor = %s
            """, (cliente_id, f["nome"]))
            if cursor.fetchone():
                print(f"   ⚠  Fornecedor já existe: {f['nome']}")
                continue

            cursor.execute("""
                INSERT INTO Fornecedores
                    (ClienteID, NomeFornecedor, NomeContato, Telefone, Email,
                     ForneceReferencia, LimiteCredito, UltimaCompraData,
                     UltimaCompraValor, PrimeiraCompraData, PrimeiraCompraValor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente_id,
                f["nome"],
                f["contato"],
                f["telefone"],
                f["email"],
                f["referencia"],
                f["limite"],
                f["ultima_compra"],
                0.0,
                None,
                0.0
            ))
            fornecedores_importados += 1
            print(f"   ✅ Fornecedor: {f['nome']}")

    conn.commit()
    conn.close()

    print(f"\n{'─'*50}")
    print(f"Importação concluída!")
    print(f"Clientes criados:      {clientes_importados}")
    print(f"Fornecedores criados:  {fornecedores_importados}")

if __name__ == "__main__":
    importar()
