"""
Hardware Integration Bridge for Arduino / ESP32 and Virtual Simulator
Communicates with microcontrollers over USB Serial or runs high-fidelity
agricultural environmental simulation when physical hardware is unplugged.
"""

import sys
import os
import time
import json
import random
import threading
from datetime import datetime
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from inference import SmartIrrigationEngine

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class HardwareBridge:
    def __init__(self, port=None, baudrate=9600, simulated=True):
        self.port = port
        self.baudrate = baudrate
        self.simulated = simulated
        self.serial_conn = None
        self.engine = SmartIrrigationEngine()
        
        # State variables
        self.is_running = False
        self.latest_telemetry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'soil_moisture': 42.0,
            'temperature': 28.5,
            'humidity': 62.0,
            'soil_temperature': 25.0,
            'sunlight_lux': 35000.0,
            'rain_sensor': 0,
            'crop_type': 'Tomato',
            'soil_type': 'Loamy',
            'irrigation_required': 0,
            'water_requirement_ml': 0.0,
            'pump_status': 'OFF',
            'pump_runtime_remaining': 0.0,
            'confidence': 98.0,
            'soil_health': 'Optimal Moisture Level',
            'badge_color': '#2f9e44',
            'mode': 'SIMULATED' if simulated else 'HARDWARE',
            'log_message': 'System Initialized.'
        }
        self.history = []
        self.manual_override = False
        self.manual_pump_state = False
        self.lock = threading.Lock()
        
    @staticmethod
    def get_available_ports():
        if not SERIAL_AVAILABLE:
            return []
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]
        
    def connect_serial(self, port_name, baudrate=9600):
        if not SERIAL_AVAILABLE:
            return False, "pyserial not installed."
        try:
            self.serial_conn = serial.Serial(port_name, baudrate, timeout=1.5)
            self.simulated = False
            self.port = port_name
            return True, f"Successfully connected to {port_name} at {baudrate} baud."
        except Exception as e:
            self.simulated = True
            return False, f"Could not connect to {port_name}: {str(e)}. Defaulting to Simulation."
            
    def set_manual_override(self, override: bool, pump_on: bool = False):
        with self.lock:
            self.manual_override = override
            self.manual_pump_state = pump_on
            if override:
                self.latest_telemetry['pump_status'] = 'ON (MANUAL)' if pump_on else 'OFF (MANUAL)'
            
    def step_simulation(self):
        """Simulate realistic dynamic environment step"""
        with self.lock:
            t = self.latest_telemetry
            
            # If pump is currently running, moisture increases
            if 'ON' in t['pump_status']:
                t['soil_moisture'] = min(92.0, t['soil_moisture'] + random.uniform(1.8, 3.2))
                if t['pump_runtime_remaining'] > 0:
                    t['pump_runtime_remaining'] = max(0.0, t['pump_runtime_remaining'] - 2.0)
                    if t['pump_runtime_remaining'] == 0:
                        t['pump_status'] = 'OFF'
                        self.send_actuation_command(False)
            else:
                # Natural drying from heat and sunlight
                drying_rate = 0.15 + (t['temperature'] - 20.0) * 0.015 + (t['sunlight_lux'] / 200000.0)
                if t['rain_sensor'] == 1:
                    t['soil_moisture'] = min(95.0, t['soil_moisture'] + random.uniform(0.5, 1.5))
                else:
                    t['soil_moisture'] = max(8.0, t['soil_moisture'] - drying_rate * random.uniform(0.7, 1.3))
                    
            # Ambient temperature & humidity slight drift
            t['temperature'] = round(float(np.clip(t['temperature'] + random.uniform(-0.4, 0.4), 16.0, 44.0)), 1)
            t['humidity'] = round(float(np.clip(t['humidity'] + random.uniform(-1.0, 1.0), 20.0, 95.0)), 1)
            t['sunlight_lux'] = round(float(np.clip(t['sunlight_lux'] + random.uniform(-1500, 1500), 100, 85000)), 0)
            t['soil_temperature'] = round(float(0.75 * t['temperature'] + 5.5 + random.uniform(-0.2, 0.2)), 1)
            
            # Occasionally toggle rain (5% chance)
            if random.random() < 0.03:
                t['rain_sensor'] = 1 if t['rain_sensor'] == 0 else 0
                
            t['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # AI Inference
            if not self.manual_override:
                decision = self.engine.predict(
                    soil_moisture=t['soil_moisture'],
                    temperature=t['temperature'],
                    humidity=t['humidity'],
                    soil_temperature=t['soil_temperature'],
                    sunlight_lux=t['sunlight_lux'],
                    rain_sensor=t['rain_sensor'],
                    crop_type=t['crop_type'],
                    soil_type=t['soil_type']
                )
                
                t['irrigation_required'] = decision['irrigation_required']
                t['water_requirement_ml'] = decision['water_requirement_ml']
                t['confidence'] = decision['confidence']
                t['soil_health'] = decision['soil_health']
                t['badge_color'] = decision['badge_color']
                t['log_message'] = decision['reasoning']
                
                # Actuate pump
                if decision['irrigation_required'] == 1:
                    t['pump_status'] = 'ON (AI AUTO)'
                    t['pump_runtime_remaining'] = decision['recommended_pump_duration_sec']
                    self.send_actuation_command(True)
                else:
                    if t['pump_runtime_remaining'] <= 0:
                        t['pump_status'] = 'OFF'
                        self.send_actuation_command(False)
            else:
                t['log_message'] = "Manual operator override active. AI automated control bypassed."
                
            # Log to history ring buffer (keep last 60 records)
            self.history.append(dict(t))
            if len(self.history) > 60:
                self.history.pop(0)

    def send_actuation_command(self, pump_on: bool):
        """Send serial command to microcontroller"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                cmd = "PUMP_ON\n" if pump_on else "PUMP_OFF\n"
                self.serial_conn.write(cmd.encode('utf-8'))
            except Exception as e:
                print(f"[SERIAL WRITE ERROR] {e}")

    def read_hardware_serial(self):
        """Parse incoming telemetry from Arduino / ESP32"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return
        try:
            line = self.serial_conn.readline().decode('utf-8').strip()
            if not line:
                return
            # Expected JSON format: {"moisture": 32.1, "temp": 29.4, "humidity": 55.2, "rain": 0}
            if line.startswith('{') and line.endswith('}'):
                data = json.loads(line)
                with self.lock:
                    self.latest_telemetry['soil_moisture'] = float(data.get('moisture', self.latest_telemetry['soil_moisture']))
                    self.latest_telemetry['temperature'] = float(data.get('temp', self.latest_telemetry['temperature']))
                    self.latest_telemetry['humidity'] = float(data.get('humidity', self.latest_telemetry['humidity']))
                    self.latest_telemetry['rain_sensor'] = int(data.get('rain', self.latest_telemetry['rain_sensor']))
                    self.latest_telemetry['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Run AI prediction on fresh hardware telemetry
                    if not self.manual_override:
                        decision = self.engine.predict(
                            soil_moisture=self.latest_telemetry['soil_moisture'],
                            temperature=self.latest_telemetry['temperature'],
                            humidity=self.latest_telemetry['humidity'],
                            rain_sensor=self.latest_telemetry['rain_sensor'],
                            crop_type=self.latest_telemetry['crop_type'],
                            soil_type=self.latest_telemetry['soil_type']
                        )
                        self.latest_telemetry['irrigation_required'] = decision['irrigation_required']
                        self.latest_telemetry['water_requirement_ml'] = decision['water_requirement_ml']
                        self.latest_telemetry['confidence'] = decision['confidence']
                        self.latest_telemetry['soil_health'] = decision['soil_health']
                        self.latest_telemetry['badge_color'] = decision['badge_color']
                        self.latest_telemetry['log_message'] = decision['reasoning']
                        
                        if decision['irrigation_required'] == 1:
                            self.latest_telemetry['pump_status'] = 'ON (AI AUTO)'
                            self.send_actuation_command(True)
                        else:
                            self.latest_telemetry['pump_status'] = 'OFF'
                            self.send_actuation_command(False)
                            
                    self.history.append(dict(self.latest_telemetry))
                    if len(self.history) > 60:
                        self.history.pop(0)
        except Exception as e:
            print(f"[SERIAL READ ERROR] {e}")

if __name__ == '__main__':
    bridge = HardwareBridge(simulated=True)
    print("Testing 3 simulation steps:")
    for i in range(3):
        bridge.step_simulation()
        print(f"Step {i+1}: Moisture={bridge.latest_telemetry['soil_moisture']:.1f}%, Temp={bridge.latest_telemetry['temperature']:.1f}C, Pump={bridge.latest_telemetry['pump_status']}")
        time.sleep(0.5)
