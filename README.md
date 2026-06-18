# Smart-Home
Projekt mit dem Ziel ein Dashboard zur Steuerung eines Smart-Homes 

1. Kundenauftrag
Ein Unternehmen möchte einen Prototyp für ein modernes Smart-Home-System entwickeln. Die Bedienung soll berührungslos über Handgesten erfolgen. Sensoren und Aktoren werden über einen ESP32 in Wokwi simuliert, die Kommunikation läuft über MQTT. Zusätzlich soll ein Dashboard entwickelt werden, das die Wohnung grafisch darstellt und alle Zustände in Echtzeit visualisiert.
Das Projekt zeigt, wie KI, IoT und moderne Softwareentwicklung zusammenarbeiten. Ziel ist eine möglichst realistische Smart-Home-Anwendung.
2. Projektziel
Entwickeln Sie ein Smart-Home-System mit folgenden Funktionen:
•	Gestensteuerung mit MediaPipe
•	MQTT-Kommunikation über einen öffentlichen Broker
•	Sensorik und Aktorik mit ESP32 in Wokwi
•	Grafische Wohnungsvisualisierung (Dashboard)
•	Gemeinsame Entwicklung mit GitHub
Das System muss als Gesamtlösung funktionieren und in einer Abschlusspräsentation am 07.07.2026 demonstriert werden.
3. Technische Anforderungen
MediaPipe
•	Mindestens zwei Gesten erkennen
•	Jede Geste erzeugt eine MQTT-Nachricht
MQTT
•	Öffentlichen Broker verwenden (z. B. broker.hivemq.com)
•	Sinnvolle und dokumentierte Topic-Struktur
Wokwi / ESP32
•	LED, Taster, DHT22, PIR-Sensor und Servo integrieren
•	Als MQTT-Subscriber agieren und auf Nachrichten reagieren
Dashboard
•	Frei wählbare Technologie
•	MQTT-Daten in Echtzeit anzeigen und Zustände visualisieren
•	Optional: Geräte über das Dashboard direkt steuern
GitHub
•	Gemeinsames Repository mit aussagekräftigem README
•	Regelmäßige, nachvollziehbare Commits (mind. ein Commit pro Projekttag)
4. Systemarchitektur
Die Komponenten kommunizieren ausschließlich über MQTT:
  MediaPipe  →  MQTT-Broker  →  ESP32 (Wokwi)
                      ↕
                  Dashboard
Das Dashboard kann zusätzlich MQTT-Nachrichten senden, um Geräte zu steuern. Die Schnittstelle ist immer MQTT.
5. Dashboard-Anforderungen
Das Dashboard ist ein zentraler Bestandteil des Projekts. Die Wohnung wird grafisch mit mindestens folgenden Elementen dargestellt:
•	Lichtzustände sichtbar (ein/aus)
•	Rollo geöffnet/geschlossen
•	Temperatur anzeigen (DHT22-Wert)
•	Bewegungsmelder (PIR) visualisieren
•	MQTT-Daten in Echtzeit aktualisieren
•	Übersichtliche und bedienbare Oberfläche
Beispiel: Wird das Wohnzimmerlicht eingeschaltet, ändert sich die Darstellung sofort. Wird das Rollo bewegt, reagiert die Visualisierung unmittelbar.
6. MQTT-Topics (Vorschlag)
Eine eigene Topic-Struktur ist erlaubt, muss aber logisch aufgebaut und dokumentiert werden.
•	home/livingroom/light
•	home/livingroom/blinds
•	home/kitchen/temperature
•	home/bedroom/pir
•	home/button
•	home/gesture
7. Arbeitsteilung
Vorgeschlagene Aufgabenteilung (Zweierteam). Anpassungen nach Absprache möglich.
Schüler A – Gestenerkennung & Publisher
•	MediaPipe-Integration
•	Gestenerkennung (mind. 2 Gesten)
•	MQTT-Publisher
Schüler B – Hardware & Subscriber
•	ESP32 in Wokwi
•	Sensoren (DHT22, PIR) und Aktoren (LED, Servo)
•	MQTT-Subscriber
Gemeinsam
•	Dashboard
•	Tests und Fehlerbehebung
•	Dokumentation
•	Abschlusspräsentation


Noah: Aufgabe Person A 
Julius: Aufgabe Person B 