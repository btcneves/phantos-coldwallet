#!/usr/bin/env bash
set -euo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# live-build não suporta caminhos com espaços — usa diretório neutro em /tmp
BUILD_DIR="/tmp/phantos-coldwallet-build"
LOG="$PROJECT_DIR/build-iso.log"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute como root: sudo $0" >&2
  exit 1
fi

for cmd in dd dpkg-deb find grub-mkstandalone lb mkfs.fat mount rsync sed tee umount xorriso; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd não encontrado. Instale: apt install live-build xorriso grub-efi-amd64-bin grub-pc-bin dosfstools rsync dpkg-dev" >&2
    exit 1
  fi
done

if [ ! -f /usr/lib/grub/i386-pc/boot_hybrid.img ]; then
  echo "/usr/lib/grub/i386-pc/boot_hybrid.img não encontrado. Instale: apt install grub-pc-bin" >&2
  exit 1
fi

echo "[1/6] Preparando diretório de build em $BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
lb clean --purge 2>/dev/null || true

echo "[2/6] Configurando live-build (Debian Bookworm amd64)"
lb config \
  --mode debian \
  --distribution bookworm \
  --architectures amd64 \
  --binary-images iso \
  --debian-installer false \
  --archive-areas "main contrib non-free-firmware" \
  --mirror-bootstrap http://deb.debian.org/debian \
  --mirror-chroot http://deb.debian.org/debian \
  --mirror-binary http://deb.debian.org/debian \
  --keyring-packages "debian-archive-keyring" \
  --linux-packages "linux-image" \
  --linux-flavours amd64 \
  --initramfs live-boot \
  --bootloader grub2 \
  --firmware-chroot false \
  --security false \
  --volatile false \
  --source false \
  --bootappend-live "boot=live components quiet init=/lib/systemd/systemd nox11autologin"

# Corrige mirrors "parent" — live-build Ubuntu aponta para ubuntu.com por padrão
DEBIAN_MIRROR="http://deb.debian.org/debian"
DEBIAN_SEC="http://security.debian.org/debian-security"
KEYRING="debian-archive-keyring"
sed -i \
  -e "s|LB_PARENT_MIRROR_BOOTSTRAP=.*|LB_PARENT_MIRROR_BOOTSTRAP=\"$DEBIAN_MIRROR\"|" \
  -e "s|LB_PARENT_MIRROR_CHROOT=.*|LB_PARENT_MIRROR_CHROOT=\"$DEBIAN_MIRROR\"|" \
  -e "s|LB_PARENT_MIRROR_CHROOT_SECURITY=.*|LB_PARENT_MIRROR_CHROOT_SECURITY=\"$DEBIAN_SEC\"|" \
  -e "s|LB_PARENT_MIRROR_CHROOT_VOLATILE=.*|LB_PARENT_MIRROR_CHROOT_VOLATILE=\"$DEBIAN_MIRROR\"|" \
  -e "s|LB_PARENT_MIRROR_BINARY=.*|LB_PARENT_MIRROR_BINARY=\"$DEBIAN_MIRROR\"|" \
  -e "s|LB_PARENT_MIRROR_BINARY_SECURITY=.*|LB_PARENT_MIRROR_BINARY_SECURITY=\"$DEBIAN_SEC\"|" \
  -e "s|LB_PARENT_MIRROR_BINARY_VOLATILE=.*|LB_PARENT_MIRROR_BINARY_VOLATILE=\"$DEBIAN_MIRROR\"|" \
  -e "s|LB_PARENT_MIRROR_DEBIAN_INSTALLER=.*|LB_PARENT_MIRROR_DEBIAN_INSTALLER=\"$DEBIAN_MIRROR\"|" \
  config/bootstrap
sed -i \
  -e "s|LB_BOOTSTRAP_KEYRING=.*|LB_BOOTSTRAP_KEYRING=\"$KEYRING\"|" \
  config/bootstrap
sed -i \
  -e "s|LB_MIRROR_CHROOT_VOLATILE=.*|LB_MIRROR_CHROOT_VOLATILE=\"$DEBIAN_MIRROR\"|" \
  -e "s|LB_MIRROR_BINARY_VOLATILE=.*|LB_MIRROR_BINARY_VOLATILE=\"$DEBIAN_MIRROR\"|" \
  config/bootstrap 2>/dev/null || true

echo "[3/6] Copiando arquivos do projeto"
mkdir -p config/includes.chroot/opt/phantos
rsync -a --delete --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='build' --exclude='.git' --exclude='tests' \
  "$PROJECT_DIR/app" \
  "$PROJECT_DIR/pyproject.toml" \
  "$PROJECT_DIR/requirements.lock" \
  config/includes.chroot/opt/phantos/

# Scripts de hardening
mkdir -p config/includes.chroot/usr/local/bin
install -m 0755 "$SCRIPT_DIR/harden_network.sh"  config/includes.chroot/usr/local/bin/phantos-harden-network
install -m 0755 "$SCRIPT_DIR/verify_offline.sh"   config/includes.chroot/usr/local/bin/phantos-verify-offline
install -m 0755 "$SCRIPT_DIR/verify_live_hardening.sh" \
  config/includes.chroot/usr/local/bin/phantos-verify-live-hardening

# Script wrapper de inicialização com fallback de diagnóstico
cat > config/includes.chroot/usr/local/bin/phantos-start <<'PSTART'
#!/bin/sh
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 0700 "$XDG_RUNTIME_DIR"
chmod -R a+rX /opt/phantos 2>/dev/null || true
cd /opt/phantos
export PYTHONPATH="/opt/phantos"
# stderr is discarded in production to avoid capturing sensitive library output.
# On crash, only the exit code is shown; enable PHANTOS_DEBUG=1 for full logs.
if [ "${PHANTOS_DEBUG:-0}" = "1" ]; then
  /opt/phantos/.venv/bin/python -m app.main --kiosk >/tmp/phantos-app.log 2>&1
else
  /opt/phantos/.venv/bin/python -m app.main --kiosk >/dev/null 2>&1
fi
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  xterm -title "PhantOS ERROR (exit $EXIT_CODE)" \
        -e "echo 'A aplicação encerrou com erro (código $EXIT_CODE).' && echo 'Para diagnóstico, reinicie com PHANTOS_DEBUG=1.' && echo && echo 'Pressione Enter para sair' && read _" &
fi
PSTART
chmod 0755 config/includes.chroot/usr/local/bin/phantos-start

# Serviço systemd
mkdir -p config/includes.chroot/etc/systemd/system
install -m 0644 "$PROJECT_DIR/packaging/systemd/phantos-coldwallet.service" \
  config/includes.chroot/etc/systemd/system/

cat > config/includes.chroot/etc/systemd/system/phantos-network-hardening.service <<'EOF'
[Unit]
Description=PhantOS offline network hardening
DefaultDependencies=no
Before=network-pre.target NetworkManager.service wpa_supplicant.service bluetooth.service graphical.target
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/phantos-harden-network
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Autostart do openbox para kiosk
mkdir -p config/includes.chroot/etc/xdg/openbox
cat > config/includes.chroot/etc/xdg/openbox/autostart <<'EOF'
/usr/local/bin/phantos-start &
EOF

# Getty autologin — mais confiável que LightDM para kiosk live
# (LightDM pode falhar ao resolver user-session + autologin em live systems)
mkdir -p config/includes.chroot/etc/systemd/system/getty@tty1.service.d
cat > config/includes.chroot/etc/systemd/system/getty@tty1.service.d/override.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin phantos --noclear %I $TERM
Type=idle
EOF

# .bash_profile: inicia X automaticamente quando logado no tty1
mkdir -p config/includes.chroot/etc/skel
cat > config/includes.chroot/etc/skel/.bash_profile <<'EOF'
HISTFILE=/dev/null
export HISTSIZE=0
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
mkdir -p "$XDG_RUNTIME_DIR" && chmod 0700 "$XDG_RUNTIME_DIR"
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx -- -nolisten tcp 2>/tmp/startx.log
    # Se startx falhar, mostra o log no terminal em vez de tela preta
    echo "=== startx falhou (veja /tmp/startx.log) ==="
    tail -30 /tmp/startx.log
    echo "=== Pressione Enter para tentar novamente ==="
    read _
fi
EOF

# .xinitrc: inicia openbox-session (que lê /etc/xdg/openbox/autostart)
cat > config/includes.chroot/etc/skel/.xinitrc <<'EOF'
#!/bin/sh
# Redireciona erros do X para log depurável
exec openbox-session 2>/tmp/openbox.log
EOF
chmod +x config/includes.chroot/etc/skel/.xinitrc

echo "[3b/6] Criando pacote dummy ubuntu-keyring (exigido pelo live-build Ubuntu)"
mkdir -p /tmp/fake-ubuntu-keyring/DEBIAN
cat > /tmp/fake-ubuntu-keyring/DEBIAN/control <<'CTL'
Package: ubuntu-keyring
Version: 2023.11.28.1
Architecture: all
Maintainer: PhantOS Build <build@phantos.local>
Description: Dummy ubuntu-keyring — satisfaz dependência interna do live-build Ubuntu
CTL
dpkg-deb --build /tmp/fake-ubuntu-keyring /tmp/ubuntu-keyring-dummy.deb
mkdir -p config/packages
cp /tmp/ubuntu-keyring-dummy.deb config/packages/

echo "[4/6] Configurando lista de pacotes"
mkdir -p config/package-lists
cat > config/package-lists/phantos.list.chroot <<'EOF'
linux-image-amd64
firmware-amd-graphics
firmware-linux
live-boot
live-config
live-config-systemd
python3
python3-pip
python3-venv
python3-dev
nftables
rfkill
xserver-xorg
xserver-xorg-legacy
xserver-xorg-video-amdgpu
xserver-xorg-video-fbdev
xserver-xorg-video-vesa
xinit
openbox
xterm
fonts-dejavu-core
libgl1
libglib2.0-0
libdbus-1-3
libxkbcommon-x11-0
libxcb-icccm4
libxcb-image0
libxcb-keysyms1
libxcb-randr0
libxcb-render-util0
libxcb-xinerama0
libxcb-xinput0
libxcb-xfixes0
libxcb-cursor0
libxcb-shape0
libxcb-shm0
libxcb-util1
libx11-xcb1
libxrender1
libegl1
libfontconfig1
libfreetype6
systemd
systemd-sysv
dbus
gstreamer1.0-plugins-good
gstreamer1.0-plugins-base
gstreamer1.0-libav
libgstreamer1.0-0
libgstreamer-plugins-base1.0-0
EOF

echo "[5/6] Criando hook de instalação Python"
mkdir -p config/hooks
cat > config/hooks/0100-phantos-setup.hook.chroot <<'HOOK'
#!/bin/bash
set -e

LOG=/var/log/phantos-setup.log
exec > >(tee -a "$LOG") 2>&1
echo "[phantos-setup] Iniciando hook $(date)"

# Cria usuário phantos sem senha (autologin via getty)
if ! id phantos >/dev/null 2>&1; then
  useradd -m -s /bin/bash -G audio,video,input,plugdev phantos
else
  # Garante que phantos está no grupo input (necessário para libinput sem logind)
  usermod -aG audio,video,input,plugdev phantos 2>/dev/null || true
fi

# Força Xorg a rodar como root (necessário sem logind ou com sessão getty)
# O postinst do xserver-xorg-legacy escreve allowed_users=console via debconf;
# usamos debconf-set-selections antes E sobrescrevemos o arquivo depois para garantir.
echo "xserver-xorg-legacy xserver/allow_anybody select true" | debconf-set-selections
mkdir -p /etc/X11
cat > /etc/X11/Xwrapper.config <<'XWRAP'
allowed_users=anybody
needs_root_rights=yes
XWRAP

# Copia arquivos de perfil do skel para o home do phantos (força substituição)
cp -f /etc/skel/.bash_profile /home/phantos/.bash_profile
cp -f /etc/skel/.xinitrc      /home/phantos/.xinitrc
chown phantos:phantos /home/phantos/.bash_profile /home/phantos/.xinitrc

# Cria venv isolado (PySide6 não existe nos repos do Bookworm — instala via pip)
python3 -m venv /opt/phantos/.venv

# Instala todas as dependências Python via pip com verificação de hashes
/opt/phantos/.venv/bin/pip install --upgrade pip --quiet
/opt/phantos/.venv/bin/pip install \
  --require-hashes \
  -r /opt/phantos/requirements.lock \
  --quiet

# Instala o app em modo editável dentro do venv
cd /opt/phantos
.venv/bin/pip install -e . --no-deps --quiet

# Ajusta permissões
chown -R phantos:phantos /opt/phantos

# Remove serviços desnecessários para segurança e estabilidade
# (phantos-coldwallet não é mais serviço systemd — inicia via openbox autostart)
systemctl disable NetworkManager bluetooth avahi-daemon lightdm 2>/dev/null || true
systemctl enable phantos-network-hardening.service 2>/dev/null || true
# Desabilita DHCP client automático do live-config (rede será bloqueada pelo harden_network)
systemctl disable networking isc-dhcp-client 2>/dev/null || true
# Fallback SysVinit: garante que mesmo sem systemd esses serviços não sobem
update-rc.d networking disable 2>/dev/null || true

# Fallback autologin SysVinit via /etc/inittab (caso init=/lib/systemd/systemd não funcione)
if [ -f /etc/inittab ]; then
  sed -i 's|^1:2345:respawn:/sbin/agetty --noclear tty1 linux|1:2345:respawn:/sbin/agetty --autologin phantos --noclear tty1 linux|' /etc/inittab
  echo "[phantos-setup] inittab: autologin phantos configurado"
fi

# Desabilita DHCP via /etc/network/interfaces (loopback apenas)
cat > /etc/network/interfaces <<'NETCFG'
auto lo
iface lo inet loopback
NETCFG

# Garante XDG_RUNTIME_DIR no .bash_profile do phantos
grep -qF 'XDG_RUNTIME_DIR' /home/phantos/.bash_profile 2>/dev/null || \
  sed -i '1s|^|export XDG_RUNTIME_DIR="/run/user/$(id -u)"\nmkdir -p "$XDG_RUNTIME_DIR"\nchmod 0700 "$XDG_RUNTIME_DIR"\n\n|' /home/phantos/.bash_profile

# ── OS Memory Hardening ────────────────────────────────────────────────────
# Desativa swap: seeds e chaves privadas nunca devem alcançar o disco.
# Em sistemas live o swap raramente existe, mas a desativação é explícita.
swapoff -a 2>/dev/null || true
# Remove qualquer referência a swap no fstab
sed -i '/\bswap\b/d' /etc/fstab 2>/dev/null || true

# Desativa core dumps: impede que conteúdo de memória seja gravado em disco.
mkdir -p /etc/security/limits.d
cat > /etc/security/limits.d/phantos-coredump.conf <<'LIMITS'
* hard core 0
* soft core 0
LIMITS

mkdir -p /etc/sysctl.d
cat > /etc/sysctl.d/99-phantos-hardening.conf <<'SYSCTL'
# Desativa core dumps via sysctl (redundante com limits.d, mas garante cobertura)
kernel.core_pattern = /dev/null
fs.suid_dumpable = 0

# Reduz janela de exposição de dados sensíveis na memória do kernel
vm.swappiness = 0

# Proteções adicionais de kernel
kernel.dmesg_restrict = 1
kernel.perf_event_paranoid = 3
kernel.unprivileged_bpf_disabled = 1
net.core.bpf_jit_harden = 2

# SYS-13: impede que qualquer processo (inclusive root sem CAP_SYS_PTRACE)
# use ptrace para inspecionar memória de outro processo — elimina vetor de
# leitura de seed/chave privada via /proc/PID/mem ou PTRACE_PEEKDATA.
kernel.yama.ptrace_scope = 3
SYSCTL

# Garante que tmpfs cobre /tmp para operações temporárias
# Em sistemas live o /tmp já costuma ser tmpfs; este bloco é explícito
if ! grep -qF 'tmpfs /tmp' /etc/fstab 2>/dev/null; then
  echo "tmpfs /tmp tmpfs defaults,nosuid,nodev,noexec,size=128m 0 0" >> /etc/fstab
fi

# Aplica as configurações de sysctl agora (dentro do chroot)
sysctl --system 2>/dev/null || true

echo "[phantos-setup] OS hardening aplicado: swap, core dumps, sysctl"
# ── Fim OS Memory Hardening ───────────────────────────────────────────────

echo "[phantos-setup] Hook concluído com sucesso $(date)"
HOOK
chmod +x config/hooks/0100-phantos-setup.hook.chroot

echo "[6/6] Iniciando build da ISO (pode levar 10-30 min)..."
lb build 2>&1 | tee "$LOG"

BINARY_DIR="$BUILD_DIR/binary"
if [ ! -d "$BINARY_DIR" ] || [ ! -d "$BINARY_DIR/live" ]; then
  echo "" >&2
  echo "ERRO: diretório binary/ não foi criado. Verifique: $LOG" >&2
  exit 1
fi

GRUB_CFG="$BINARY_DIR/boot/grub/grub.cfg"
if [ ! -f "$GRUB_CFG" ]; then
  echo "AVISO: grub.cfg não encontrado, criando configuração básica..."
  mkdir -p "$BINARY_DIR/boot/grub"
  VMLINUZ=$(find "$BINARY_DIR/live/" -maxdepth 1 -name 'vmlinuz*' 2>/dev/null | sort | head -1 | sed "s|$BINARY_DIR||")
  INITRD=$(find "$BINARY_DIR/live/" -maxdepth 1 -name 'initrd*' 2>/dev/null | sort | head -1 | sed "s|$BINARY_DIR||")
  cat > "$GRUB_CFG" <<GRUBCFG
set default=0
set timeout=5

menuentry "PhantOS ColdWallet" {
  linux  $VMLINUZ boot=live components quiet
  initrd $INITRD
}
GRUBCFG
fi

# Patcha o grub.cfg gerado pelo live-build:
# 1. "search" define $root como o volume PHANTOS (ISO/pendrive), não a partição EFI
# 2. Remove "splash" — trava o framebuffer sem plymouth configurado → tela preta
# 3. Remove a entrada memtest86+ — arquivo live/memtest não existe na ISO
# 4. Adiciona timeout e remove "boot=live" duplicado que live-build injeta
sed -i "1s|^|search --no-floppy --label --set=root PHANTOS\nset timeout=5\n\n|" "$GRUB_CFG"
sed -i 's/ splash\b//g' "$GRUB_CFG"
sed -i '/menuentry[[:space:]].*[Mm]emtest/,/^}/d' "$GRUB_CFG"
# Remove referência a xbmc.tga que não existe (erro silencioso, mas evita warnings)
sed -i '/background_image\|insmod tga/d' "$GRUB_CFG"
# live-build adiciona "boot=live config" antes do nosso --bootappend-live → "boot=live config boot=live components..."
# Remove o "boot=live" extra que fica duplicado nas entradas linux
sed -i 's/boot=live config boot=live/boot=live config/g' "$GRUB_CFG"

echo "[6b/6] Criando suporte EFI (grub-mkstandalone + FAT image)..."
EFI_BOOT_DIR="$BINARY_DIR/EFI/BOOT"
mkdir -p "$EFI_BOOT_DIR"

grub-mkstandalone \
  --format=x86_64-efi \
  --output="$EFI_BOOT_DIR/bootx64.efi" \
  --locales="" \
  --fonts="" \
  "boot/grub/grub.cfg=$GRUB_CFG"

# Imagem FAT para El Torito EFI (4 MB é suficiente)
EFIIMG="$BUILD_DIR/efiboot.img"
dd if=/dev/zero of="$EFIIMG" bs=1M count=4 2>/dev/null
mkfs.fat -F 12 -n "EFIBOOT" "$EFIIMG" >/dev/null
MNT=$(mktemp -d)
mount "$EFIIMG" "$MNT"
mkdir -p "$MNT/EFI/BOOT"
cp "$EFI_BOOT_DIR/bootx64.efi" "$MNT/EFI/BOOT/"
umount "$MNT"
rmdir "$MNT"
cp "$EFIIMG" "$BINARY_DIR/boot/grub/efiboot.img"

echo "[6c/6] Criando ISO híbrida BIOS+UEFI com xorriso..."
FINAL_ISO="$BUILD_DIR/phantos-coldwallet-hybrid.iso"

BIOS_OPTS=""
BIOS_MBR_OPTS=""
if [ -f "$BINARY_DIR/boot/grub/grub_eltorito" ]; then
  # -boot-info-table: patcha o El Torito com info do CD; sem --grub2-boot-info (causa MISHAP)
  BIOS_OPTS="-b boot/grub/grub_eltorito -no-emul-boot -boot-load-size 4 -boot-info-table"
  BIOS_MBR_OPTS="--grub2-mbr /usr/lib/grub/i386-pc/boot_hybrid.img"
else
  echo "AVISO: grub_eltorito não encontrado — ISO será apenas UEFI"
fi

# shellcheck disable=SC2086
xorriso -as mkisofs \
  -iso-level 3 \
  -r -J -l \
  -full-iso9660-filenames \
  -volid "PHANTOS" \
  ${BIOS_MBR_OPTS} \
  -partition_offset 16 \
  --mbr-force-bootable \
  -append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b "$EFIIMG" \
  -appended_part_as_gpt \
  -iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7 \
  -c boot/grub/boot.cat \
  ${BIOS_OPTS} \
  -eltorito-alt-boot \
  -e --interval:appended_partition_2:all:: \
  -no-emul-boot \
  -isohybrid-gpt-basdat \
  -o "$FINAL_ISO" \
  "$BINARY_DIR/" \
  2>&1 | tee -a "$LOG"

if [ ! -f "$FINAL_ISO" ]; then
  echo "" >&2
  echo "ERRO: ISO final não criada pelo xorriso. Verifique: $LOG" >&2
  exit 1
fi

ISONAME="phantos-coldwallet-1.0.0-amd64.iso"
cp "$FINAL_ISO" "$PROJECT_DIR/$ISONAME"
echo ""
echo "ISO gerada com sucesso: $PROJECT_DIR/$ISONAME ($(du -sh "$PROJECT_DIR/$ISONAME" | cut -f1))"
echo ""
echo "Para gravar no pendrive (/dev/sdX):"
echo "  sudo umount /dev/sdX* 2>/dev/null; sudo dd if=$PROJECT_DIR/$ISONAME of=/dev/sdX bs=4M status=progress conv=fsync"
