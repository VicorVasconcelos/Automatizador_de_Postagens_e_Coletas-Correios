# 📋 Instruções pra Testar e Ajustar Seletores

## ⚠️ Importante

O código já tá com o **fluxo correto** do sistema Correios:

1. ✅ Login manual (usuário faz, sistema aguarda)
2. ✅ Navegação pra pré-postagem
3. ✅ Clica em "Pré-postagem a faturar de objetos registrados"  
4. ✅ Clica em "Nova pré-postagem"
5. ✅ Seleciona remetente "CEBRASPE"
6. ⚠️ Clica em "Novo Destinatário" (abre modal)
7. ⚠️ Preenche 11 campos no modal
8. ⚠️ Salva modal e confirma

A parte que pode dar problema são os seletores - quando o site dos Correios muda, quebra tudo.

---

## 🧪 Como testar

### 1. Primeira execução

Roda normalmente:

```powershell
python main.py
```

Ou clica em `executar.bat` (mais fácil)

### 2. Acompanha o navegador

- O Chrome vai abrir (não tá em headless por padrão)
- Observa cada passo sendo executado
- **Presta atenção onde ele trava ou dá erro**

### 3. Verifica os logs

Logs ficam em: `logs/automacao_XXXXXXXX.log`

Procura por:
- ✅ Mensagens de sucesso
- ⚠️ Avisos (elementos não encontrados)
- ❌ Erros críticos

### 4. Analisa os screenshots

Quando dá erro, ele tira screenshot automaticamente em `logs/`:

- `passo2_navegacao_direta.png` - Não achou link de "objetos registrados"
- `erro_passo3_botao_nova_postagem.png` - Não achou "Nova pré-postagem"
- `passo4_erro_selecionar_remetente.png` - Não conseguiu selecionar Cebraspe
- `erro_botao_confirmar.png` - Não achou botão de confirmação
- `sucesso_linha_X.png` - Quando dá certo (usa pra identificar onde fica o código)
- `erro_linha_X.png` - Quando dá erro no processamento

---

## 🔧 Como ajustar os seletores

### Passo 1: Identifica o elemento

1. Abre DevTools do Chrome (F12)
2. Clica no ícone de seleção (canto superior esquerdo do DevTools)
3. Clica no elemento da página que quer selecionar
4. DevTools mostra o HTML do elemento

### Passo 2: Acha um seletor único

Procura por (nessa ordem de preferência):

1. **`id`** - Exemplo: `<input id="nomeDestinatario">`
   - Seletor: `By.ID, "nomeDestinatario"`

2. **`name`** - Exemplo: `<input name="cep">`
   - Seletor: `By.NAME, "cep"`

3. **`class` única** - Exemplo: `<button class="btn-confirmar">`
   - Seletor: `By.CLASS_NAME, "btn-confirmar"`

4. **XPath** - Pra casos complexos
   - Exemplo: `By.XPATH, "//button[text()='Confirmar']"`

### Passo 3: Atualiza o código

Abre: `correios.py`

Acha o método `processar_postagem` (linha ~177)

**Exemplo de ajuste:**

```python
# ❌ Código atual (chute):
campo_nome = self.wait.until(
    EC.presence_of_element_located((By.NAME, "nomeDestinatario"))
)

# ✅ Ajuste com seletor correto:
campo_nome = self.wait.until(
    EC.presence_of_element_located((By.ID, "destinatario-nome"))
)
```

---

## 🎯 Seletores mais comuns pra ajustar

### 1. Botão "Nova pré-postagem" (Passo 3)

**Localização no código**: Linha ~237

```python
# Tenta identificar:
# - id do botão
# - class do botão  
# - texto exato do botão
# - atributo onclick ou data-*

# Exemplos possíveis:
By.ID, "btn-nova-prepostagem"
By.CLASS_NAME, "nova-postagem"
By.XPATH, "//button[@data-action='nova']"
```

### 2. Campo de Remetente (Passo 4)

**Localização no código**: Linha ~250

```python
# Identifica:
# - Campo de busca/autocomplete de remetente
# - Botão de busca (lupa)
# - Item clicável na lista de resultados

# Exemplos:
By.ID, "remetente-busca"
By.NAME, "searchRemetente"
By.XPATH, "//input[@placeholder='Buscar remetente']"
```

### 3. Campos do Destinatário (Passo 5 - Modal)

**Localização no código**: Linha ~270+

Campos críticos (11 no total):
- Nome/Destinatário
- CEP
- Endereço/Logradouro
- Número
- Bairro
- Cidade
- Estado/UF
- CPF
- Telefone
- Email
- Complemento

**Identifica cada campo e ajusta:**

```python
# Exemplo - Campo de CEP:
# Se o atual não funcionar:
campo_cep = self.driver.find_element(By.NAME, "cep")

# Tenta alternativas:
campo_cep = self.driver.find_element(By.ID, "endereco-cep")
campo_cep = self.driver.find_element(By.XPATH, "//input[@placeholder='CEP']")
```

### 4. Botão Salvar (no modal)

**Localização no código**: Linha ~320

```python
# Identifica o botão que salva o modal de "Novo Destinatário"
# Geralmente é "Salvar" no rodapé do modal

# Ajusta conforme necessário:
By.ID, "btn-salvar-modal"
By.XPATH, "//button[contains(text(), 'Salvar')]"
By.CSS_SELECTOR, "button.modal-salvar"
```

### 5. Botão Confirmar (tela principal)

**Localização no código**: Linha ~356

```python
# Depois que o modal fecha, precisa confirmar na tela principal
# Pode ser: "Confirmar", "Finalizar", "Enviar"

# Ajusta:
By.ID, "btn-confirmar"
By.XPATH, "//button[contains(text(), 'Confirmar')]"
By.CLASS_NAME, "btn-primary"
```

### 6. Código de Rastreamento (captura final)

**Localização no código**: Linha ~383+

```python
# Depois de confirmar, o sistema mostra o código
# Olha no screenshot 'sucesso_linha_X.png' pra ver onde fica

# Ajusta os seletores:
By.CLASS_NAME, "tracking-code"
By.ID, "codigo-objeto"
By.XPATH, "//div[@class='resultado']//span"
```

---

## 📝 Checklist de teste

- [ ] Login funciona
- [ ] Navega pra pré-postagem
- [ ] Abre tela de "objetos registrados"
- [ ] Clica em "Nova pré-postagem"
- [ ] Seleciona remetente "CEBRASPE"
- [ ] Clica em "Novo Destinatário" (abre modal)
- [ ] Preenche campos no modal
- [ ] Salva modal (fecha)
- [ ] Confirma na tela principal
- [ ] Captura código de rastreamento
- [ ] Preenche endereço/logradouro
- [ ] Preenche número (ou S/N)
- [ ] Preenche complemento
- [ ] Preenche bairro
- [ ] Seleciona cidade
- [ ] Seleciona estado/UF
- [ ] Preenche telefone
- [ ] Preenche email
- [ ] Clica em confirmar/finalizar
- [ ] Captura código de rastreamento
- [ ] Gera relatório com sucesso

---

## 🐛 Solução de Problemas Comuns

### Erro: "Elemento não encontrado"

**Causa**: Seletor incorreto ou elemento não carregado

**Solução**:
1. Verifique o screenshot gerado
2. Abra DevTools (F12) no navegador
3. Identifique o seletor correto
4. Atualize o código

### Erro: "Timeout ao aguardar elemento"

**Causa**: Página demora a carregar ou elemento com nome diferente

**Solução**:
1. Aumente o timeout em `config.py`: `TEMPO_ESPERA_ELEMENTO = 20`
2. Verifique se o elemento realmente existe na página
3. Adicione `time.sleep(3)` antes de buscar o elemento

### Campo não preenche corretamente

**Causa**: Elemento pode estar desabilitado ou ser do tipo select

**Solução**:
```python
# Para campos de select (dropdown):
from selenium.webdriver.support.ui import Select
select_estado = Select(self.driver.find_element(By.ID, "estado"))
select_estado.select_by_visible_text("AC")

# Para campos que precisam de clique antes:
campo.click()
campo.clear()
campo.send_keys("valor")
```

### Código de rastreamento não capturado

**Causa**: Seletor incorreto para o código

**Solução**:
1. Verifique o screenshot `sucesso_linha_X.png`
2. Identifique onde o código aparece
3. Use DevTools para encontrar o seletor
4. Atualize a lista de seletores em `processar_postagem` (linha ~383)

---

## 💡 Dicas Importantes

1. **Teste com UMA linha primeiro**: Crie uma planilha de teste com apenas 1 linha para ajustar os seletores rapidamente

2. **Modo não-headless**: Mantenha `HEADLESS_MODE = False` em `config.py` para ver o que está acontecendo

3. **Use os screenshots**: Eles são salvos automaticamente para facilitar a depuração

4. **Logs detalhados**: Todos os passos são registrados em `logs/automacao_*.log`

5. **Screenshots de sucesso**: Mesmo quando funciona, é gerado um screenshot para você verificar o código capturado

---

## 📞 Próximos Passos

Depois de ajustar os seletores e **confirmar que funciona para 1 linha**:

1. ✅ Teste com 2-3 linhas
2. ✅ Verifique se os códigos estão sendo capturados corretamente
3. ✅ Analise o relatório gerado
4. ✅ Após confirmar funcionamento, processe a planilha completa

---

**Última atualização**: 06/02/2026  
**Versão do código**: 2.0 (com fluxo real do sistema)
