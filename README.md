# Automatizador de Correios

Automatiza preenchimento de pré-postagens no site dos Correios. Lê Excel, preenche formulários via Selenium, captura códigos de rastreio.

## Setup rápido

```bash
pip install -r requirements.txt
python main.py
```

## Como funciona

1. Coloca tua planilha em `dados/dados_postagem.xlsx`
2. Roda `python main.py`
3. Navegador abre → faz login manualmente
4. Aperta ENTER no terminal
5. Sistema processa tudo sozinho
6. Relatórios ficam em `relatorios/`

## Colunas obrigatórias da planilha

- COORDENADOR MUNICIPAL (nome)
- CEP
- LOGRADOURO
- NÚMERO
- BAIRRO
- CIDADE
- UF.1 (estado)

Resto é opcional. Se não tiver planilha, roda uma vez que ele cria um template.

## Arquivos importantes

- `config.py` - Configura timeouts e outras paradas
- `correios.py` - Automação Selenium (1000+ linhas, a parte chata)
- `logs/` - Quando der erro, olha aqui primeiro
- `relatorios/` - Excel e TXT com resultados

## Se der problema

**Elemento não encontrado**: Site dos Correios mudou. Abre DevTools (F12), pega os novos seletores e atualiza em `correios.py`

**Timeout**: Aumenta `TIMEOUT_PADRAO` no `config.py`

**ChromeDriver**: `pip install --upgrade webdriver-manager`

---

Feito pra rodar em produção. Login é manual (mais seguro), resto é automático.

Desenvolvido por Victor Vasconcelos com muito **☕**
