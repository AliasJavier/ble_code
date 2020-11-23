import network
import time
from ubluetooth import BLE, UUID, FLAG_NOTIFY, FLAG_READ, FLAG_WRITE
import ubinascii
from micropython import const
import urequests as requests
from machine import Pin, WDT

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)
_IRQ_GATTS_INDICATE_DONE = const(20)
_IRQ_MTU_EXCHANGED = const(21)

class beacon_scanner:
    def __init__(self):
        a=0
        while a<=10:
          a=a+1
          print("REINICIO\n")


        self.wdt= WDT(timeout=100000) #Watchdog configurado para que si no se alimenta en 100 seg realimente
        self.p13 = Pin(13, Pin.IN) #Pin para interrumpir el main

        self.mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
        print("Esto es la mac:",self.mac)

        # Scan for 10s (at 100% duty cycle)
        self.bt = BLE()

        self.lista_id=[]
        self.lista_rssi=[]

    def filtro(self, data):
        if "0201061aff4c000215" in data: #Filtramos los dispositivos deseados a partir de su mac
          return True
        else:
            return False

    def adv_decode(self, adv_type, data):
        i = 0
        while i + 1 < len(data):
            if data[i + 1] == adv_type:
                return data[i + 2:i + data[i] + 1]
            i += 1 + data[i]
        return None

    def adv_decode_name(self, data):
        n = self.adv_decode(0x09, data)
        if n:
            return n.decode('utf-8')
        return data
    def do_connect(self): #Funcion para conectarse al wifi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('Acciona Innovacion', 'Innovacion_IoT')
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())

    def bt_irq(self, event, data):

        #i=0
        if event == _IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral.
            conn_handle, addr_type, addr = data
        elif event == _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            conn_handle, addr_type, addr = data
        elif event == _IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.
            conn_handle, attr_handle = data
        elif event == _IRQ_GATTS_READ_REQUEST:
            # A client has issued a read. Note: this is a hard IRQ.
            # Return None to deny the read.
            # Note: This event is not supported on ESP32.
            conn_handle, attr_handle = data
        elif event == _IRQ_SCAN_RESULT: #Cuando escanea algo interrumpe aqui
            # A single scan result.
            addr_type, addr, adv_type, rssi, adv_data = data

            addr = ubinascii.hexlify(addr)
            adv_data = ubinascii.hexlify(adv_data)
            if self.filtro(adv_data) == True:
            #if filtro(addr) == True:  #Introducimos la mac para el filtro

              self.lista_id.append({"addr": addr, "rssi": rssi})

              #= urequests.post("https://innovacion-smartoffice.azurewebsites.net/snifferbluetooth/",

              #print(adv_data)
              #print("addr_type", "PUBLIC" if addr_type == 0 else "RANDOM",
               #    "addr", addr, "adv_type",adv_type,"rssi", rssi,
                #  "adv_data", adv_data )
              self.wdt.feed()





        elif event == _IRQ_SCAN_DONE:
            # Scan duration finished or manually stopped.
            import gc
            import micropython
            gc.collect()
            micropython.mem_info()
            print('-----------------------------')
            print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
            pass
        elif event == _IRQ_PERIPHERAL_CONNECT:
            # A successful gap_connect().
            conn_handle, addr_type, addr = data
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Connected peripheral has disconnected.
            conn_handle, addr_type, addr = data
        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Called for each service found by gattc_discover_services().
            conn_handle, start_handle, end_handle, uuid = data
        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Called once service discovery is complete.
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, status = data
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Called for each characteristic found by gattc_discover_services().
            conn_handle, def_handle, value_handle, properties, uuid = data
        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # Called once service discovery is complete.
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, status = data
        elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
            # Called for each descriptor found by gattc_discover_descriptors().
            conn_handle, dsc_handle, uuid = data
        elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
            # Called once service discovery is complete.
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, status = data
        elif event == _IRQ_GATTC_READ_RESULT:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data
        elif event == _IRQ_GATTC_READ_DONE:
            # A gattc_read() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
        elif event == _IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
        elif event == _IRQ_GATTC_NOTIFY:
            # A server has sent a notify request.
            conn_handle, value_handle, notify_data = data
        elif event == _IRQ_GATTC_INDICATE:
            # A server has sent an indicate request.
            conn_handle, value_handle, notify_data = data
        elif event == _IRQ_GATTS_INDICATE_DONE:
            # A client has acknowledged the indication.
            # Note: Status will be zero on successful acknowledgment, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
        elif event == _IRQ_MTU_EXCHANGED:
            # MTU exchange complete (either initiated by us or the remote device).
            conn_handle, mtu = data

    def run(self):
        #self.do_connect()

        self.bt.active(True)
        self.bt.irq(handler=self.bt_irq)
        while self.p13.value() != 1:
          self.bt.gap_scan(1000, 30000, 30000) #Escaneo total 1000 ms, cada 30000 us escanea, y escanea durante 30000 us
          time.sleep(5)
          if len(self.lista_id) >= 1:
                    url = "http://innovacion-smartoffice.azurewebsites.net/snifferbluetooth/"
                    data = self.mac + '\n'
                    for elemento in self.lista_id:
                      data = data + elemento['addr'].decode("utf-8")  + "," #Lo ponemos en el formato deseado
                      data = data + str(elemento['rssi']) +"\n"

                    print(data)
                    header_data = { "content-type": 'text/plain'}
                    try: #Comprueba si puede enviar por wifi
                      r = requests.post(url, data=data, headers = header_data)
                      results = r.text
                      print(results)
                      self.lista_id= []
                    except: #En caso de no estar conectado lo forzamos a reconectarse
                      self.do_connect()

        #bt.gap_connect(0, b'\xf4^\xab\x91k\x97', 2000)
        #bt.gattc_discover_services(0)

















