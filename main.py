"""
Automatizador de Postagens e Coletas - Correios Empresa
Autor: Victor Vasconcelos
Data: 02/2026

Sistema que automatiza a emissão de códigos de rastreio no site dos Correios.
"""
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict
import config
from excel import ExcelHandler
from correios import CorreiosAutomator
from relatorio import ReportGenerator

# O sistema de log é essencial pra debugar quando o site dos Correios muda alguma coisa
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOGS_DIR / f"automacao_{time.strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AutomatizadorCorreios:
    """Classe principal do automatizador"""
    
    def __init__(self, tipo_processo: str = "postagem", usuario: str = None, senha: str = None, caminho_planilha: str = None):
        """
        Inicializa o automatizador
        
        Args:
            tipo_processo: 'postagem' ou 'coleta'
            usuario: Usuário dos Correios
            senha: Senha dos Correios
            caminho_planilha: Caminho completo da planilha
        """
        self.tipo_processo = tipo_processo
        self.usuario = usuario
        self.senha = senha
        self.caminho_planilha = caminho_planilha
        
        # Gambiarra necessária porque alguns usuários arrastam o arquivo e outros digitam o caminho
        if caminho_planilha:
            arquivo_entrada = Path(caminho_planilha).name
            self.excel_handler = ExcelHandler(arquivo_entrada)
            self.excel_handler.caminho_entrada = Path(caminho_planilha)
        else:
            self.excel_handler = ExcelHandler()
        
        self.automator = CorreiosAutomator()
        self.report_generator = ReportGenerator()
        
        self.resultados_sucesso = []
        self.resultados_erro = []
        self.dados_invalidos = []
    
    def executar(self):
        """Executa o processo completo de automação"""
        try:
            print("\n" + "="*80)
            print(f"AUTOMATIZADOR DE {self.tipo_processo.upper()} - CORREIOS EMPRESA")
            print("="*80 + "\n")
            
            # 1. Ler dados da planilha
            logger.info("=" * 50)
            logger.info("ETAPA 1: Leitura de dados da planilha")
            logger.info("=" * 50)
            
            try:
                dados = self.excel_handler.ler_dados_postagem()
                print(f"✓ {len(dados)} registros carregados da planilha")
            except FileNotFoundError:
                print("\n⚠ Arquivo de entrada não encontrado!")
                print("Criando template de exemplo...\n")
                self.excel_handler.criar_planilha_template(self.tipo_processo)
                print(f"✓ Template criado em: {config.DADOS_DIR / f'template_{self.tipo_processo}.xlsx'}")
                print("\nPreencha o template e execute novamente.")
                return
            
            # 2. Valida dados
            logger.info("\n" + "=" * 50)
            logger.info("ETAPA 2: Validação de dados")
            logger.info("=" * 50)
            
            dados_validos, self.dados_invalidos = self.excel_handler.validar_dados(dados)
            print(f"✓ Dados válidos: {len(dados_validos)}")
            if self.dados_invalidos:
                print(f"⚠ Dados inválidos: {len(self.dados_invalidos)} (não serão processados)")
            
            if not dados_validos:
                print("\n✗ Nenhum dado válido para processar!")
                self._gerar_relatorios()
                return
            
            # Aprendi da pior forma que é melhor pedir confirmação antes de processar 100 registros
            print(f"\nSerão processados {len(dados_validos)} registros.")
            resposta = input("Deseja continuar? (S/N): ").strip().upper()
            
            if resposta != 'S':
                print("Operação cancelada pelo usuário.")
                return
            
            # 4. Inicia navegador e faz login
            logger.info("\n" + "=" * 50)
            logger.info("ETAPA 3: Inicialização e Login Manual")
            logger.info("=" * 50)
            
            print("\n🌐 Abrindo navegador Chrome...")
            self.automator.iniciar_navegador()
            time.sleep(1)
            
            print("🔓 Abrindo sistema de pré-postagem (vai pedir login)...\n")
            if not self.automator.fazer_login(usuario=self.usuario, senha=self.senha):
                print("\n✗ Processo de login cancelado.")
                logger.error("Processo de login cancelado")
                return
            
            print("="*80)
            print("✓ Sistema logado e pronto! Iniciando processamento automático...")
            print("="*80 + "\n")
            time.sleep(1)
            
            # 5. Processar cada registro
            logger.info("\n" + "=" * 50)
            logger.info(f"ETAPA 4: Processamento de {self.tipo_processo}")
            logger.info("=" * 50)
            
            print(f"\nIniciando processamento automático de {len(dados_validos)} registros...\n")
            
            for idx, registro in enumerate(dados_validos, 1):
                print(f"\n{'='*80}")
                print(f"[{idx}/{len(dados_validos)}] PROCESSANDO LINHA {registro.get('_linha')} - {registro.get('COORDENADOR MUNICIPAL', 'N/A')}")
                print(f"{'='*80}\n")
                
                try:
                    if self.tipo_processo == "postagem":
                        resultado = self.automator.processar_postagem(registro)
                    else:  # coleta
                        resultado = self.automator.processar_coleta(registro)
                    
                    if resultado.get('status') == 'sucesso':
                        self.resultados_sucesso.append(resultado)
                        codigo = resultado.get('codigo_rastreamento', 'N/A')
                        print(f"\n✓ SUCESSO - Código: {codigo}\n")
                    else:
                        self.resultados_erro.append(resultado)
                        erro = resultado.get('erro', 'Erro desconhecido')
                        print(f"\n✗ ERRO - {erro}\n")
                    
                    # Pausa entre registros pq já vi o sites derrubar a sessão por requisições muito rápidas
                    if idx < len(dados_validos):
                        print("\n" + "-"*80)
                        print(f"Próximo: Linha {dados_validos[idx].get('_linha')} - {dados_validos[idx].get('COORDENADOR MUNICIPAL', 'N/A')}")
                        print("-"*80)
                        resposta = input("\nContinuar para o próximo registro? (S/N ou ENTER para continuar): ").strip().upper()
                        if resposta == 'N':
                            print("\n⚠️ Processamento interrompido pelo usuário.")
                            logger.info("Usuário optou por interromper o processamento")
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Erro inesperado no registro {registro.get('_linha')}: {str(e)}")
                    self.resultados_erro.append({
                        'linha': registro.get('_linha'),
                        'destinatario': registro.get('COORDENADOR MUNICIPAL', 'N/A'),
                        'erro': f"Erro inesperado: {str(e)}",
                        'status': 'erro'
                    })
                    print(f"\n✗ ERRO INESPERADO: {str(e)}\n")
                    
                    # Print salvou minha vida várias vezes quando o sistema falha em produção
                    self.automator.tirar_screenshot(f"erro_linha_{registro.get('_linha')}.png")
            
            print("\n✓ Processamento concluído!")
            
        except KeyboardInterrupt:
            print("\n\n⚠ Interrompido pelo usuário")
            logger.warning("Processamento interrompido pelo usuário")
            
        except Exception as e:
            logger.error(f"Erro crítico: {str(e)}", exc_info=True)
            print(f"\n✗ Erro crítico: {str(e)}")
            
        finally:
            logger.info("\n" + "=" * 50)
            logger.info("ETAPA 5: Finalização")
            logger.info("=" * 50)
            
            print("\nFechando navegador...")
            self.automator.fechar_navegador()
            
            self._gerar_relatorios()
    
    def _gerar_relatorios(self):
        """Gera os relatórios finais"""
        logger.info("\n" + "=" * 50)
        logger.info("ETAPA 6: Geração de Relatórios")
        logger.info("=" * 50)
        
        print("\nGerando relatórios...")
        
        try:
            self.report_generator.exibir_resumo_console(
                self.resultados_sucesso,
                self.resultados_erro,
                self.dados_invalidos
            )
            
            arquivo_excel = self.report_generator.gerar_relatorio_completo(
                self.resultados_sucesso,
                self.resultados_erro,
                self.dados_invalidos
            )
            print(f"✓ Relatório Excel: {arquivo_excel}")
            
            arquivo_txt = self.report_generator.gerar_relatorio_texto(
                self.resultados_sucesso,
                self.resultados_erro,
                self.dados_invalidos
            )
            print(f"✓ Relatório TXT: {arquivo_txt}")
            
            print("\n✓ Relatórios gerados com sucesso!")
            print(f"   Localização: {config.RELATORIOS_DIR}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatórios: {str(e)}")
            print(f"✗ Erro ao gerar relatórios: {str(e)}")


def solicitar_caminho_planilha():
    """Solicita o caminho da planilha"""
    print("\n" + "="*80)
    print("CAMINHO DA PLANILHA")
    print("="*80)
    print("\nForneça o caminho completo da planilha Excel:")
    print("Exemplo: C:\\planilhas\\dados_postagem.xlsx")
    print("\nOu pressione ENTER para usar o padrão: dados/dados_postagem.xlsx\n")
    
    caminho = input("Caminho da planilha: ").strip()
    
    if not caminho:
        caminho_padrao = config.DADOS_DIR / config.ARQUIVO_ENTRADA
        print(f"\nUsando caminho padrão: {caminho_padrao}")
        return str(caminho_padrao)
    
    # Windows adora adicionar aspas quando você arrasta arquivos pro terminal
    caminho = caminho.strip('"').strip("'")
    
    caminho_path = Path(caminho)
    if not caminho_path.exists():
        print(f"\n⚠ Arquivo não encontrado: {caminho}")
        resposta = input("Deseja continuar mesmo assim? (S/N): ").strip().upper()
        if resposta != 'S':
            return None
    
    print(f"\n✓ Caminho da planilha: {caminho}")
    return caminho


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("AUTOMATIZADOR DE CORREIOS - SISTEMA DE POSTAGEM E COLETA")
    print("="*80)
    
    print("\nSelecione o tipo de processo:")
    print("1 - Postagem de objetos")
    print("2 - Solicitação de coleta")
    print("0 - Sair")
    
    opcao = input("\nOpção: ").strip()
    
    if opcao == "0":
        print("Saindo...")
        return
    elif opcao not in ["1", "2"]:
        print("Opção inválida!")
        return
    
    tipo_processo = "postagem" if opcao == "1" else "coleta"
    
    caminho_planilha = solicitar_caminho_planilha()
    if not caminho_planilha:
        print("\n✗ Caminho da planilha inválido. Encerrando...")
        return
    
    # Essas instruções são necessárias pq sempre tem um usuário abençoado navegando pro lugar errado após o login
    print("\n" + "="*80)
    print("PRONTO PARA INICIAR")
    print("="*80)
    print(f"\nTipo: {tipo_processo.upper()}")
    print(f"Planilha: {caminho_planilha}")
    print("\n➤ Ao pressionar ENTER:")
    print("   1. O navegador Chrome será aberto na página de pré-postagem")
    print("   2. O site vai pedir login - faça login normalmente")
    print("   3. Após login, fique na página de pré-postagem e pressione ENTER")
    print("   4. A automação processará os registros da planilha")
    print("\n💡 NÃO navegue para outras páginas após fazer login!")
    print("\nPressione ENTER para abrir o navegador...")
    input()
    
    # Login manual porque a autenticação dos Correios mudou e quebrou meu sistema de login automático
    automatizador = AutomatizadorCorreios(
        tipo_processo=tipo_processo,
        usuario="manual",
        senha="manual",
        caminho_planilha=caminho_planilha
    )
    automatizador.executar()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}", exc_info=True)
        print(f"\n✗ Erro fatal: {str(e)}")
        input("\nPressione Enter para sair...")
