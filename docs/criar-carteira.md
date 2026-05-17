# Criar Carteira

O padrão recomendado é seed BIP39 de **24 palavras em inglês**, com BIP84 Native
SegWit (`m/84'/0'/0'`) e endereços `bc1q`.

---

## Passo a passo

### 1. Selecionar parâmetros

- **Palavras:** 24 (recomendado) ou 12
- **Tipo:** BIP84 Native SegWit (padrão)
- Clique em **⊕ Criar Carteira**

### 2. Anotar a seed

O PhantOS gera as 24 palavras automaticamente e as exibe no word picker.
Cada campo mostra uma palavra — anote-as **em papel, na ordem numérica**.

> **Regras absolutas:**
>
> - Nunca tire foto da seed
> - Nunca salve em nuvem, e-mail ou notas digitais
> - Nunca envie para ninguém
> - Anote em papel agora e guarde em local seguro

### 3. Verificar a seed (opcional, mas recomendado)

Após anotar, clique em **🔒 Bloquear** para limpar a tela.
Em seguida, **restaure a seed** digitando as palavras pelo word picker:

1. Clique no campo **#1** e comece a digitar a primeira palavra
2. Selecione a sugestão correta (Tab / Enter / clique)
3. Repita para todas as 24 palavras
4. Confirme que o **fingerprint** e os **endereços de recebimento** exibidos
   são idênticos aos da geração inicial

### 4. Decidir sobre passphrase (avançado)

A passphrase BIP39 é uma senha adicional que cria uma carteira completamente
diferente da mesma seed. É opcional e recomendada apenas para usuários experientes.

- Se usar passphrase, anote-a **separadamente da seed**, em local diferente
- Passphrase esquecida = fundos permanentemente inacessíveis — não há recuperação

### 5. Exportar a carteira observadora

1. Clique em **▦ QR Carteira**
2. Escaneie o QR com o app online (BlueWallet, Sparrow, Electrum)
3. O app importa sua carteira como watch-only — pode ver saldo sem expor a seed

### 6. Bloquear

Clique em **🔒 Bloquear** para limpar todos os campos da memória.

---

## Sobre o word picker

A partir da v0.2.1, o PhantOS usa campos individuais com autocomplete para a seed:

- **Borda verde** = palavra BIP39 válida
- **Borda vermelha** = nenhuma palavra BIP39 começa com esse texto
- **`24/24 ✓ checksum OK`** = seed completa e checksum correto

---

## Tipos de carteira suportados

| Tipo | Derivação | Endereços | Recomendação |
| --- | --- | --- | --- |
| BIP84 Native SegWit | `m/84'/0'/0'` | `bc1q…` | Padrão recomendado |
| BIP49 Nested SegWit | `m/49'/0'/0'` | `3…` | Compatibilidade legada |
| BIP44 Legacy | `m/44'/0'/0'` | `1…` | Legado, evitar |
| BIP86 Taproot | `m/86'/0'/0'` | `bc1p…` | Experimental |
