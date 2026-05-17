# Segurança

## Padrões do projeto

- Wi-Fi desativado no sistema live.
- Bluetooth desativado no sistema live.
- Firewall nftables bloqueando toda entrada e saída (apenas loopback permitido).
- Sem navegador, sem telemetria, sem atualização automática.
- Sem consulta de saldo online — use uma carteira observadora separada.
- Sem transmissão de transações Bitcoin — a cold wallet só assina, nunca transmite.

## Isolamento de rede

Use `/usr/local/bin/phantos-harden-network` no sistema live para aplicar as regras de firewall.
Use `/usr/local/bin/phantos-verify-live-hardening` para validar o estado após o boot.
Use `scripts/verify_offline.sh` para confirmar que o dispositivo está offline antes de assinar.

A assinatura de PSBTs é bloqueada pela aplicação se o isolamento de rede não for verificado.

## Limpeza de dados sensíveis na UI

- A seed (mnemônica BIP39) é exibida na tela apenas durante o processo de criação ou restauração.
- A passphrase é limpa automaticamente após o carregamento do contexto da carteira.
- No fluxo de restauração, a seed também é limpa automaticamente após uso.
- No fluxo de criação, a seed permanece visível para que o usuário possa verificar a cópia em papel.
  Após verificar, use o botão **🔒 Bloquear** para limpar todos os dados da tela.
- O botão **🔒 Bloquear** zera o contexto da carteira, limpa todos os campos e o painel de saída.
- A aplicação **não usa o clipboard** para seeds, passphrases ou chaves privadas.

## Limitação conhecida — zeroização de memória em Python

Python não oferece garantia de zeroização imediata de strings na RAM após o uso.
Strings e bytes são objetos imutáveis gerenciados pelo garbage collector — não é possível
sobrescrever seu conteúdo diretamente, ao contrário de linguagens como C ou Rust.

**Implicação:** Mesmo após limpar os campos da UI e chamar `lock_wallet()`, fragmentos da
seed, passphrase, chaves ou objetos de biblioteca podem permanecer na RAM até o garbage
collector coletar os objetos ou até o processo terminar.

**Mitigação implementada e recomendada:**

- O buffer de seed controlado pelo PhantOS usa `bytearray`, tenta aplicar `mlock`
  quando disponível e é sobrescrito no bloco `finally` de `create_wallet_context()`.
- Cópias internas em `str`, `bytes`, objetos Qt e bibliotecas de terceiros continuam
  fora de controle direto do PhantOS.
- Encerre a aplicação imediatamente após o uso.
- Reinicie ou desligue o sistema antes de entregar o computador a terceiros.
- O sistema live bootável reduz a exposição ao reiniciar/desligar, mas isso não é
  garantia contra ataques físicos como cold boot.
- Não use o sistema live como computador diário.

Esta limitação permanece documentada até que a estratégia de memória seja revisada e
auditada externamente.

## Hardening de memória do sistema operacional

O hook de instalação (`scripts/build_iso.sh`) aplica as seguintes proteções no sistema live:

### Swap desativado

```bash
swapoff -a
```

Qualquer entrada de swap é removida do `/etc/fstab`. Sem swap ativo, o sistema reduz
o risco de dados da RAM (incluindo seeds e chaves privadas) serem paginados para o disco.

**Limitação:** Desativa swap existente ao instalar, mas o sistema live Debian
não costuma ter swap configurado por padrão — esta medida é explícita e defensiva.

### Core dumps desabilitados

```ini
# /etc/security/limits.d/phantos-coredump.conf
* hard core 0
* soft core 0

# /etc/sysctl.d/99-phantos-hardening.conf (trecho)
kernel.core_pattern = /dev/null
fs.suid_dumpable = 0
```

Em caso de falha do processo, o kernel não gravará conteúdo de memória em disco.

### Parâmetros de kernel via sysctl

```ini
# /etc/sysctl.d/99-phantos-hardening.conf
vm.swappiness = 0
kernel.dmesg_restrict = 1
kernel.perf_event_paranoid = 3
kernel.unprivileged_bpf_disabled = 1
net.core.bpf_jit_harden = 2
```

### /tmp em tmpfs

O `/tmp` é montado como `tmpfs` (RAM), garantindo que arquivos temporários
nunca alcancem storage persistente. Configuração via `/etc/fstab`:

```fstab
tmpfs /tmp tmpfs defaults,nosuid,nodev,noexec,size=128m 0 0
```

### Limitações documentadas

- A zeroização de objetos Python (`str`, `bytes`) não é garantida mesmo com as
  proteções de SO acima — ver seção "Limitação conhecida — zeroização de memória em Python".
- Core dumps via `systemd-coredump` ou outros coletores não estão presentes no sistema live,
  mas a proteção via `sysctl` e `limits.d` é defensiva.

## Serviços desabilitados no live system

- NetworkManager
- wpa_supplicant
- bluetooth
- avahi-daemon
- cups (impressão; não instalado ou verificado como inativo)
- ssh / sshd (não instalado ou verificado como inativo)
- isc-dhcp-client
- lightdm (substituído por autologin getty + openbox kiosk)
