# ThermoTrack

**A smart fridge health monitor that detects cooling faults early and tries to fix them on its own.**

ThermoTrack watches a refrigerator's temperature and compressor current in real time. Instead of reacting to fixed limits alone, it looks at how the readings are *changing*. When something goes wrong, it cuts power, lets the system rest, and checks whether it recovered, all without anyone stepping in. Every reading is streamed to a live web dashboard.

## Functionality

### Self-healing
When a fault is detected, ThermoTrack does not just sound an alarm. It runs a recovery cycle:

1. **Power off** temporarily to let the system settle.
2. **Power back on** for a monitoring window.
3. **Check** whether temperature and current have stabilised.
4. **Heal again** if they haven't.

This repeats until the readings are healthy again.

### Trend-based fault detection
The algorithm cares about the *shape* of the data, not just absolute values. A sudden spike or a continuous rise in temperature or current triggers an alert, which catches a failing cooling system before it crosses a hard threshold.

### Live monitoring
The ESP32 posts a JSON reading to the backend about every 2 seconds. The Flask dashboard stores and displays them, so you can see the fridge's condition as it happens.

## How it works

```
DS18B20 (temperature) ─┐
                       ├──► ESP32 ──► Relay ──► Compressor
ACS712 5A (current)  ──┘      │
                              ├──► Buzzer + LED (alerts)
                              └──► HTTP POST (JSON) ──► Flask + SQLite dashboard
```

The firmware runs a state machine with two states: normal monitoring and healing mode. Moving between them is driven by the temperature and current trends.

## Hardware

| Component | Role |
|---|---|
| ESP32 | Main controller and Wi-Fi link |
| DS18B20 | Temperature sensing |
| ACS712 (5A) | Current sensing |
| Relay | Switches power for the healing cycle |
| Buzzer + LED | Local fault indication |

## Software

- **Firmware:** ESP32 Arduino sketch (`.ino`)
- **Backend:** Flask with SQLite
- **Dashboard:** Web interface hosted on PythonAnywhere
- **Simulation:** Wokwi project for testing the full flow without hardware
