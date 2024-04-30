from django.http import JsonResponse
import redis, json
from django.shortcuts import render
# Redis 연결 설정
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def fetch_data(request):
    # Redis에서 데이터를 가져옴
    pcs_data = json.loads(redis_client.get('mqtt/pcs'))
    bat_data = json.loads(redis_client.get('mqtt/bat'))
    
    # JSON 형태로 웹에 반환
    return JsonResponse({
        'pcs_data': pcs_data,
        'bat_data': bat_data,
    })

def index(request):
    return render(request, 'mqtt_app/index.html')