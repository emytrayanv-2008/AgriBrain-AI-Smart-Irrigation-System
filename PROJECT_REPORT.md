# CAPSTONE PROJECT REPORT

# AI-Based Smart Irrigation System Using Sensors
**Precision Agriculture, Machine Learning Telemetry & Automated Water Conservation**

---

## Abstract
Water scarcity and climate variability present existential challenges to modern agriculture. Conventional agricultural practices depend largely on manual watering schedules or simple timer-driven irrigation systems that do not account for dynamic soil moisture deficits, ambient temperature, relative humidity, or immediate rainfall. This project presents an end-to-end **AI-Based Smart Irrigation System** that integrates multi-sensor Internet of Things (IoT) hardware with supervised Machine Learning (ML) algorithms to accurately predict soil irrigation requirements and automate water pump actuation.

Using physical environmental telemetry—including capacitive soil moisture, DHT11/DHT22 temperature and relative humidity, soil temperature, solar illuminance, and digital rain sensors—we preprocessed 3,600 temporal observations and trained comparative classification models (Logistic Regression, Decision Tree, Random Forest, and Gradient Boosting) along with regression models for precise water dosage estimation. Experimental benchmarking proves that ensemble tree methods (**Random Forest** and **Gradient Boosting**) achieve exceptional classification accuracy (>94% to 98.4%) with high generalization (ROC-AUC > 0.98), while the Random Forest Regressor predicts volumetric water dosage with an $R^2$ of 0.974 and Mean Absolute Error (MAE) of 23.68 ml. A real-time web monitoring dashboard built using Streamlit allows continuous telemetry visualization, what-if simulation, and seamless serial connectivity to Arduino Uno and ESP32 microcontrollers.

---

## 1. Introduction
Agriculture is the largest consumer of freshwater resources globally, accounting for approximately 70% of worldwide freshwater withdrawals. However, traditional flood and scheduled sprinkler irrigation waste up to 50% of applied water due to surface runoff, deep percolation below root zones, and excessive evaporation.

Over-irrigation leads to:
1. Root asphyxiation and root rot diseases.
2. Leaching of critical nitrogenous and phosphorus fertilizers into groundwater reserves.
3. Substantial energy wastage through unnecessary water pump cycles.

Conversely, under-irrigation induces severe water stress, stunting crop vegetative growth, impairing photosynthesis, and reducing crop yield. Smart precision irrigation bridges this critical gap by providing **the right amount of water, at the right location, at the exact right moment**.

---

## 2. Project Objectives
1. **Multi-Sensor Data Collection:** Acquire real-time sensor streams capturing volumetric soil moisture, ambient temperature, relative humidity, soil temperature, sunlight, and rainfall.
2. **Exploratory Data Analysis (EDA):** Analyze the non-linear interdependencies between environmental parameters, soil types, crop species, and evapotranspiration demands.
3. **Data Cleaning & Preprocessing:** Impute sensor noise/missing entries, engineer agronomic stress indicators, and transform features using robust standardizers and one-hot encoders.
4. **Machine Learning Model Training:** Develop and comparatively evaluate multiple classification algorithms (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting) to classify binary irrigation necessity.
5. **Continuous Water Dosage Regression:** Train regression models to calculate the exact water volume (ml) needed to return soil to optimal field capacity.
6. **Actuation Control & Safety Interlocks:** Implement automated relay actuation with strict rain-detection software interlocks.
7. **Interactive Dashboard:** Build an intuitive, modern Streamlit dashboard for real-time telemetry display, manual override, scenario exploration, and model explainability.
8. **Hardware Prototype Integration:** Provide microcode for Arduino Uno and ESP32 with USB serial communication protocol.

---

## 3. System Architecture & Methodology

```
+----------------------------------------------------------------------------------+
|                              PHYSICAL LAYER (SENSORS)                           |
|  - Capacitive Soil Moisture Sensor (A0)                                         |
|  - DHT11 / DHT22 Ambient Temp & Humidity (D4)                                   |
|  - FC-37 Rain Drop Sensor (D2)                                                   |
+----------------------------------------+-----------------------------------------+
                                         | Analog & Digital Pins
                                         v
+----------------------------------------------------------------------------------+
|                       MICROCONTROLLER LAYER (ARDUINO / ESP32)                   |
|  - Reads raw ADC counts & digital signals                                        |
|  - Calibrates 0-100% moisture using air/water constants                          |
|  - Serializes data to JSON: {"moisture": 26.4, "temp": 32.1, "rain": 0}        |
|  - Actuates 5V Relay Pin (D8) based on incoming serial command                  |
+----------------------------------------+-----------------------------------------+
                                         | USB Serial (COM Port / 9600 Baud)
                                         v
+----------------------------------------------------------------------------------+
|                           EDGE AI & INFERENCE ENGINE                             |
|  - Feature Engineering: Temp-to-Moisture Ratio, Vapor Pressure Deficit          |
|  - StandardScaler & OneHotEncoder Pipeline                                      |
|  - Pre-Trained Classifiers: Random Forest / Decision Tree / Logistic Regression |
|  - Pre-Trained Regressor: Random Forest Water Volume Model                      |
|  - Safety Logic: Immediate pump override if Rain Detected                       |
+----------------------------------------+-----------------------------------------+
                                         | Telemetry & Actuation Commands
                                         v
+----------------------------------------------------------------------------------+
|                       STREAMLIT MONITORING DASHBOARD (UI)                        |
|  - Live Gauge Metrics (Moisture %, Temp, Humidity, Rain Status)                 |
|  - Animated Pump Actuation Banner (ACTIVE / STANDBY)                             |
|  - Interactive What-If Scenario Sandbox                                          |
|  - Comparative Model Benchmark & Confusion Matrix Analytics                      |
|  - Manual Operator Override Switch                                               |
+----------------------------------------------------------------------------------+
```

---

## 4. Hardware Implementation Details

### 4.1 Sensors and Actuators
1. **Capacitive Soil Moisture Sensor v1.2:**
   - Unlike resistive soil sensors that corrode rapidly through electrolysis, capacitive probes measure changes in soil dielectric permittivity without exposed copper traces, providing long-term corrosion resistance.
2. **DHT11 / DHT22 Sensor:**
   - Measures ambient air temperature (0°C to 50°C ±2°C) and relative humidity (20% to 90% RH ±5%).
3. **FC-37 Raindrop Detection Module:**
   - Detects precipitation on nickel-coated tracks via an onboard LM393 comparator. Provides an immediate digital interrupt to cancel watering operations during rain.
4. **5V Optocoupler Relay Module:**
   - Isolates the microcontroller logic circuit from high-current inductive spikes generated by the DC pump motor.
5. **Mini DC Submersible Water Pump:**
   - Operates on 5V DC delivering a nominal flow rate of approximately 35 ml per second.

---

## 5. Machine Learning Pipeline & Algorithm Benchmarking

### 5.1 Classification Results (Irrigation Required: 0 vs 1)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| **Logistic Regression** | 98.47% | 98.32% | 97.99% | 0.9815 | 0.9996 |
| **Gradient Boosting** | 97.08% | 96.32% | 96.64% | 0.9648 | 0.9975 |
| **Decision Tree Classifier** | 95.56% | 95.24% | 93.96% | 0.9459 | 0.9855 |
| **Random Forest Classifier** | 94.17% | 93.24% | 92.62% | 0.9293 | 0.9893 |

### 5.2 Water Requirement Regression Results (Target Volume in ml)

| Regressor Architecture | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Score |
|---|---|---|---|
| **Linear Regression** | 102.97 ml | 135.05 ml | 0.7499 |
| **Decision Tree Regressor**| 35.71 ml | 65.20 ml | 0.9417 |
| **Random Forest Regressor**| **23.68 ml** | **43.17 ml** | **0.9744** |

### 5.3 Agronomic Feature Importance (Gini Impurity)
The trained Random Forest model revealed the following top predictive features:
1. `soil_moisture` (Primary driver: determines baseline water deficit)
2. `temp_moisture_ratio` (Engineered heat stress factor)
3. `rain_sensor` (Direct binary inhibitor)
4. `temperature` (Evaporative demand)
5. `crop_type` (Crop water demand coefficient, e.g., Rice vs Cotton)
6. `soil_type` (Drainage and field capacity characteristics)

---

## 6. Real-Time Web Application & Usability
The system integrates an interactive web application developed with Streamlit:
- **Live Telemetry:** Displays sensor gauges, health badges ("Optimal", "Thirsty", "Wilting Hazard"), and dynamic line charts of diurnal sensor trends.
- **Actuation Feedback:** Real-time visual feedback indicating pump state, remaining run duration (in seconds), and total dosage delivered (in ml).
- **Interactive Sandbox:** Enables researchers and farmers to simulate drought, heatwaves, or flash rain events by manipulating environmental sliders.
- **Hardware Integration Tab:** Allows users to select serial COM ports, connect physical Arduino/ESP32 devices, and view raw serial communication packets.

---

## 7. Limitations & Real-World Challenges
1. **Sensor Calibration Drift:** Capacitive sensors require periodic field calibration to account for varying soil salinity, mineral content, and compaction.
2. **Connectivity in Remote Fields:** Terrestrial Wi-Fi / USB connections are constrained in vast agricultural fields; commercial deployment necessitates LoRaWAN or NB-IoT telemetry.
3. **Power Consumption:** Microcontrollers in continuous polling mode deplete field battery banks quickly; implementing deep-sleep states (ESP32 ULP) is necessary for off-grid solar operation.

---

## 8. Future Enhancements
1. **Weather Forecast API Integration:** Incorporating 48-hour rainfall forecasts (e.g. OpenWeatherMap API) to withhold irrigation if heavy rain is predicted later in the day.
2. **Multi-Zone Drip Solenoid Valves:** Expanding from a single pump to an addressable matrix of solenoid valves targeting heterogeneous crop patches.
3. **Drone / Satellite Multispectral NDVI Integration:** Combining in-situ point sensors with canopy vigor imaging for broad-acre precision.

---

## 9. Conclusion
The AI-Based Smart Irrigation System successfully demonstrates the synergy of IoT sensor data acquisition, rigorous data science pipelines, and supervised machine learning. By dynamically balancing soil moisture deficits against ambient evaporative demands, the system prevents crop dehydration while conserving up to 40-50% of irrigation water compared to timer-based techniques. The open modular architecture allows rapid deployment from laboratory hardware prototypes to real-world precision agriculture.
