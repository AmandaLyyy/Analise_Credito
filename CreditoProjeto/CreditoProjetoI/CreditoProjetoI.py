import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import mysql.connector
import csv
from datetime import datetime
from decimal import Decimal
import re
import hashlib



class DBManager:
    """Gerencia a conexão e operações com o banco de dados MySQL."""
    
    def __init__(self, host, database, username, password):
        self.host = host
        self.database = database
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None

    def connect(self):
        """Estabelece a conexão com o MySQL."""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.username,
                password=self.password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.conn.cursor()
            print("Conexão com MySQL estabelecida com sucesso!")
            return True
        except mysql.connector.Error as err:
            error_msg = ""
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                error_msg = "Nome de usuário ou senha inválidos para o MySQL."
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                error_msg = "Banco de dados MySQL não existe."
            else:
                error_msg = f"Erro ao conectar ao MySQL: {err}"
            
            messagebox.showerror("Erro de Conexão", error_msg)
            self.conn = None
            self.cursor = None
            return False

    def disconnect(self):
        """Fecha a conexão com o MySQL."""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Conexão com MySQL fechada.")

    def is_connected(self):
        """Verifica se a conexão está ativa."""
        return self.conn and self.conn.is_connected()

    def execute_query(self, query, params=None):
        """Executa uma query SQL com parâmetros opcionais."""
        if not self.is_connected():
            print("Tentando reconectar ao banco de dados...")
            if not self.connect():
                return None
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Erro de Banco de Dados",
                f"Erro ao executar a query: {err}"
            )
            return None

    def commit(self):
        """Confirma as alterações no banco de dados."""
        if self.conn and self.is_connected():
            try:
                self.conn.commit()
                return True
            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Erro de Commit",
                    f"Erro ao confirmar alterações: {err}"
                )
                return False
        return False

    def fetch_all(self, query, params=None):
        """Busca todas as linhas resultantes de uma query."""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []

    def fetch_one(self, query, params=None):
        """Busca uma única linha resultante de uma query."""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def insert_client(self, nome, cpf, renda_mensal, historico_pagamento,
                      dividas_atuais, idade_credito, mix_credito, 
                      consultas_recentes, setor_atuacao, tempo_emprego):
        """Insere um novo cliente na tabela Clientes."""
        query = """
        INSERT INTO Clientes 
        (Nome, CPF, RendaMensal, HistoricoPagamento, DividasAtuais,
         IdadeCredito, MixCredito, ConsultasRecentes, SetorAtuacao, 
         TempoEmprego)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            nome,
            cpf,
            renda_mensal,
            historico_pagamento,
            dividas_atuais,
            idade_credito,
            mix_credito,
            consultas_recentes,
            setor_atuacao,
            tempo_emprego
        )
        cursor = self.execute_query(query, params)
        if cursor:
            if self.commit():
                print(f"Cliente {nome} inserido com sucesso!")
                return cursor.lastrowid
        return 0

    def update_client(self, cliente_id, nome, cpf, renda_mensal,
                      historico_pagamento, dividas_atuais, idade_credito,
                      mix_credito, consultas_recentes, setor_atuacao,
                      tempo_emprego):
        """Atualiza os dados de um cliente existente."""
        query = """
        UPDATE Clientes 
        SET Nome = %s, CPF = %s, RendaMensal = %s, 
            HistoricoPagamento = %s, DividasAtuais = %s,
            IdadeCredito = %s, MixCredito = %s, ConsultasRecentes = %s,
            SetorAtuacao = %s, TempoEmprego = %s
        WHERE ClienteID = %s
        """
        params = (
            nome,
            cpf,
            renda_mensal,
            historico_pagamento,
            dividas_atuais,
            idade_credito,
            mix_credito,
            consultas_recentes,
            setor_atuacao,
            tempo_emprego,
            cliente_id
        )
        cursor = self.execute_query(query, params)
        if cursor:
            if self.commit():
                print(f"Cliente ID {cliente_id} atualizado com sucesso!")
                return True
        return False

    def insert_analysis(self, cliente_id, pontuacao_credito, decisao_credito,
                       limite_sugerido, taxa_juros, detalhes_score):
        """Insere uma nova análise de crédito."""
        query = """
        INSERT INTO AnalisesCredito 
        (ClienteID, PontuacaoCredito, DecisaoCredito, DataAnalise,
         LimiteSugerido, TaxaJuros, DetalhesScore)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            cliente_id,
            pontuacao_credito,
            decisao_credito,
            datetime.now(),
            limite_sugerido,
            taxa_juros,
            detalhes_score
        )
        cursor = self.execute_query(query, params)
        if cursor:
            if self.commit():
                print(
                    f"Análise de crédito para ClienteID {cliente_id} "
                    "inserida com sucesso!"
                )
                return cursor.rowcount
        return 0

    def get_all_credit_analyses_for_export(self):
        """Retorna todas as análises de crédito para exportação."""
        query = """
        SELECT
            C.Nome,
            C.CPF,
            C.RendaMensal,
            C.HistoricoPagamento,
            C.DividasAtuais,
            C.IdadeCredito,
            C.MixCredito,
            C.ConsultasRecentes,
            C.SetorAtuacao,
            C.TempoEmprego,
            AC.DataAnalise,
            AC.PontuacaoCredito,
            AC.DecisaoCredito,
            AC.LimiteSugerido,
            AC.TaxaJuros
        FROM
            AnalisesCredito AS AC
        INNER JOIN
            Clientes AS C ON AC.ClienteID = C.ClienteID
        ORDER BY
            AC.DataAnalise DESC
        """
        cursor = self.execute_query(query)
        if cursor:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        return [], []

    def get_recent_analyses(self, limit=20):
        """Retorna as análises de crédito mais recentes."""
        query = """
        SELECT
            C.Nome,
            C.CPF,
            AC.DataAnalise,
            AC.PontuacaoCredito,
            AC.DecisaoCredito,
            AC.LimiteSugerido,
            AC.TaxaJuros
        FROM
            AnalisesCredito AS AC
        INNER JOIN
            Clientes AS C ON AC.ClienteID = C.ClienteID
        ORDER BY
            AC.DataAnalise DESC
        LIMIT %s
        """
        return self.fetch_all(query, (limit,))

    def get_statistics(self):
        """Retorna estatísticas gerais do sistema."""
        stats = {}
        
        total_query = "SELECT COUNT(*) FROM AnalisesCredito"
        result = self.fetch_one(total_query)
        stats['total_analises'] = result[0] if result else 0
        
        decisao_query = """
        SELECT DecisaoCredito, COUNT(*) 
        FROM AnalisesCredito 
        GROUP BY DecisaoCredito
        """
        decisoes = self.fetch_all(decisao_query)
        stats['aprovados'] = 0
        stats['pendentes'] = 0
        stats['negados'] = 0
        
        for decisao, count in decisoes:
            if decisao == 'Aprovado':
                stats['aprovados'] = count
            elif decisao == 'Pendente':
                stats['pendentes'] = count
            elif decisao == 'Negado':
                stats['negados'] = count
        
        score_query = "SELECT AVG(PontuacaoCredito) FROM AnalisesCredito"
        result = self.fetch_one(score_query)
        stats['score_medio'] = round(result[0], 2) if result and result[0] else 0
        
        return stats

    def create_tables_if_not_exists(self):
        """Cria as tabelas necessárias se não existirem."""
        try:
            create_clientes = """
            CREATE TABLE IF NOT EXISTS Clientes (
                ClienteID INT AUTO_INCREMENT PRIMARY KEY,
                Nome VARCHAR(255) NOT NULL,
                CPF VARCHAR(11) NOT NULL UNIQUE,
                RendaMensal DECIMAL(15, 2) NOT NULL,
                HistoricoPagamento ENUM('Excelente', 'Bom', 'Regular', 'Ruim') NOT NULL,
                DividasAtuais DECIMAL(15, 2) NOT NULL,
                IdadeCredito INT NOT NULL COMMENT 'Idade do histórico de crédito em meses',
                MixCredito INT NOT NULL COMMENT 'Diversidade de tipos de crédito (1-5)',
                ConsultasRecentes INT NOT NULL COMMENT 'Consultas de crédito nos últimos 6 meses',
                SetorAtuacao VARCHAR(100) DEFAULT 'Outros',
                TempoEmprego INT NOT NULL COMMENT 'Tempo no emprego atual em meses',
                DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cpf (CPF),
                INDEX idx_setor (SetorAtuacao)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            self.execute_query(create_clientes)
            
            create_analises = """
            CREATE TABLE IF NOT EXISTS AnalisesCredito (
                AnaliseID INT AUTO_INCREMENT PRIMARY KEY,
                ClienteID INT NOT NULL,
                DataAnalise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PontuacaoCredito INT NOT NULL,
                DecisaoCredito ENUM('Aprovado', 'Pendente', 'Negado') NOT NULL,
                LimiteSugerido DECIMAL(15, 2) DEFAULT 0.00,
                TaxaJuros DECIMAL(5, 2) DEFAULT 0.00 COMMENT 'Taxa de juros mensal em %',
                DetalhesScore TEXT COMMENT 'Detalhamento dos componentes do score',
                FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID)
                    ON DELETE CASCADE,
                INDEX idx_cliente (ClienteID),
                INDEX idx_data (DataAnalise),
                INDEX idx_decisao (DecisaoCredito)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            self.execute_query(create_analises)
            
            self.commit()
            print("Tabelas verificadas/criadas com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
            return False


class ModernCreditAnalyzer:
    """Analisador de crédito baseado em scoring moderno."""
    
    PAYMENT_HISTORY_WEIGHT = 40
    CREDIT_UTILIZATION_WEIGHT = 20
    CREDIT_AGE_WEIGHT = 21
    CREDIT_MIX_WEIGHT = 10
    RECENT_CREDIT_WEIGHT = 5
    EMPLOYMENT_STABILITY_WEIGHT = 4
    
    SETOR_ALTO_RISCO = ['Outros', 'Novo Negócio']
    SETOR_MEDIO_RISCO = ['Varejo', 'Serviços']
    SETOR_BAIXO_RISCO = ['Importação', 'Pescados', 'Alimentos', 'Distribuição']
    
    LIMITE_APROVADO = 700
    LIMITE_PENDENTE = 600
    
    TAXA_EXCELENTE = 1.99
    TAXA_BOA = 2.99
    TAXA_REGULAR = 3.99
    TAXA_ALTA = 5.99

    def calculate_modern_score(self, renda_mensal, historico_pagamento,
                               dividas_atuais, idade_credito, mix_credito,
                               consultas_recentes, setor_atuacao,
                               tempo_emprego):
        """Calcula pontuação de crédito (300-850 pontos)."""
        score = 300
        detalhes = {}
        
        historico_scores = {
            'Excelente': 220,
            'Bom': 180,
            'Regular': 120,
            'Ruim': 60
        }
        hist_score = historico_scores.get(historico_pagamento, 60)
        score += hist_score
        detalhes['historico_pagamento'] = hist_score
        
        if renda_mensal > 0:
            debt_to_income = dividas_atuais / renda_mensal
        else:
            debt_to_income = 1.0
        
        if debt_to_income == 0:
            util_score = 110
        elif debt_to_income <= 0.10:
            util_score = 100
        elif debt_to_income <= 0.30:
            util_score = 80
        elif debt_to_income <= 0.50:
            util_score = 50
        else:
            util_score = 20
        
        score += util_score
        detalhes['utilizacao_credito'] = util_score
        
        if idade_credito >= 120:
            age_score = 115
        elif idade_credito >= 84:
            age_score = 100
        elif idade_credito >= 60:
            age_score = 85
        elif idade_credito >= 36:
            age_score = 70
        elif idade_credito >= 24:
            age_score = 55
        elif idade_credito >= 12:
            age_score = 40
        else:
            age_score = 20
        
        score += age_score
        detalhes['idade_credito'] = age_score
        
        mix_scores = {5: 55, 4: 45, 3: 35, 2: 25, 1: 15}
        mix_score = mix_scores.get(mix_credito, 15)
        score += mix_score
        detalhes['mix_credito'] = mix_score
        
        if consultas_recentes == 0:
            recent_score = 27
        elif consultas_recentes <= 2:
            recent_score = 22
        elif consultas_recentes <= 4:
            recent_score = 15
        elif consultas_recentes <= 6:
            recent_score = 8
        else:
            recent_score = 0
        
        score += recent_score
        detalhes['consultas_recentes'] = recent_score
        
        if tempo_emprego >= 60:
            emp_score = 23
        elif tempo_emprego >= 36:
            emp_score = 18
        elif tempo_emprego >= 24:
            emp_score = 14
        elif tempo_emprego >= 12:
            emp_score = 10
        else:
            emp_score = 5
        
        score += emp_score
        detalhes['estabilidade_emprego'] = emp_score
        
        if setor_atuacao in self.SETOR_BAIXO_RISCO:
            setor_bonus = 20
        elif setor_atuacao in self.SETOR_MEDIO_RISCO:
            setor_bonus = 0
        else:
            setor_bonus = -15
        
        score += setor_bonus
        detalhes['ajuste_setorial'] = setor_bonus
        
        if renda_mensal >= 20000:
            renda_bonus = 15
        elif renda_mensal >= 10000:
            renda_bonus = 10
        elif renda_mensal >= 5000:
            renda_bonus = 5
        else:
            renda_bonus = 0
        
        score += renda_bonus
        detalhes['ajuste_renda'] = renda_bonus
        
        final_score = max(300, min(850, score))
        detalhes['score_final'] = final_score
        
        return final_score, detalhes

    def make_credit_decision(self, score):
        """Determina a decisão de crédito."""
        if score >= self.LIMITE_APROVADO:
            return "Aprovado"
        elif score >= self.LIMITE_PENDENTE:
            return "Pendente"
        else:
            return "Negado"

    def calculate_credit_limit(self, renda_mensal, score, dividas_atuais):
        """Calcula limite de crédito sugerido."""
        if score >= 800:
            multiplicador = 5.0
        elif score >= 750:
            multiplicador = 4.0
        elif score >= 700:
            multiplicador = 3.0
        elif score >= 650:
            multiplicador = 2.0
        elif score >= 600:
            multiplicador = 1.5
        else:
            multiplicador = 1.0
        
        limite_bruto = renda_mensal * multiplicador
        limite_ajustado = limite_bruto - (dividas_atuais * 0.5)
        limite_final = max(5000, min(500000, limite_ajustado))
        
        return round(limite_final, 2)

    def calculate_interest_rate(self, score, setor_atuacao):
        """Calcula taxa de juros mensal baseada no score e setor."""
        if score >= 800:
            taxa_base = self.TAXA_EXCELENTE
        elif score >= 750:
            taxa_base = self.TAXA_BOA
        elif score >= 700:
            taxa_base = self.TAXA_REGULAR
        else:
            taxa_base = self.TAXA_ALTA
        
        if setor_atuacao in self.SETOR_BAIXO_RISCO:
            taxa_final = taxa_base * 0.9
        elif setor_atuacao in self.SETOR_MEDIO_RISCO:
            taxa_final = taxa_base
        else:
            taxa_final = taxa_base * 1.2
        
        return round(taxa_final, 2)


class CreditApp:
    """Sistema de análise de crédito."""
    
    def __init__(self, master):
        self.master = master
        master.title("ECIL - Sistema de Análise de Crédito | Vila Olímpia - SP")
        master.geometry("1100x720")
        master.minsize(900, 700)
        
        try:
            master.iconbitmap('ecil_icon.ico')
        except:
            pass

        self.db_manager = DBManager(
            host='localhost',
            database='ECIL_CreditoProjetoDB',
            username='root',
            password='Youandnever5'
        )
        
        if self.db_manager.connect():
            self.db_manager.create_tables_if_not_exists()

        self.credit_analyzer = ModernCreditAnalyzer()
        
        self.configure_styles()
        self.create_widgets()
        self.load_recent_analyses()
        self.update_statistics()

    def configure_styles(self):
        """Configura estilos personalizados."""
        style = ttk.Style()
        style.theme_use("clam")
        
        bg_color = "#f5f5f5"
        accent_color = "#0066cc"
        fg_color = "#2c3e50"
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color,
                        font=("Segoe UI", 10))
        style.configure("TLabelframe", background=bg_color,
                        foreground=accent_color, borderwidth=2)
        style.configure("TLabelframe.Label", background=bg_color,
                        foreground=accent_color, font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("TButton",
                  background=[('active', accent_color), ('!disabled', '#e8e8e8')],
                  foreground=[('active', 'white')])
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                       background=accent_color, foreground="white")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 9))
        style.map("Treeview",
                  background=[('selected', accent_color)],
                  foreground=[('selected', 'white')])

    def create_widgets(self):
        """Cria interface completa do sistema."""
        self.master.grid_columnconfigure(0, weight=3)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=0)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(3, weight=1)

        header_frame = tk.Frame(self.master, bg="#0066cc", height=60)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Empreendimento Comercial Industrial Ecil LTDA",
            font=("Segoe UI", 16, "bold"),
            bg="#0066cc",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Sistema de Análise de Crédito | Vila Olímpia - SP",
            font=("Segoe UI", 10),
            bg="#0066cc",
            fg="white"
        )
        subtitle_label.pack(side=tk.LEFT, padx=20)

        self.input_frame = ttk.LabelFrame(
            self.master,
            text="Dados do Cliente",
            padding=(15, 10)

        )
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        for i in range(2):
            self.input_frame.grid_columnconfigure(i*2+1, weight=1)

        row = 0
        ttk.Label(self.input_frame, text="Nome Completo do Cliente:").grid(
            row=row, column=0, sticky="w", pady=5, padx=(0, 10)
        )
        self.nome_entry = ttk.Entry(self.input_frame, width=30)
        self.nome_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))

        ttk.Label(self.input_frame, text="CPF/CNPJ:").grid(
            row=row, column=2, sticky="w", pady=5, padx=(0, 10)
        )
        self.cpf_entry = ttk.Entry(self.input_frame, width=30)
        self.cpf_entry.grid(row=row, column=3, sticky="ew", pady=5)
        self.cpf_entry.bind('<KeyRelease>', self.format_cpf)

        row += 1
        ttk.Label(self.input_frame, text="Sugestão Limite de Crédito (R$):").grid(
            row=row, column=0, sticky="w", pady=5, padx=(0, 10)
        )
        self.renda_entry = ttk.Entry(self.input_frame, width=30)
        self.renda_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))

        ttk.Label(self.input_frame, text="Situação:").grid(
            row=row, column=2, sticky="w", pady=5, padx=(0, 10)
        )
        situacao_frame = ttk.Frame(self.input_frame)
        situacao_frame.grid(row=row, column=3, sticky="ew", pady=5)

        self.situacao_var = tk.StringVar(value="Pendente")
        for opcao in ["Aprovado", "Recusado", "Pendente"]:
            ttk.Radiobutton(
                situacao_frame,
                text=opcao,
                variable=self.situacao_var,
                value=opcao
            ).pack(side=tk.LEFT, padx=4)

        # Mantém o campo oculto para os cálculos não quebrarem
        self.dividas_entry = ttk.Entry(self.input_frame, width=1)
        self.dividas_entry.insert(0, "0")
        # Não colocamos .grid() — fica invisível mas existe

        row += 1
        ttk.Label(self.input_frame, text="Histórico de Pagamento:").grid(
            row=row, column=0, sticky="w", pady=5, padx=(0, 10)
        )
        self.historico_var = tk.StringVar(value="Bom")
        self.historico_option = ttk.Combobox(
            self.input_frame,
            textvariable=self.historico_var,
            values=["Excelente", "Bom", "Regular", "Ruim"],
            state="readonly",
            width=27
        )
        self.historico_option.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))

        ttk.Label(self.input_frame, text="Serasa (observação):").grid(
            row=row, column=2, sticky="nw", pady=5, padx=(0, 10)
        )
        serasa_frame = ttk.Frame(self.input_frame)
        serasa_frame.grid(row=row, column=3, sticky="ew", pady=5)
        serasa_frame.grid_columnconfigure(0, weight=1)

        self.serasa_text = tk.Text(
            serasa_frame, width=28, height=4,
            font=("Segoe UI", 9), wrap=tk.WORD,
            relief="solid", borderwidth=1
        )
        self.serasa_text.grid(row=0, column=0, sticky="ew")

        serasa_scroll = ttk.Scrollbar(serasa_frame, orient="vertical",
                                        command=self.serasa_text.yview)
        serasa_scroll.grid(row=0, column=1, sticky="ns")
        self.serasa_text.config(yscrollcommand=serasa_scroll.set)
        self.serasa_text.bind("<KeyRelease>", self._limit_serasa_chars)

        # Mantém campo oculto para os cálculos não quebrarem
        self.idade_credito_entry = ttk.Entry(self.input_frame, width=1)
        self.idade_credito_entry.insert(0, "0")
        # Sem .grid() — invisível mas existe

        def _limit_serasa_chars(self, event=None):
            """Limita o campo Serasa a 10.000 caracteres."""
            content = self.serasa_text.get("1.0", tk.END)
            if len(content) > 10001:
                self.serasa_text.delete("10000.0", tk.END)

        row += 1
        ttk.Label(self.input_frame, text="Mix de Crédito (1-5):").grid(
            row=row, column=0, sticky="w", pady=5, padx=(0, 10)
        )
        self.mix_credito_var = tk.StringVar(value="3")
        self.mix_credito_option = ttk.Combobox(
            self.input_frame,
            textvariable=self.mix_credito_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=27
        )
        self.mix_credito_option.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))

        ttk.Label(self.input_frame, text="Consultas Recentes:").grid(
            row=row, column=2, sticky="w", pady=5, padx=(0, 10)
        )
        self.consultas_entry = ttk.Entry(self.input_frame, width=30)
        self.consultas_entry.grid(row=row, column=3, sticky="ew", pady=5)

        row += 1
        ttk.Label(self.input_frame, text="Setor de Atuação:").grid(
            row=row, column=0, sticky="w", pady=5, padx=(0, 10)
            
        )
        
        self.setor_var = tk.StringVar(value="Pescados")
        self.setor_option = ttk.Combobox(
            self.input_frame,
            textvariable=self.setor_var,
            values=["Pescados", "Ingredientes", "Nutrição Animal", "Outros"],
            state="readonly",
            width=27
        )
        self.setor_option.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))

        row += 1
        ttk.Label(self.input_frame, text="Fornecedores:").grid(
            row=row, column=0, sticky="nw", pady=5, padx=(0, 10)
        )
        self.forn_sidebar_listbox = tk.Listbox(
            self.input_frame,
            height=1,
            font=("Segoe UI", 9),
            relief="solid",
            borderwidth=1,
            selectmode=tk.SINGLE
        )
        self.forn_sidebar_listbox.grid(
            row=row, column=1, columnspan=3, sticky="ew", pady=5
        )

        # Campo oculto para não quebrar os cálculos internos  ← linha 746 original
        self.tempo_emprego_entry = ttk.Entry(self.input_frame, width=1)

        # Campo oculto para não quebrar os cálculos internos
        self.tempo_emprego_entry = ttk.Entry(self.input_frame, width=1)
        self.tempo_emprego_entry.insert(0, "12")
        # Sem .grid() — invisível mas existe

        # PAINEL DE FORNECEDORES
        self.forn_frame = ttk.LabelFrame(
            self.master, text="Referências de Fornecedores", padding=(15, 10)
        )
        self.forn_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Botão para adicionar novo fornecedor
        btn_add_forn = ttk.Button(
            self.forn_frame,
            text="+ Adicionar Fornecedor",
            command=self.adicionar_fornecedor_linha
        )
        btn_add_forn.pack(anchor="w", pady=(0, 8))

        # Frame com scroll para lista de fornecedores
        forn_scroll_container = ttk.Frame(self.forn_frame)
        forn_scroll_container.pack(fill=tk.BOTH, expand=True)

        self.forn_canvas = tk.Canvas(forn_scroll_container, height=100, bg="#f0f0f0")
        forn_scrollbar = ttk.Scrollbar(
            forn_scroll_container, orient="vertical", command=self.forn_canvas.yview
        )
        self.forn_canvas.configure(yscrollcommand=forn_scrollbar.set)
        self.forn_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        forn_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.forn_inner_frame = ttk.Frame(self.forn_canvas)
        self.forn_canvas_window = self.forn_canvas.create_window(
            (0, 0), window=self.forn_inner_frame, anchor="nw"
        )
        self.forn_inner_frame.bind(
            "<Configure>",
            lambda e: self.forn_canvas.configure(
                scrollregion=self.forn_canvas.bbox("all")
            )
        )

        # Lista interna de fornecedores
        self.fornecedores_lista = []

        # Adiciona o primeiro fornecedor automaticamente
        self.adicionar_fornecedor_linha()


        self.stats_frame = ttk.LabelFrame(
            self.master,
            text="Estatísticas do Sistema",
            padding=(15, 10)
        )
        self.stats_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.stats_labels = {}
        stats_items = [
            ("Total de Análises:", "total"),
            ("Créditos Aprovados:", "aprovados"),
            ("Em Análise:", "pendentes"),
            ("Créditos Negados:", "negados"),
            ("Score Médio:", "score_medio")
        ]

        for idx, (label_text, key) in enumerate(stats_items):
            ttk.Label(self.stats_frame, text=label_text, 
                     font=("Segoe UI", 9)).grid(
                row=idx, column=0, sticky="w", pady=5
            )
            value_label = ttk.Label(self.stats_frame, text="0",
                                   font=("Segoe UI", 11, "bold"))
            value_label.grid(row=idx, column=1, sticky="e", pady=5, padx=(10, 0))
            self.stats_labels[key] = value_label

        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="new")

        ttk.Button(
            button_frame,
            text="Analisar Crédito",
            command=self.perform_analysis
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Limpar Campos",
            command=self.clear_fields
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Exportar CSV",
            command=self.export_to_csv
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Atualizar Estatísticas",
            command=self.update_statistics
        ).pack(fill=tk.X, pady=5)

        self.result_frame = ttk.LabelFrame(
            button_frame,
            text="Resultado da Análise",
            padding=(10, 10)
        )
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        ttk.Label(self.result_frame, text="Score:", 
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.score_label = ttk.Label(
            self.result_frame,
            text="N/A",
            font=("Segoe UI", 18, "bold"),
            foreground="#0066cc"
        )
        self.score_label.pack(anchor="w", pady=(0, 10))

        ttk.Label(self.result_frame, text="Decisão:", 
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.decision_label = ttk.Label(
            self.result_frame,
            text="N/A",
            font=("Segoe UI", 16, "bold"),
            foreground="#0066cc"
        )
        self.decision_label.pack(anchor="w", pady=(0, 10))

        ttk.Label(self.result_frame, text="Limite:", 
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.limit_label = ttk.Label(
            self.result_frame,
            text="N/A",
            font=("Segoe UI", 12, "bold"),
            foreground="#2c3e50"
        )
        self.limit_label.pack(anchor="w", pady=(0, 10))

        ttk.Label(self.result_frame, text="Taxa (% a.m.):", 
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.rate_label = ttk.Label(
            self.result_frame,
            text="N/A",
            font=("Segoe UI", 12, "bold"),
            foreground="#2c3e50"
        )
        self.rate_label.pack(anchor="w")

        self.history_frame = ttk.LabelFrame(
            self.master,
            text="Histórico de Análises de Crédito",
            padding=(10, 10)
        )
        self.history_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(0, weight=1)

        tree_container = ttk.Frame(self.history_frame)
        tree_container.grid(row=0, column=0, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        y_scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        
        x_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        columns = ("Nome", "CPF", "Data", "Score", "Decisão", "Limite", "Taxa")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Data", text="Data/Hora")
        self.tree.heading("Score", text="Score")
        self.tree.heading("Decisão", text="Decisão")
        self.tree.heading("Limite", text="Limite (R$)")
        self.tree.heading("Taxa", text="Taxa %")

        self.tree.column("Nome", width=160, anchor=tk.W)
        self.tree.column("CPF", width=110, anchor=tk.CENTER)
        self.tree.column("Data", width=150, anchor=tk.CENTER)
        self.tree.column("Score", width=70, anchor=tk.CENTER)
        self.tree.column("Decisão", width=90, anchor=tk.CENTER)
        self.tree.column("Limite", width=110, anchor=tk.E)
        self.tree.column("Taxa", width=70, anchor=tk.CENTER)

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.tag_configure('oddrow', background='#ffffff')
        self.tree.tag_configure('evenrow', background='#f8f9fa')
        self.tree.tag_configure('aprovado', foreground='#28a745')
        self.tree.tag_configure('pendente', foreground='#ffc107')
        self.tree.tag_configure('negado', foreground='#dc3545')

    def _limit_serasa_chars(self, event=None):
        """Limita o campo Serasa a 10.000 caracteres."""
        content = self.serasa_text.get("1.0", tk.END)
        if len(content) > 10001:
            self.serasa_text.delete("10000.0", tk.END)

    def adicionar_fornecedor_linha(self):
        """Adiciona um bloco de campos para um novo fornecedor."""
        idx = len(self.fornecedores_lista) + 1

        # Frame do fornecedor com borda
        frame = ttk.LabelFrame(
            self.forn_inner_frame,
            text=f"Fornecedor {idx}",
            padding=(10, 5)
        )
        frame.pack(fill=tk.X, pady=4, padx=4)

        campos = {}

        # Linha 1
        ttk.Label(frame, text="Fornecem Referência?").grid(
            row=0, column=0, sticky="w", padx=(0,8), pady=2
        )
        ref_var = tk.StringVar(value="Sim")
        campos['referencia'] = ref_var
        ref_f = ttk.Frame(frame)
        ref_f.grid(row=0, column=1, sticky="w", pady=2)
        for op in ["Sim", "Não"]:
            ttk.Radiobutton(ref_f, text=op,
                            variable=ref_var, value=op).pack(side=tk.LEFT, padx=4)
            
        ttk.Label(frame, text="E-mail:").grid(
            row=0, column=2, sticky="w", padx=(16,8), pady=2
        )
        e_email = ttk.Entry(frame, width=26)
        e_email.grid(row=0, column=3, sticky="ew", pady=2)
        campos['email'] = e_email

        # Linha 2
        ttk.Label(frame, text="Telefone:").grid(
            row=1, column=0, sticky="w", padx=(0,8), pady=2
        )
        e_tel = ttk.Entry(frame, width=18)
        e_tel.grid(row=1, column=1, sticky="ew", pady=2)
        campos['telefone'] = e_tel

        ttk.Label(frame, text="Contato (nome):").grid(
            row=1, column=2, sticky="w", padx=(16,8), pady=2
        )
        e_contato = ttk.Entry(frame, width=26)
        e_contato.grid(row=1, column=3, sticky="ew", pady=2)
        campos['contato'] = e_contato

        # Linha 3
        ttk.Label(frame, text="1ª Compra — Data:").grid(
            row=2, column=0, sticky="w", padx=(0,8), pady=2
        )
        e_p_data = ttk.Entry(frame, width=18)
        e_p_data.insert(0, "DD/MM/AAAA")
        e_p_data.grid(row=2, column=1, sticky="ew", pady=2)
        e_p_data.bind("<FocusIn>",
            lambda e, w=e_p_data: w.delete(0, tk.END)
            if w.get() == "DD/MM/AAAA" else None)
        campos['primeira_data'] = e_p_data


       
        e_p_valor = ttk.Entry(frame, width=26)
        e_p_valor.grid(row=2, column=3, sticky="ew", pady=2)
        campos['primeira_valor'] = e_p_valor

        # Linha 4
        ttk.Label(frame, text="Última Compra — Data:").grid(
            row=3, column=0, sticky="w", padx=(0,8), pady=2
        )
        e_u_data = ttk.Entry(frame, width=18)
        e_u_data.insert(0, "DD/MM/AAAA")
        e_u_data.grid(row=3, column=1, sticky="ew", pady=2)
        e_u_data.bind("<FocusIn>",
            lambda e, w=e_u_data: w.delete(0, tk.END)
            if w.get() == "DD/MM/AAAA" else None)
        campos['ultima_data'] = e_u_data

       
        e_u_valor = ttk.Entry(frame, width=26)
        e_u_valor.grid(row=3, column=3, sticky="ew", pady=2)
        campos['ultima_valor'] = e_u_valor

        # Linha 5
        ttk.Label(frame, text="Limite de Crédito (R$):").grid(
            row=4, column=0, sticky="w", padx=(0,8), pady=2
        )
        e_limite = ttk.Entry(frame, width=18)
        e_limite.grid(row=4, column=1, sticky="ew", pady=2)
        campos['limite'] = e_limite

        ttk.Label(frame, text="Data de Cadastro:").grid(
            row=4, column=2, sticky="w", padx=(16,8), pady=2
        )
        e_cadastro = ttk.Entry(frame, width=26)
        e_cadastro.insert(0, "DD/MM/AAAA")
        e_cadastro.grid(row=4, column=3, sticky="ew", pady=2)
        e_cadastro.bind("<FocusIn>",
            lambda e, w=e_cadastro: w.delete(0, tk.END)
            if w.get() == "DD/MM/AAAA" else None)
        campos['cadastro'] = e_cadastro

        # Botão remover
        ttk.Button(
            frame, text="✕ Remover",
            command=lambda f=frame, c=campos: self.remover_fornecedor(f, c)
        ).grid(row=0, column=4, padx=(12,0), pady=2)
        
        campos['frame'] = frame
        self.fornecedores_lista.append(campos)
        self.atualizar_lista_fornecedores_sidebar()

    def remover_fornecedor(self, frame, campos):
        """Remove um bloco de fornecedor."""
        frame.destroy()
        self.fornecedores_lista = [
            f for f in self.fornecedores_lista if f.get('frame') != frame
        ]
        self.atualizar_lista_fornecedores_sidebar()

    def atualizar_lista_fornecedores_sidebar(self):
        """Atualiza a listbox lateral com os fornecedores cadastrados."""
        self.forn_sidebar_listbox.delete(0, tk.END)
        for i, forn in enumerate(self.fornecedores_lista, 1):
            email = forn['email'].get() or "—"
            self.forn_sidebar_listbox.insert(tk.END, f"Fornecedor {i}: {email}")




    def format_cpf(self, event=None):
        raw = self.cpf_entry.get()
        digits = ''.join(filter(str.isdigit, raw))

        if len(digits) <= 11:
            digits = digits[:11]
            if len(digits) > 9:
                formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
            elif len(digits) > 6:
                formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
            elif len(digits) > 3:
                formatted = f"{digits[:3]}.{digits[3:]}"
            else:
                formatted = digits
        else: 
            digits = digits[:14]
            if len(digits) > 12:
                formatted = (f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}"
                             f"/{digits[8:12]}-{digits[12:]}")
            elif len(digits) > 8:
                formatted = (f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}"
                             f"/{digits[8:]}")
            elif len(digits) > 5:
                formatted =  f"{digits[:2]}.{digits[2:5]}.{digits[5:]}"
            elif len(digits) > 2:
                formatted =  f"{digits[:2]}.{digits[2:]}"
            else:
                formatted = digits

        if formatted != raw:
            pos = self.cpf_entry.index(tk.INSERT)
            self.cpf_entry.delete(0, tk.END)
            self.cpf_entry.insert(0, formatted)
            new_pos = min(pos + (len(formatted) - len(raw)), len(formatted))
            self.cpf_entry.icursor(new_pos)

    def validate_cpf(self, cpf):
        """Valida CPF (11 dígitos) ou CNPJ (14 dígitos)."""
        digits = ''.join(filter(str.isdigit, cpf))

        # ── CPF ──────────────────────────────────────────
        if len(digits) == 11:
            if digits == digits[0] * 11:
                return False
            def calc(partial, weights):
                total = sum(int(d) * w for d, w in zip(partial, weights))
                r = total % 11
                return 0 if r < 2 else 11 - r
            if calc(digits[:9], range(10, 1, -1)) != int(digits[9]):
                return False
            if calc(digits[:10], range(11, 1, -1)) != int(digits[10]):
                return False
            return True

        # ── CNPJ ─────────────────────────────────────────
        if len(digits) == 14:
            if digits == digits[0] * 14:
                return False
            def calc(partial, weights):
                total = sum(int(d) * w for d, w in zip(partial, weights))
                r = total % 11
                return 0 if r < 2 else 11 - r
            w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            if calc(digits[:12], w1) != int(digits[12]):
                return False
            if calc(digits[:13], w2) != int(digits[13]):
                return False
            return True

        return False

    def parse_currency(self, value_str):
        """Converte string para float."""
        if not value_str or value_str.strip() == "":
            return None
        
        value_str = value_str.strip().replace('R$', '').strip()
        
        if ',' in value_str and '.' in value_str:
            value_str = value_str.replace('.', '')
        
        value_str = value_str.replace(',', '.')
        
        try:
            return float(value_str)
        except ValueError:
            return None

    def perform_analysis(self):
        """Realiza análise de crédito completa."""
        nome = self.nome_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        renda_str = self.renda_entry.get().strip()
        dividas_str = self.dividas_entry.get().strip()
        historico = self.historico_var.get()
        idade_credito_str = self.idade_credito_entry.get().strip()
        mix_credito = int(self.mix_credito_var.get())
        consultas_str = self.consultas_entry.get().strip()
        setor = self.setor_var.get()
        tempo_emprego_str = self.tempo_emprego_entry.get().strip()

        if not all([nome, cpf, renda_str, dividas_str, idade_credito_str,
                   consultas_str, tempo_emprego_str]):
            messagebox.showwarning(
                "Campos Incompletos",
                "Por favor, preencha todos os campos obrigatórios."
            )
            return

        if not self.validate_cpf(cpf):
            messagebox.showerror(
                "CPF Inválido",
                "O CPF informado não é válido. Verifique os dígitos."
            )
            self.cpf_entry.focus()
            return

        renda_mensal = self.parse_currency(renda_str)
        dividas_atuais = self.parse_currency(dividas_str)
        
        try:
            idade_credito = int(idade_credito_str)
            consultas_recentes = int(consultas_str)
            tempo_emprego = int(tempo_emprego_str)
        except ValueError:
            messagebox.showerror(
                "Valores Inválidos",
                "Idade de crédito, consultas e tempo de emprego devem ser números inteiros."
            )
            return

        if renda_mensal is None or dividas_atuais is None:
            messagebox.showerror(
                "Valores Inválidos",
                "Renda e dívidas devem ser valores numéricos válidos."
            )
            return

        if renda_mensal < 0 or dividas_atuais < 0:
            messagebox.showerror(
                "Valores Negativos",
                "Valores financeiros não podem ser negativos."
            )
            return

        if idade_credito < 0 or consultas_recentes < 0 or tempo_emprego < 0:
            messagebox.showerror(
                "Valores Inválidos",
                "Idade de crédito, consultas e tempo de emprego não podem ser negativos."
            )
            return

        cpf_clean = ''.join(filter(str.isdigit, cpf))

        cliente_existente = self.db_manager.fetch_one(
            "SELECT ClienteID FROM Clientes WHERE CPF = %s",
            (cpf_clean,)
        )

        if cliente_existente:
            cliente_id = cliente_existente[0]
            self.db_manager.update_client(
                cliente_id, nome, cpf_clean, renda_mensal, historico,
                dividas_atuais, idade_credito, mix_credito,
                consultas_recentes, setor, tempo_emprego
            )
        else:
            cliente_id = self.db_manager.insert_client(
                nome, cpf_clean, renda_mensal, historico, dividas_atuais,
                idade_credito, mix_credito, consultas_recentes, setor,
                tempo_emprego
            )
            if cliente_id == 0:
                messagebox.showerror("Erro", "Não foi possível cadastrar o cliente.")
                return

        score, detalhes = self.credit_analyzer.calculate_modern_score(
            renda_mensal, historico, dividas_atuais, idade_credito,
            mix_credito, consultas_recentes, setor, tempo_emprego
        )
        
        decisao = self.credit_analyzer.make_credit_decision(score)
        limite = self.credit_analyzer.calculate_credit_limit(
            renda_mensal, score, dividas_atuais
        )
        taxa = self.credit_analyzer.calculate_interest_rate(score, setor)

        self.score_label.config(text=f"{score}")
        self.decision_label.config(text=decisao)
        self.limit_label.config(text=f"R$ {limite:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.rate_label.config(text=f"{taxa}%")

        color_map = {
            "Aprovado": "#28a745",
            "Pendente": "#ffc107",
            "Negado": "#dc3545"
        }
        self.decision_label.config(foreground=color_map.get(decisao, "#0066cc"))

        detalhes_json = str(detalhes)
        if self.db_manager.insert_analysis(cliente_id, score, decisao, 
                                          limite, taxa, detalhes_json):
            messagebox.showinfo(
                "Análise Concluída",
                f"Análise de crédito realizada com sucesso!\n\n"
                f"Cliente: {nome}\n"
                f"Score: {score}/850\n"
                f"Decisão: {decisao}\n"
                f"Limite Sugerido: R$ {limite:,.2f}\n"
                f"Taxa Mensal: {taxa}%"
            )
            self.load_recent_analyses()
            self.update_statistics()
        else:
            messagebox.showwarning("Aviso", "Erro ao salvar análise no banco.")

    def clear_fields(self):
        """Limpa todos os campos."""
        self.nome_entry.delete(0, tk.END)
        self.cpf_entry.delete(0, tk.END)
        self.renda_entry.delete(0, tk.END)
        self.dividas_entry.delete(0, tk.END)
        self.idade_credito_entry.delete(0, tk.END)
        self.consultas_entry.delete(0, tk.END)
        self.tempo_emprego_entry.delete(0, tk.END)
        self.historico_var.set("Bom")
        self.mix_credito_var.set("3")
        self.setor_var.set("Pescados")
        self.score_label.config(text="N/A", foreground="#0066cc")
        self.decision_label.config(text="N/A", foreground="#0066cc")
        self.limit_label.config(text="N/A")
        self.rate_label.config(text="N/A")
        # Limpa painel fornecedores
        self.forn_referencia_var.set("Sim")
        self.forn_email_entry.delete(0, tk.END)
        self.forn_telefone_entry.delete(0, tk.END)
        self.forn_contato_entry.delete(0, tk.END)
        self.forn_primeira_data_entry.delete(0, tk.END)
        self.forn_primeira_data_entry.insert(0, "DD/MM/AAAA")
        self.forn_primeira_valor_entry.delete(0, tk.END)
        self.forn_ultima_data_entry.delete(0, tk.END)
        self.forn_ultima_data_entry.insert(0, "DD/MM/AAAA")
        self.forn_ultima_valor_entry.delete(0, tk.END)
        self.forn_limite_entry.delete(0, tk.END)
        self.forn_cadastro_entry.delete(0, tk.END)
        self.forn_cadastro_entry.insert(0, "DD/MM/AAAA")
        self.nome_entry.focus()

    def load_recent_analyses(self):
        """Carrega histórico de análises."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        analyses = self.db_manager.get_recent_analyses(limit=25)
        
        for idx, analysis in enumerate(analyses):
            nome, cpf, data, score, decisao, limite, taxa = analysis
            
            cpf_formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            
            if isinstance(data, datetime):
                data_formatted = data.strftime("%d/%m/%Y %H:%M")
            else:
                data_formatted = str(data)
            
            limite_formatted = f"R$ {limite:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            taxa_formatted = f"{taxa}%"
            
            row_tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            decision_tag = decisao.lower()
            
            self.tree.insert(
                "",
                tk.END,
                values=(nome, cpf_formatted, data_formatted, score, 
                       decisao, limite_formatted, taxa_formatted),
                tags=(row_tag, decision_tag)
            )

    def update_statistics(self):
        """Atualiza painel de estatísticas."""
        stats = self.db_manager.get_statistics()
        
        self.stats_labels['total'].config(text=str(stats.get('total_analises', 0)))
        self.stats_labels['aprovados'].config(
            text=str(stats.get('aprovados', 0)),
            foreground="#28a745"
        )
        self.stats_labels['pendentes'].config(
            text=str(stats.get('pendentes', 0)),
            foreground="#ffc107"
        )
        self.stats_labels['negados'].config(
            text=str(stats.get('negados', 0)),
            foreground="#dc3545"
        )
        self.stats_labels['score_medio'].config(
            text=f"{stats.get('score_medio', 0)}/850"
        )

    def export_to_csv(self):
        """Exporta análises para CSV."""
        columns, rows = self.db_manager.get_all_credit_analyses_for_export()
        
        if not rows:
            messagebox.showinfo("Exportar", "Não há dados para exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Todos", "*.*")],
            title="Exportar Análises",
            initialfile=f"ECIL_analises_{datetime.now():%Y%m%d_%H%M%S}.csv"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(columns)
                
                for row in rows:
                    formatted_row = []
                    for item in row:
                        if isinstance(item, datetime):
                            formatted_row.append(item.strftime("%d/%m/%Y %H:%M:%S"))
                        elif isinstance(item, Decimal):
                            formatted_row.append(str(item).replace('.', ','))
                        else:
                            formatted_row.append(str(item))
                    writer.writerow(formatted_row)
            
            messagebox.showinfo(
                "Exportação Concluída",
                f"Dados exportados com sucesso!\n\n"
                f"Arquivo: {file_path}\n"
                f"Total de registros: {len(rows)}"
            )
            
            if messagebox.askyesno("Abrir Arquivo", "Deseja abrir o arquivo?"):
                import os
                import platform
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':
                    os.system(f'open "{file_path}"')
                else:
                    os.system(f'xdg-open "{file_path}"')
                    
        except PermissionError:
            messagebox.showerror(
                "Erro de Permissão",
                "Arquivo pode estar aberto em outro programa."
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def on_closing(self):
        """Encerra aplicação."""
        if messagebox.askokcancel("Sair", "Deseja sair do Sistema ECIL?"):
            self.db_manager.disconnect()
            self.master.destroy()


def main():
    """Inicia aplicação ECIL."""
    root = tk.Tk()
    app = CreditApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()


    


