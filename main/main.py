import machine
from ota_updater import OTAUpdater


def download_and_install_update_if_available():
    ota_updater = OTAUpdater('https://github.com/AliasJavier/ble_code.git')
    ota_updater.download_and_install_update_if_available('Acciona Innovacion', 'Innovacion_IoT')

def start():
   print("DOOOOoaa")

def boot():
    download_and_install_update_if_available()
    start()


boot()



