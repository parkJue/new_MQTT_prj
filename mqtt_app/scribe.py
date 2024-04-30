import paho.mqtt.client as mqtt
import json
import mysql.connector

# MariaDB 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="your_database"
)

cursor = db.cursor()

def save_to_db(topic, payload):
    data = json.loads(payload)
    if topic == 'mqtt/pcs':
        cursor.execute("""
            INSERT INTO PCSData (active_power, frequency, R_vol, S_vol, T_vol, R_cur, S_cur, T_cur)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['active_power'], data['frequency'], data['R_vol'], data['S_vol'], data['T_vol'], data['R_cur'], data['S_cur'], data['T_cur']))
    elif topic == 'mqtt/bat':
        cursor.execute("""
            INSERT INTO BATData (SOC, SOH, vol, cur)
            VALUES (%s, %s, %s, %s)
        """, (data['SOC'], data['SOH'], data['vol'], data['cur']))
    db.commit()

def on_message(client, userdata, msg):
    print('Message received on topic:', msg.topic)
    save_to_db(msg.topic, msg.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('localhost', 1883, 60)
client.subscribe('mqtt/pcs')
client.subscribe('mqtt/bat')

client.loop_forever()
