# 🚀 COMO USAR - Modo Interativo com Login Manual

## O esquema

O sistema é **interativo** e **seguro**:
- Você informa tipo de processo e planilha no terminal
- **Login é 100% MANUAL no navegador** (suas credenciais nunca passam pelo sistema)
- Depois do login, sistema automatiza tudo sozinho

## Passo a passo

### 1️⃣ Rodar o sistema

**Opção A - Jeito fácil:**
- Dá duplo clique em `executar.bat`

**Opção B - Via terminal:**
```powershell
cd "C:\Users\victor.vasconcelos\Documents\Automatizador Correios"
python main.py
```

### 2️⃣ Escolher o tipo

```
Selecione o tipo de processo:
1 - Postagem de objetos
2 - Solicitação de coleta
0 - Sair

Opção: _
```

Digita `1` pra postagem ou `2` pra coleta.

### 3️⃣ Caminho da planilha

```
================================================================================
CAMINHO DA PLANILHA
================================================================================

Forneça o caminho completo da planilha Excel:
Exemplo: C:\planilhas\dados_postagem.xlsx

Ou pressione ENTER para usar o padrão: dados/dados_postagem.xlsx

Caminho da planilha: _
```

Duas opções:

**A - Usar padrão:**
- Só aperta ENTER (sem digitar nada)
- Usa: `dados/dados_postagem.xlsx`

**B - Caminho específico:**
- Digita ou cola o caminho: `C:\Users\victor.vasconcelos\Desktop\minhas_postagens.xlsx`
- Aperta ENTER

💡 **Dica**: Arrasta o arquivo pra janela do terminal que ele cola o caminho sozinho!

### 4️⃣ Login no navegador (MANUAL)

🎯 **IMPORTANTE**: Essa é a parte que mudou!

```
================================================================================
LOGIN MANUAL - SITE DOS CORREIOS
================================================================================

O navegador Chrome vai abrir agora no site dos Correios.

Por favor:
1. FAÇA LOGIN MANUALMENTE no site (como sempre fez)
2. Após fazer login com sucesso, VOLTE AQUI
3. Pressione ENTER para continuar...

Aguardando login manual...
```

**O que fazer:**
1. Chrome abre automaticamente no site dos Correios
2. **Você faz login NORMALMENTE no site** (digita usuário e senha NO NAVEGADOR)
3. Após login bem-sucedido, volta no terminal
4. Aperta ENTER
5. Sistema continua sozinho

🔒 **Segurança**: Suas credenciais nunca passam pelo sistema - login é 100% no site dos Correios.

### 5️⃣ Sistema processa

Depois que você apertar ENTER (após login manual), o sistema assume:

```
✅ Lendo planilha...
✅ Validando dados...
✅ Navegando para pré-postagem...
✅ Processando registro 1/50...
✅ Código capturado: AA123456789BR
...
✅ Gerando relatórios...
✅ Concluído!
```

Acompanha o terminal pra ver o progresso em tempo real.

## 🎯 Fluxo Completo Ilustrado

```
┌─────────────────────────────────────┐
│  Executar sistema (BAT ou Python)   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Escolher: Postagem ou Coleta (1/2) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Informar CAMINHO DA PLANILHA       │
│  (ou ENTER para usar padrão)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  🌐 Chrome abre site dos Correios   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  🔑 VOCÊ FAZ LOGIN MANUAL        │
│     (digita no NAVEGADOR)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Voltar no TERMINAL e ENTER         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  ✅ Sistema processa automaticamente │
│  • Lê e valida planilha            │
│  • Navega no site                   │
│  • Preenche formulários            │
│  • Captura códigos                 │
│  • Gera relatórios                  │
└─────────────────────────────────────┘
```

## 💡 Dicas

### Sobre o login
- Login é MANUAL no navegador, não no terminal
- Suas credenciais NUNCA passam pelo sistema Python
- Você tem total controle do processo de login

### Sobre o caminho da planilha
- Se tá em `dados/dados_postagem.xlsx`, só aperta ENTER
- Se não, passa o caminho completo
- Ele verifica se o arquivo existe e avisa se não achar

### Se errar alguma coisa
- Fecha o programa (Ctrl+C ou fecha a janela)
- Roda de novo e digita certo dessa vez

## ⚠️ Problemas comuns

### "Falha após login" ou "Página não carregou"
- Aguarda a página dos Correios carregar COMPLETAMENTE antes de fazer login
- Depois de logar, confirma que tá na página inicial antes de apertar ENTER no terminal
- Se o site dos Correios tá lento, dá uns segundos a mais

### "Arquivo não encontrado"
- Verifica o caminho da planilha
- Usa caminho completo ou copia/cola
- Certifica que o arquivo existe

## 📁 Onde ficam os resultados

Depois que rodar, os relatórios vão pra:
- **Excel**: `relatorios/relatorio_YYYYMMDD_HHMMSS.xlsx`
- **Texto**: `relatorios/relatorio_YYYYMMDD_HHMMSS.txt`
- **Logs**: `logs/automacao_YYYYMMDD_HHMMSS.log`

## 🔄 Rodar de novo

Pra processar outra planilha:
- Só roda de novo
- Caminho da planilha será perguntado novamente
- Login manual no navegador de novo

---

**Sistema com login 100% manual e seguro - suas credenciais nunca passam pelo código! 🔒**
