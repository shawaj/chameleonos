
import logging
import os
import psutil
import subprocess

from typing import Any, Dict, Optional, Tuple


ETH_MAC_FILE = '/sys/class/net/eth0/address'
WLAN_MAC_FILE = '/sys/class/net/wlan0/address'
FW_VERSION_CMD = '/sbin/fwupdate current'
UPTIME_CMD = 'cat /proc/uptime | grep -oE "^[[:digit:]]+"'
REBOOT_CMD = '/sbin/reboot'
NET_TEST_CMD = '/sbin/nettest'
DATA_DIR = '/data'

LOG_DIR = '/var/log'
MINER_DATA_DIR = '/var/lib/miner'
FACTORY_RESET_SERVICES = ['miner', 'packetforwarder', 'gatewayconfig', 'connman']
FACTORY_RESET_CONF_FILES = [
    '/var/lib/reg.conf',
    '/data/etc/nat.conf',
    '/data/etc/packet_forwarder.conf'
    '/data/etc/ledstrip.conf'
]
FACTORY_RESET_CONNMAN_PATH_PREFIXES = [
    '/var/lib/connman/wifi_*',
    '/var/lib/connman/ethernet_*'
]


def get_rpi_sn() -> str:
    with open('/proc/cpuinfo', 'rt') as f:
        for line in f:
            if line.startswith('Serial'):
                return line.strip()[-8:]

    return '00000000'


def reboot() -> None:
    logging.info('rebooting')
    os.system(REBOOT_CMD)


def factory_reset() -> None:
    logging.info('factory resetting')

    for service in FACTORY_RESET_SERVICES:
        try:
            logging.info('stopping %s', service)
            subprocess.check_output(f'service {service} stop', shell=True)

        except Exception:
            pass

    for file in FACTORY_RESET_CONF_FILES:
        logging.info('removing %s', file)
        os.system(f'rm -f {file}')

    logging.info('removing network settings')
    for prefix in FACTORY_RESET_CONNMAN_PATH_PREFIXES:
        os.system(f'rm -rf {prefix}')

    logging.info('removing log files')
    os.system(f'rm -rf {LOG_DIR}/*')

    logging.info('removing miner data')
    os.system(f'rm -rf {MINER_DATA_DIR}')

    logging.info('rebooting')
    os.system(REBOOT_CMD)


def get_eth_mac() -> Optional[str]:
    try:
        with open(ETH_MAC_FILE, 'rt') as f:
            return f.read().strip()

    except Exception:
        pass


def get_wlan_mac() -> Optional[str]:
    try:
        with open(WLAN_MAC_FILE, 'rt') as f:
            return f.read().strip()

    except Exception:
        pass


def get_uptime() -> Optional[int]:
    try:
        return int(subprocess.check_output(UPTIME_CMD, shell=True).decode().strip())

    except Exception:
        pass


def get_fw_version() -> Optional[str]:
    try:
        return subprocess.check_output(FW_VERSION_CMD, shell=True).decode().strip()

    except Exception:
        pass


def get_cpu_usage() -> float:
    return psutil.cpu_percent()


def get_mem_info() -> Tuple[int, int]:
    vm = psutil.virtual_memory()
    return int(vm.used / 1024 / 1024), int(vm.total / 1024 / 1024)


def get_storage_info() -> Tuple[int, int]:
    du = psutil.disk_usage(DATA_DIR)
    return int(du.used / 1024 / 1024), int(du.total / 1024 / 1024)


def get_temperature() -> int:
    return int(psutil.sensors_temperatures()['cpu_thermal'][0].current)


def net_test() -> Dict[str, Any]:
    result = {
        'download_speed': None,
        'latency': None,
        'public_ip': None
    }

    try:
        output = subprocess.check_output(NET_TEST_CMD, shell=True).decode().strip()

    except Exception:
        return result

    for line in output.split('\n'):
        parts = line.split(':', 1)
        if len(parts) < 2:
            continue

        key, value = parts
        key = key.strip().lower().replace(' ', '_')
        value = value.strip()

        # Decode numeric values
        if key in ('download_speed', 'latency'):
            value = float(value.split()[0]) or None
            if value > 10:
                value = int(value)

        result[key] = value

    return result
