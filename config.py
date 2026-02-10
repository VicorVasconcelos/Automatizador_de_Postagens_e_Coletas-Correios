"""
Configurações do Automatizador de Correios

Centralizei tudo aqui porque já cansei de procurar URLs e timeouts espalhados pelo código.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DADOS_DIR = BASE_DIR / "dados"
RELATORIOS_DIR = BASE_DIR / "relatorios"
LOGS_DIR = BASE_DIR / "logs"

CORREIOS_LOGIN_URL = "https://empresas.correios.com.br/#/login"
CORREIOS_PRE_POSTAGEM_URL = "https://prepostagem.correios.com.br/bem-vindo"
CORREIOS_PRE_POSTAGEM_REGISTRADOS_URL = "https://prepostagem.correios.com.br/prepostagem/painels/faturar/registrados"
CORREIOS_POSTAGEM_URL = "https://empresas.correios.com.br/#/postagem"
CORREIOS_COLETA_URL = "https://empresas.correios.com.br/#/coleta"

CORREIOS_USUARIO = os.getenv("CORREIOS_USUARIO", "")
CORREIOS_SENHA = os.getenv("CORREIOS_SENHA", "")
CORREIOS_CARTAO = os.getenv("CORREIOS_CARTAO", "")

# === CONFIGURAÇÕES DA API DOS CORREIOS ===
# Credenciais para Web Service SOAP/XML
API_USUARIO = os.getenv("CORREIOS_API_USUARIO", "empresacws")  # ID do cliente
API_SENHA = os.getenv("CORREIOS_API_SENHA", "123456")  # Senha da API
API_CONTRATO = os.getenv("CORREIOS_API_CONTRATO", "9912369087")  # Código do contrato
API_CARTAO_POSTAGEM = os.getenv("CORREIOS_API_CARTAO", "0079803601")  # Cartão de postagem
API_CODIGO_SERVICO = os.getenv("CORREIOS_API_SERVICO", "04170")  # 04170=SEDEX, 04677=SEDEX COM CONTRATO

# Ambiente: 'producao' ou 'homologacao'
API_AMBIENTE = os.getenv("CORREIOS_API_AMBIENTE", "homologacao")

# Esses timeouts foram calibrados depois de MUITO teste com o site dos Correios
HEADLESS_MODE = False
TIMEOUT_PADRAO = 30  # segundos
TEMPO_ESPERA_ELEMENTO = 10

ARQUIVO_ENTRADA = "dados_postagem.xlsx"
ABA_PRINCIPAL = 0

# Colunas esperadas na planilha de entrada (mapeamento da Pasta3.xlsx)
COLUNAS_POSTAGEM = {
    "nome_destinatario": "COORDENADOR MUNICIPAL",
    "cpf_cnpj": "CPF",
    "endereco": "LOGRADOURO",
    "numero": "NÚMERO",
    "complemento": "COMPLEMENTO",
    "bairro": "BAIRRO",
    "cidade": "CIDADE",
    "estado": "UF.1",
    "cep": "CEP",
    "telefone": "TELEFONE",
    "email": "EMAIL",
    "tipo_servico": "Tipo de Serviço",
    "peso": "Peso (kg)",
    "valor_declarado": "Valor Declarado",
    "aviso_recebimento": "AR",
    "mao_propria": "Mão Própria",
}

COLUNAS_COLETA = {
    "tipo_objeto": "Tipo de Objeto",
    "quantidade": "Quantidade",
    "peso_total": "Peso Total (kg)",
    "data_coleta": "Data da Coleta",
    "periodo": "Período",
    "observacoes": "Observações",
}

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Sistema de retry porque o site dos Correios às vezes dá pau do nada
MAX_TENTATIVAS = 3
TEMPO_ENTRE_TENTATIVAS = 5
