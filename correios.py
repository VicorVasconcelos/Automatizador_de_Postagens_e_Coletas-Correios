"""
Módulo de automação do portal Correios Empresa

A parte mais complicada de todo o sistema. O site dos Correios muda sem avisar,
então tem que ter seletores múltiplos pra cada elemento e bastante screenshot pra debugar.
"""
import logging
import time
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import config

logger = logging.getLogger(__name__)


class CorreiosAutomator:
    
    def __init__(self, headless: bool = None):
        """Inicializa o automatizador"""
        self.headless = headless if headless is not None else config.HEADLESS_MODE
        self.driver = None
        self.wait = None
        self.logado = False
        
    def iniciar_navegador(self):
        """Inicializa o navegador Chrome"""
        try:
            logger.info("Inicializando navegador...")
            
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Essas flags são necessárias pra evitar que o site detecte que é automação
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Desabilita TODOS os popups: senha, notificações, avisos de segurança, etc
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "autofill.profile_enabled": False,
                # Desabilita avisos de senha comprometida
                "profile.password_manager_leak_detection": False,
                "password_manager_enabled": False,
                # Desabilita popups de atualização e avisos
                "download.prompt_for_download": False,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Argumentos adicionais para desabilitar popups e notificações
            chrome_options.add_argument("--disable-save-password-bubble")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-extensions")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, config.TEMPO_ESPERA_ELEMENTO)
            
            logger.info("Navegador iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar navegador: {str(e)}")
            raise
    
    def fechar_navegador(self):
        """Fecha o navegador"""
        if self.driver:
            logger.info("Fechando navegador...")
            self.driver.quit()
            self.driver = None
            self.logado = False
    
    def aguardar_elemento(self, by: By, valor: str, timeout: int = None, descricao: str = "") -> object:
        """Aguarda um elemento aparecer na página com mensagem de debug"""
        timeout = timeout or config.TEMPO_ESPERA_ELEMENTO
        msg = f"elemento '{descricao}'" if descricao else f"elemento '{valor}'"
        
        try:
            logger.info(f"Aguardando {msg}...")
            elemento = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, valor))
            )
            logger.info(f"✓ {msg.capitalize()} encontrado")
            return elemento
        except TimeoutException:
            logger.error(f"✗ Timeout ao aguardar {msg}")
            self.tirar_screenshot(f"erro_timeout_{descricao or 'elemento'}.png")
            raise Exception(f"Elemento não encontrado: {msg}")
    
    def fazer_login(self, usuario: str = None, senha: str = None, cartao: str = None) -> bool:
        """
        Abre a página de pré-postagem (que redireciona para login) e aguarda o usuário fazer login manualmente
        
        IMPORTANTE: Mudei pra abrir direto em prepostagem.correios.com.br porque tava perdendo
        a sessão quando navegava de empresas.correios.com.br pra lá - problema de cookie entre domínios
        """
        try:
            logger.info("Acessando sistema de pré-postagem dos Correios...")
            self.driver.get(config.CORREIOS_PRE_POSTAGEM_URL)
            time.sleep(3)
            
            self.driver.maximize_window()
            
            # Mensagem pro usuário - tem que ser bem clara porque sempre tem alguém que não entende
            print("\n" + "="*80)
            print("🔐 FAÇA SEU LOGIN AGORA NO NAVEGADOR")
            print("="*80)
            print("\n➤ O Chrome foi aberto no sistema de PRÉ-POSTAGEM dos Correios.")
            print("➤ Se aparecer tela de login, digite seu USUÁRIO e SENHA.")
            print("➤ Complete qualquer verificação necessária (CAPTCHA, 2FA, etc).")
            print("➤ Aguarde até estar logado e ver a página de pré-postagem.")
            print("\n💡 IMPORTANTE: NÃO navegue para outras páginas!")
            print("   Fique na página de pré-postagem após fazer login.")
            print("\n" + "="*80)
            print("⏸️  Quando estiver LOGADO e na tela de pré-postagem, pressione ENTER...")
            print("="*80 + "\n")
            
            input()
            
            logger.info("Usuário confirmou login manual - continuando automação")
            print("✓ Login confirmado! Iniciando processamento...\n")
            
            # Pausa maior aqui porque o site às vezes demora pra carregar depois do login
            logger.info("Aguardando página estabilizar...")
            time.sleep(5)
            
            self.logado = True
            return True
                
        except Exception as e:
            logger.error(f"Erro durante processo de login: {str(e)}")
            print(f"\n✗ Erro: {str(e)}")
            return False
    
    def _verificar_campo_preenchido(self, seletores: list) -> bool:
        """
        Verifica se um campo já está preenchido (útil após preenchimento automático do CEP)
        Retorna True se o campo tem valor, False caso contrário
        """
        for by, selector in seletores:
            try:
                campo = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((by, selector))
                )
                valor = campo.get_attribute('value') or ''
                if valor.strip():
                    return True
            except:
                continue
        return False
    
    def _tentar_preencher_campo(self, label: str, valor: str, seletores: list) -> bool:
        """
        Tenta preencher um campo usando múltiplos seletores
        
        Essa abordagem de múltiplos seletores foi necessária porque o site muda sem avisar.
        Quando um seletor para de funcionar, o próximo da lista tenta.
        """
        if not valor or str(valor).strip() in['', 'nan', 'None', 'N/A']:
            logger.info(f"Campo '{label}' sem valor, pulando...")
            return True
            
        logger.info(f"Preenchendo campo '{label}' com valor: {valor}")
        
        for idx, (by, selector) in enumerate(seletores, 1):
            try:
                # Timeout reduzido para 5 segundos (suficiente para modal já aberto)
                campo = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                
                # Aguarda o campo estar visível e interativo
                WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )

                self.driver.execute_script("arguments[0].scrollIntoView(true);", campo)
                time.sleep(0.1)
                
                # Tenta clicar no campo primeiro para garantir foco
                try:
                    campo.click()
                except:
                    self.driver.execute_script("arguments[0].click();", campo)
                
                time.sleep(0.1)
                
                campo.clear()
                time.sleep(0.1)
                campo.send_keys(str(valor))
                
                logger.info(f"✓ Campo '{label}' preenchido com sucesso (tentativa {idx})")
                return True
                
            except Exception as e:
                logger.debug(f"Tentativa {idx} falhou para '{label}': {str(e)[:80]}")
                continue
        
        logger.warning(f"⚠ Não foi possível preencher campo '{label}'")
        self.tirar_screenshot(f"erro_campo_{label.replace('/', '_')}.png")
        return False
    
    def _preencher_campo_destinatario(self, dados: Dict):
        """
        Preenche todos os campos do formulário de destinatário
        
        Esse mapeamento é crítico: COORDENADOR MUNICIPAL da planilha vira "Destinatário" no site,
        NÚMERO vira "Número", UF.1 vira "Estado", etc.
        
        Cada campo tem 5-7 seletores diferentes porque o HTML do site dos Correios não segue padrão.
        
        IMPORTANTE: Os seletores agora priorizam campos dentro de modal/popup para evitar conflitos
        """
        
        seletores_nome = [
            # ID exato do site
            (By.ID, "nomeDestinatario"),
            (By.NAME, "nomeDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='nomeDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='nomeDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='nomeDestinatario']"),
        ]
        logger.info(f"Preenchendo Destinatário com: {dados.get('COORDENADOR MUNICIPAL')}")
        self._tentar_preencher_campo("Destinatário/Nome", dados.get('COORDENADOR MUNICIPAL'), seletores_nome)
        time.sleep(0.3)
        
        seletores_cpf = [
            # ID exato do site
            (By.ID, "cpfCnpjDestinatario"),
            (By.NAME, "cpfCnpjDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='cpfCnpjDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='cpfCnpjDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='cpfCnpjDestinatario']"),
        ]
        logger.info(f"Preenchendo CPF com: {dados.get('CPF')}")
        self._tentar_preencher_campo("CPF", dados.get('CPF'), seletores_cpf)
        time.sleep(0.3)
        
        seletores_cep = [
            # ID exato do site - IMPORTANTE: é type="number"
            (By.ID, "cepDestinatario"),
            (By.NAME, "cepDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='cepDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='cepDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='cepDestinatario']"),
        ]
        cep = str(dados.get('CEP', '')).replace('-', '').replace('.', '').strip()
        logger.info(f"Preenchendo CEP com: {cep}")
        if self._tentar_preencher_campo("CEP", cep, seletores_cep):
            # Delay de 3s aqui porque o site faz busca automática do CEP e preenche endereço/bairro/cidade
            logger.info("Aguardando busca automática de CEP (3s)...")
            time.sleep(3)
        
        # Endereço/Logradouro (Planilha: LOGRADOURO)
        seletores_endereco = [
            # ID exato do site
            (By.ID, "logradouroDestinatario"),
            (By.NAME, "logradouroDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='logradouroDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='logradouroDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='logradouroDestinatario']"),
        ]
        
        # Verifica se o campo de endereço foi preenchido automaticamente
        endereco_preenchido_auto = self._verificar_campo_preenchido(seletores_endereco)
        if endereco_preenchido_auto:
            logger.info("✓ Endereço foi preenchido automaticamente pelo CEP")
        else:
            logger.info(f"Preenchendo Endereço com: {dados.get('LOGRADOURO')}")
            self._tentar_preencher_campo("Endereço", dados.get('LOGRADOURO'), seletores_endereco)
        time.sleep(0.3)
        
        seletores_numero = [
            # ID exato do site
            (By.ID, "numeroDestinatario"),
            (By.NAME, "numeroDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='numeroDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='numeroDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='numeroDestinatario']"),
        ]
        numero = str(dados.get('NÚMERO', '')).strip().upper()
        if numero in ['S/Nº', 'S/N', 'SN', '']:
            numero = 'S/N'
        logger.info(f"Preenchendo Número com: {numero}")
        self._tentar_preencher_campo("Número", numero, seletores_numero)
        time.sleep(0.3)
        
        seletores_complemento = [
            # ID exato do site
            (By.ID, "complementoDestinatario"),
            (By.NAME, "complementoDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='complementoDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='complementoDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='complementoDestinatario']"),
        ]
        if dados.get('COMPLEMENTO'):
            logger.info(f"Preenchendo Complemento com: {dados.get('COMPLEMENTO')}")
        self._tentar_preencher_campo("Complemento", dados.get('COMPLEMENTO'), seletores_complemento)
        time.sleep(0.3)
        
        seletores_bairro = [
            # ID exato do site
            (By.ID, "bairroDestinatario"),
            (By.NAME, "bairroDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='bairroDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='bairroDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='bairroDestinatario']"),
        ]
        
        # Verifica se o campo de bairro foi preenchido automaticamente
        bairro_preenchido_auto = self._verificar_campo_preenchido(seletores_bairro)
        if bairro_preenchido_auto:
            logger.info("✓ Bairro foi preenchido automaticamente pelo CEP")
        else:
            logger.info(f"Preenchendo Bairro com: {dados.get('BAIRRO')}")
            self._tentar_preencher_campo("Bairro", dados.get('BAIRRO'), seletores_bairro)
        time.sleep(0.3)
        
        seletores_cidade = [
            # ID exato do site - IMPORTANTE: disabled="true" por padrão!
            (By.ID, "cidadeDestinatario"),
            (By.NAME, "cidadeDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='cidadeDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='cidadeDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='cidadeDestinatario']"),
        ]
        
        # Verifica se o campo de cidade foi preenchido automaticamente
        cidade_preenchido_auto = self._verificar_campo_preenchido(seletores_cidade)
        if cidade_preenchido_auto:
            logger.info("✓ Cidade foi preenchida automaticamente pelo CEP")
        else:
            # Cidade - Está DISABLED - precisa habilitar com JavaScript
            if dados.get('CIDADE'):
                logger.info(f"Preenchendo Cidade com: {dados.get('CIDADE')}")
                # Tenta habilitar o campo primeiro (ele está disabled no HTML)
                try:
                    campo_cidade = self.driver.find_element(By.ID, "cidadeDestinatario")
                    self.driver.execute_script("arguments[0].removeAttribute('disabled')", campo_cidade)
                    time.sleep(0.3)
                except:
                    logger.debug("Não foi possível remover disabled do campo Cidade")
            
            self._tentar_preencher_campo("Cidade", dados.get('CIDADE'), seletores_cidade)
        time.sleep(0.3)
        
        seletores_estado = [
            # ID exato do site - IMPORTANTE: disabled="true" e é INPUT, não SELECT!
            (By.ID, "ufDestinatario"),
            (By.NAME, "ufDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='ufDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='ufDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='ufDestinatario']"),
        ]
        
        # Verifica se o campo de UF foi preenchido automaticamente
        uf_preenchido_auto = self._verificar_campo_preenchido(seletores_estado)
        if uf_preenchido_auto:
            logger.info("✓ UF foi preenchida automaticamente pelo CEP")
        else:
            # Estado - É INPUT (não SELECT) e está DISABLED - precisa habilitar com JavaScript
            estado = str(dados.get('UF.1', '')).strip().upper()
            if estado:
                logger.info(f"Preenchendo Estado/UF com: {estado}")
                # Tenta habilitar o campo primeiro (ele está disabled no HTML)
                try:
                    campo_uf = self.driver.find_element(By.ID, "ufDestinatario")
                    self.driver.execute_script("arguments[0].removeAttribute('disabled')", campo_uf)
                    time.sleep(0.3)
                except:
                    logger.debug("Não foi possível remover disabled do campo UF")
                
                # Agora tenta preencher
                self._tentar_preencher_campo("UF", estado, seletores_estado)
        time.sleep(0.3)
        
        # Telefone (Planilha: TELEFONE) - ID é telefoneDes (não telefoneDestinatario!)
        seletores_telefone = [
            # ID exato do site - type="tel"
            (By.ID, "telefoneDes"),
            (By.NAME, "telefoneDes"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='telefoneDes']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='telefoneDes']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='telefoneDes']"),
        ]
        logger.info(f"Preenchendo Telefone com: {dados.get('TELEFONE')}")
        self._tentar_preencher_campo("Telefone", dados.get('TELEFONE'), seletores_telefone)
        time.sleep(0.3)
        
        seletores_email = [
            # ID exato do site - type="email"
            (By.ID, "emailDestinatario"),
            (By.NAME, "emailDestinatario"),
            # Dentro do modal
            (By.XPATH, "//div[@id='cadastroDestinatario']//input[@id='emailDestinatario']"),
            (By.XPATH, "//form[@id='formDestinatario']//input[@id='emailDestinatario']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='emailDestinatario']"),
        ]
        logger.info(f"Preenchendo Email com: {dados.get('EMAIL')}")
        self._tentar_preencher_campo("Email", dados.get('EMAIL'), seletores_email)
    
    def _salvar_destinatario_modal(self):
        """
        Clica no botão Salvar dentro do modal de destinatário
        
        A parte crítica aqui: depois de preencher os campos no modal popup,
        precisa salvar e fechar o modal antes de confirmar a pré-postagem.
        """
        
        logger.info("Procurando botão 'Salvar' dentro do modal...")
        
        # 13 seletores diferentes porque botão de salvar de modal é caótico em HTML
        seletores_salvar = [
            # Botão "Salvar" - várias variações
            (By.XPATH, "//button[contains(text(), 'Salvar')]"),
            (By.XPATH, "//button[normalize-space()='Salvar']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//button[contains(text(), 'Salvar')]"),
            (By.XPATH, "//div[contains(@class, 'popup')]//button[contains(text(), 'Salvar')]"),
            # ID comum para botões Salvar
            (By.ID, "btnSalvar"),
            (By.ID, "btn-salvar"),
            (By.ID, "salvar"),
            # Classes comuns
            (By.CSS_SELECTOR, "button.btn-salvar"),
            (By.CSS_SELECTOR, "button.salvar"),
            (By.CSS_SELECTOR, ".modal button[type='submit']"),
            (By.CSS_SELECTOR, ".popup button[type='submit']"),
            # Botão submit dentro de modal
            (By.XPATH, "//div[contains(@class, 'modal')]//button[@type='submit']"),
            (By.XPATH, "//div[contains(@class, 'popup')]//button[@type='submit']"),
        ]
        
        botao_encontrado = False
        for idx, (by, selector) in enumerate(seletores_salvar, 1):
            try:
                logger.debug(f"Tentativa {idx}: Procurando 'Salvar' com {by}...")
                botao = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", botao)
                time.sleep(0.5)
                
                try:
                    botao.click()
                except:
                    self.driver.execute_script("arguments[0].click();", botao)
                
                logger.info(f"✓ Botão 'Salvar' clicado com sucesso (tentativa {idx})")
                botao_encontrado = True
                time.sleep(2)
                break
            except:
                continue
        
        if not botao_encontrado:
            self.tirar_screenshot("erro_botao_salvar_modal.png")
            logger.error("Botão 'Salvar' não encontrado - solicitando ajuda manual")
            print("\n" + "="*80)
            print("⚠️  AÇÃO MANUAL NECESSÁRIA")
            print("="*80)
            print("\n➤ Não foi possível clicar no botão 'Salvar' automaticamente.")
            print("➤ Por favor, CLIQUE no botão SALVAR no popup/modal.")
            print("➤ Aguarde o modal fechar e volte aqui.")
            print("\n⏸️  Pressione ENTER após salvar e o modal fechar...")
            print("="*80 + "\n")
            input()
            time.sleep(2)
    
    def _confirmar_postagem(self, dados: Dict):
        """
        Confirma a postagem e captura o código de rastreamento
        
        Esse método busca o botão Confirmar/Finalizar na tela principal
        (diferente do Salvar que é dentro do modal)
        """
        
        logger.info("Procurando botão de confirmação...")
        
        seletores_confirmar = [
            (By.XPATH, "//button[contains(text(), 'Confirmar')]"),
            (By.XPATH, "//button[contains(text(), 'Finalizar')]"),
            (By.XPATH, "//button[contains(text(), 'Salvar')]"),
            (By.XPATH, "//button[contains(text(), 'Enviar')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button.btn-primary"),
            (By.CSS_SELECTOR, "button.confirmar"),
            (By.CSS_SELECTOR, "button[type='submit']"),
        ]
        
        botao_encontrado = False
        for by, selector in seletores_confirmar:
            try:
                botao = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", botao)
                time.sleep(0.5)
                
                try:
                    botao.click()
                except:
                    self.driver.execute_script("arguments[0].click();", botao)
                
                logger.info("✓ Botão de confirmação clicado")
                botao_encontrado = True
                break
            except:
                continue
        
        if not botao_encontrado:
            self.tirar_screenshot("erro_botao_confirmar.png")
            logger.error("Botão confirmar não encontrado - solicitando ajuda manual")
            print("\n" + "="*80)
            print("⚠️  AÇÃO MANUAL NECESSÁRIA")
            print("="*80)
            print("\n➤ Não foi possível clicar no botão de confirmação automaticamente")
            print("➤ Por favor, CLIQUE no botão CONFIRMAR/FINALIZAR no navegador.")
            print("➤ Após clicar e ver a tela de sucesso, volte aqui.")
            print("\n⏸️  Pressione ENTER após confirmar e ver tela de sucesso...")
            print("="*80 + "\n")
            input()
        
        # Aguarda uns segundos pro site processar
        logger.info("Aguardando processamento...")
        time.sleep(5)
        
        self.tirar_screenshot(f"sucesso_linha_{dados.get('_linha')}.png")
    
    def processar_postagem(self, dados: Dict) -> Dict:
        """
        Processa uma postagem seguindo o fluxo do sistema Correios
        
        FLUXO COMPLETO:
        1. Navegar pra pré-postagem
        2. Clicar em "Pré-postagem a faturar de objetos registrados"
        3. Clicar em "Nova pré-postagem"
        4. Selecionar remetente "CEBRASPE"
        5. Clicar em "Novo Destinatário" (abre modal)
        6. Preencher formulário dentro do modal
        7. Clicar em "Salvar" (fecha modal)
        8. Confirmar pré-postagem na tela principal
        9. Capturar código de rastreamento
        
        Os seletores (By.NAME, By.XPATH, etc) foram descobertos na base da tentativa e erro
        com F12 no Chrome. Sempre que o site muda, precisa voltar aqui e ajustar.
        """
        codigo_rastreamento = None
        
        try:
            logger.info(f"Processando postagem linha {dados.get('_linha', 'N/A')}")
            logger.info(f"Destinatário: {dados.get('COORDENADOR MUNICIPAL', 'N/A')}")
            
            if not self.logado:
                raise Exception("Não está logado no sistema")
            
            # PASSO 1: Garantir que tá na página certa
            logger.info("Passo 1: Verificando se está na página de pré-postagem...")
            url_atual = self.driver.current_url
            logger.info(f"URL atual: {url_atual}")
            
            if "prepostagem.correios.com.br" not in url_atual:
                logger.info("Não está na pré-postagem, navegando...")
                self.driver.get(config.CORREIOS_PRE_POSTAGEM_URL)
                time.sleep(3)
            else:
                logger.info("Já está na página de pré-postagem")
                # Volta pra página inicial da pré-postagem pra garantir que tá tudo limpo
                self.driver.get(config.CORREIOS_PRE_POSTAGEM_URL)
                time.sleep(3)
            
            # Aguarda página carregar completamente
            logger.info("Aguardando página carregar completamente...")
            time.sleep(2)
            
            self.tirar_screenshot("passo1_pagina_inicial.png")
            
            # PASSO 2: Clica em "Pré-postagem a faturar de objetos registrados"
            logger.info("Passo 2: Procurando link 'Pré-postagem a faturar de objetos registrados'...")
            
            self.tirar_screenshot("passo2_antes_clicar.png")
            
            # 10 seletores pra esse botão porque ele muda de lugar/classe dependendo do layout
            seletores_registrados = [
                # Texto completo ou parcial no link
                (By.XPATH, "//a[contains(text(), 'objetos registrados')]"),
                (By.XPATH, "//a[contains(text(), 'Pré-postagem a faturar')]"),
                (By.XPATH, "//a[contains(., 'registrados')]"),
                # Por href
                (By.XPATH, "//a[contains(@href, 'registrados')]"),
                (By.XPATH, "//a[contains(@href, 'faturar')]"),
                # Div ou span clicável
                (By.XPATH, "//div[contains(text(), 'objetos registrados')]"),
                (By.XPATH, "//span[contains(text(), 'objetos registrados')]"),
                # Botão
                (By.XPATH, "//button[contains(text(), 'objetos registrados')]"),
                # Classe ou ID
                (By.CSS_SELECTOR, "[class*='registrados']"),
                (By.CSS_SELECTOR, "[id*='registrados']"),
            ]
            
            elemento_encontrado = False
            for idx, (by, selector) in enumerate(seletores_registrados, 1):
                try:
                    logger.info(f"Tentativa {idx}: Procurando elemento com {by}...")
                    elemento = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                    time.sleep(1)
                    
                    try:
                        elemento.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", elemento)
                    
                    logger.info(f"✓ Clique realizado com sucesso usando tentativa {idx}")
                    elemento_encontrado = True
                    time.sleep(3)
                    break
                    
                except Exception as e:
                    logger.debug(f"Tentativa {idx} falhou: {str(e)[:100]}")
                    continue
            
            if not elemento_encontrado:
                # Última cartada: navegação direta pela URL
                logger.warning("Nenhum seletor funcionou. Tentando navegação direta...")
                self.driver.get("https://prepostagem.correios.com.br/prepostagem/painels/faturar/registrados")
                time.sleep(3)
                self.tirar_screenshot("passo2_navegacao_direta.png")
                logger.info("Navegação direta realizada")
                
                # Verifica se deu certo
                if "registrados" not in self.driver.current_url.lower():
                    # Só pede ajuda manual se realmente não conseguiu
                    print("\n" + "="*80)
                    print("⚠️  AÇÃO MANUAL NECESSÁRIA")
                    print("="*80)
                    print("\n➤ O sistema não conseguiu clicar automaticamente em:")
                    print("   'Pré-postagem a faturar de objetos registrados'")
                    print("\n➤ Por favor, CLIQUE MANUALMENTE nessa opção no navegador.")
                    print("➤ Após clicar e a página carregar, volte aqui.")
                    print("\n⏸️  Pressione ENTER quando estiver na tela de objetos registrados...")
                    print("="*80 + "\n")
                    input()
                    time.sleep(2)
            
            # PASSO 3: Botão "Nova pré postagem"
            logger.info("Passo 3: Procurando botão 'Nova pré-postagem'...")
            
            self.tirar_screenshot("passo3_antes_clicar.png")
            
            seletores_nova_postagem = [
                # Texto no botão
                (By.XPATH, "//button[contains(text(), 'Nova pré-postagem')]"),
                (By.XPATH, "//button[contains(., 'Nova')]"),
                (By.XPATH, "//a[contains(text(), 'Nova pré-postagem')]"),
                (By.XPATH, "//a[contains(., 'Nova')]"),
                # Span ou div dentro de botão
                (By.XPATH, "//button//span[contains(text(), 'Nova')]"),
                (By.XPATH, "//button//div[contains(text(), 'Nova')]"),
                # Classes comuns
                (By.CSS_SELECTOR, "button[class*='nova']"),
                (By.CSS_SELECTOR, "button[class*='novo']"),
                (By.CSS_SELECTOR, "a[class*='nova']"),
                (By.CSS_SELECTOR, "[class*='btn-nova']"),
                # Ícone de adicionar/plus
                (By.XPATH, "//button[contains(@class, 'add') or contains(@class, 'plus')]"),
                (By.XPATH, "//button[@title='Nova pré-postagem' or @aria-label='Nova pré-postagem']"),
            ]
            
            botao_encontrado = False
            for idx, (by, selector) in enumerate(seletores_nova_postagem, 1):
                try:
                    logger.info(f"Tentativa {idx}: Procurando botão com {by}...")
                    botao = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", botao)
                    time.sleep(0.3)
                    
                    try:
                        botao.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", botao)
                    
                    logger.info(f"✓ Clique no botão realizado com sucesso usando tentativa {idx}")
                    botao_encontrado = True
                    time.sleep(1)
                    break
                    
                except Exception as e:
                    logger.debug(f"Tentativa {idx} falhou: {str(e)[:100]}")
                    continue
            
            if not botao_encontrado:
                logger.error("Botão 'Nova pré postagem' não encontrado")
                self.tirar_screenshot("erro_passo3_botao_nova_postagem.png")
                
                print("\n" + "="*80)
                print("⚠️  AÇÃO MANUAL NECESSÁRIA")
                print("="*80)
                print("\n➤ O sistema não conseguiu clicar automaticamente em:")
                print("   Botão 'Nova pré-postagem'")
                print("\n➤ Por favor, CLIQUE MANUALMENTE nesse botão no navegador.")
                print("➤ Após clicar e o formulário abrir, volte aqui.")
                print("\n⏸️  Pressione ENTER quando o formulário de nova pré-postagem abrir...")
                print("="*80 + "\n")
                input()
                time.sleep(2)
            
            # PASSO 4: Verifica se remetente já está preenchido, senão preenche com "Cebraspe"
            logger.info("Passo 4: Verificando remetente...")
            
            # Aguarda a página carregar um pouco
            time.sleep(1)
            
            # Verifica se o remetente já está preenchido/selecionado
            remetente_ja_preenchido = False
            try:
                # Tenta encontrar "Cebraspe" ou "CEBRASPE" já exibido na página como remetente
                seletores_verificacao = [
                    # Texto "Cebraspe" próximo ao label "Remetente:"
                    (By.XPATH, "//*[contains(text(), 'Cebraspe') and not(self::button) and not(self::a) and not(self::input)]"),
                    (By.XPATH, "//*[contains(text(), 'CEBRASPE') and not(self::button) and not(self::a) and not(self::input)]"),
                    # Dentro de divs ou spans com classe relacionada
                    (By.XPATH, "//div[contains(text(), 'Cebraspe')]"),
                    (By.XPATH, "//span[contains(text(), 'Cebraspe')]"),
                    (By.XPATH, "//p[contains(text(), 'Cebraspe')]"),
                    # CPF específico do Cebraspe (18.284.407/0001-53)
                    (By.XPATH, "//*[contains(text(), '18.284.407')]"),
                    (By.XPATH, "//*[contains(text(), '18284407')]"),
                ]
                
                for by, selector in seletores_verificacao:
                    try:
                        elemento = self.driver.find_element(by, selector)
                        if elemento and elemento.is_displayed():
                            texto = elemento.text.strip()
                            if texto and ('cebraspe' in texto.lower() or '18.284.407' in texto or '18284407' in texto):
                                remetente_ja_preenchido = True
                                logger.info(f"✓ Remetente CEBRASPE já está preenchido automaticamente (detectado: '{texto[:50]}')")
                                break
                    except:
                        continue
            except:
                pass
            
            # Se não estiver preenchido, preenche manualmente
            if not remetente_ja_preenchido:
                logger.info("Preenchendo remetente 'Cebraspe'...")
                try:
                    campo_remetente = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Busca de objetos pré-postados pelo código do objeto' or contains(@name, 'remetente') or @id='remetente']"))
                    )
                    campo_remetente.clear()
                    campo_remetente.send_keys("Cebraspe")
                    time.sleep(1)
                    
                    botao_lupa = self.driver.find_element(By.XPATH, "//button[@type='submit' or contains(@class, 'busca') or contains(., 'Buscar')]")
                    botao_lupa.click()
                    time.sleep(2)
                    
                    opcao_cebraspe = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//td[text()='CEBRASPE' or text()='Cebraspe']//parent::tr | //div[contains(text(), 'CEBRASPE')]"))
                    )
                    opcao_cebraspe.click()
                    time.sleep(2)
                    logger.info("✓ Remetente 'Cebraspe' selecionado com sucesso")
                except Exception as e:
                    logger.warning(f"Não foi possível selecionar remetente automaticamente: {str(e)}")
                    self.tirar_screenshot("passo4_erro_selecionar_remetente.png")
                    # Continua mesmo assim - pode ser que já esteja selecionado
                    logger.info("Continuando o processamento...")
            else:
                # Pequeno delay para estabilizar
                time.sleep(1)
            
            # PASSO 4.5: IMPORTANTE - Clicar em "Novo Destinatário" pra abrir o modal
            logger.info("Passo 4.5: Clicando em 'Novo Destinatário'...")
            
            seletores_novo_destinatario = [
                # Texto no botão/link
                (By.XPATH, "//button[contains(text(), 'Novo Destinatário')]"),
                (By.XPATH, "//a[contains(text(), 'Novo Destinatário')]"),
                (By.XPATH, "//button[contains(., 'Novo Destinatário')]"),
                (By.XPATH, "//a[contains(., 'Novo Destinatário')]"),
                # Variações do texto
                (By.XPATH, "//button[contains(text(), 'Novo destinatário')]"),
                (By.XPATH, "//a[contains(text(), 'Novo destinatário')]"),
                # Classes comuns
                (By.CSS_SELECTOR, "button[class*='novo-destinatario']"),
                (By.CSS_SELECTOR, "a[class*='novo-destinatario']"),
                # Por título/aria-label
                (By.XPATH, "//button[@title='Novo Destinatário' or @aria-label='Novo Destinatário']"),
                (By.XPATH, "//a[@title='Novo Destinatário' or @aria-label='Novo Destinatário']"),
            ]
            
            botao_novo_dest_clicado = False
            for idx, (by, selector) in enumerate(seletores_novo_destinatario, 1):
                try:
                    logger.info(f"Tentativa {idx}: Procurando 'Novo Destinatário' com {by}...")
                    botao = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", botao)
                    time.sleep(0.2)
                    
                    try:
                        botao.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", botao)
                    
                    logger.info(f"✓ Botão 'Novo Destinatário' clicado com sucesso (tentativa {idx})")
                    botao_novo_dest_clicado = True
                    break  # Sai do loop após clicar com sucesso
                except Exception as e:
                    logger.debug(f"Tentativa {idx} falhou: {str(e)[:100]}")
                    continue
            
            if not botao_novo_dest_clicado:
                logger.error("Botão 'Novo Destinatário' não encontrado")
                self.tirar_screenshot("erro_botao_novo_destinatario.png")
                
                print("\n" + "="*80)
                print("⚠️  AÇÃO MANUAL NECESSÁRIA")
                print("="*80)
                print("\n➤ O sistema não conseguiu clicar em 'Novo Destinatário'.")
                print("➤ Por favor, CLIQUE MANUALMENTE no botão 'Novo Destinatário'.")
                print("➤ Aguarde o popup/modal abrir e volte aqui.")
                print("\n⏸️  Pressione ENTER quando o formulário aparecer...")
                print("="*80 + "\n")
                input()
                time.sleep(2)
            
            # IMPORTANTE: Aguardar o modal/popup aparecer (detecção rápida)
            logger.info("Aguardando modal de destinatário abrir...")
            
            # Detecta pelo campo de nome que é o primeiro campo do modal
            modal_apareceu = False
            try:
                # Aguarda o campo de nome aparecer (indicador direto de que o modal está aberto)
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.ID, "nomeDestinatario"))
                )
                logger.info("✓ Modal aberto e pronto para preenchimento")
                modal_apareceu = True
                time.sleep(0.1)  # Pausa mínima para estabilizar
            except:
                # Fallback: tenta outros seletores
                logger.debug("Campo nomeDestinatario não encontrado, tentando seletores alternativos...")
                seletores_modal_fallback = [
                    (By.XPATH, "//div[contains(@class, 'modal')]//input[@name='nomeDestinatario']"),
                    (By.XPATH, "//input[@id='cpfCnpjDestinatario']"),
                    (By.XPATH, "//div[contains(@class, 'modal') and contains(@style, 'display: block')]"),
                ]
                
                for by, selector in seletores_modal_fallback:
                    try:
                        WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        logger.info("✓ Modal detectado por seletor alternativo")
                        modal_apareceu = True
                        time.sleep(0.1)
                        break
                    except:
                        continue
            
            if not modal_apareceu:
                logger.warning("⚠ Modal não detectado automaticamente, aguardando 1s...")
                time.sleep(1)
            
            # PASSO 5: Preenche o formulário do destinatário dentro do modal
            logger.info("Passo 5: Preenchendo formulário do destinatário no modal...")
            
            # Tira screenshot do formulário vazio
            self.tirar_screenshot(f"formulario_antes_preencher_linha_{dados.get('_linha')}.png")
            
            self._preencher_campo_destinatario(dados)
            
            logger.info("Formulário preenchido com sucesso")
            time.sleep(0.3)
            
            self.tirar_screenshot(f"formulario_preenchido_linha_{dados.get('_linha')}.png")
            
            # PASSO 5.5: Salva e fecha o modal
            logger.info("Passo 5.5: Salvando destinatário e fechando modal...")
            self._salvar_destinatario_modal()
            
            logger.info("Destinatário salvo! Modal fechado. Continuando com confirmação da pré-postagem...")
            time.sleep(1)
            
            # PASSO 6: Confirmar a pré-postagem (botão final)
            logger.info("Passo 6: Confirmando pré-postagem...")
            self._confirmar_postagem(dados)
            
            # CAPTURA DO CÓDIGO - tenta com 13 seletores diferentes
            logger.info("Tentando capturar código de rastreamento automaticamente...")
            time.sleep(1)
            
            # Tenta múltiplos seletores possíveis
            seletores_codigo = [
                (By.CLASS_NAME, "codigo-rastreamento"),
                (By.CLASS_NAME, "codigo-objeto"),
                (By.CLASS_NAME, "tracking-code"),
                (By.XPATH, "//span[contains(@class, 'codigo')]"),
                (By.XPATH, "//div[contains(text(), 'Código')]//following-sibling::div"),
                (By.XPATH, "//label[contains(text(), 'Código')]//following-sibling::*"),
                (By.XPATH, "//span[contains(text(), 'Código')]//parent::div//following-sibling::*"),
                (By.XPATH, "//*[contains(text(), 'Rastreamento')]//following-sibling::*"),
                (By.CSS_SELECTOR, "[class*='tracking'], [class*='rastreamento'], [class*='codigo']"),
                (By.XPATH, "//input[@readonly and contains(@value, 'AN')]"),
                (By.XPATH, "//td[contains(text(), 'AN') or contains(text(), 'BR')]"),
                (By.XPATH, "//strong[contains(text(), 'AN') or contains(text(), 'BR')]"),
                (By.XPATH, "//p[contains(text(), 'AN') or contains(text(), 'BR')]"),
            ]
            
            codigo_rastreamento = None
            for by, selector in seletores_codigo:
                try:
                    elemento = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    if elemento:
                        # Tenta text ou value
                        codigo = elemento.text.strip() or elemento.get_attribute('value') or ''
                        if codigo and len(codigo) >= 10:
                            codigo_rastreamento = codigo
                            logger.info(f"✓ Código capturado automaticamente: {codigo_rastreamento}")
                            break
                except:
                    continue
            
            # Se não capturou, registra pra conferir depois no screenshot
            if not codigo_rastreamento:
                logger.warning("⚠ Código de rastreamento NÃO capturado automaticamente")
                codigo_rastreamento = f"NÃO CAPTURADO - VERIFICAR SCREENSHOT sucesso_linha_{dados.get('_linha')}.png"
                print(f"⚠️  Código não capturado - verifique o screenshot depois: sucesso_linha_{dados.get('_linha')}.png")
            
            return {
                'linha': dados.get('_linha'),
                'destinatario': dados.get('COORDENADOR MUNICIPAL'),
                'codigo_rastreamento': codigo_rastreamento,
                'status': 'sucesso',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar postagem: {str(e)}")
            return {
                'linha': dados.get('_linha'),
                'destinatario': dados.get('COORDENADOR MUNICIPAL'),
                'erro': str(e),
                'status': 'erro',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def processar_coleta(self, dados: Dict) -> Dict:
        """
        Processa uma solicitação de coleta
        
        AVISO: Esse método é mais genérico que processar_postagem porque ainda não testei
        extensivamente com coletas reais. Os seletores vão precisar de ajuste.
        """
        codigo_coleta = None
        
        try:
            logger.info(f"Processando coleta linha {dados.get('_linha', 'N/A')}")
            
            if not self.logado:
                raise Exception("Não está logado no sistema")
            
            self.driver.get(config.CORREIOS_COLETA_URL)
            time.sleep(2)
            
            # Os seletores abaixo são chutes educados - precisam ser validados com o site real
            campo_tipo = self.wait.until(
                EC.presence_of_element_located((By.NAME, "tipoObjeto"))
            )
            campo_tipo.clear()
            campo_tipo.send_keys(dados.get('Tipo de Objeto', ''))
            
            campo_qtd = self.driver.find_element(By.NAME, "quantidade")
            campo_qtd.clear()
            campo_qtd.send_keys(str(dados.get('Quantidade', '')))
            
            campo_peso = self.driver.find_element(By.NAME, "pesoTotal")
            campo_peso.clear()
            campo_peso.send_keys(str(dados.get('Peso Total (kg)', '')))
            
            if dados.get('Data da Coleta'):
                campo_data = self.driver.find_element(By.NAME, "dataColeta")
                campo_data.clear()
                campo_data.send_keys(dados.get('Data da Coleta'))
            
            if dados.get('Período'):
                select_periodo = Select(self.driver.find_element(By.NAME, "periodo"))
                select_periodo.select_by_visible_text(dados.get('Período'))
            
            if dados.get('Observações'):
                campo_obs = self.driver.find_element(By.NAME, "observacoes")
                campo_obs.clear()
                campo_obs.send_keys(dados.get('Observações'))
            
            botao_confirmar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Solicitar') or contains(text(), 'Confirmar')]")
            botao_confirmar.click()
            
            time.sleep(3)
            
            try:
                elemento_codigo = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "codigo-coleta"))
                )
                codigo_coleta = elemento_codigo.text.strip()
                logger.info(f"Código de coleta obtido: {codigo_coleta}")
            except:
                codigo_coleta = "Código não capturado - verificar implementação"
                logger.warning("Não foi possível capturar código de coleta")
            
            return {
                'linha': dados.get('_linha'),
                'tipo_objeto': dados.get('Tipo de Objeto'),
                'codigo_coleta': codigo_coleta,
                'status': 'sucesso',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar coleta: {str(e)}")
            return {
                'linha': dados.get('_linha'),
                'tipo_objeto': dados.get('Tipo de Objeto', 'N/A'),
                'erro': str(e),
                'status': 'erro',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def tirar_screenshot(self, nome_arquivo: str = "screenshot.png"):
        """Tira screenshot da tela atual - salva-vidas ao debugar"""
        try:
            caminho = config.LOGS_DIR / nome_arquivo
            self.driver.save_screenshot(str(caminho))
            logger.info(f"Screenshot salvo: {caminho}")
            return caminho
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {str(e)}")
            return None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT
    )
    
    automator = CorreiosAutomator(headless=False)
    
    try:
        automator.iniciar_navegador()
        print("Navegador iniciado. Teste concluído.")
        time.sleep(2)
    finally:
        automator.fechar_navegador()
