# Smart Irrigation Sensor Dataset Specification

## 1. Overview
This dataset contains **3,600 time-series observations** capturing multi-sensor environmental telemetry across varying agricultural crop types and soil textures. The data models physical dynamics including diurnal temperature cycles, evaporative water loss, rain inhibition, and crop-specific moisture stress thresholds.

---

## 2. Feature Dictionary

| Column Name | Data Type | Physical Unit | Sensor / Module Source | Description |
|---|---|---|---|---|
| `timestamp` | Datetime | YYYY-MM-DD HH:MM | Real-Time Clock (RTC) / NTP | Hourly timestamp of sensor acquisition |
| `soil_moisture` | Float | Percentage (%) | Capacitive Soil Moisture v1.2 | Volumetric soil moisture content (0% to 100%) |
| `temperature` | Float | Degrees Celsius (°C) | DHT11 / DHT22 | Ambient air temperature (14°C to 46°C) |
| `humidity` | Float | Percentage (%) | DHT11 / DHT22 | Ambient relative humidity (16% to 98%) |
| `soil_temperature`| Float | Degrees Celsius (°C) | DS18B20 Probe | Thermal profile of soil (12°C to 39°C) |
| `sunlight_lux` | Float | Illuminance (Lux) | LDR / BH1750 Sensor | Solar radiation intensity (0 to 95,000 Lux) |
| `rain_sensor` | Binary Integer| 0 or 1 | FC-37 Rain Drop Sensor | Rain detection (0 = Dry/No rain, 1 = Rain) |
| `crop_type` | Categorical | String | Field Agronomy Config | Crop variety (Tomato, Wheat, Maize, Rice, Cotton) |
| `soil_type` | Categorical | String | Soil Taxonomy Config | Texture category (Sandy, Loamy, Clay) |
| `irrigation_required` | Binary Target | 0 or 1 | Ground Truth / Actuator | **Target 1**: 0 = OFF (No water needed), 1 = ON (Irrigation Required) |
| `water_requirement_ml`| Continuous Target| Milliliters (ml) | Flow Meter / Actuator | **Target 2**: Recommended water dosage per plant/zone |
| `next_day_moisture_estimate`| Float | Percentage (%) | Predictive Estimator | Forecasted soil moisture after 24 hours |

---

## 3. Agronomic Principles & Physics Modeling
1. **Critical Moisture Thresholds:**
   - Rice: 65% moisture (flooded / saturated requirement)
   - Tomato: 42% moisture (moderate to high water demand)
   - Wheat: 34% moisture (moderate requirement)
   - Maize: 32% moisture (deep roots, moderate drought tolerance)
   - Cotton: 28% moisture (drought-hardy)
2. **Soil Retention Dynamics:**
   - Clay: High water retention capacity; high moisture threshold.
   - Sandy: Low retention, fast drainage; dries quickly under heat.
   - Loamy: Balanced moisture retention and aeration.
3. **Precipitation Interlock:**
   - Whenever `rain_sensor == 1`, irrigation is forcibly overridden to 0 to prevent waterlogging and conserve pump energy.
