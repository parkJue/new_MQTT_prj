from pymodbus.client import ModbusTcpClient
import random
from threading import Thread
import time
import struct
import json
import paho.mqtt.client as mqtt
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    print('result code ' + str(rc))

mqttc = mqtt.Client()
modtc = ModbusTcpClient(host="127.0.0.1", port=503)

mqttc.on_connect = on_connect
mqttc.connect('localhost', 1883, 60)

mqttc.loop_start()

pcs_data = {
    'active_power': 0,
    'frequency': 0,
    'R_vol': 0,
    'S_vol': 0,
    'T_vol': 0,
    'R_cur': 0,
    'S_cur': 0,
    'T_cur': 0,
}

bat_data = {
    'SOC': 0,
    'SOH': 0,
    'vol': 0,
    'cur': 0,
}

def write_data():
    while True:
        for key in pcs_data:
            if 'vol' in key:
                pcs_data[key] = random.uniform(400, 500)
            elif key == 'frequency':
                pcs_data[key] = random.uniform(60, 61)
            else:
                pcs_data[key] = random.uniform(0, 100)
        for key in bat_data:
            bat_data[key] = random.uniform(0, 1000) if key in ['vol', 'cur'] else random.uniform(0, 100)


        all_values = []
        for value in list(pcs_data.values()) + list(bat_data.values()):
            packed_data = struct.pack('>f', value)
            registers = struct.unpack('>HH', packed_data)

            all_values.extend(registers)

        
        # 레지스터에 모든 데이터를 한 번에 쓰기
        modtc.write_registers(0, all_values[0])

        print(datetime.now())
        time.sleep(1)

def read_data():
    while True:
        # 모든 PCS 및 BAT 데이터에 대한 레지스터 수 계산
        num_registers = 2 * (len(pcs_data) + len(bat_data))  # 각 데이터 포인트에 2개 레지스터가 필요

        # Modbus 레지스터에서 데이터 읽기
        all_data = modtc.read_holding_registers(0, num_registers, unit=1)
        if not all_data.isError():
            pcs_values = all_data.registers[:2*len(pcs_data)]
            bat_values = all_data.registers[2*len(pcs_data):]

            # PCS 데이터 변환
            for i, key in enumerate(pcs_data.keys()):
                packed_data = struct.pack('>HH', pcs_values[2*i], pcs_values[2*i+1])
                pcs_data[key], = struct.unpack('>f', packed_data)

            # BAT 데이터 변환
            for i, key in enumerate(bat_data.keys()):
                packed_data = struct.pack('>HH', bat_values[2*i], bat_values[2*i+1])
                bat_data[key], = struct.unpack('>f', packed_data)

        mqttc.publish('mqtt/pcs', json.dumps(pcs_data))
        mqttc.publish('mqtt/bat', json.dumps(bat_data))

        time.sleep(1)

def main():
    try:
        # write_thread = Thread(target=write_data)
        write_data()
        # read_thread = Thread(target=read_data)

        # write_thread.start()
        # read_thread.start()

        # write_thread.join()
        # read_thread.join()

    except KeyboardInterrupt:
        print("프로그램 종료.")
    finally:
        modtc.close()

if __name__ == "__main__":
    main()