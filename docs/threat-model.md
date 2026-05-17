# Modelo de Ameaças

O PhantOS protege contra exposição remota da seed quando utilizado em ambiente
offline verificado — sem interfaces de rede ativas, sem rotas padrão, sem
serviços de rede em execução.

## O que é protegido

- Geração e armazenamento da seed em memória RAM temporária (não persistida em disco).
- Assinatura de transações PSBT sem contato com a internet.
- Derivação de endereços e exportação watch-only sem exposição da chave privada.

## O que não é protegido

- Firmware comprometido (BIOS, UEFI, controladores USB).
- Teclado ou câmera maliciosos capturando a seed durante a digitação.
- Ataques físicos diretos ao dispositivo (Evil Maid, cold-boot attack).
- Computador host comprometido em nível de hardware ou hypervisor.
- Erros do operador: seed fotografada, tela visível a terceiros, backup inseguro.
- Falha na verificação offline: o sistema apenas avisa se detectar interfaces ativas
  ou serviços de rede — a verificação depende de acesso a `/sys`, `/proc` e
  `systemctl`, e pode ser incompleta em ambientes não-padrão ou sem privilégios.

## Limitações conhecidas

- A zeroização de segredos em Python não é garantida: `str` e `bytes` são imutáveis
  e o garbage collector pode manter cópias na memória. O PhantOS zera o buffer de seed
  controlado pelo app, mas objetos Qt, bibliotecas e cópias internas ainda reduzem a
  garantia. A limpeza dos campos de UI reduz a janela de exposição, mas não elimina o risco.
- A estimativa de vbytes para cálculo de taxa é aproximada (baseada no tamanho da
  transação não assinada). O valor real após assinatura pode ser maior.
- PSBTs exportadas por carteiras externas (Sparrow, Electrum, BlueWallet) não foram
  testadas extensivamente nesta versão — use com cautela em valores altos.

Para valores expressivos, use hardware dedicado, backups robustos e auditoria
externa independente.
