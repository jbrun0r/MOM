import paho.mqtt.client as mqtt
import threading
import random
import time
import json
from datetime import datetime

BROKER = "test.mosquitto.org"

class Sensor:
    def __init__(self):
        self.topic = ""
        self.tipo = ""
        self.min_val = 0
        self.max_val = 0
        self.running = False
        self.client = mqtt.Client()
        self.client.connect(BROKER)

    def setup(self):
        self.topic = input("Tópico: ").strip()
        self.tipo = input("Tipo: ").strip()
        self.min_val = int(input("Min: ").strip())
        self.max_val = int(input("Max: ").strip())

        sensor_info = json.dumps({
            "topic": self.topic,
            "tipo": self.tipo,
            "min_val": self.min_val,
            "max_val": self.max_val
        })
        self.client.publish("discovery/sensores", sensor_info)

        self.ligar()

    def ligar(self):
        self.running = True
        self.client.publish(self.topic, f'[INFO][{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: ON')
        threading.Thread(target=self._gerar_valores, daemon=True).start()

    def desligar(self):
        print(f"\nDesligando sensor {self.topic}...")
        self.client.publish(self.topic, f'[INFO][{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: OFF')
        self.running = False
        self.client.disconnect()
        print("Sensor desligado.")
        exit(0)

    def _gerar_valores(self):
        while self.running:
            valor = random.uniform(self.min_val - 5, self.max_val + 5)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            mensagem = f"[WARN][{timestamp}]: {valor:.2f}"
            if valor <= self.min_val or valor >= self.max_val:
                valor_str = f"\033[91m{valor:.2f}\033[0m"
                self.client.publish(self.topic, mensagem)
            else:
                valor_str = f"{valor:.2f}"

            print(f"[{self.topic}]: {valor_str}")
            
            time.sleep(1)

if __name__ == "__main__":
    sensor = Sensor()
    sensor.setup()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sensor.desligar()
