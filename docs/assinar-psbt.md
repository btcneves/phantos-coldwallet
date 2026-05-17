# Assinar PSBT

PSBT e o formato correto para transacoes nao assinadas em fluxos offline.

Antes de assinar, o PhantOS revisa:

- inputs assinaveis;
- valor total de saida;
- taxa;
- taxa estimada em sats/vB;
- troco reconhecido;
- fingerprint e derivation path;
- alertas de Taproot/PSBTv2.

Nunca assine se destino, valor, taxa ou troco estiverem estranhos.

