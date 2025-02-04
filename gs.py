import paho.mqtt.client as mqtt
import time

BROKER = "test.mosquitto.org"

class GerenciadorSensores:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(BROKER)

        self.sensores = set()  # Armazena os tópicos dos sensores descobertos

        # Escuta o canal de descoberta para novos sensores
        self.client.subscribe("discovery/sensores")
        print("Aguardando sensores se registrarem...")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            topic = msg.topic

            if topic == "discovery/sensores":
                if payload not in self.sensores:
                    self.sensores.add(payload)
                    self.client.subscribe(payload)  # Faz subscribe no novo sensor
                    print(f"Novo sensor detectado: {payload}")

            else:
                print(f"[{topic}]: {payload}")  # Exibe as mensagens dos sensores monitorados

        except:
            pass

    def monitorar(self):
        print("Monitorando sensores...")
        self.client.loop_start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.client.loop_stop()
            print("Monitoramento encerrado.")

if __name__ == "__main__":
    gs = GerenciadorSensores()
    gs.monitorar()
