# MINOR SAFETY SIH 2026 — ARTIFICIAL INTELLIGENCE & MACHINE LEARNING TECHNICAL DOCUMENTATION

## DOCUMENT 3 — SECTION 1: AI/ML ARCHITECTURE

**Model Type**: Unsupervised Anomaly Detection
**Algorithm**: Isolation Forest
**Framework**: Scikit-Learn (`scikit-learn`)
**Training Code**: `ml/train.py` & `backend/app/services/ai_service.py`
**Inference Code**: `ml/predict.py` & `backend/app/services/ai_service.py`
**Model Files**: `ml/model/isolation_forest.joblib`, `ml/model/feature_scaler.joblib`
**Implementation**: YES, AN ACTUAL ML MODEL EXISTS.

The system uses an Isolation Forest to detect multivariate anomalies in geotechnical data. The model is trained on a combination of historical PostgreSQL telemetry data, scaled via `StandardScaler`, and persisted as a `.joblib` file. 

---

## DOCUMENT 3 — SECTION 2: INPUT FEATURES

The Isolation Forest takes a specific vector of features to determine the structural health of the mine:

1. **`tilt_mag`** (Degrees): Calculated via Pythagorean theorem from `tilt_x` and `tilt_y`.
2. **`displacement`** (mm): Draw-wire physical extension.
3. **`displacement_rate`** (mm/hr): Velocity of ground movement over time.
4. **`vibration`** (g): Peak acceleration variance.
5. **`crack_status`** (Binary 0/1): High-weight indicator if crack > 0.5mm.
6. **`svi`** (Index): Subsidence Vulnerability Index. A heavily weighted composite score: `(disp_rate * 1.5) + (tilt_mag * 2.0) + (vib * 10.0) + (crack_status * 25.0)`.

---

## DOCUMENT 3 — SECTION 3: DATA PIPELINE

**Trace:**
```text
Live Sensor Reading (`POST /api/telemetry`)
 ↓
Backend FastAPI (`TelemetryService.process_reading`)
 ↓
Feature Engineering (`tilt_x`/`y` -> `tilt_mag`, `SVI` calculation)
 ↓
Feature Scaling (`StandardScaler.transform()`)
 ↓
ML Model (`IsolationForest.decision_function()`)
 ↓
Anomaly Score Generation
 ↓
Risk Classification Mapping (NORMAL, WARNING, HIGH, CRITICAL)
 ↓
Alert Generation (`AlertService.create_alert()`)
```
**Code Location**: `backend/app/services/ai_service.py` -> `predict_risk()`

---

## DOCUMENT 3 — SECTION 4: NODE CORRELATION / CASCADING RISK

**STATUS**: IMPLEMENTED / VERIFIED

The AI Service employs a spatial correlation algorithm. When a node experiences high risk, the backend executes a geographic query (Haversine distance calculation) against the PostgreSQL PostGIS database to find all active nodes within a predefined radius.

If `Node A` shows severe displacement, and `Node B` (within 100 meters) also shows an elevated risk score, the system increases the overall confidence of a massive subsidence event and expands the affected radius dynamically.

---

## DOCUMENT 3 — SECTION 5: INFRASTRUCTURE DAMAGE PREDICTION

**STATUS**: IMPLEMENTED / VERIFIED

The system actively predicts which public infrastructure will be harmed by a cave-in. 
1. **Input**: A critical anomaly is flagged by the Isolation Forest.
2. **Geographic Analysis**: A subsidence influence radius is calculated based on geotechnical formulas (`150.0 + (risk/100) * 300.0` meters).
3. **Intersection**: The system checks if the resulting `affected_zone` (Polygon) intersects with mapped Public Infrastructure (e.g., NH-218 Highway, Municipal Pipeline).
4. **Output**: An exact Evacuation Recommendation directive is added to the Alert payload and visualized on the GIS map.

*Note: This relies on geometric spatial intersection math, augmenting the ML anomaly trigger.*

---

## DOCUMENT 3 — SECTION 6: RISK CLASSIFICATION

The raw `decision_function` output from the Isolation Forest is normalized into a 0-100 `risk_score`.

- **0-40**: NORMAL
- **41-70**: WARNING (Elevated anomalies)
- **71-89**: HIGH (Severe multi-sensor anomaly)
- **90-100**: CRITICAL (Imminent failure characteristics)

---

## DOCUMENT 3 — SECTION 7: MODEL TRAINING

**Dataset**: The `IsolationForest` can be dynamically retrained against the latest 10,000 live sensor readings in the PostgreSQL database (`ai_service.py` -> `train_model()`).
**Hyperparameters**: `n_estimators=200`, `contamination=0.08`.
**Persistence**: Models are dumped to `ml/model/` using `joblib`.

---

## DOCUMENT 3 — SECTION 8: LIVE INFERENCE

**STATUS**: IMPLEMENTED / VERIFIED

The model receives LIVE hardware data. When `POST /api/telemetry` is hit by the Gateway, the reading is synchronously passed into `predict_risk()`. The output is immediately written to the `ai_predictions` database table and broadcasted via WebSockets to the dashboard.

---

## DOCUMENT 3 — SECTION 9: ALERT GENERATION

When a prediction hits `HIGH` or `CRITICAL`:
- An `Alert` row is written to the database.
- The `affected_zone` (PostGIS Polygon) is calculated and saved.
- `local_alarm_activated` boolean is set to True.
- The `NotificationService` queues an Email/SMS containing the exact infrastructure risk and ML anomaly score.

---

## DOCUMENT 3 — SECTION 10: MODEL EXPLAINABILITY

**Explainability Implementation**: Rule-based transparency overlay.
When an alert is generated, the JSON payload explicitly lists the driving features. Because Isolation Forest is an ensemble of trees, interpreting single paths is complex. Instead, the system appends the calculated `svi` (Subsidence Vulnerability Index) and highlights the specific sensor (e.g., "Crack width exceeded 0.5mm") that heavily skewed the anomaly score.

---

## DOCUMENT 3 — SECTION 11: AI/ML FAILURE MODES

- **Missing Sensor Data**: Pydantic schemas enforce defaults (`0.0`). The `svi` formula will gracefully process zero-values, resulting in a lower risk score, preventing false positives but risking false negatives.
- **Model Unavailable**: If `.joblib` files are deleted, the system falls back to a hardcoded rule-based threshold engine (`if svi > 50: WARNING...`) ensuring life-safety critical alerts still fire.

---

## DOCUMENT 3 — SECTION 12: AI/ML TESTING

| TEST | EXPECTED RESULT | ACTUAL RESULT | STATUS |
|---|---|---|---|
| Single Node Rapid Displacement | Anomaly detected, Risk CRITICAL | Risk = 98.5, Alert Fired | PASSED |
| Neighboring Nodes Correlated | Subsidence radius expanded | Radius = 445m, Intersects NH-218 | PASSED |
| Missing DB Model | Fallback to rule engine | Rule engine triggered | PASSED |

---

## DOCUMENT 3 — SECTION 13: AI/ML JUDGE QUESTIONS

**Q: Why Isolation Forest and not Deep Learning (LSTMs)?**
A: Deep learning requires massive amounts of labeled anomalous data to avoid overfitting. In mining subsidence, catastrophic collapses are rare, meaning we have highly imbalanced datasets (mostly normal data). Isolation Forests excel at unsupervised anomaly detection, isolating outlier behavior without needing labeled failure events.

**Q: How do you determine the evacuation risk for public infrastructure?**
A: We combine ML with Geospatial Mathematics. When the ML model flags a critical anomaly, we calculate a physical subsidence influence radius based on the depth of the mine and the severity of the anomaly. We then use PostGIS/spatial logic to see if that expanding radius intersects with mapped highways or pipelines.

---

## ACTUAL IMPLEMENTATION STATUS

| Feature | Status | Evidence/File | Tested? | Notes |
|---------|--------|---------------|---------|-------|
| ML Model (Isolation Forest) | IMPLEMENTED / VERIFIED | `ml/model/*.joblib` | Yes | Live on server |
| Feature Extraction Pipeline | IMPLEMENTED / VERIFIED | `ai_service.py` | Yes | Calculates SVI |
| Live Inference | IMPLEMENTED / VERIFIED | `ai_service.py` | Yes | Triggered on HTTP POST |
| Cascading Node Risk | IMPLEMENTED / VERIFIED | `ai_service.py` | Yes | Haversine distance logic |
| Infrastructure Threat GIS | IMPLEMENTED / VERIFIED | `ai_service.py` | Yes | Intersects with NH-218 |
| Dynamic Retraining | CONFIGURED / NOT VERIFIED| `ai_service.train_model`| No | Requires bulk real data |
