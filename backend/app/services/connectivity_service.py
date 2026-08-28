import socket
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectivityManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectivityManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.internet_online = True
        self.cellular_available = True
        self.gateway_online = True
        self.mqtt_connected = True
        self.email_reachable = True
        self.sms_reachable = True
        self.last_checked = datetime.now()
        self.mock_mode = False

    def _check_internet(self) -> bool:
        if self.mock_mode:
            return self.internet_online
        try:
            # Connect to Google DNS to check internet
            socket.setdefaulttimeout(3)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except Exception:
            return False

    async def check_connectivity(self):
        if self.mock_mode:
            return
            
        self.internet_online = self._check_internet()
        self.email_reachable = self.internet_online
        
        # In a real deployed edge gateway (like Raspberry Pi), we would query the cellular modem via AT commands.
        # For the prototype, we assume Cellular is available if gateway is online.
        self.cellular_available = self.gateway_online

        self.last_checked = datetime.now()
        logger.info(f"[Connectivity] Internet: {self.internet_online}, Cellular: {self.cellular_available}")
        
    def get_status(self) -> dict:
        return {
            "internet_online": self.internet_online,
            "cellular_available": self.cellular_available,
            "gateway_online": self.gateway_online,
            "mqtt_connected": self.mqtt_connected,
            "email_reachable": self.email_reachable,
            "sms_reachable": self.sms_reachable,
            "last_checked": self.last_checked.isoformat()
        }

connectivity_manager = ConnectivityManager()
