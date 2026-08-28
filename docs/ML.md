# RED HACK Machine Learning & Subsidence Risk Prediction Engine

> [!IMPORTANT]
> **PROTOTYPE NOTICE**: The mathematical risk thresholds and synthetic training distributions described herein represent a functional prototype built for demonstration and evaluation under **Smart India Hackathon 2026 (SIH26025)**. They are not official Directorate General of Mines Safety (DGMS) statutory safety limits.

---

## 1. Problem Formulation
Mine roof collapse and surface subsidence events are rarely instantaneous; they are preceded by micro-fractures, subtle angle changes in rock strata, rate-of-displacement spikes, and micro-seismic vibrations. 

The machine learning objective is twofold:
1. **Unsupervised Anomaly Detection**: Detect abnormal multi-sensor patterns without requiring thousands of labeled catastrophic collapse records.
2. **Hybrid Geotechnical Risk Scoring**: Combine data-driven anomaly scores with physical rule-based geotechnical limits to produce an interpretable 0–100 Risk Score.

---

## 2. Model Architecture: Isolation Forest

We implement **Isolation Forest (iForest)** (`sklearn.ensemble.IsolationForest`), which isolates anomalies by randomly selecting a feature and randomly selecting a split value between the maximum and minimum values of the selected feature.

```
       [Normal Data Point]                        [Subsidence Anomaly Point]
      Requires deep partitioning                     Isolated near tree root
              (Tree Depth > 12)                            (Tree Depth <= 3)

                 o                                            o
               /   \                                        /   \
              o     o                                    [ANOMALY] o
             / \   / \                                            / \
            o   o o   o                                          o   o
           / \ ...
          [NORMAL]
```

### Advantages for Underground Mining:
- **Low Computational Complexity**: $O(n \cdot \log n)$ training and $O(t \cdot \text{depth})$ edge inference, running in < 5ms on a Raspberry Pi.
- **Unsupervised Learning**: Learns baseline healthy strata behavior and flags any uncharacteristic drift.
- **Robustness to Multi-Collinearity**: Handles correlated sensor readings (e.g. displacement accompanying tilt).

---

## 3. Feature Engineering Pipeline

Every incoming raw sensor frame is transformed into a rich 6-dimensional feature vector:

$$\mathbf{x} = \begin{bmatrix} \theta \\ d \\ v \\ c \\ \frac{\Delta \theta}{\Delta t} \\ \frac{\Delta d}{\Delta t} \end{bmatrix}$$

| Feature Symbol | Feature Name | Unit | Geotechnical Significance |
| :--- | :--- | :--- | :--- |
| $\theta$ | **Roof Tilt** | Degrees ($^\circ$) | Absolute inclination of roof strata from horizontal |
| $d$ | **Displacement** | Millimeters (mm) | Convergence between roof and floor / pillar movement |
| $v$ | **Seismic Vibration** | $g$ ($9.81 \, \text{m/s}^2$) | Micro-seismic rumbling from shearing rock layers |
| $c$ | **Crack Line State**| Boolean ($0$ or $1$) | 1 = Conductive fracture line severed |
| $\frac{\Delta \theta}{\Delta t}$ | **Tilt Rate** | $^\circ/\text{min}$ | Velocity of angular deformation (critical precursor) |
| $\frac{\Delta d}{\Delta t}$ | **Convergence Rate** | $\text{mm}/\text{min}$ | Speed of roof downward acceleration |

---

## 4. Synthetic Training Dataset (PROTOTYPE)

In the absence of live destructive rockfall data during the prototype phase, a physics-informed synthetic generator creates 10,000 baseline telemetry samples with embedded subsidence profiles:

1. **Normal Baseline (90% of data)**:
   - Tilt $\sim \mathcal{N}(1.0^\circ, 0.3^\circ)$
   - Displacement $\sim \mathcal{N}(2.5\,\text{mm}, 0.8\,\text{mm})$
   - Vibration $\sim \text{Weibull}(k=1.2, \lambda=0.03\,g)$
   - Crack state = `False`
2. **Accelerated Creep Phase (7% of data)**:
   - Continuous positive drift in $\frac{\Delta d}{\Delta t}$ and $\frac{\Delta \theta}{\Delta t}$.
3. **Imminent Subsidence / Rupture Phase (3% of data)**:
   - Tilt $> 5.0^\circ$, Displacement $> 25\,\text{mm}$, Vibration $> 0.25\,g$, Crack = `True`.

---

## 5. Hybrid Risk Scoring Formula

The aggregate Risk Score $R \in [0, 100]$ combines the model anomaly score $S_{\text{ML}} \in [0, 1]$ with geotechnical penalty weights:

$$R = \min\left(100, \; 40 \cdot S_{\text{ML}} + 25 \cdot \left(\frac{\theta}{\theta_{\text{crit}}}\right) + 20 \cdot \left(\frac{d}{d_{\text{crit}}}\right) + 15 \cdot \left(\frac{v}{v_{\text{crit}}}\right) + 30 \cdot c\right)$$

*Where default prototype normalization constants are:*
- $\theta_{\text{crit}} = 5.0^\circ$
- $d_{\text{crit}} = 20.0\,\text{mm}$
- $v_{\text{crit}} = 0.30\,g$

---

## 6. Risk Level Classification

| Risk Level | Score Range | Color Code | Action Required |
| :--- | :---: | :---: | :--- |
| **NORMAL** | $0 \le R < 25$ | Green (`#10B981`) | Normal mining operations |
| **LOW** | $25 \le R < 50$ | Blue (`#3B82F6`) | Routine inspection |
| **MEDIUM** | $50 \le R < 70$ | Yellow (`#F59E0B`) | Increase sensor polling; alert shift in-charge |
| **HIGH** | $70 \le R < 85$ | Orange (`#F97316`) | Halt heavy machinery; inspect roof bolting |
| **CRITICAL** | $85 \le R \le 100$ | Red (`#EF4444`) | **SOUND INDUSTRIAL SIREN; EVACUATE PANEL** |

---

## 7. Spatial Multi-Node Correlation

To prevent false alarms caused by accidental physical strikes (e.g. a miner's tool striking a single sensor node):
- The system checks if neighboring nodes within a radius $r \le 50\,\text{m}$ (or sharing the same working panel) also detect elevated risk ($R > 50$).
- If only 1 node spikes in isolation with zero neighbor correlation, the event is flagged as an `ISOLATED_ANOMALY` (confidence dampened).
- If $\ge 2$ neighboring nodes correlate simultaneously, the event is escalated to `CONFIRMED_STRATA_MOVEMENT` with confidence $> 95\%$.
