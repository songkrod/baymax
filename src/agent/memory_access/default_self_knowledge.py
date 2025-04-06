DEFAULT_SELF_KNOWLEDGE = {
    "name": "baymax",
    "appearance": {
        "color": "white",
        "material": "TPU fabric",
        "size": "30cm",
        "features": [
            "inflatable body",
            "black translucent eye band made from 0.2mm TPU",
            "round base for balance"
        ],
        "skin_material": {
            "main": "0.4mm translucent white TPU",
            "eye_band": "0.2mm black translucent TPU"
        }
    },
    "hardware": {
        "main_processor": "Raspberry Pi Zero 2 W with Header",

        "audio": {
            "microphone": {
                "type": "Adafruit I2S MEMS Microphone Breakout",
                "model": "SPH0645LM4H",
                "interface": "I2S",
                "gpio": {
                    "clock": "GPIO18",
                    "data": "GPIO20"
                },
                "location": "center front",
                "role": "capture speech"
            },
            "speaker": {
                "type": "MAX98357",
                "interface": "I2S",
                "gpio": {
                    "din": "GPIO21",
                    "bclk": "GPIO19",
                    "lrclk": "GPIO18"
                },
                "location": "front chest",
                "role": "play TTS audio",
                "amp": "3W 4 ohm speaker"
            }
        },

        "vision": {
            "camera": {
                "model": "Pi Camera V2",
                "resolution": "8MP",
                "location": "behind eye band",
                "mount": "Enclosure case",
                "cable": "1m FFC"
            }
        },

        "display": {
            "eyes": {
                "left": {
                    "model": "SSD1315",
                    "type": "OLED",
                    "size": "0.96\" 128x64",
                    "i2c_address": "0x3C",
                    "location": "left eye",
                    "role": "display left eye expression"
                },
                "right": {
                    "model": "SSD1315",
                    "type": "OLED",
                    "size": "0.96\" 128x64",
                    "i2c_address": "0x3D",
                    "location": "right eye",
                    "role": "display right eye expression"
                }
            }
        },

        "motion": {
            "pump": {
                "type": "6V Mini Pump",
                "gpio": "GPIO22",
                "control": "IRLZ44N MOSFET",
                "role": "inflate body"
            },
            "valve": {
                "type": "Fa0520F DC 6V Solenoid Valve",
                "gpio": "GPIO23",
                "control": "IRLZ44N MOSFET",
                "role": "release air"
            },
            "mosfet": {
                "model": "IRLZ44N",
                "quantity": 3
            },
            "diode_protection": {
                "model": "1N4007",
                "quantity": 5
            }
        },

        "sensors": {
            "pressure": {
                "model": "MPX5010DP",
                "type": "analog",
                "location": "air tube",
                "role": "monitor internal air pressure"
            },
            "temperature": [
                {
                    "model": "DS18B20",
                    "location": "inside body",
                    "gpio": "GPIO4",
                    "role": "monitor body temperature"
                },
                {
                    "model": "DS18B20 TO-92",
                    "location": "inside logic box",
                    "gpio": "GPIO5",
                    "role": "monitor logic box temperature"
                }
            ],
            "current": {
                "model": "INA219",
                "interface": "I2C",
                "address": "0x40",
                "location": "battery input",
                "role": "measure power usage"
            }
        },

        "power": {
            "battery": {
                "model": "Samsung 30Q 18650",
                "quantity": 2,
                "capacity_each": "3000mAh",
                "arrangement": "series",
                "holder": "2-slot 18650 holder"
            },
            "charging": {
                "module": "TP4056 USB-C",
                "current_limit": "1A",
                "port": "USB Type-C"
            },
            "boost_converter": {
                "model": "XL6009",
                "quantity": 2
            }
        },

        "connectivity": {
            "wifi": "Built-in",
            "bluetooth": "Built-in"
        },

        "thermal_management": {
            "heatsink_kit": "Aluminum heatsink kit for Raspberry Pi"
        },

        "wiring": {
            "signal_wires": "AWG26 UL1007 white",
            "power_wires": "22AWG silicone, red-black, 200°C"
        },

        "external_structure": {
            "zippers": "Waterproof nylon zip #5 with head"
        },

        "tubing": {
            "type": "Silicone",
            "size": "3/5 mm"
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