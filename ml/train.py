"""
=============================================================================
RED HACK Mine Subsidence Monitoring System (SIH26025)
Machine Learning Model Training Pipeline
-----------------------------------------------------------------------------
Trains an IsolationForest unsupervised anomaly detector and calibrates
risk evaluation metrics against synthetic mine strata subsidence data.
=============================================================================
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score

from feature_engineering import FeatureEngineer, FEATURE_COLUMNS
from data.synthetic.generate_dataset import generate_synthetic_mine_data

def train_subsidence_anomaly_model(
    data_path: str = "ml/data/synthetic/mine_subsidence_synthetic.csv",
    model_dir: str = "ml/model"
):
    print("===================================================================")
    print(" [ML TRAIN] Starting Mine Subsidence Anomaly Detector Training")
    print("===================================================================")
    
    # 1. Load or generate synthetic dataset
    if not os.path.exists(data_path):
        print(f"[ML TRAIN] Dataset not found at {data_path}. Generating new synthetic dataset...")
        df_raw = generate_synthetic_mine_data(output_path=data_path)
    else:
        print(f"[ML TRAIN] Loading dataset from: {data_path}")
        df_raw = pd.read_csv(data_path)
        
    print(f"[ML TRAIN] Raw records loaded: {len(df_raw)}")
    
    # 2. Feature Engineering
    fe = FeatureEngineer()
    df_transformed = fe.transform_dataframe(df_raw)
    
    # Clean NaNs or infinities
    X_df = df_transformed[FEATURE_COLUMNS].fillna(0.0).replace([np.inf, -np.inf], 0.0)
    
    # Filter training normal data for baseline fitting
    normal_mask = df_transformed["scenario_label"] == "NORMAL"
    X_normal = X_df[normal_mask]
    
    print(f"[ML TRAIN] Training feature matrix shape: {X_df.shape}")
    print(f"[ML TRAIN] Normal baseline instances: {len(X_normal)} ({len(X_normal)/len(X_df)*100:.1f}%)")
    print(f"[ML TRAIN] Feature list: {FEATURE_COLUMNS}")
    
    # 3. Fit Feature Scaler (StandardScaler)
    scaler = StandardScaler()
    scaler.fit(X_normal)
    X_scaled_all = scaler.transform(X_df)
    X_scaled_normal = scaler.transform(X_normal)
    
    # 4. Train Isolation Forest
    # Contamination corresponds to expected non-normal / anomaly proportion in mine operation (~8-10%)
    model = IsolationForest(
        n_estimators=200,
        max_samples="auto",
        contamination=0.08,
        random_state=42,
        bootstrap=False,
        n_jobs=-1
    )
    
    print("[ML TRAIN] Fitting IsolationForest on baseline & exploratory features...")
    model.fit(X_scaled_normal)
    
    # 5. Evaluate on all scenarios
    # raw anomaly score: negative for anomalies, positive for normal
    raw_scores = model.decision_function(X_scaled_all)
    # Map to [0.0, 1.0] where 1.0 is most anomalous
    # Decision function roughly in range [-0.5, 0.5]
    min_dec = np.min(raw_scores)
    max_dec = np.max(raw_scores)
    norm_anomaly_score = 1.0 - ((raw_scores - min_dec) / (max_dec - min_dec + 1e-9))
    
    df_transformed["raw_anomaly_score"] = raw_scores
    df_transformed["anomaly_score_0_1"] = norm_anomaly_score
    df_transformed["ml_anomaly_pred"] = model.predict(X_scaled_all) # -1: anomaly, 1: normal
    
    print("\n---------------- Scenario Evaluation Breakdown ----------------")
    eval_summary = df_transformed.groupby("scenario_label").agg({
        "anomaly_score_0_1": ["mean", "min", "max"],
        "ml_anomaly_pred": lambda x: (x == -1).mean() * 100.0
    })
    eval_summary.columns = ["Score_Mean", "Score_Min", "Score_Max", "Anomaly_Detection_Rate_%"]
    print(eval_summary.to_string())
    
    # Binary Ground Truth vs ML Detection
    ground_truth_binary = (df_transformed["risk_class"] > 0).astype(int)
    pred_binary = (df_transformed["ml_anomaly_pred"] == -1).astype(int)
    
    try:
        auc = roc_auc_score(ground_truth_binary, norm_anomaly_score)
        print(f"\n[ML TRAIN] Anomaly Detection ROC-AUC Score: {auc:.4f}")
    except Exception as e:
        print(f"[ML TRAIN] Could not compute ROC-AUC: {e}")
        
    # 6. Save Model Artifacts
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "isolation_forest.joblib")
    scaler_path = os.path.join(model_dir, "feature_scaler.joblib")
    meta_path = os.path.join(model_dir, "model_metadata.json")
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    metadata = {
        "model_type": "IsolationForest",
        "n_estimators": 200,
        "features": FEATURE_COLUMNS,
        "score_normalization": {
            "min_decision_value": float(min_dec),
            "max_decision_value": float(max_dec)
        },
        "training_samples_count": len(X_df),
        "trained_timestamp": pd.Timestamp.now().isoformat(),
        "performance": {
            "normal_score_mean": float(df_transformed[df_transformed['scenario_label'] == 'NORMAL']['anomaly_score_0_1'].mean()),
            "critical_score_mean": float(df_transformed[df_transformed['scenario_label'] == 'CRITICAL']['anomaly_score_0_1'].mean())
        }
    }
    
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"\n[ML TRAIN] Saved trained model to: {os.path.abspath(model_path)}")
    print(f"[ML TRAIN] Saved feature scaler to: {os.path.abspath(scaler_path)}")
    print(f"[ML TRAIN] Saved metadata to: {os.path.abspath(meta_path)}")
    print("===================================================================\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "data", "synthetic", "mine_subsidence_synthetic.csv")
    model_folder = os.path.join(current_dir, "model")
    train_subsidence_anomaly_model(data_path=data_file, model_dir=model_folder)
