# ACC

ACC using LiDAR


# Eingangssignale
- Mindestens ein Signal von einem LiDAR Sensor für die Messung des Abstand zu einem Objekt.
- Geschwindigkeit des Fahrzeugs, via CAN bzw. OBD2.

# Ausgangssignale
- Bremswarnung bei bevorstehender Kollision.


# Aufgabenpaket
- [ ] Geeignetes System für Cortex-A72 finden und installieren(ggf. ein ROS Linux oder rtos System).
- [ ] LiDAR Sensor auf Hardware-Ebene ordentlich mit dem Cortex-A72 Verbinden.
- [ ] LiDAR Sensor auf Software-Ebene mit dem Cortex-A72 Verbinden und die Register auslesen.
- [ ] Aus den Registern des LiDAR einen Abstand berechnen.
- [ ] Modelle für Abstands/Geschwindigkeits abschätzung entwickeln/finden.
- [ ] Modelle als Simulation entwerfen.

# Bis zum 11.11.2020
- [ ] Linux für Cortex-A72 ist gefgunden und installiert.
- [ ] LiDAR Konnektivität zum Cortex-A72 ist hergestellt.
