
This project is a complete mini‑pipeline for 'industrial defect classification' based on 'sensor data', including FFT‑derived frequency-domain features. The model uses a 'Naive Bayes classifier', supported by PCA, resampling, feature selection, and correlation analysis.

The goal is to simulate a realistic workflow from 'raw manufacturing data' → 'balancing' → 'feature reduction' → 'model tuning' → 'classification evaluation', similar to what would occur in industrial predictive maintenance or sensor‑based QA systems.

---
Key Concepts Demonstrated

This project shows real industrial ML workflow skills:

Handling imbalanced industrial datasets
- Bootstrapping (upsampling)
- SMOTE over‑sampling
- Stratified train-test splitting

Feature engineering & selection
- Dropping zero‑value FFT rows
- Removing highly-correlated features (|ρ| ≥ 0.95)
- Correlation ratio (η²) scoring
- Mutual Information (MI) ranking
- PCA dimensionality reduction
- SelectFromModel (Random Forest importance)

ML pipeline & hyperparameter tuning
- Gaussian Naive Bayes + PCA + PowerTransformer
- GridSearchCV optimisation
- RandomForest alternative model for comparison

Industrial signal characteristics
- FFT temperature, vibration, and pressure bins
- Time-domain sensor readings (Temp, Current, Vibration, Pressure, Flow, Voltage)

This is a project on predictive maintenance, manufacturing analytics, and industrial AI.

---

Key Learnings
-Naive Bayes struggles on:
  -Continuous data that deviates from Gaussian assumptions
  -Highly correlated input features
  -Complex nonlinear boundaries
-FFT industrial signals produce strong multicollinearity, requiring PCA or feature removal
-SMOTE + bootstrapping helps significantly
-Random Forests generally outperform NB in industrial fault detection due to:
  -Nonlinearity
  -Complex signal interactions
