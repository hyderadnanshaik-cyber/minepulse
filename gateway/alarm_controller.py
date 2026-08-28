import logging
import time
from gateway.config import GATEWAY_CONFIG

logger = logging.getLogger("AlarmController")

class GPIOAlarmOutputAdapter:
    def __init__(self, pin: int = 18):
        self.pin = pin
        self.is_active = False
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
            self.gpio.setmode(self.gpio.BCM)
            self.gpio.setup(self.pin, self.gpio.OUT, initial=self.gpio.LOW)
            self.has_hardware = True
        except ImportError:
            self.has_hardware = False
            logger.info("RPi.GPIO not detected. Running in SIMULATION alarm mode.")

    def activate(self, duration_sec: int = 10):
        self.is_active = True
        logger.warning(f"🚨 [EMERGENCY ALARM ACTIVATED] Local Siren/Buzzer ON for {duration_sec}s")
        if self.has_hardware:
            self.gpio.output(self.pin, self.gpio.HIGH)

    def silence(self):
        self.is_active = False
        logger.info("🔕 [ALARM SILENCED] Local Siren/Buzzer OFF")
        if self.has_hardware:
            self.gpio.output(self.pin, self.gpio.LOW)

    def test(self):
        logger.info("⚡ [ALARM TEST] Activating siren for 3 seconds...")
        self.activate(3)
        time.sleep(3)
        self.silence()

alarm_controller = GPIOAlarmOutputAdapter(pin=GATEWAY_CONFIG["alarm_pin"])
