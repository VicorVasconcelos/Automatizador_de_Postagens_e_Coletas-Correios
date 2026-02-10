# 🚀 GUIA RÁPIDO

## Passo 1: Instalar dependências

Abre o PowerShell nessa pasta:

```powershell
pip install -r requirements.txt
```

Se der erro de permissão, adiciona `--user` no final.

## Passo 2: Preparar planilha

Coloca tua planilha Excel em `dados/dados_postagem.xlsx` ou prepara o caminho completo dela.

**Dica**: Se não tem planilha ainda, só roda o sistema uma vez que ele te avisa e pode gerar um template.

## Passo 3: Rodar o sistema

```powershell
python main.py
```

Ou clica duas vezes em: `executar.bat` (mais fácil)

## Passo 4: Seguir as instruções na tela

O sistema vai pedir:
1. **Tipo de processo**: Postagem (1) ou Coleta (2)
2. **Caminho da planilha**: ENTER pra usar padrão ou digita o caminho
3. **Navegador abre automaticamente** no site dos Correios
4. **Faz login MANUALMENTE** na página (usuário e senha)
5. **Aperta ENTER no terminal** depois de fazer login
6. **Sistema processa tudo sozinho**

🔑 **IMPORTANTE**: Login é MANUAL. O navegador abre, você faz login normalmente no site dos Correios e depois volta no terminal pra apertar ENTER.

## 📊 Resultados

Depois de rodar, verifica:
- `relatorios/` - Excel e TXT com tudo que aconteceu
- `logs/` - Logs detalhados e screenshots quando dá erro

## ⚠️ IMPORTANTE - Seletores

Os seletores em `correios.py` são **genéricos**. Quando o site dos Correios mudar (e vai), precisa ajustar:

1. Abre o site manualmente
2. F12 pra abrir DevTools
3. Inspeciona os campos
4. Atualiza em `correios.py`

Exemplo:
```python
# Antes (exemplo genérico):
campo_nome = self.driver.find_element(By.NAME, "nomeDestinatario")

# Depois (ajustado pro site real):
campo_nome = self.driver.find_element(By.ID, "input-destinatario-nome")
```

## 🔧 Testes

Pra testar e ver o que tá acontecendo:
1. Deixa `HEADLESS_MODE = False` em `config.py` (já é o padrão - abre o navegador)
2. Roda o sistema
3. Faz login manualmente quando o navegador abrir
4. Observa cada passo no navegador
5. Ajusta os seletores em `correios.py` se necessário

## 📞 Dúvidas?

Dá uma olhada no `README.md` ou `COMO_USAR.md` pra guia completo.

---

**Boa automação! 🚀**
