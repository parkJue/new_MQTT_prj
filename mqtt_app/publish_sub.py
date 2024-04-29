from pymodbus.client import ModbusTcpClient
import random
from threading import Thread
import time
import struct
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print('result code ' + str(rc))

mqttc = mqtt.Client()
modtc = ModbusTcpClient(host="127.0.0.1", port=502)

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
    scale_factor = 1000
    while True:
        # 부동소수점 값들을 직접 Modbus 레지스터에 저장 
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


        # 스케일링 방법 - 소수점세자리 방법 연구 필요 
        # for key in pcs_data:
        #     if 'vol' in key:
        #         pcs_data[key] = random.uniform(400, 500)
        #     elif key == 'frequency':
        #         pcs_data[key] = random.uniform(60, 61)
        #     else:
        #         pcs_data[key] = random.uniform(0, 100)
        # for key in bat_data:
        #     bat_data[key] = random.uniform(0, 1000) if key in ['vol', 'cur'] else random.uniform(0, 100)
        
        # all_values = []
        # max_value=65535
        # for value in list(pcs_data.values()) + list(bat_data.values()):
        #     scaled_value = int(value * scale_factor)
        #     if scaled_value > max_value:
        #         scaled_value = max_value  # 최대값을 초과하지 않도록 조정
        #     scaled_value = round(scaled_value, 3)
        #     all_values.append(scaled_value)


        # 레지스터에 모든 데이터를 한 번에 쓰기
        modtc.write_registers(0, all_values)

        time.sleep(1)

def read_data():
    while True:
        all_data = modtc.read_holding_registers(0, len(pcs_data) + len(bat_data), unit=1)
        if not all_data.isError():
            # 읽은 데이터를 적절하게 할당
            pcs_values = all_data.registers[:len(pcs_data)]
            bat_values = all_data.registers[len(pcs_data):]

            for i, key in enumerate(pcs_data.keys()):
                pcs_data[key] = pcs_values[i]
            for i, key in enumerate(bat_data.keys()):
                bat_data[key] = bat_values[i]

        mqttc.publish('sensor/pcs', json.dumps(pcs_data))
        mqttc.publish('sensor/bat', json.dumps(bat_data))

        # print("PCS 데이터:", pcs_data)
        # print("BAT 데이터:", bat_data)
        
def main():
    try:
        write_thread = Thread(target=write_data)
        read_thread = Thread(target=read_data)

        write_thread.start()
        read_thread.start()

        write_thread.join()
        read_thread.join()

    except KeyboardInterrupt:
        print("프로그램 종료.")
    finally:
        modtc.close()

if __name__ == "__main__":
    main()