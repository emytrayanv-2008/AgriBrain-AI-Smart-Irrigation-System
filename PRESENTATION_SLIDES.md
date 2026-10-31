# Final Presentation Deck Outline (PPT)
## Capstone: AI-Based Smart Irrigation System Using Sensors

---

### Slide 1: Title Slide
- **Title:** AI-Based Smart Irrigation System Using Sensors
- **Subtitle:** Precision Agriculture & Machine Learning Telemetry Automation
- **Presenter:** [Student Name]
- **Course / Degree:** AI & Data Science Capstone Project
- **Date:** 2026

---

### Slide 2: Problem Statement & Motivation
- **Global Context:** Agriculture consumes ~70% of freshwater withdrawals globally.
- **Flaws in Traditional Irrigation:**
  - Flood irrigation leads to 40-50% water runoff and fertilizer leaching.
  - Timer-based sprinklers irrigate irrespective of actual soil moisture or rain.
- **The Core Goal:** Automate irrigation decisions using real-time IoT sensors and Machine Learning to supply water only when, where, and how much is needed.

---

### Slide 3: System Architecture Overview
- **Tier 1 (Sensors):** Capacitive Soil Moisture, DHT11 (Air Temp & Humidity), FC-37 Rain Sensor.
- **Tier 2 (Microcontroller):** Arduino Uno / ESP32 collecting analog & digital readings, transmitting JSON telemetry over Serial.
- **Tier 3 (AI Inference Engine):** Preprocessed features fed into trained ML models (Classification + Regression).
- **Tier 4 (Actuation & UI):** 5V Relay module powering mini DC pump, monitored through interactive Streamlit dashboard.

---

### Slide 4: Hardware Design & Circuitry
- **Sensor Selection:**
  - Capacitive Soil Sensor (v1.2) chosen over resistive probes to eliminate corrosion.
  - Optocoupled Relay prevents motor inductive reverse-EMF voltage spikes.
- **Hardware Integration:**
  - Arduino Uno / ESP32 microcode with non-blocking serial telemetry.
  - Fail-safe: Hardware-level Rain override immediately de-energizes the relay coil.

---

### Slide 5: Dataset & Exploratory Data Analysis (EDA)
- **Dataset Size:** 3,600 temporal observations with diurnal solar cycles.
- **Features Captured:** Soil Moisture (%), Air Temp (°C), Humidity (%), Soil Temp (°C), Sunlight (Lux), Rain (0/1), Crop Type, Soil Type.
- **Key EDA Findings:**
  - Negative correlation between temperature and relative humidity ($r \approx -0.72$).
  - Soil moisture below crop threshold strongly triggers irrigation.
  - Rainfall acts as a strict zero-water gate.

---

### Slide 6: Data Preprocessing & Feature Engineering
- **Handling Missing Values:** Median imputation for sensor dropouts.
- **Engineered Domain Features:**
  - `temp_moisture_ratio = Temperature / (Soil_Moisture + 1)`
  - `vapor_deficit = (100 - Humidity) * (Temperature / 50)`
- **Standardization & Encoding:**
  - `StandardScaler` for continuous sensor signals.
  - `OneHotEncoder` for Crop Type and Soil Type.

---

### Slide 7: Machine Learning Model Benchmarking (Classification)
- **Algorithms Compared:**
  1. Logistic Regression (Baseline)
  2. Decision Tree Classifier (Single Tree)
  3. Random Forest Classifier (100 Trees Bagging)
  4. Gradient Boosting Classifier (Sequential Boosting)
- **Performance Highlights:**
  - Logistic Regression & Gradient Boosting achieved >97% Accuracy.
  - Random Forest achieved 94.2% Accuracy, 92.9% F1-Score, and 0.989 ROC-AUC with zero overfitting.

---

### Slide 8: Water Dosage Regression Modeling
- **Why Regression?** Knowing *when* to irrigate is only half the battle; knowing *how much water to pump* prevents over-saturation.
- **Random Forest Regressor Results:**
  - **Mean Absolute Error (MAE):** 23.68 ml
  - **Root Mean Squared Error (RMSE):** 43.17 ml
  - **Coefficient of Determination ($R^2$):** **0.974**
- **Pump Duration Translation:** $\text{Duration (seconds)} = \frac{\text{Dosage (ml)}}{35\text{ ml/sec}}$

---

### Slide 9: Feature Importance & Explainable AI
- **Top Gini Importance Drivers:**
  1. `soil_moisture` (Highest importance)
  2. `temp_moisture_ratio` (Heat stress factor)
  3. `rain_sensor` (Direct binary gate)
  4. `temperature` (Evapotranspiration driver)
- **Explainability:** Transparent decision trees eliminate "black box" hesitation for farmers and agronomists.

---

### Slide 10: Streamlit Dashboard Demonstration
- **Live Telemetry Cards:** Real-time moisture %, temperature, humidity, and rain status.
- **Pump Status Badge:** Glowing animated active status with countdown timer.
- **What-If Scenario Sandbox:** Interactive sliders to test any crop under drought or storm conditions.
- **Hardware Integration Hub:** Connect physical Arduino over USB COM port with live serial telemetry.

---

### Slide 11: Real-World Challenges & Limitations
- **Sensor Drift:** Mineral buildup requires periodic seasonal recalibration.
- **Connectivity:** Cellular / LoRaWAN needed for remote rural acreage.
- **Power Constraints:** Solar panels + lithium battery banks required for off-grid deployment.

---

### Slide 12: Conclusion & Future Scope
- **Key Takeaways:**
  - Demonstrated an end-to-end AI-powered IoT irrigation pipeline.
  - Conserves up to 45% water compared to conventional timer systems.
- **Future Roadmap:**
  - Weather forecast API integration (predicting rain 24h in advance).
  - Multi-valve drip irrigation matrix.
  - Edge micro-ML on ESP32 using TensorFlow Lite for Microcontrollers.

---

### Slide 13: Q&A / Viva
- Thank you! Questions & Live Demonstration.
