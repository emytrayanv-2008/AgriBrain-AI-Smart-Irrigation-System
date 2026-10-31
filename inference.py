"""
Real-Time Inference and Irrigation Decision Engine
Loads pre-trained pipelines to classify irrigation necessity,
predict water requirements, and calculate pump run durations.
"""

import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

class SmartIrrigationEngine:
    def __init__(self):
        self.preprocessor = joblib.load(os.path.join(MODELS_DIR, 'preprocessor.pkl'))
        self.models = {
            'Random Forest': joblib.load(os.path.join(MODELS_DIR, 'irrigation_classifier.pkl')),
            'Decision Tree': joblib.load(os.path.join(MODELS_DIR, 'decision_tree_classifier.pkl')),
            'Logistic Regression': joblib.load(os.path.join(MODELS_DIR, 'logistic_regression.pkl'))
        }
        self.water_regressor = joblib.load(os.path.join(MODELS_DIR, 'water_regressor.pkl'))
        
        # Pump specification: standard 5V/12V mini DC submersible water pump delivers ~35 ml/sec
        self.pump_flow_rate_ml_per_sec = 35.0
        
    def predict(self, 
                soil_moisture: float, 
                temperature: float, 
                humidity: float, 
                soil_temperature: float = None,
                sunlight_lux: float = None, 
                rain_sensor: int = 0, 
                crop_type: str = 'Tomato', 
                soil_type: str = 'Loamy',
                model_name: str = 'Random Forest'):
        """
        Evaluate sensor inputs and return AI determination.
        """
        if soil_temperature is None:
            soil_temperature = round(0.75 * temperature + 5.0, 1)
        if sunlight_lux is None:
            sunlight_lux = 45000.0 if (20.0 <= temperature <= 45.0) else 15000.0
            
        # Feature engineering matching training data
        temp_moisture_ratio = temperature / (soil_moisture + 1.0)
        vapor_deficit = (100.0 - humidity) * (temperature / 50.0)
        
        input_dict = {
            'soil_moisture': [float(soil_moisture)],
            'temperature': [float(temperature)],
            'humidity': [float(humidity)],
            'soil_temperature': [float(soil_temperature)],
            'sunlight_lux': [float(sunlight_lux)],
            'rain_sensor': [int(rain_sensor)],
            'temp_moisture_ratio': [float(temp_moisture_ratio)],
            'vapor_deficit': [float(vapor_deficit)],
            'crop_type': [str(crop_type)],
            'soil_type': [str(soil_type)]
        }
        
        df_input = pd.DataFrame(input_dict)
        X_proc = self.preprocessor.transform(df_input)
        
        clf = self.models.get(model_name, self.models['Random Forest'])
        
        # Strict Rain Override check for real-world agronomy: If sensor detects active rain,
        # immediate water savings mandate pump shut-off
        if rain_sensor == 1:
            irrigation_required = 0
            confidence = 0.999
            water_ml = 0.0
            pump_duration_sec = 0.0
            status_text = "RAIN DETECTED - PUMP INHIBITED (SAVING WATER)"
            reasoning = "Active rainfall detected by rain sensor module. Irrigation disabled to prevent waterlogging and conserve pump energy."
        else:
            pred_class = clf.predict(X_proc)[0]
            irrigation_required = int(pred_class)
            
            if hasattr(clf, "predict_proba"):
                probas = clf.predict_proba(X_proc)[0]
                confidence = float(probas[irrigation_required])
            else:
                confidence = 0.95
                
            if irrigation_required == 1:
                water_ml = max(100.0, float(self.water_regressor.predict(X_proc)[0]))
                pump_duration_sec = round(water_ml / self.pump_flow_rate_ml_per_sec, 1)
                status_text = "IRRIGATION REQUIRED - PUMP ACTIVATED"
                reasoning = (f"Soil moisture ({soil_moisture:.1f}%) is below optimal threshold for {crop_type} in {soil_type} soil. "
                             f"Ambient temperature ({temperature:.1f}°C) and evaporative demand indicate immediate hydration needed.")
            else:
                water_ml = 0.0
                pump_duration_sec = 0.0
                status_text = "SOIL MOISTURE SUFFICIENT - PUMP OFF"
                reasoning = (f"Current soil moisture ({soil_moisture:.1f}%) is adequate for {crop_type}. "
                             f"Environmental conditions do not necessitate supplemental irrigation.")
                
        # Classify Soil Health status
        if soil_moisture < 20.0:
            health_status = "Severely Dry / Wilting Hazard"
            badge_color = "#e03131"
        elif soil_moisture < 35.0:
            health_status = "Low Moisture / Thirsty"
            badge_color = "#f59f00"
        elif soil_moisture <= 75.0:
            health_status = "Optimal Moisture Level"
            badge_color = "#2f9e44"
        else:
            health_status = "High Moisture / Saturated"
            badge_color = "#1971c2"
            
        return {
            'irrigation_required': irrigation_required,
            'confidence': round(confidence * 100, 1),
            'status_text': status_text,
            'water_requirement_ml': round(water_ml, 1),
            'recommended_pump_duration_sec': pump_duration_sec,
            'soil_health': health_status,
            'badge_color': badge_color,
            'reasoning': reasoning,
            'model_used': model_name
        }

if __name__ == '__main__':
    engine = SmartIrrigationEngine()
    test_res = engine.predict(soil_moisture=22.5, temperature=34.2, humidity=38.0, crop_type='Tomato', soil_type='Sandy')
    print("Test Decision Engine Inference:")
    print(test_res)
