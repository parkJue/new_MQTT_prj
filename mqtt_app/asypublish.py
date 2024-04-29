import random
import struct
import json
import paho.mqtt.client as mqtt
import asyncio
from pymodbus.client import AsyncModbusTcpClient

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

async def write_data(client, mqttc):
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

        await client.write_registers(0, all_values, unit=1)
        await asyncio.sleep(1)

async def read_data(client, mqttc):
    while True:
        response = await client.read_holding_registers(0, len(pcs_data) + len(bat_data), unit=1)
        if not response.isError():
            data = response.registers
            # 읽은 데이터를 적절하게 할당
            pcs_values = data[:len(pcs_data)]
            bat_values = data[len(pcs_data):]

            for i, key in enumerate(pcs_data.keys()):
                pcs_data[key] = pcs_values[i]
            for i, key in enumerate(bat_data.keys()):
                bat_data[key] = bat_values[i]

            mqttc.publish('sensor/pcs', json.dumps(pcs_data))
            mqttc.publish('sensor/bat', json.dumps(bat_data))

async def main():
    mqttc = mqtt.Client()
    mqttc.connect('localhost', 1883, 60)
    mqttc.loop_start()

    async with AsyncModbusTcpClient('127.0.0.1') as client:
        await asyncio.gather(
            write_data(client, mqttc),
            read_data(client, mqttc),
            return_exceptions=True
        )

if __name__ == "__main__":
    asyncio.run(main())
