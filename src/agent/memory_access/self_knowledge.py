
import json
from utils.file import ensure_file
from config.settings import settings

class SelfKnowledge:
    KNOWLEDGE_PATH = settings.SELF_KNOWLEDGE_PATH
    def __init__(self):
        ensure_file(self.KNOWLEDGE_PATH, default=self.default_knowledge())

    def default_knowledge(self):
        return {
            "name": settings.ROBOT_NAME,
            "appearance": {
                "color": "white",
                "material": "TPU fabric",
                "size": "30cm",
                "features": ["inflatable body", "black translucent eye band", "round base for balance"]
            },
            "hardware": {
                "main_processor": "Raspberry Pi Zero 2 W",
                "audio": {
                    "microphone": "USB Microphone",
                    "speaker": "PAM8403 module + speaker"
                },
                "vision": {
                    "camera": "Raspberry Pi Camera Module (integrated behind eye band)"
                },
                "display": {
                    "oled": "0.96\" I2C OLED Display"
                },
                "motion": {
                    "pump": "12V Air Pump",
                    "valve": "12V Solenoid Valve",
                    "mosfet": "IRLZ44N Logic-Level MOSFET"
                },
                "sensors": {
                    "pressure_sensor": "MPX5010DP",
                    "temperature_sensors": ["DS18B20 (inside body)", "DS18B20 (in logic box)"],
                    "current_sensor": "INA219"
                },
                "power": {
                    "battery": "1x 18650 Li-ion (3000mAh, extendable to 2 cells)",
                    "boost_converter": "MT3608 x2"
                },
                "connectivity": {
                    "wifi": "Built-in",
                    "bluetooth": "Built-in"
                }
            },
            "abilities": [
                "listen and recognize speech",
                "identify speaker by voice",
                "respond using natural TTS",
                "understand conversation context",
                "control inflation/deflation via sensors",
                "express personality and emotion",
                "update itself from remote repository",
                "learn new skills dynamically"
            ],
            "limitations": [
                "no arms",
                "limited CPU performance",
                "single-threaded audio processing",
                "can't process vision in real-time"
            ]
        }

    def get_knowledge(self):
        with open(self.KNOWLEDGE_PATH, "r") as f:
            return json.load(f)

    def update_knowledge(self, data: dict):
        with open(self.KNOWLEDGE_PATH, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
