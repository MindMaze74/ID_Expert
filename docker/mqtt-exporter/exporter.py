import json
import os
import yaml
import time
from prometheus_client import start_http_server, Gauge, Info, Counter
import paho.mqtt.client as mqtt

gps_lat = Gauge('vehicle_gps_lat', 'GPS latitude', ['vehicle_id', 'vehicle_type', 'fuel_type'])
gps_lon = Gauge('vehicle_gps_lon', 'GPS longitude', ['vehicle_id', 'vehicle_type', 'fuel_type'])
gps_alt = Gauge('vehicle_gps_alt', 'GPS altitude', ['vehicle_id', 'vehicle_type', 'fuel_type'])
speed_kmh = Gauge('vehicle_speed_kmh', 'Speed km/h', ['vehicle_id', 'vehicle_type', 'fuel_type'])
engine_status = Gauge('vehicle_engine_status', 'Engine status (1=on, 0=off)', ['vehicle_id', 'vehicle_type', 'fuel_type'])

engine_rpm = Gauge('vehicle_engine_rpm', 'Engine RPM', ['vehicle_id', 'vehicle_type', 'fuel_type'])
fuel_level_pct = Gauge('vehicle_fuel_level_pct', 'Fuel level %', ['vehicle_id', 'vehicle_type', 'fuel_type'])
temp_c = Gauge('vehicle_temp_c', 'Temperature Celsius', ['vehicle_id', 'vehicle_type', 'fuel_type'])
oil_pressure_bar = Gauge('vehicle_oil_pressure_bar', 'Oil pressure bar', ['vehicle_id', 'vehicle_type', 'fuel_type'])
engine_hours = Gauge('vehicle_engine_hours', 'Engine hours', ['vehicle_id', 'vehicle_type', 'fuel_type'])

battery_soc_pct = Gauge('vehicle_battery_soc_pct', 'Battery SoC %', ['vehicle_id', 'vehicle_type', 'fuel_type'])
battery_temp_c = Gauge('vehicle_battery_temp_c', 'Battery temp C', ['vehicle_id', 'vehicle_type', 'fuel_type'])
current_a = Gauge('vehicle_current_a', 'Current A', ['vehicle_id', 'vehicle_type', 'fuel_type'])
voltage_v = Gauge('vehicle_voltage_v', 'Voltage V', ['vehicle_id', 'vehicle_type', 'fuel_type'])

mode = Info('vehicle_mode', 'Robot mode', ['vehicle_id', 'vehicle_type', 'fuel_type'])
mission_status = Info('vehicle_mission_status', 'Mission status', ['vehicle_id', 'vehicle_type', 'fuel_type'])
mission_id = Info('vehicle_mission_id', 'Mission ID', ['vehicle_id', 'vehicle_type', 'fuel_type'])
estop_status = Info('vehicle_estop_status', 'E-stop status', ['vehicle_id', 'vehicle_type', 'fuel_type'])
rtk_status = Info('vehicle_rtk_status', 'RTK status', ['vehicle_id', 'vehicle_type', 'fuel_type'])
steering_angle_deg = Gauge('vehicle_steering_angle_deg', 'Steering angle deg', ['vehicle_id', 'vehicle_type', 'fuel_type'])
temp_cpu_c = Gauge('vehicle_temp_cpu_c', 'CPU temp C', ['vehicle_id', 'vehicle_type', 'fuel_type'])
lte_rssi = Gauge('vehicle_lte_rssi', 'LTE RSSI', ['vehicle_id', 'vehicle_type', 'fuel_type'])

events_total = Counter('vehicle_events_total', 'Total events', ['vehicle_id', 'vehicle_type', 'fuel_type', 'event_type', 'severity'])
last_seen = Gauge('vehicle_last_seen_timestamp', 'Last seen unix timestamp', ['vehicle_id', 'vehicle_type', 'fuel_type'])

def on_connect(client, userdata, flags, rc):
    print(f"Connected with code {rc}")
    for topic in topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)
    except:
        return
    parts = msg.topic.split('/')
    if len(parts) != 4:
        return
    vehicle_type, fuel_type, vehicle_id, _ = parts
    last_seen.labels(vehicle_id, vehicle_type, fuel_type).set(time.time())
    metrics = payload.get('metrics', {})
    if 'gps_lat' in metrics:
        gps_lat.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['gps_lat'])
    if 'gps_lon' in metrics:
        gps_lon.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['gps_lon'])
    if 'gps_alt' in metrics:
        gps_alt.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['gps_alt'])
    if 'speed_kmh' in metrics:
        speed_kmh.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['speed_kmh'])
    if 'engine_status' in metrics:
        engine_status.labels(vehicle_id, vehicle_type, fuel_type).set(1 if metrics['engine_status'] == 'on' else 0)

    if fuel_type == 'diesel' or vehicle_type in ['tractor', 'cart']:
        if 'engine_rpm' in metrics:
            engine_rpm.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['engine_rpm'])
        if 'fuel_level_pct' in metrics:
            fuel_level_pct.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['fuel_level_pct'])
        if 'temp_c' in metrics:
            temp_c.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['temp_c'])
        if 'oil_pressure_bar' in metrics:
            oil_pressure_bar.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['oil_pressure_bar'])
        if 'engine_hours' in metrics:
            engine_hours.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['engine_hours'])

    if fuel_type == 'electric' or vehicle_type in ['forklift', 'robot', 'cart']:
        if 'battery_soc_pct' in metrics:
            battery_soc_pct.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['battery_soc_pct'])
        if 'battery_temp_c' in metrics:
            battery_temp_c.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['battery_temp_c'])
        if 'current_a' in metrics:
            current_a.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['current_a'])
        if 'voltage_v' in metrics:
            voltage_v.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['voltage_v'])

    if vehicle_type == 'robot':
        if 'mode' in metrics:
            mode.labels(vehicle_id, vehicle_type, fuel_type).info({'mode': metrics['mode']})
        if 'mission_status' in metrics:
            mission_status.labels(vehicle_id, vehicle_type, fuel_type).info({'status': metrics['mission_status']})
        if 'mission_id' in metrics:
            mission_id.labels(vehicle_id, vehicle_type, fuel_type).info({'id': metrics['mission_id']})
        if 'estop_status' in metrics:
            estop_status.labels(vehicle_id, vehicle_type, fuel_type).info({'status': metrics['estop_status']})
        if 'rtk_status' in metrics:
            rtk_status.labels(vehicle_id, vehicle_type, fuel_type).info({'status': metrics['rtk_status']})
        if 'steering_angle_deg' in metrics:
            steering_angle_deg.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['steering_angle_deg'])
        if 'temp_cpu_c' in metrics:
            temp_cpu_c.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['temp_cpu_c'])
        if 'lte_rssi' in metrics:
            lte_rssi.labels(vehicle_id, vehicle_type, fuel_type).set(metrics['lte_rssi'])

    for evt in payload.get('events', []):
        events_total.labels(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            event_type=evt.get('event_type', 'unknown'),
            severity=evt.get('severity', 'info')
        ).inc()

def main():
    global topics
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        topics = config.get('topics', [])
    broker = os.getenv('MQTT_BROKER', 'mqtt://mosquitto:1883')
    if broker.startswith('mqtt://'):
        broker = broker[7:]
    host, port = broker.split(':') if ':' in broker else (broker, 1883)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, int(port))
    client.loop_start()
    port_http = int(os.getenv('METRICS_PORT', '9125'))
    start_http_server(port_http)
    print(f"MQTT exporter listening on {port_http}")
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
