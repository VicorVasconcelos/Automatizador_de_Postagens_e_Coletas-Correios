# Automatizador de Correios Empresa

Cansamos de preencher formulário manualmente no site dos Correios. Esse sistema lê planilhas Excel e preenche tudo sozinho - inclusive captura os códigos de rastreamento.

## 📋 O que ele faz

- ✅ Lê planilhas Excel (testado com arquivos de 48 colunas)
- ✅ Valida os dados antes de processar
- ✅ Faz login automático no portal Correios Empresa
- ✅ Preenche formulários de postagem usando Selenium
- ✅ Solicita coletas automaticamente
- ✅ Captura códigos de rastreamento (ou tira screenshot se falhar)
- ✅ Gera relatórios em Excel e TXT (Excel mais detalhado, TXT menos detalhado)
- ✅ Loga tudo - quando der erro, você vai saber onde
- ✅ Tira screenshots de erros automaticamente

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+ (testado na 3.14)
- Chrome instalado (Firefox não rola, Selenium é chato com Firefox)
- ChromeDriver (o webdriver-manager instala sozinho, deixa ele)

### Instalar dependências

```powershell
cd "C:\Users\victor.vasconcelos\Documents\Automatizador Correios"
pip install -r requirements.txt
```

Se der erro de permissão, adiciona `--user` no final.

## ⚙️ Como usar

### Preparar a planilha

Coloca tua planilha Excel em `dados/dados_postagem.xlsx` ou prepara o caminho completo dela.

**Não tem planilha?** Sem problema - roda o programa uma vez:

```powershell
python main.py
```

Ele te pergunta se quer gerar um template. Diz sim e usa `template_postagem.xlsx` como base.

### Login

🔑 **IMPORTANTE**: O sistema NÃO pede usuário e senha mais. Funciona assim:

1. Você roda o programa
2. Navegador abre no site dos Correios
3. **Você faz login MANUALMENTE** no site (como sempre fez)
4. Volta no terminal e aperta ENTER
5. Sistema processa tudo sozinho

Sem configurar credenciais, sem variáveis de ambiente, sem nada. Login 100% manual e seguro.

## 📊 Formato da Planilha

### Postagens

Essas são as colunas que o sistema espera. Algumas são obrigatórias (testei sem e deu erro):

| Coluna             | Obrigatório | Descrição                      |
| ------------------ | ------------ | -------------------------------- |
| Nome Destinatário | Sim          | Nome completo do destinatário   |
| CPF/CNPJ           | Não         | CPF ou CNPJ do destinatário     |
| Endereço          | Sim          | Logradouro                       |
| Número            | Sim          | Número do endereço             |
| Complemento        | Não         | Complemento do endereço         |
| Bairro             | Sim          | Bairro                           |
| Cidade             | Sim          | Cidade                           |
| Estado             | Sim          | UF (ex: SP, RJ)                  |
| CEP                | Sim          | CEP (com ou sem formatação)    |
| Telefone           | Não         | Telefone de contato              |
| Email              | Não         | E-mail de contato                |
| Tipo de Serviço   | Não         | PAC, SEDEX, etc                  |
| Peso (kg)          | Não         | Peso do objeto                   |
| Valor Declarado    | Não         | Valor para declaração          |
| AR                 | Não         | S ou N para Aviso de Recebimento |
| Mão Própria      | Não         | S ou N para Mão Própria        |

### Coletas

Pra solicitar coleta, esses são os campos:

| Coluna          | Obrigatório | Descrição               |
| --------------- | ------------ | ------------------------- |
| Tipo de Objeto  | Sim          | Tipo de objeto a coletar  |
| Quantidade      | Sim          | Quantidade de objetos     |
| Peso Total (kg) | Sim          | Peso total                |
| Data da Coleta  | Sim          | Data desejada para coleta |
| Período        | Sim          | Manhã ou Tarde           |
| Observações   | Não         | Observações adicionais  |

## 🎯 Como rodar isso

### 1. Executar

```powershell
python main.py
```

Ou clica duas vezes no `executar.bat` (fiz isso pra facilitar).

### 2. Escolher o que fazer

Ele pergunta se é postagem ou coleta:

```
1 - Postagem de objetos
2 - Solicitação de coleta
0 - Sair
```

### 3. Deixa rolar

O sistema vai:

1. Ler a planilha e validar tudo antes
2. Abrir o Chrome e fazer login
3. Processar linha por linha
4. Gerar os relatórios no final

Enquanto roda, acompanha o terminal pra ver se tá tudo certo.

## 📁 Como tá organizado

```
Automatizador Correios/
├── dados/                      # Joga suas planilhas aqui
│   └── dados_postagem.xlsx
├── relatorios/                 # Relatórios gerados automaticamente
│   ├── relatorio_YYYYMMDD_HHMMSS.xlsx
│   └── relatorio_YYYYMMDD_HHMMSS.txt
├── logs/                       # Logs e screenshots de erro
│   ├── automacao_YYYYMMDD_HHMMSS.log
│   └── erro_linha_X.png        # Quando der pau, olha aqui
├── config.py                   # Todas as configurações
├── main.py                     # Ponto de entrada
├── excel.py                    # Lê e valida Excel
├── correios.py                 # Automação Selenium (a parte mais chata)
├── relatorio.py                # Gera os relatórios
└── requirements.txt            # Dependências
```

## 📊 Relatórios gerados

### Excel (relatorio_*.xlsx)

Gera um arquivo com 4 abas:

- **Resumo**: Números gerais - quantos deram certo, quantos deram erro
- **Sucessos**: Tudo que processou direitinho, com os códigos de rastreio
- **Erros**: O que deu ruim durante o processamento
- **Dados Inválidos**: Linhas que falharam na validação e nem foram tentadas

### TXT (relatorio_*.txt)

Mesmas infos do Excel, mas em texto puro. Uso mais esse pra dar uma olhada rápida.

## 🔧 Customizações

### Rodar sem abrir o navegador (headless)

Edita `config.py`:

```python
HEADLESS_MODE = True
```

Bom pra rodar em servidor, mas complica pra debugar.

### Ajustar timeouts

Se o site dos Correios tá lento (sempre tá), aumenta os timeouts em `config.py`:

```python
TIMEOUT_PADRAO = 30  # Calibrei esse valor depois de MUITO teste
TEMPO_ESPERA_ELEMENTO = 10  # Alguns elementos demoram pra aparecer
```

### Adicionar/remover campos

Os mapeamentos de colunas tão em `config.py`. Mexe em:

- `COLUNAS_POSTAGEM`
- `COLUNAS_COLETA`

## ⚠️ Avisos importantes

1. **Seletores Web**: O arquivo `correios.py` tem vários seletores pra tentar encontrar os elementos da página. Mesmo assim, quando o site dos Correios muda alguma coisa (e eles mudam), vai precisar ajustar. Olha a seção de troubleshooting abaixo.
2. **Screenshots**: Quando dá erro, o sistema tira screenshot automaticamente. Salva-vidas pra debugar.
3. **Logs**: Tudo é logado na pasta `logs/`. Se der problema, começa por lá.
4. **Validação**: O sistema valida ANTES de processar. Se tem dados inválidos, ele nem tenta - vai direto pro relatório de inválidos.

## 🐛 Quando der problema

### ChromeDriver deu erro

```powershell
pip install --upgrade webdriver-manager
```

Se continuar, desinstala e instala de novo:

```powershell
pip uninstall webdriver-manager selenium
pip install selenium webdriver-manager
```

### "Falha no login" ou não consegue acessar

Isso acontece quando:

1. O site dos Correios tá fora do ar
2. Tentou fazer login muito rápido (aguarda a página carregar completamente)
3. Usou credenciais erradas no site

**Solução**:

- Aguarda a página dos Correios carregar COMPLETAMENTE antes de fazer login
- Confere usuário e senha
- Se o site tá lento, aumenta `TIMEOUT_PADRAO` em `config.py`

### "Elemento não encontrado" ou timeout

Isso acontece quando:

1. O site dos Correios mudou o layout (frequente)
2. A internet tá lenta e o timeout é curto demais
3. O site tá fora do ar ou com problema

**Solução**: Analisa o HTML do site e atualiza os seletores em `correios.py`.

## 📝 Como ajustar os seletores (quando o site mudar)

O site dos Correios muda com frequência. Quando der erro de "elemento não encontrado":

1. Abre o site dos Correios manualmente
2. Aperta F12 pra abrir DevTools
3. Usa a setinha de inspeção (canto superior esquerdo do DevTools)
4. Clica no elemento que quer encontrar
5. Copia o seletor (botão direito no HTML > Copy > Copy selector)
6. Atualiza em `correios.py`:

```python
# Exemplo:
campo_nome = self.wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#seletor-que-voce-copiou"))
)
```

O código já tem múltiplos seletores como fallback, mas as vezes precisa adicionar mais.

## 📞 Se precisar de ajuda

1. Olha os logs em `logs/` primeiro
2. Analisa os screenshots de erro (se tiver)
3. Confere o relatório de erros
4. Se ainda tá travado, adiciona `HEADLESS_MODE = False` no config.py e roda de novo vendo o navegador aberto

---

**Sistema feito pra automatizar postagens no Correios Empresa - economiza horas de trabalho manual**
