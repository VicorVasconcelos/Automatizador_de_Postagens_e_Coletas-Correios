"""
Módulo para geração de relatórios

Gerar relatórios em Excel e TXT pq o Excel é melhor de visualizar e eu prefiro TXT pra auditar rápido.
"""
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def gerar_relatorio(self, resultados: Dict, tipo: str = 'api') -> Path:
        """
        
        Args:
            resultados: Dict com 'sucesso', 'erro' e 'total'
            tipo: Tipo do relatório ('api' ou 'selenium')
            
        Returns:
            Caminho do arquivo de relatório gerado
        """
        # Adapta formato da API para formato do ReportGenerator
        sucesso_list = []
        for item in resultados.get('sucesso', []):
            sucesso_list.append({
                'linha': item.get('linha'),
                'destinatario': item.get('nome'),
                'codigo_rastreamento': item.get('codigo')
            })
        
        erro_list = []  
        for item in resultados.get('erro', []):
            erro_list.append({
                'linha': item.get('linha'),
                'destinatario': item.get('nome'),
                'erro': item.get('erro')
            })
        
        # Gera relatórios
        self.gerar_relatorio_texto(sucesso_list, erro_list, None)
        return self.gerar_relatorio_completo(sucesso_list, erro_list, None)
        
    def gerar_relatorio_completo(
        self, 
        resultados_sucesso: List[Dict],
        resultados_erro: List[Dict],
        dados_invalidos: List[Dict] = None
    ) -> Path:
        """Gera relatório completo em Excel com abas"""
        nome_arquivo = f"relatorio_{self.timestamp}.xlsx"
        caminho_relatorio = config.RELATORIOS_DIR / nome_arquivo
        
        try:
            with pd.ExcelWriter(caminho_relatorio, engine='openpyxl') as writer:
                self._criar_aba_resumo(
                    writer, 
                    len(resultados_sucesso), 
                    len(resultados_erro),
                    len(dados_invalidos) if dados_invalidos else 0
                )
                
                if resultados_sucesso:
                    df_sucesso = pd.DataFrame(resultados_sucesso)
                    df_sucesso.to_excel(writer, sheet_name='Sucessos', index=False)
                    logger.info(f"{len(resultados_sucesso)} sucessos registrados")
                
                if resultados_erro:
                    df_erro = pd.DataFrame(resultados_erro)
                    df_erro.to_excel(writer, sheet_name='Erros', index=False)
                    logger.info(f"{len(resultados_erro)} erros registrados")
                
                if dados_invalidos:
                    df_invalidos = pd.DataFrame(dados_invalidos)
                    df_invalidos.to_excel(writer, sheet_name='Dados Inválidos', index=False)
                    logger.info(f"{len(dados_invalidos)} dados inválidos registrados")
            
            logger.info(f"Relatório gerado: {caminho_relatorio}")
            return caminho_relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
            raise
    
    def _criar_aba_resumo(self, writer, total_sucesso: int, total_erro: int, total_invalido: int):
        total_processado = total_sucesso + total_erro
        total_geral = total_processado + total_invalido
        
        taxa_sucesso = (total_sucesso / total_geral * 100) if total_geral > 0 else 0
        
        resumo_data = {
            'Métrica': [
                'Data/Hora do Processamento',
                'Total de Registros',
                'Dados Inválidos (não processados)',
                'Processados com Sucesso',
                'Processados com Erro',
                'Taxa de Sucesso (%)'
            ],
            'Valor': [
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                total_geral,
                total_invalido,
                total_sucesso,
                total_erro,
                f"{taxa_sucesso:.2f}%"
            ]
        }
        
        df_resumo = pd.DataFrame(resumo_data)
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
    
    def gerar_relatorio_texto(
        self,
        resultados_sucesso: List[Dict],
        resultados_erro: List[Dict],
        dados_invalidos: List[Dict] = None
    ) -> Path:
        """Gera relatório em formato texto simples"""
        nome_arquivo = f"relatorio_{self.timestamp}.txt"
        caminho_relatorio = config.RELATORIOS_DIR / nome_arquivo
        
        try:
            with open(caminho_relatorio, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("RELATÓRIO DE PROCESSAMENTO - AUTOMATIZADOR CORREIOS\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                total_processado = len(resultados_sucesso) + len(resultados_erro)
                total_invalido = len(dados_invalidos) if dados_invalidos else 0
                total_geral = total_processado + total_invalido
                
                f.write("RESUMO\n")
                f.write("-"*80 + "\n")
                f.write(f"Total de Registros: {total_geral}\n")
                f.write(f"Dados Inválidos (não processados): {total_invalido}\n")
                f.write(f"Processados com Sucesso: {len(resultados_sucesso)}\n")
                f.write(f"Processados com Erro: {len(resultados_erro)}\n")
                if total_geral > 0:
                    taxa = (len(resultados_sucesso) / total_geral * 100)
                    f.write(f"Taxa de Sucesso: {taxa:.2f}%\n")
                f.write("\n")
                
                if resultados_sucesso:
                    f.write("\n" + "="*80 + "\n")
                    f.write("PROCESSAMENTOS BEM-SUCEDIDOS\n")
                    f.write("="*80 + "\n\n")
                    for idx, resultado in enumerate(resultados_sucesso, 1):
                        f.write(f"{idx}. Linha {resultado.get('linha', 'N/A')}\n")
                        f.write(f"   Destinatário: {resultado.get('destinatario', 'N/A')}\n")
                        f.write(f"   Código de Rastreamento: {resultado.get('codigo_rastreamento', 'N/A')}\n")
                        if 'codigo_coleta' in resultado:
                            f.write(f"   Código de Coleta: {resultado.get('codigo_coleta', 'N/A')}\n")
                        f.write("\n")
                
                if resultados_erro:
                    f.write("\n" + "="*80 + "\n")
                    f.write("PROCESSAMENTOS COM ERRO\n")
                    f.write("="*80 + "\n\n")
                    for idx, resultado in enumerate(resultados_erro, 1):
                        f.write(f"{idx}. Linha {resultado.get('linha', 'N/A')}\n")
                        f.write(f"   Destinatário: {resultado.get('destinatario', 'N/A')}\n")
                        f.write(f"   Erro: {resultado.get('erro', 'Erro desconhecido')}\n")
                        f.write("\n")
                
                if dados_invalidos:
                    f.write("\n" + "="*80 + "\n")
                    f.write("DADOS INVÁLIDOS (NÃO PROCESSADOS)\n")
                    f.write("="*80 + "\n\n")
                    for idx, resultado in enumerate(dados_invalidos, 1):
                        f.write(f"{idx}. Linha {resultado.get('_linha', 'N/A')}\n")
                        f.write(f"   Destinatário: {resultado.get('Nome Destinatário', 'N/A')}\n")
                        erros = resultado.get('_erros', ['Erro de validação'])
                        for erro in erros:
                            f.write(f"   - {erro}\n")
                        f.write("\n")
            
            logger.info(f"Relatório texto gerado: {caminho_relatorio}")
            return caminho_relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório texto: {str(e)}")
            raise
    
    def exibir_resumo_console(
        self,
        resultados_sucesso: List[Dict],
        resultados_erro: List[Dict],
        dados_invalidos: List[Dict] = None
    ):
        """Exibe resumo no console"""
        print("\n" + "="*80)
        print("RESUMO DO PROCESSAMENTO")
        print("="*80)
        
        total_invalido = len(dados_invalidos) if dados_invalidos else 0
        total_processado = len(resultados_sucesso) + len(resultados_erro)
        total_geral = total_processado + total_invalido
        
        print(f"\nTotal de Registros: {total_geral}")
        print(f"Dados Inválidos (não processados): {total_invalido}")
        print(f"✓ Processados com Sucesso: {len(resultados_sucesso)}")
        print(f"✗ Processados com Erro: {len(resultados_erro)}")
        
        if total_geral > 0:
            taxa = (len(resultados_sucesso) / total_geral * 100)
            print(f"\nTaxa de Sucesso: {taxa:.2f}%")
        
        print("="*80 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    generator = ReportGenerator()
    
    sucesso = [
        {"linha": 2, "destinatario": "João Silva", "codigo_rastreamento": "AA123456789BR"},
        {"linha": 3, "destinatario": "Maria Santos", "codigo_rastreamento": "AA987654321BR"}
    ]
    
    erro = [
        {"linha": 4, "destinatario": "Pedro Oliveira", "erro": "CEP não encontrado"}
    ]
    
    invalidos = [
        {"_linha": 5, "Nome Destinatário": "Ana Costa", "_erros": ["Campo 'CEP' está vazio"]}
    ]
    
    # Gera relatórios
    generator.exibir_resumo_console(sucesso, erro, invalidos)
    generator.gerar_relatorio_texto(sucesso, erro, invalidos)
    generator.gerar_relatorio_completo(sucesso, erro, invalidos)
    
    print("Relatórios gerados com sucesso!")


# compatibilidade com diferentes módulos
RelatorioHandler = ReportGenerator
