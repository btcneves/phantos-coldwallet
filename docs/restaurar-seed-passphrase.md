# Restaurar Seed e Passphrase

## Como funciona a entrada de seed words

A partir da versão 0.2.1, o campo de seed usa um **word picker individual** com autocomplete,
similar ao Electrum e ao Sparrow Wallet.

### O que você verá na tela

A área de seed exibe **24 campos numerados** (ou 12, conforme selecionado):

```text
 1.[    ] 2.[    ] 3.[    ] 4.[    ] 5.[    ] 6.[    ]
 7.[    ] 8.[    ] 9.[    ]10.[    ]11.[    ]12.[    ]
13.[    ]14.[    ]15.[    ]16.[    ]17.[    ]18.[    ]
19.[    ]20.[    ]21.[    ]22.[    ]23.[    ]24.[    ]
                                              0/24
```

### Como digitar cada palavra

1. Clique no campo **#1** ou pressione Tab para focar o primeiro campo
2. Comece a digitar — as sugestões da lista BIP39 aparecem automaticamente
3. Quando a palavra desejada aparecer em destaque no menu, pressione:
   - **Enter** ou **Tab** ou **Espaço** → aceita a palavra e move para o próximo campo
   - **Clique** na sugestão → mesmo efeito
4. Repita para cada uma das 24 (ou 12) palavras
5. Acompanhe o contador no canto inferior direito: `24/24 ✓ checksum OK`

### Indicadores visuais

| Cor da borda | Significado |
| --- | --- |
| **Verde** | Palavra válida na lista BIP39 |
| **Sem destaque** | Prefixo ainda pode ser completado — continue digitando |
| **Vermelha** | Nenhuma palavra BIP39 começa com esse texto |

O status abaixo da grade:

| Status | Significado |
| --- | --- |
| `15/24` | 15 campos preenchidos, 9 ainda vazios |
| `24/24 ✓ checksum OK` | Todas as palavras válidas e checksum BIP39 correto |
| `24/24 ✗ checksum inválido` | Alguma palavra foi digitada errada ou a ordem está errada |

---

## Passo a passo para restaurar

1. Selecione **24** ou **12** palavras no combo superior
2. Selecione o **tipo de carteira** (padrão: BIP84 Native SegWit)
3. Digite cada palavra no campo correspondente usando o autocomplete
4. Se a carteira usava **passphrase**, informe no campo "Passphrase"
5. Clique em **⟲ Restaurar Seed**
6. Verifique o fingerprint e os endereços exibidos na área de saída

---

## Passphrase BIP39 (opcional, avançado)

A passphrase é diferente da seed. É uma senha adicional opcional que altera
completamente a carteira derivada.

- A **mesma seed com passphrase diferente** gera uma carteira diferente
- **Passphrase esquecida = fundos permanentemente inacessíveis** — não há recuperação possível
- Se você não configurou passphrase ao criar a carteira, deixe o campo em branco
- Anote a passphrase separadamente da seed, em local diferente

---

## Dicas de segurança

- **Nunca fotografe** a tela com as palavras visíveis
- **Nunca digite** a seed em um dispositivo conectado à internet
- Após restaurar e verificar os endereços, clique em **🔒 Bloquear** para limpar a memória
- Em caso de dúvida, compare o **fingerprint** e os primeiros endereços com os que você anotou ao criar a carteira

---

## Suporte a múltiplos tipos de carteira

Ao restaurar, sempre selecione o mesmo tipo que foi usado ao criar:

| Tipo | Padrão | Endereços |
| --- | --- | --- |
| BIP84 Native SegWit | Recomendado | `bc1q…` |
| BIP49 Nested SegWit | Legado | `3…` |
| BIP44 Legacy | Legado | `1…` |
| BIP86 Taproot | Experimental | `bc1p…` |

Se não tiver certeza do tipo, use **⊙ Recuperar Endereços** — ele mostra o primeiro
endereço de cada tipo para você identificar qual corresponde à sua carteira.
