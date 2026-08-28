# MINEGUARD LoRa RF Field Network
## SIH26025 — Sub-GHz Long-Range Radio Architecture

---

### 1. RF Physical Parameters
- **Frequency**: 868.1 MHz – 868.5 MHz (EU868 / IN865 ISM Bands)
- **Modulation**: Chirp Spread Spectrum (LoRa)
- **Spreading Factors**: SF7 (High data rate) to SF9 (Maximum penetration)
- **Bandwidth**: 125 kHz
- **Coding Rate**: 4/5
- **Output Power**: +14 dBm to +20 dBm EIRP

---

### 2. Topology & Multi-Channel Reception
The MINEGATE base station features an **SX1302 / SX1303 LoRa Concentrator** supporting 8 concurrent demodulation channels. 
Nodes transmit asynchronously using randomized ALOHA backoff intervals to minimize packet collisions across large mining panels.
