import bluetooth
from micropython import const
from mat_controller import MatController

# BLEeventDef
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

##UUID
_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_RX_CHAR_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

class AppFramework:
    def __init__(self, device_name="DogMat"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._on_ble_event)
        
        rx_char = (_RX_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE)
        service = (_SERVICE_UUID, (rx_char,),)
        ((self.rx_handle,),) = self.ble.gatts_register_services((service,))
        
        self.controller = MatController()
        self._start_advertising(device_name)

    def _on_ble_event(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            print("[BLE] Connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            print("[BLE] Disconnected")
            self._start_advertising()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self.rx_handle:
                command = self.ble.gatts_read(self.rx_handle).decode('utf-8').strip()
                # 
                self.controller.execute(command)

    def _start_advertising(self, name="DogMat"):
        name_bytes = bytes(name, 'utf-8')
        adv_data = bytearray(b'\x02\x01\x06') + bytearray((len(name_bytes) + 1, 0x09)) + name_bytes
        self.ble.gap_advertise(100000, adv_data=adv_data)
        print(f"[BLE] Waiting for connection as '{name}'...")

if __name__ == "__main__":
    app = AppFramework()
    while True:
        pass