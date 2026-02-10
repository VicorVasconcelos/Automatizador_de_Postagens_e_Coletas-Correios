# Fluxo do Sistema Correios - Pré-postagem

## Como funciona

### 📋 Resumo

```
Login (manual) 
  → Pré-postagem 
  → Objetos Registrados 
  → Nova Pré-postagem 
  → Selecionar Remetente "CEBRASPE"
  → ⭐ Clicar "Novo Destinatário"
  → ⭐ Preencher formulário no MODAL
  → ⭐ Clicar "Salvar" (fecha modal)
  → Confirmar pré-postagem
  → Capturar código de rastreamento
```

---

### 1️⃣ Login

- **URL**: https://empresas.correios.com.br/#/login
- **Campos**: Usuário, Senha, Cartão (opcional)
- **Importante**: Login é MANUAL. Sistema aguarda usuário fazer login e apertar ENTER.

### 2️⃣ Navegação

- Acessa: https://prepostagem.correios.com.br/bem-vindo
- Se necessário, clica em "Pré Postagem" no menu lateral

### 3️⃣ Tipo de pré-postagem

- Clica em **"Pré-postagem a faturar de objetos registrados"**
- **URL direta**: https://prepostagem.correios.com.br/prepostagem/painels/faturar/registrados

### 4️⃣ Nova pré-postagem

- Clica no botão **"Nova pré-postagem"** (topo da lista)

### 5️⃣ Remetente

- No campo de busca, digita: **"Cebraspe"**
- Clica na lupa pra buscar
- Seleciona **"CEBRASPE"** nos resultados

### 6️⃣ Novo Destinatário ⭐ CRUCIAL

- Após selecionar remetente, localiza botão/link **"Novo Destinatário"**
- Clica pra abrir **modal/popup**
- Aguarda formulário aparecer sobreposto à tela

### 7️⃣ Preencher dados no modal

**ATENÇÃO**: Formulário abre em popup sobreposto. Todos os campos ficam DENTRO do modal.

Campos (mapeados da planilha Pasta3.xlsx):

- **Destinatário/Nome** ← COORDENADOR MUNICIPAL
- **CPF/CNPJ** ← CPF
- **CEP** ← CEP (sistema busca endereço automaticamente)
- **Endereço/Logradouro** ← LOGRADOURO
- **Número** ← NÚMERO ("S/Nº" vira "S/N")
- **Complemento** ← COMPLEMENTO (opcional)
- **Bairro** ← BAIRRO
- **Cidade/Município** ← CIDADE
- **Estado/UF** ← UF.1
- **Telefone** ← TELEFONE
- **E-mail** ← EMAIL

### 8️⃣ Salvar modal ⭐ CRUCIAL

- Depois de preencher, clica **"Salvar"** no rodapé do modal
- Aguarda modal fechar
- Sistema volta pra tela principal com destinatário já selecionado

### 9️⃣ Confirmar pré-postagem

- Na tela principal (modal já fechou), clica **"Confirmar"** ou **"Finalizar"**
- Aguarda processamento

### 🔟 Capturar código

- Sistema mostra tela de sucesso com código de rastreamento
- **Captura automática** do código (formato: AN123456789BR)
- Se falhar, tira screenshot pra verificação manual depois

---

## Detalhes importantes

### Modal "Novo Destinatário" ⭐ O MAIS IMPORTANTE

**Após selecionar remetente:**

1. Clica em **"Novo Destinatário"** na tela principal
2. Modal/popup abre (janela sobreposta)
3. Preenche os 11 campos dentro do modal
4. Clica **"Salvar"** no rodapé do modal
5. Aguarda modal fechar e voltar pra tela principal
6. SÓ DEPOIS confirma a pré-postagem

**⚠️ CRÍTICO**: Não tenta preencher na tela principal. TODOS os campos do destinatário ficam **dentro do modal**.

### Estrutura da planilha (Pasta3.xlsx)

- Total: 48 colunas
- Obrigatórios: COORDENADOR MUNICIPAL, CEP, LOGRADOURO, CIDADE, UF.1
- Campo NÚMERO aceita: números, "S/Nº", "S/N", "SN" (sistema converte tudo pra "S/N")
- Estado fica na coluna **UF.1** (não "UF" - aprendi isso do jeito difícil)

### Remetente

- Sempre: **CEBRASPE**
- Fixo pra todas as postagens

### Mapeamento: Planilha → Site

| Coluna da Planilha        | Campo no Site        | Observação                                         |
| ------------------------- | -------------------- | ---------------------------------------------------- |
| `COORDENADOR MUNICIPAL` | Destinatário/Nome   | Principal                                            |
| `CPF`                   | CPF/CNPJ             | Com ou sem formatação                              |
| `CEP`                   | CEP                  | Remove pontuação; aguarda 3s pra busca automática |
| `LOGRADOURO`            | Endereço/Logradouro | Rua, Avenida, etc                                    |
| `NÚMERO`               | Número              | Converte "S/Nº" pra "S/N"                           |
| `COMPLEMENTO`           | Complemento          | Opcional                                             |
| `BAIRRO`                | Bairro               |                                                      |
| `CIDADE`                | Cidade/Município    |                                                      |
| `UF.1`                  | Estado/UF            | DF, SP, RJ, etc                                      |
| `TELEFONE`              | Telefone             | Celular ou fixo                                      |
| `EMAIL`                 | E-mail               |                                                      |

### URLs identificadas

```
Login:            https://empresas.correios.com.br/#/login
Pré-postagem:     https://prepostagem.correios.com.br/bem-vindo
Obj. Registrados: https://prepostagem.correios.com.br/prepostagem/painels/faturar/registrados
```

---

## Implementação

Código em `correios.py` segue esse fluxo completo:

1. ✅ **Login manual** - Usuário loga, sistema aguarda confirmação
2. ✅ **Navegação** - Acessa pré-postagem automaticamente
3. ✅ **Objetos registrados** - Clica em "Pré-postagem a faturar de objetos registrados"
4. ✅ **Nova pré-postagem** - Clica "Nova pré-postagem"
5. ✅ **Remetente** - Seleciona "CEBRASPE"
6. ✅ **Novo Destinatário** ⭐ - Clica pra abrir modal
7. ✅ **Preenchimento** ⭐ - Preenche 11 campos no modal
8. ✅ **Salvar** ⭐ - Salva e fecha modal
9. ✅ **Confirmar** - Confirmação final
10. ✅ **Captura** - Tenta capturar código (ou screenshot)

### Métodos implementados:

- `processar_postagem()` - Orquestra todo o fluxo
- `_preencher_campo_destinatario()` - Preenche os 11 campos (múltiplos seletores por campo)
- `_salvar_destinatario_modal()` ⭐ - Salva e fecha o modal
- `_confirmar_postagem()` - Confirmação final
- `_tentar_preencher_campo()` - Método genérico com 5-7 seletores por elemento

### Estratégia de seletores:

Cada elemento tem **múltiplos seletores** (5-13 por elemento) pra maximizar chance de funcionar:

- By.NAME, By.ID, By.XPATH, By.CSS_SELECTOR
- Fallback pra clique JavaScript se clique normal falhar
- Fallback pra ação manual com instruções se tudo falhar

---

**Última atualização**: 06/02/2026
**Status**: Fluxo completo implementado com workflow do modal "Novo Destinatário"
