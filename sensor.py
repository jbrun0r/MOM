import paho.mqtt.client as mqtt
import threading
import random
import time

BROKER = "test.mosquitto.org"

class Sensor:
    def __init__(self, topic, tipo, min_val, max_val):
        self.topic = topic
        self.tipo = tipo
        self.min_val = min_val
        self.max_val = max_val
        self.running = False
        self.client = mqtt.Client(self.topic)
        self.client.connect(BROKER)

        # Publica seu próprio tópico no canal de descoberta
        self.client.publish("discovery/sensores", self.topic)

    def ligar(self):
        self.running = True
        threading.Thread(target=self._gerar_valores, daemon=True).start()

    def desligar(self):
        self.running = False

    def _gerar_valores(self):
        while self.running:
            valor = random.uniform(self.min_val - 5, self.max_val + 5)
            
            if valor <= self.min_val or valor >= self.max_val:
                valor_str = f"\033[91m{valor:.2f}\033[0m"
                self.client.publish(self.topic, valor_str)
            else:
                valor_str = f"{valor:.2f}"
            
            print(f"[{self.topic}]: {valor_str}")
            time.sleep(1)


if __name__ == "__main__":
    sensor = Sensor('sensor/vento', "Velocidade", 0, 10)
    sensor.ligar()

    while True:
        pass
