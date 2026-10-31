"""
Smart Irrigation Sensor Dataset Generator
Simulates realistic agronomic sensor streams incorporating:
- Capacitive Soil Moisture Sensor (%)
- DHT11 / DHT22 Ambient Temperature (C) & Relative Humidity (%)
- LDR / Solar Lux Sensor (Lux)
- Soil Temperature Sensor DS18B20 (C)
- Digital Rain Drop Sensor (0=No Rain, 1=Rain)
- Agronomic parameters: Crop Type, Soil Type, Evapotranspiration
- Targets:
  1) irrigation_required (Classification: 0=OFF, 1=ON)
  2) water_requirement_ml (Regression: recommended irrigation volume)
"""

import numpy as np
import pandas as pd
import datetime
import random
import os

def generate_smart_irrigation_dataset(n_samples=3500, random_state=42):
    np.random.seed(random_state)
    random.seed(random_state)
    
    crops = ['Wheat', 'Tomato', 'Maize', 'Rice', 'Cotton']
    soils = ['Sandy', 'Loamy', 'Clay']
    
    # Base crop moisture threshold definitions (% moisture below which plant is stressed)
    crop_moisture_threshold = {
        'Rice': 65.0,
        'Tomato': 42.0,
        'Wheat': 34.0,
        'Maize': 32.0,
        'Cotton': 28.0
    }
    
    # Soil drainage and retention modifier
    soil_modifier = {
        'Sandy': -5.0,  # Dries faster, lower retention
        'Loamy': 0.0,   # Ideal
        'Clay': +6.0    # Retains water more tightly
    }

    start_date = datetime.datetime(2026, 4, 1, 6, 0)
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(n_samples)]
    
    data = []
    
    for i, ts in enumerate(timestamps):
        hour = ts.hour
        month = ts.month
        
        # Diurnal temperature cycle: coolest at 5 AM, hottest at 2 PM (14:00)
        daily_temp_cycle = np.sin((hour - 8) / 24.0 * 2 * np.pi)
        base_temp = 28.0 + 8.5 * daily_temp_cycle + np.random.normal(0, 2.0)
        temperature = round(float(np.clip(base_temp, 14.0, 46.0)), 2)
        
        # Humidity inversely correlates with temperature
        base_humidity = 70.0 - (temperature - 20.0) * 1.6 + np.random.normal(0, 4.5)
        humidity = round(float(np.clip(base_humidity, 16.0, 96.0)), 2)
        
        # Soil temperature lags behind air temperature and has smaller variance
        soil_temp = round(float(np.clip(0.7 * temperature + 7.0 + np.random.normal(0, 1.2), 12.0, 39.0)), 2)
        
        # Sunlight (Lux): peaks at noon, 0 at night
        if 6 <= hour <= 18:
            sun_angle = np.sin((hour - 6) / 12.0 * np.pi)
            sunlight_lux = round(float(np.clip(sun_angle * 85000 + np.random.normal(0, 4000), 100, 95000)), 1)
        else:
            sunlight_lux = round(float(np.clip(np.random.normal(5, 3), 0, 40)), 1)
            
        # Rain chance (approx 12% probability)
        is_raining = 1 if np.random.rand() < 0.12 else 0
        if is_raining:
            humidity = round(float(np.clip(humidity + 25.0, 60.0, 99.0)), 2)
            temperature = round(float(max(18.0, temperature - 5.0)), 2)
            sunlight_lux = round(float(sunlight_lux * 0.2), 1)
            
        # Select crop and soil
        crop = random.choice(crops)
        soil = random.choice(soils)
        
        # Soil moisture distribution
        # If raining, moisture spikes higher
        if is_raining:
            soil_moisture = round(float(np.clip(np.random.normal(75, 12), 35.0, 98.0)), 2)
        else:
            # General distribution with realistic dry, medium, wet states
            state = np.random.choice(['dry', 'optimal', 'wet'], p=[0.42, 0.40, 0.18])
            if state == 'dry':
                soil_moisture = round(float(np.clip(np.random.normal(24, 7), 5.0, 40.0)), 2)
            elif state == 'optimal':
                soil_moisture = round(float(np.clip(np.random.normal(50, 8), 35.0, 70.0)), 2)
            else:
                soil_moisture = round(float(np.clip(np.random.normal(78, 6), 65.0, 95.0)), 2)
                
        # Agronomic threshold calculation
        threshold = crop_moisture_threshold[crop] + soil_modifier[soil]
        
        # Evaporative demand factor based on temperature, humidity, and sunlight
        vapor_pressure_deficit = ((temperature / 20.0) ** 1.3) * ((100.0 - humidity) / 50.0)
        
        # Determine Irrigation Requirement
        # Core Rule: If raining, no irrigation needed
        if is_raining == 1:
            irrigation_required = 0
            water_requirement_ml = 0.0
        else:
            moisture_deficit = threshold - soil_moisture
            
            # If soil moisture is well below threshold, irrigation is definitely needed
            # If borderline, high temp/sunlight pushes need for irrigation
            urgency_score = moisture_deficit + 0.15 * (temperature - 28.0) - 0.10 * (humidity - 50.0) + 0.00005 * sunlight_lux
            
            # Classification outcome with slight realistic stochasticity
            prob_irrigation = 1.0 / (1.0 + np.exp(-urgency_score / 2.2))
            irrigation_required = 1 if prob_irrigation > 0.50 else 0
            
            # Regression outcome: amount of water (ml per square meter/plant zone)
            if irrigation_required == 1:
                base_water = max(150.0, moisture_deficit * 22.0)
                temp_factor = max(1.0, 1.0 + (temperature - 25.0) * 0.02)
                water_requirement_ml = round(float(np.clip(base_water * temp_factor + np.random.normal(0, 25), 100.0, 1200.0)), 1)
            else:
                water_requirement_ml = 0.0
                
        # Predicted next-day moisture if left untreated
        evap_loss = (0.25 * vapor_pressure_deficit) + (0.00002 * sunlight_lux)
        next_day_moisture = round(float(np.clip(soil_moisture - evap_loss + (15.0 if is_raining else 0), 2.0, 99.0)), 2)
        
        data.append({
            'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity,
            'soil_temperature': soil_temp,
            'sunlight_lux': sunlight_lux,
            'rain_sensor': is_raining,
            'crop_type': crop,
            'soil_type': soil,
            'irrigation_required': irrigation_required,
            'water_requirement_ml': water_requirement_ml,
            'next_day_moisture_estimate': next_day_moisture
        })
        
    df = pd.DataFrame(data)
    
    # Introduce a few realistic NaN values (about 0.8% of rows) to demonstrate robust data preprocessing
    mask_indices = np.random.choice(df.index, size=int(0.008 * len(df)), replace=False)
    for idx in mask_indices[:len(mask_indices)//2]:
        df.loc[idx, 'humidity'] = np.nan
    for idx in mask_indices[len(mask_indices)//2:]:
        df.loc[idx, 'temperature'] = np.nan
        
    return df

if __name__ == '__main__':
    output_path = os.path.join(os.path.dirname(__file__), 'smart_irrigation_data.csv')
    df = generate_smart_irrigation_dataset(n_samples=3600)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Dataset generated with {len(df)} samples and saved to {output_path}")
    print(df.head())
    print("\nTarget Class Distribution:")
    print(df['irrigation_required'].value_counts(normalize=True))
