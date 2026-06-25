import tkinter as tk
from tkinter import font as tkfont
import paho.mqtt.client as mqtt
import threading
import time

BROKER = "broker.hivemq.com"
PORT   = 1883

TOPIC_LIGHT       = "home/livingroom/light"
TOPIC_BLINDS      = "home/livingroom/blinds"
TOPIC_TEMPERATURE = "home/kitchen/temperature"
TOPIC_PIR         = "home/bedroom/pir"
TOPIC_BUTTON      = "home/button"
TOPIC_GESTURE     = "home/gesture"

# Farben
BG        = "#1a1a2e"
CARD      = "#16213e"
ACCENT    = "#0f3460"
ON_COLOR  = "#e2b714"
OFF_COLOR = "#3a3a5c"
TEXT      = "#eaeaea"
MUTED     = "#888aaa"
GREEN     = "#4ecca3"
RED       = "#e84545"


class SmartHomeDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Home Dashboard")
        self.root.configure(bg=BG)
        self.root.geometry("900x620")
        self.root.resizable(False, False)

        # Zustandsvariablen
        self.light_on   = tk.BooleanVar(value=False)
        self.blinds_open = tk.BooleanVar(value=False)
        self.temperature = tk.StringVar(value="--")
        self.pir_active  = tk.BooleanVar(value=False)
        self.last_gesture = tk.StringVar(value="–")
        self.last_button  = tk.StringVar(value="–")
        self.mqtt_status  = tk.StringVar(value="Verbinde...")
        self.log_lines = []

        self._build_ui()
        self._connect_mqtt()

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(header, text="🏠  Smart Home Dashboard",
                 font=("Helvetica", 20, "bold"), bg=BG, fg=TEXT).pack(side="left")
        tk.Label(header, textvariable=self.mqtt_status,
                 font=("Helvetica", 11), bg=BG, fg=MUTED).pack(side="right", pady=6)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=8)

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(main, bg=BG, width=260)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        # --- Wohnzimmer-Karte ---
        self.light_canvas = self._room_card(
            left, "Wohnzimmer", row=0,
            extra=self._make_light_widget
        )

        # --- Küche / Rollo ---
        self._room_card(left, "Küche & Rollo", row=1,
                        extra=self._make_kitchen_widget)

        # --- Steuerungs-Panel rechts ---
        self._control_panel(right)

        # --- Log ---
        log_frame = tk.Frame(self.root, bg=CARD, bd=0)
        log_frame.pack(fill="x", padx=20, pady=(4, 16))
        tk.Label(log_frame, text="MQTT-Log", font=("Courier", 10, "bold"),
                 bg=CARD, fg=MUTED, anchor="w").pack(fill="x", padx=10, pady=(6, 2))
        self.log_text = tk.Text(log_frame, height=5, bg=CARD, fg=GREEN,
                                font=("Courier", 9), bd=0, state="disabled",
                                insertbackground=TEXT)
        self.log_text.pack(fill="x", padx=10, pady=(0, 8))

    def _room_card(self, parent, title, row, extra):
        frame = tk.Frame(parent, bg=CARD, bd=0)
        frame.pack(fill="both", expand=True, pady=(0, 10))
        tk.Label(frame, text=title, font=("Helvetica", 13, "bold"),
                 bg=CARD, fg=TEXT, anchor="w").pack(fill="x", padx=14, pady=(10, 4))
        inner = tk.Frame(frame, bg=CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        extra(inner)
        return frame

    def _make_light_widget(self, parent):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x")

        # Glühbirne (Canvas)
        self.bulb = tk.Canvas(row, width=60, height=60, bg=CARD,
                              highlightthickness=0)
        self.bulb.pack(side="left", padx=(0, 16))
        self._draw_bulb(False)

        info = tk.Frame(row, bg=CARD)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text="Licht", font=("Helvetica", 11),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.light_label = tk.Label(info, text="AUS",
                                    font=("Helvetica", 15, "bold"),
                                    bg=CARD, fg=OFF_COLOR)
        self.light_label.pack(anchor="w")

        # Pir-Status
        pir_row = tk.Frame(parent, bg=CARD)
        pir_row.pack(fill="x", pady=(10, 0))
        tk.Label(pir_row, text="Bewegungsmelder (PIR)", font=("Helvetica", 11),
                 bg=CARD, fg=MUTED).pack(side="left")
        self.pir_label = tk.Label(pir_row, text="● Klar",
                                  font=("Helvetica", 11, "bold"),
                                  bg=CARD, fg=GREEN)
        self.pir_label.pack(side="right")

        # Letzte Geste / Button
        gesture_row = tk.Frame(parent, bg=CARD)
        gesture_row.pack(fill="x", pady=(6, 0))
        tk.Label(gesture_row, text="Letzte Geste:", font=("Helvetica", 10),
                 bg=CARD, fg=MUTED).pack(side="left")
        tk.Label(gesture_row, textvariable=self.last_gesture,
                 font=("Helvetica", 10, "bold"), bg=CARD, fg=TEXT).pack(side="left", padx=8)

        btn_row = tk.Frame(parent, bg=CARD)
        btn_row.pack(fill="x", pady=(2, 0))
        tk.Label(btn_row, text="Letzter Tasterdruck:", font=("Helvetica", 10),
                 bg=CARD, fg=MUTED).pack(side="left")
        tk.Label(btn_row, textvariable=self.last_button,
                 font=("Helvetica", 10, "bold"), bg=CARD, fg=TEXT).pack(side="left", padx=8)

    def _make_kitchen_widget(self, parent):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x")

        # Thermometer
        temp_box = tk.Frame(row, bg=ACCENT, padx=16, pady=10)
        temp_box.pack(side="left")
        tk.Label(temp_box, text="Temperatur", font=("Helvetica", 10),
                 bg=ACCENT, fg=MUTED).pack()
        self.temp_big = tk.Label(temp_box, textvariable=self.temperature,
                                 font=("Helvetica", 24, "bold"), bg=ACCENT, fg=ON_COLOR)
        self.temp_big.pack()
        tk.Label(temp_box, text="°C (DHT22)", font=("Helvetica", 10),
                 bg=ACCENT, fg=MUTED).pack()

        # Rollo
        blinds_box = tk.Frame(row, bg=CARD, padx=24)
        blinds_box.pack(side="left", fill="y")
        tk.Label(blinds_box, text="Rollo", font=("Helvetica", 11),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.blinds_canvas = tk.Canvas(blinds_box, width=80, height=60,
                                       bg=CARD, highlightthickness=0)
        self.blinds_canvas.pack()
        self.blinds_label = tk.Label(blinds_box, text="GESCHLOSSEN",
                                     font=("Helvetica", 10, "bold"),
                                     bg=CARD, fg=OFF_COLOR)
        self.blinds_label.pack()
        self._draw_blinds(False)

    def _control_panel(self, parent):
        tk.Label(parent, text="Steuerung", font=("Helvetica", 13, "bold"),
                 bg=BG, fg=TEXT, anchor="w").pack(fill="x", pady=(0, 8))

        def btn(text, cmd, color=ACCENT):
            b = tk.Button(parent, text=text, command=cmd,
                          bg=color, fg=TEXT, activebackground=ON_COLOR,
                          activeforeground=BG, font=("Helvetica", 11, "bold"),
                          bd=0, padx=10, pady=8, cursor="hand2")
            b.pack(fill="x", pady=3)
            return b

        btn("Licht AN",       lambda: self._publish(TOPIC_LIGHT, "ON"),   "#2d6a4f")
        btn("Licht AUS",      lambda: self._publish(TOPIC_LIGHT, "OFF"),  "#7b2d2d")
        btn("Rollo ÖFFNEN",   lambda: self._publish(TOPIC_BLINDS, "OPEN"), "#1d4e89")
        btn("Rollo SCHLIESSEN", lambda: self._publish(TOPIC_BLINDS, "CLOSE"), "#4a3000")

        sep = tk.Frame(parent, bg=MUTED, height=1)
        sep.pack(fill="x", pady=10)

        tk.Label(parent, text="Geste simulieren", font=("Helvetica", 10),
                 bg=BG, fg=MUTED).pack(anchor="w")
        btn("✋  Licht an (Geste)",
            lambda: self._publish(TOPIC_GESTURE, "licht_an"), ACCENT)
        btn("✊  Licht aus (Geste)",
            lambda: self._publish(TOPIC_GESTURE, "licht_aus"), ACCENT)

    # --------------------------------------------------------------- Zeichnen

    def _draw_bulb(self, on: bool):
        self.bulb.delete("all")
        color = ON_COLOR if on else OFF_COLOR
        self.bulb.create_oval(10, 4, 50, 40, fill=color, outline="")
        self.bulb.create_rectangle(20, 38, 40, 50, fill=color, outline="")
        if on:
            for r in range(3):
                self.bulb.create_oval(5-r*4, 0-r*4, 55+r*4, 45+r*4,
                                      outline=ON_COLOR, width=1,
                                      stipple="gray25")

    def _draw_blinds(self, open_: bool):
        self.blinds_canvas.delete("all")
        c = self.blinds_canvas
        c.create_rectangle(0, 0, 80, 60, fill="#2a2a4a", outline="")
        if open_:
            c.create_rectangle(0, 0, 80, 8, fill="#7ecfee", outline="")
        else:
            for y in range(0, 60, 10):
                c.create_rectangle(0, y, 80, y+8, fill="#7ecfee", outline="")
                c.create_line(0, y+8, 80, y+8, fill="#1a3a4a", width=1)

    # ---------------------------------------------------------- Zustand update

    def _update_light(self, on: bool):
        self.light_on.set(on)
        self._draw_bulb(on)
        self.light_label.config(
            text="AN" if on else "AUS",
            fg=ON_COLOR if on else OFF_COLOR
        )

    def _update_blinds(self, open_: bool):
        self.blinds_open.set(open_)
        self._draw_blinds(open_)
        self.blinds_label.config(
            text="GEÖFFNET" if open_ else "GESCHLOSSEN",
            fg=GREEN if open_ else OFF_COLOR
        )

    def _update_pir(self, active: bool):
        self.pir_active.set(active)
        self.pir_label.config(
            text="● Bewegung!" if active else "● Klar",
            fg=RED if active else GREEN
        )

    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.log_lines.append(line)
        if len(self.log_lines) > 80:
            self.log_lines = self.log_lines[-80:]
        self.log_text.config(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ----------------------------------------------------------------- MQTT --

    def _connect_mqtt(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id="dashboard-julius")
        self.client.on_connect    = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message    = self._on_message

        def _try_connect():
            try:
                self.client.connect(BROKER, PORT, keepalive=60)
                self.client.loop_start()
            except Exception as e:
                self.root.after(0, lambda: self.mqtt_status.set(f"Fehler: {e}"))

        threading.Thread(target=_try_connect, daemon=True).start()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        status = "Verbunden ✓" if reason_code == 0 else f"rc={reason_code}"
        self.root.after(0, lambda: self.mqtt_status.set(f"MQTT: {status}"))
        if reason_code == 0:
            for t in [TOPIC_LIGHT, TOPIC_BLINDS, TOPIC_TEMPERATURE,
                      TOPIC_PIR, TOPIC_BUTTON, TOPIC_GESTURE]:
                client.subscribe(t)
            self.root.after(0, lambda: self._log("MQTT verbunden – alle Topics abonniert"))

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.root.after(0, lambda: self.mqtt_status.set("MQTT: getrennt"))

    def _on_message(self, client, userdata, msg):
        topic   = msg.topic
        payload = msg.payload.decode("utf-8", errors="replace")

        def update():
            self._log(f"{topic}  →  {payload}")

            if topic == TOPIC_LIGHT:
                self._update_light(payload == "ON")

            elif topic == TOPIC_GESTURE:
                self.last_gesture.set(payload)
                if payload == "licht_an":
                    self._update_light(True)
                elif payload == "licht_aus":
                    self._update_light(False)

            elif topic == TOPIC_BLINDS:
                self._update_blinds(payload == "OPEN")

            elif topic == TOPIC_TEMPERATURE:
                self.temperature.set(payload)

            elif topic == TOPIC_PIR:
                self._update_pir(payload == "DETECTED")

            elif topic == TOPIC_BUTTON:
                self.last_button.set(payload)

        self.root.after(0, update)

    def _publish(self, topic: str, payload: str):
        self.client.publish(topic, payload)
        self._log(f"GESENDET  {topic}  →  {payload}")

    # ------------------------------------------------------------------ Run --

    def run(self):
        self.root.mainloop()
