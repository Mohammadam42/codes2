from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Setup
mqtt_broker = "mqtt.eclipse.org"  # Change this to your broker
mqtt_port = 1883
mqtt_topic = "robot/status"
mqtt_client = mqtt.Client()

# Robot state
robot_status = "Stopped"
voltage = 30  # Default voltage value
schedule = []

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    global robot_status
    payload = msg.payload.decode("utf-8")
    if payload == "start":
        robot_status = "Running"
    elif payload == "stop":
        robot_status = "Stopped"

# Connect MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# Routes
@app.route('/')
def index():
    return render_template('index.html', robot_status=robot_status, voltage=voltage, schedule=schedule)

@app.route('/start', methods=['POST'])
def start_robot():
    mqtt_client.publish(mqtt_topic, "start")
    return jsonify(status="Started")

@app.route('/stop', methods=['POST'])
def stop_robot():
    mqtt_client.publish(mqtt_topic, "stop")
    return jsonify(status="Stopped")

@app.route('/schedule', methods=['POST'])
def set_schedule():
    days = request.json.get('days')
    time = request.json.get('time')
    global schedule
    schedule = {"days": days, "time": time}
    return jsonify(schedule=schedule)

@app.route('/status')
def status():
    return jsonify(robot_status=robot_status, voltage=voltage, schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True)
