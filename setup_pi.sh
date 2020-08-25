#!/bin/bash
# Raspbian setup script for https://github.com/jantman/pi2graphite

# check arguments
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "USAGE: setup_pi.sh BASEDEV HOSTNAME AUTHKEYS_PATH [SSID PSK]"
  echo "where BASEDEV is the base device, e.g. '/dev/sdX'"
  echo "where AUTHKEYS_PATH is the path to an authorized_keys file to copy to the pi user"
  exit 0
fi

if [[ "$#" -ne 3 && "$#" -ne 5 ]]; then
  echo "ERROR: wrong number of arguments (see --help)" >&2
  exit 1
fi

# check for root
if [[ "$EUID" != "0" ]]; then
  echo "ERROR: this script must be run as root" >&2
  exit 1
fi

# assign to meaningful var names
BASEDEV=$1
HOSTNAME=$2
AUTHKEYS_PATH=$3
SSID=$4
PSK=$5
COUNTRY="US"  # WiFi Regulatory Domain

# check that partitions look right
if [[ ! -e "${BASEDEV}1" ]]; then
  echo "ERROR: ${BASEDEV}1 does not exist; wrong BASEDEV or bad partition layout" >&2
  exit 1
fi

if [[ ! -e "${BASEDEV}2" ]]; then
  echo "ERROR: ${BASEDEV}2 does not exist; wrong BASEDEV or bad partition layout" >&2
  exit 1
fi

if [[ -e "${BASEDEV}3" ]]; then
  echo "ERROR: ${BASEDEV}3 exists; wrong BASEDEV or bad partition layout" >&2
  exit 1
fi

if [[ ! -f $AUTHKEYS_PATH ]]; then
  echo "ERROR: AUTHKEYS_PATH (${AUTHKEYS_PATH}) does not exist" >&2
  exit 1
fi

# echo out settings
echo "Starting Raspbian configuration"
echo "Base device: $BASEDEV"
echo "Hostname: $HOSTNAME"
echo "Authorized keys file: $AUTHKEYS_PATH"
if [ -n "$SSID" ]; then
  echo "SSID: $SSID"
  echo "WiFi Key: $PSK"
  echo "WiFi Country: $COUNTRY"
fi

# make sure it looks right to the user
read -p "Does this look right? [y|N]" response
if [[ "$response" != "y" ]]; then
  echo "Ok, exiting." >&2
  exit 1
fi

# create a temporary directory
TMPDIR=$(mktemp -d)

# error handling
cleanup() {
  echo "Syncing disks"
  sync
  echo "Unmounting $TMPDIR"
  umount --recursive $TMPDIR
  echo "Removing $TMPDIR"
  rm -Rf $TMPDIR
}
trap cleanup 0

echo "Mounting SD card"
mount "${BASEDEV}2" $TMPDIR
mount "${BASEDEV}1" "${TMPDIR}/boot"

echo "Done mounting SD card; chroot'ing"

echo "Touching boot/ssh"
touch "${TMPDIR}/boot/ssh"

PI_UID=$(stat --printf='%u' "${TMPDIR}/home/pi")
PI_GID=$(stat --printf='%g' "${TMPDIR}/home/pi")
echo "Found pi user; UID=${PI_UID} GID=${PI_GID}"

if [[ ! -e "${TMPDIR}/home/pi/.ssh" ]]; then
  echo "Creating pi user .ssh directory"
  install -d -m 0700 -o $PI_UID -g $PI_GID "${TMPDIR}/home/pi/.ssh"
fi

AKPATH="${TMPDIR}/home/pi/.ssh/authorized_keys"
echo "Copying authorized keys file (${AUTHKEYS_PATH}) to $AKPATH"
install -m 0644 -o $PI_UID -g $PI_GID $AUTHKEYS_PATH $AKPATH

echo "Setting hostname"
echo $HOSTNAME > "${TMPDIR}/etc/hostname"
sed -i "s/raspberrypi/${HOSTNAME}/g" "${TMPDIR}/etc/hosts"

if [ -n "$SSID" ]; then
  echo "Setting up WiFi configuration..."
  if ! grep "country=${COUNTRY}" "${TMPDIR}/etc/wpa_supplicant/wpa_supplicant.conf" &>/dev/null; then
    echo "Setting country code"
    sed -i "s/country=.*/country=${COUNTRY}/" "${TMPDIR}/etc/wpa_supplicant/wpa_supplicant.conf"
  fi
  netconf=$(cat <<EOF
network={
    ssid="${SSID}"
    psk="${PSK}"
}
EOF
  )
  if ! grep "ssid=\"${SSID}\"" "${TMPDIR}/etc/wpa_supplicant/wpa_supplicant.conf" &>/dev/null; then
    echo "Adding network configuration"
    echo "$netconf" >> "${TMPDIR}/etc/wpa_supplicant/wpa_supplicant.conf"
  fi
fi
