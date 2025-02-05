import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import threading
import time
import json

BROKER = "test.mosquitto.org"

class GerenciadorSensores:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Sensores")
        self.root.geometry("500x400")
        self.root.resizable(False, True)

        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(BROKER)

        self.sensores_disponiveis = {}
        self.sensores_subscritos = {}

        self.setup_ui()
        threading.Thread(target=self.monitorar, daemon=True).start()

    def setup_ui(self):
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill="x")

        tk.Label(frame_top, text="Sensores disponíveis:", font=("Arial", 10, "bold")).pack(anchor="w")

        self.combobox_sensores = ttk.Combobox(frame_top, state="readonly", width=40)
        self.combobox_sensores.pack(pady=5, anchor="w")

        self.btn_adicionar = tk.Button(frame_top, text="Escutar Sensor", command=self.adicionar_sensor)
        self.btn_adicionar.pack(pady=5, anchor="w")

        self.frame_sensores = tk.Frame(self.root, padx=10, pady=5)
        self.frame_sensores.pack(fill="both", expand=True)

        self.client.subscribe("discovery/sensores")

    def adicionar_sensor(self):
        topico = self.combobox_sensores.get()
        if topico and topico not in self.sensores_subscritos:
            info = self.sensores_disponiveis[topico]
            self.sensores_subscritos[topico] = self.criar_frame_sensor(info)
            self.client.subscribe(topico)

    def criar_frame_sensor(self, info):
        frame_sensor = tk.Frame(self.frame_sensores, pady=5, padx=5, relief="groove", borderwidth=2)
        frame_sensor.pack(fill="x", padx=5, pady=5, anchor="w")

        if info['tipo'] == 'Temperatura':
            sufix = '°C'
        elif info['tipo'] == 'Pressao':
            sufix = 'bar'
        elif info['tipo'] == 'Umidade':
            sufix = '% UR'
        else:
            sufix = 'rpm'

        label = tk.Label(frame_sensor, text=f"Sensor | Tópico: {info['topic']} | min: {info['min_val']}{sufix} max: {info['max_val']}{sufix} ({info['tipo']})", font=("Arial", 10, "bold"))
        label.pack(anchor="w")

        texto_saida = tk.Text(frame_sensor, height=5, width=50, wrap="word")
        texto_saida.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(frame_sensor, command=texto_saida.yview)
        scrollbar.pack(side="right", fill="y")
        texto_saida.config(yscrollcommand=scrollbar.set)
        texto_saida.tag_config("alert", foreground="red")

        texto_saida.tag_configure("WARN", foreground="red")
        texto_saida.tag_configure("INFO", foreground="black")

        return texto_saida

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            topic = msg.topic

            if topic == "discovery/sensores":
                sensor_info = json.loads(payload)
                sensor_topic = sensor_info["topic"]

                if sensor_topic not in self.sensores_disponiveis:
                    self.sensores_disponiveis[sensor_topic] = sensor_info
                    self.combobox_sensores["values"] = list(self.sensores_disponiveis.keys())

            elif topic in self.sensores_subscritos:
                if "[WARN]" in payload:
                    self.log_mensagem(topic, payload, "WARN")
                else:
                    self.log_mensagem(topic, payload, "INFO")

        except Exception as e:
            print(f"Erro: {str(e)}")

    def log_mensagem(self, topico, mensagem, tag):
        info = self.sensores_disponiveis.get(topico, {})
        tipo = info.get("tipo", "")
        if tag == 'INFO':
                    sufix = ''
        elif tipo == "Temperatura":
            sufix = "°C"
        elif tipo == "Pressao":
            sufix = " bar"
        elif tipo == "Umidade":
            sufix = "% UR"
        else:
            sufix = "rpm"

        if topico in self.sensores_subscritos:
            caixa_mensagem = self.sensores_subscritos[topico]
            caixa_mensagem.insert(tk.END, mensagem + sufix + "\n", tag)
            caixa_mensagem.see(tk.END)

    def monitorar(self):
        self.client.loop_start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorSensores(root)
    root.mainloop()
