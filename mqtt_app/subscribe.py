import paho.mqtt.client as mqtt
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

# MQTT 클라이언트가 브로커에 연결되었을 때 호출
# 연결이 성공적으로 이루어졌는지 확인하고 필요한 초기화 작업 수행
def on_connect(client, userdata, flags, rc):
    print('flags : ' + str(flags))
    print('result code ' + str(rc))


# 토픽으로 구독한 메시지를 확인할 수 있고 메시지를 가지고 수행할 기능을 넣음 
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    redis_client.set(msg.topic, msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('localhost', 1883, 60)


client.subscribe('mqtt/pcs')
client.subscribe('mqtt/bat')

client.loop_forever()