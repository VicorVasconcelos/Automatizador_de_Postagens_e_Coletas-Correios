"""
Módulo para manipulação de planilhas Excel

Lidar com Excel em Python é sempre uma dor de cabeça, mas pandas + openpyxl resolvem bem.
"""
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class ExcelHandler:
    
    def __init__(self, arquivo_entrada: Optional[str] = None):
        """
        Inicializa o manipulador de Excel
        
        Args:
            arquivo_entrada: Nome do arquivo de entrada (opcional)
        """
        self.arquivo_entrada = arquivo_entrada or config.ARQUIVO_ENTRADA
        self.caminho_entrada = config.DADOS_DIR / self.arquivo_entrada
        
    def ler_dados_postagem(self) -> List[Dict]:
        """
        Lê os dados de postagem da planilha
        
        Returns:
            Lista de dicionários com os dados de cada postagem
        """
        try:
            if not self.caminho_entrada.exists():
                logger.error(f"Arquivo não encontrado: {self.caminho_entrada}")
                raise FileNotFoundError(f"Arquivo {self.caminho_entrada} não encontrado")
            
            logger.info(f"Lendo arquivo: {self.caminho_entrada}")
            df = pd.read_excel(self.caminho_entrada, sheet_name=config.ABA_PRINCIPAL)
            
            df = df.dropna(how='all')
            
            dados = df.to_dict('records')
            
            logger.info(f"Total de {len(dados)} registros carregados")
            return dados
            
        except Exception as e:
            logger.error(f"Erro ao ler planilha: {str(e)}")
            raise
    
    def validar_dados(self, dados: List[Dict]) -> tuple:
        """
        Valida os dados lidos da planilha
        
        Args:
            dados: Lista de registros
            
        Returns:
            Tupla (dados_validos, dados_invalidos)
        """
        dados_validos = []
        dados_invalidos = []
        
        # Esses campos são obrigatórios - aprendi isso testando com dados reais da Pasta3.xlsx
        campos_obrigatorios = ['COORDENADOR MUNICIPAL', 'CEP', 'LOGRADOURO', 'CIDADE', 'UF.1']
        
        for idx, registro in enumerate(dados, start=2):
            erros = []
            
            for campo in campos_obrigatorios:
                if campo not in registro or pd.isna(registro[campo]) or str(registro[campo]).strip() == '':
                    erros.append(f"Campo obrigatório '{campo}' está vazio")
            
            if 'CEP' in registro and not pd.isna(registro['CEP']):
                cep = str(registro['CEP']).replace('-', '').replace('.', '').strip()
                if not cep.isdigit() or len(cep) != 8:
                    erros.append(f"CEP inválido: {registro['CEP']}")
            
            # Validação flexível para número porque tem gente que coloca "S/Nº", "SN", ou deixa vazio
            if 'NÚMERO' in registro and not pd.isna(registro['NÚMERO']):
                numero = str(registro['NÚMERO']).strip().upper()
                if numero not in ['S/Nº', 'S/N', 'SN', ''] and not numero.replace(' ', '').isdigit():
                    erros.append(f"Número inválido: {registro['NÚMERO']}")
            
            if erros:
                registro['_linha'] = idx
                registro['_erros'] = erros
                dados_invalidos.append(registro)
                logger.warning(f"Linha {idx} com erros: {', '.join(erros)}")
            else:
                registro['_linha'] = idx
                dados_validos.append(registro)
        
        logger.info(f"Validação concluída: {len(dados_validos)} válidos, {len(dados_invalidos)} inválidos")
        return dados_validos, dados_invalidos
    
    def criar_planilha_template(self, tipo: str = "postagem"):
        """Cria uma planilha template para preenchimento"""
        if tipo == "postagem":
            colunas = list(config.COLUNAS_POSTAGEM.values())
        else:
            colunas = list(config.COLUNAS_COLETA.values())
        
        df = pd.DataFrame(columns=colunas)
        
        if tipo == "postagem":
            exemplo = {
                "COORDENADOR MUNICIPAL": "João da Silva",
                "CPF": "123.456.789-00",
                "LOGRADOURO": "Rua Exemplo",
                "NÚMERO": "123",
                "COMPLEMENTO": "Apto 101",
                "BAIRRO": "Centro",
                "CIDADE": "São Paulo",
                "UF.1": "SP",
                "CEP": "01234-567",
                "TELEFONE": "(11) 98765-4321",
                "EMAIL": "email@exemplo.com",
                "Tipo de Serviço": "PAC",
                "Peso (kg)": "1.5",
                "Valor Declarado": "100.00",
                "AR": "N",
                "Mão Própria": "N"
            }
            df = pd.DataFrame([exemplo])
        
        arquivo_template = config.DADOS_DIR / f"template_{tipo}.xlsx"
        nome_aba = "Dados" if tipo == "postagem" else "Coleta"
        df.to_excel(arquivo_template, index=False, sheet_name=nome_aba)
        logger.info(f"Template criado: {arquivo_template}")
        print(f"✓ Template criado: {arquivo_template}")


if __name__ == "__main__":
    # Teste do módulo
    logging.basicConfig(level=logging.INFO)
    handler = ExcelHandler()
    
    # Cria template se não existir arquivo de entrada
    if not handler.caminho_entrada.exists():
        print("Criando template de exemplo...")
        handler.criar_planilha_template("postagem")
