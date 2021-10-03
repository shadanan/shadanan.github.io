# Avocado Raspberry Pi

Notes on my Raspberry Pi configuration.

## Installation

- Download the latest [64 bit Raspberry Pi OS](https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2020-08-24/2020-08-20-raspios-buster-arm64-lite.zip).
- Use the [Raspberry Pi Imager](https://www.raspberrypi.org/downloads/) to prepare the SSD.

## Terminal & SSH

### Username and Password

- Login to Raspberry Pi.
  - User: `pi`
  - Password: `raspberry`
- Set the root password.
  ```console
  $ sudo passwd root
  ```
- Logout and login as root.
- Change the `pi` user to `shad`.
  ```console
  $ usermod -l shad pi
  $ usermod -m -d /home/shad shad
  ```

### Mount the Old Root

- List the available devices.
  ```console
  $ sudo lsblk -o name,label,size,mountpoint
  NAME   LABEL      SIZE MOUNTPOINT
  sda             465.8G
  ├─sda1 boot       256M /boot
  └─sda2 rootfs   465.5G /
  sdb               1.8T
  └─sdb1 tanpopo    1.8T
  sdc               4.6T
  └─sdc1 ajisai     4.6T
  sdd              29.8G
  ├─sdd1 RECOVERY   2.2G
  ├─sdd2              1K
  ├─sdd5 SETTINGS    32M
  ├─sdd6 boot       256M
  └─sdd7 root      27.3G /mnt/oldroot
  ```
- Mount the appropriate partition.
  ```console
  $ sudo mkdir /mnt/oldroot
  $ sudo mount /dev/sdd7 /mnt/oldroot
  ```

### SSH

- Enable SSH.
  ```console
  $ sudo systemctl enable ssh
  $ sudo systemctl start ssh
  ```
- Restore SSH keys from backup.
  ```console
  $ cp -a /mnt/oldroot/home/shad/.ssh ~
  ```

### Zsh

- Restore the old `zsh` history.
  ```console
  $ cp /mnt/oldroot/home/shad/.zsh_history ~
  ```
- Install `zsh`.
  ```console
  $ sudo apt install zsh
  ```
- Switch the default shell.
  ```console
  $ chsh
  Password:
  Changing the login shell for shad
  Enter the new value, or press ENTER for the default
      Login Shell [/bin/bash]: /usr/bin/zsh
  ```
- Logout and log back in.

### Dot Files

- Install `.dotfiles`.
  ```console
  $ sudo apt install git curl
  $ git clone git@github.com:shadanan/dotfiles.git .dotfiles
  $ .dotfiles/install
  ```
- Logout and log back in.

### Passwordless `sudo`

- Open the sudo config editor.
  ```console
  $ sudo visudo
  ```
- Add the following to the file.
  ```visudo
  shad    ALL=(ALL) NOPASSWD:ALL
  ```

### SSH Two Factor Authentication

- Install the Google Authenticator PAM module.
  ```console
  $ sudo apt install libpam-google-authenticator
  ```
- Initialize the configuration. Answer yes to everything.
  ```console
  $ google-authenticator
  ```
- Add the following to the top of `/etc/pam.d/sshd`.
  ```
  # Google Two Factor Authentication
  auth required pam_google_authenticator.so
  ```
- In `/etc/ssh/sshd_config`, change `ChallengeResponseAuthentication` from `no` to `yes`.
- Restart the `sshd` daemon.
  ```console
  $ sudo systemctl restart sshd.service
  ```

### Debian Sid

- Replace the contents of `/etc/apt/sources.list` with:
  ```
  deb http://deb.debian.org/debian unstable main contrib non-free
  ```
- Update and upgrade.
  ```console
  $ sudo apt update
  $ sudo apt dist-upgrade
  ```
- Clean up and reboot.
  ```console
  $ sudo apt-get autoremove
  $ sudo reboot
  ```

### Vim

- Install `vim`.
  ```console
  $ sudo apt install vim
  ```

### tmux

- Install `tmux`.
  ```console
  $ sudo apt install tmux
  ```
- Launch `tmux` and install plugins by pressing `ctrl+a, I`

### Message of the Day (MotD)

- Add the following to the top of `/etc/motd`
  ```
  🥑.shad.io
  ```

## Console Beautification

### Console Font Size

- Start the console configuration.
  ```console
  $ sudo dpkg-reconfigure console-setup
  ```
- In the Configuring console-setup, select:
  - UTF-8
  - Guess optimal character set
  - Terminus
  - 16x32

### Console Overscan

- In `/boot/config.txt`, uncomment `disable_overscan=1`.
- Reboot.

## Dynamic DNS

- Install `ddclient`.
  ```console
  $ sudo apt install ddclient
  ```
- Restore the original ddclient config.
  ```console
  $ cp /mnt/oldroot/etc/ddclient.conf /etc/ddclient.conf
  ```
- Or use this template:
  ```
  #usev6=if
  #if=eth0
  protocol=dyndns2
  use=web
  ssl=yes
  server=domains.google.com
  login=<get this from domains.google.com>
  password=<get this from domains.google.com>
  *.shad.io
  ```
- Restart the `ddclient` service.
  ```console
  $ sudo systemctl restart ddclient
  ```

## Mount Media Volumes

- List the available HDDs.
  ```console
  $ sudo lsblk -o name,label,size,mountpoint
  NAME   LABEL      SIZE MOUNTPOINT
  sda             465.8G
  ├─sda1 boot       256M /boot
  └─sda2 rootfs   465.5G /
  sdb               1.8T
  └─sdb1 tanpopo    1.8T
  sdc               4.6T
  └─sdc1 ajisai     4.6T
  sdd              29.8G
  ├─sdd1 RECOVERY   2.2G
  ├─sdd2              1K
  ├─sdd5 SETTINGS    32M
  ├─sdd6 boot       256M
  └─sdd7 root      27.3G /mnt/oldroot
  ```
- Add the following to `/etc/fstab`.
  ```
  LABEL=tanpopo   /mnt/tanpopo    exfat   defaults,auto,uid=1000,gid=1000,umask=0022,users,rw,nofail 0 0
  LABEL=ajisai    /mnt/ajisai     exfat   defaults,auto,uid=1000,gid=1000,umask=0022,users,rw,nofail 0 0
  ```
- Install `exfat`.
  ```console
  $ sudo apt install exfat-fuse exfat-utils
  ```
- Create the mount points.
  ```console
  $ sudo mkdir /mnt/tanpopo
  $ sudo mkdir /mnt/ajisai
  ```
- Mount the volumes.
  ```console
  $ sudo mount /mnt/tanpopo
  FUSE exfat 1.3.0
  $ sudo mount /mnt/ajisai
  FUSE exfat 1.3.0
  ```

## Share Media Volumes

- Install `samba`
  ```console
  $ sudo apt install samba
  ```
- Create shares for the mounted volumes in `/etc/samba/smb.conf`:
  ```
  [tanpopo]
     comment = Tanpopo 2TB External Drive
     valid users = shad
     path = /mnt/tanpopo
     read only = no
     guest ok = no

  [ajisai]
     comment = Ajisai 5TB External Drive
     valid users = shad
     path = /mnt/ajisai
     read only = no
     guest ok = no
  ```
- Set the password for user `shad`.
  ```console
  $ sudo smbpasswd -a shad
  ```
- Restart the `smbd.service`.
  ```console
  $ sudo systemctl restart smbd.service
  ```

## Transmission

- Install `transmission-daemon`.
  ```console
  $ sudo apt install transmission-daemon
  ```
- Change the run as user to `shad`.
  ```console
  $ sudo systemctl edit transmission-daemon.service
  ```
- Add the following to the file:
  ```
  [Service]
  User=shad
  ```
- Restart the transmission daemon to create configuration files.
  ```console
  $ sudo systemctl restart transmission-daemon
  ```
- Edit `~/.config/transmission-daemon/settings.json`.
- Update the following values:
  - `"rpc-username": "shad"`
  - `"rpc-password": "<new password>"`
  - `"rpc-whitelist": "192.168.*.*"`
  - `"rpc-host-whitelist-enabled": false`
- Reload the transmission daemon.
  ```console
  $ sudo systemctl reload transmission-daemon.service
  ```

## Caddy

- Install Caddy.
  ```console
  $ echo "deb [trusted=yes] https://apt.fury.io/caddy/ /" | sudo tee -a /etc/apt/sources.list.d/caddy-fury.list
  $ sudo apt update
  $ sudo apt install caddy
  ```
- Configure reverse proxies by adding the following to `/etc/caddy/Caddyfile`:

  ```
  mixair.shad.io {
      reverse_proxy localhost:8000
  }

  covid.shad.io {
      reverse_proxy localhost:8501
  }

  brita.shad.io {
      reverse_proxy localhost:8502
  }
  ```

- Restart Caddy.
  ```console
  $ sudo systemctl restart caddy.service
  ```

## Golang

- [Download the latest Linux ARMv8 version of Go](https://golang.org/dl/) and install.
  ```console
  $ mkdir ~/Downloads
  $ cd ~/Downloads
  $ curl -LO https://golang.org/dl/go1.15.2.linux-arm64.tar.gz
  $ sudo tar -C /usr/local -xzf go1.15.2.linux-arm64.tar.gz
  ```
