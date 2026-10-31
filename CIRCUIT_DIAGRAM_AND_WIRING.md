# Hardware Circuit Diagram & Wiring Guide
## Capstone Project: AI-Based Smart Irrigation System Using Sensors

This document provides complete circuit schematics, pin mappings, calibration instructions, and electrical safety measures for building and presenting the hardware prototype.

---

### 1. Hardware Components Required

| Item | Component | Specification | Function |
|---|---|---|---|
| 1 | **Microcontroller** | Arduino Uno R3 or ESP32 NodeMCU | Collects sensor data, drives relay |
| 2 | **Soil Moisture Sensor** | Capacitive Soil Moisture v1.2 / v2.0 | Measures volumetric soil moisture |
| 3 | **Temperature & Humidity** | DHT11 or DHT22 | Measures ambient climatic factors |
| 4 | **Raindrop Sensor Module** | FC-37 with LM393 comparator | Detects precipitation / rainfall |
| 5 | **Relay Module** | 5V 1-Channel Relay with Optocoupler | Switches high-current water pump |
| 6 | **Water Pump** | 5V / 12V DC Submersible Mini Pump | Delivers irrigation water |
| 7 | **Power Supply** | 5V 2A USB Adapter or 9V/12V DC Jack | Powers circuit and pump |
| 8 | **Jumper Wires & Tubing** | Male-to-Female, Silicone Tubing | Connections and plumbing |

---

### 2. Microcontroller Pin Mapping Table

#### For Arduino Uno:
| Sensor / Module | Sensor Pin | Arduino Uno Pin | Power / Ground |
|---|---|---|---|
| **Capacitive Soil Sensor** | `AOUT` | `A0` | `VCC` -> `5V`, `GND` -> `GND` |
| **DHT11 / DHT22** | `DATA` | `D4` | `VCC` -> `5V`, `GND` -> `GND` |
| **Rain Sensor Module** | `DO` (Digital Out) | `D2` | `VCC` -> `5V`, `GND` -> `GND` |
| **Relay Module** | `IN` | `D8` | `VCC` -> `5V`, `GND` -> `GND` |
| **Water Pump** | `+` (Red) | Connected via Relay `NO` | `-` (Black) -> `GND` |

#### For ESP32 (3.3V Logic):
| Sensor / Module | Sensor Pin | ESP32 Pin | Power / Ground |
|---|---|---|---|
| **Capacitive Soil Sensor** | `AOUT` | `GPIO 34` (ADC1) | `VCC` -> `3.3V`, `GND` -> `GND` |
| **DHT11 / DHT22** | `DATA` | `GPIO 4` | `VCC` -> `3.3V`, `GND` -> `GND` |
| **Rain Sensor Module** | `DO` | `GPIO 15` | `VCC` -> `3.3V`, `GND` -> `GND` |
| **Relay Module** | `IN` | `GPIO 23` | `VCC` -> `5V` (or 3.3V), `GND` -> `GND` |

---

### 3. Circuit Schematic Diagram (ASCII Architecture)

```
        +---------------------------------------------------+
        |                  ARDUINO UNO                      |
        |                                                   |
        |   5V   GND    A0     D2     D4     D8    USB-COM  |
        +---+-----+-----+------+------+------+----+----+----+
            |     |     |      |      |      |         |
            |     +-----+------+------+------+         +=====> PC / Python
            |     |     |      |      |      |                 (Hardware Bridge)
            |     |     |      |      |      |
            |     |     |      |      |      +--------+ [IN]
            |     |     |      |      |               |
            |     |     |      |      +----+ [DATA]   |   +-------------------+
            |     |     |      |           |          |   |  5V RELAY MODULE  |
            |     |     |      +----+ [DO] |          |   |                   |
            |     |     |           |      |          +-->| IN  VCC  GND      |
            |     |     +----+ [AOUT|      |              |      |    |       |
            |     |          |      |      |              |     5V   GND      |
            |     |          |      |      |              |  [COM]   [NO]     |
            |     |          |      |      |              +----+------+-------+
            |     |          |      |      |                   |      |
            |     |          |      |      +-> DHT11/22        |      +--+
            |     |          |      +--------> Rain Sensor     |         |
            |     |          +---------------> Soil Moisture   |         |
            |     |                                            |         |
            |     +--------------------------------------------+         |
            |                                                            |
            +------------[ DC Power Supply (+) ]                         |
                                 |                                       |
                                 +-----------------------+               |
                                                         |               |
                                                  +------v-------+       |
                                                  | DC SUBMERSIBLE<------+
                                                  |  WATER PUMP  |
                                                  +--------------+
```

---

### 4. Soil Moisture Sensor Calibration Procedure
Capacitive soil sensors output an analog voltage inversely proportional to soil water content:
1. **Air Calibration (0% Moisture):** Hold the sensor dry in air. Note down the analog reading in Arduino Serial Monitor (`AIR_VALUE` ≈ 620 on Uno, 3200 on ESP32).
2. **Water Calibration (100% Moisture):** Dip the probe into a glass of plain water up to the marked line (do not submerge electronic circuit). Note the reading (`WATER_VALUE` ≈ 280 on Uno, 1350 on ESP32).
3. Update the constants `AIR_VALUE` and `WATER_VALUE` in `arduino_uno_irrigation.ino` to calibrate your specific probe.

---

### 5. Water Pump Safety Precautions
- Use a **flyback diode** (e.g. 1N4007) across the DC pump terminals if connecting directly, or use an optocoupled relay board to isolate the microcontroller from inductive motor spikes.
- Never run the mini DC submersible water pump dry for extended periods (submerge in small reservoir/cup for demonstration).
- Power the water pump with an external 5V/9V battery or wall adapter rather than pulling high current directly from the Arduino 5V pin.
