from machine import WDT
from ota_updater import OTAUpdater
from sniffers import beacon_scanner

def do_connect(): #Funcion para conectarse al wifi
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Acciona Innovacion', 'Innovacion_IoT')
        while not wlan.isconnected():
            pass
    else:
        print('connected')
    print('network config:', wlan.ifconfig())


def download_and_install_update_if_available():
    ota_updater = OTAUpdater('https://github.com/AliasJavier/ble_code')
    ota_updater.check_for_update_to_install_during_next_reboot()
    ota_updater.download_and_install_update_if_available('Acciona Innovacion', 'Innovacion_IoT')

def start():
   scanner = beacon_scanner()
   scanner.run()



def boot():
    download_and_install_update_if_available()
    start()



do_connect()
boot()

