
This project builds a full machine learning pipeline for predicting whether an individual earns  
“> 50K” or “≤ 50K” annually, using the widely studied 'Adult Income Prediction Dataset' (UCI / Kaggle).

The workflow includes:
- Exploratory data analysis (EDA)
- Categorical & numerical distribution plots
- Handling categorical variables and missing values
- Class imbalance processing with SMOTE
- Feature reduction using correlation analysis
- Mutual Information–based feature selection
- Training and comparison of multiple models:
  - Random Forest
  - Multinomial Naive Bayes
  - Gaussian Naive Bayes
- Evaluation using classification reports and confusion matrices

This project demonstrates practical ML engineering with a realistic, messy, mixed‑type dataset.

---

Key Skills Demonstrated

Data Cleaning & Preprocessing
- Loaded dataset directly from **KaggleHub**
- Replaced `'?'` with `NaN` and removed incomplete rows
- Identified categorical & numerical columns programmatically
- Trained models with a **ColumnTransformer pipeline** to avoid data leakage

Exploratory Data Analysis (EDA)
- Categorical feature distributions vs. income
- Numerical feature histograms with KDE
- Pearson correlation heatmap for numeric features
- Manual removal of redundant variables (`race`, `native.country`, `fnlwgt`)

Handling Imbalanced Data
- Income distribution:
  - <=50K → 22,654 samples
  - 50K → 7,508 samples
  Used:
    - SMOTE oversampling for minority class
    - Stratified train–test split
    - Balanced-class Random Forest baseline

Feature Selection
- Pearson correlation for numeric redundancy
- Mutual Information (MI) feature scoring
- SelectKBest to retain the top 15 informative features

Machine Learning Modelling
Three models were trained and evaluated:
1. Random Forest Classifier (class_weight='balanced')
2. Multinomial Naive Bayes
3. Gaussian Naive Bayes
All models are embedded inside a unified SMOTE + preprocessing pipeline.
