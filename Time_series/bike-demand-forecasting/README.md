This project is a practical exploration into 'machine learning', 'time series analysis', and 'predictive modelling'.  
The goal was to understand an existing dataset, perform exploratory time-based analysis, and build a baseline predictive model for forecasting bike rental demand using classical ML techniques.

Using the 'Seoul Bike Sharing Demand' dataset from the UCI Machine Learning Repository, this project explores:

- Time-of-day analysis of bike rental patterns  
- Feature relationships (temperature, humidity, visibility, seasons, etc.)  
- A supervised learning model for predicting rental demand  
- Time series–aware evaluation using `TimeSeriesSplit`  
- Visualisation of actual vs. predicted rental trends  

---

Technologies & Libraries
- 'Python'  
- 'Pandas', 'NumPy'  
- 'Matplotlib'  
- 'scikit-learn' (RandomForestRegressor, ColumnTransformer, Pipeline, TimeSeriesSplit)  
- 'ucimlrepo' for dataset retrieval  

---

Dataset
Dataset: Seoul Bike Sharing Demand  
Source: UCI Machine Learning Repository  
Rows: 8,760  
Fields: Date, Hour, Temperature, Humidity, Wind Speed, Visibility, Solar Radiation, Seasons, Holidays, etc.

This dataset contains hourly rental demand records for the period from 2017 to 2018.

---

Results Summary
- Average MAE: ~206 bikes per hour  
- Model captures general patterns but struggles with extreme values  
- Daily smoothed trends show a closer match between actual and predicted values  
- Provides a baseline for more advanced forecasting approaches  

---

Learnings & Takeaways
- Understanding the importance of proper time-based evaluation  
- How categorical and numerical features influence demand  
- Random Forests are useful but not inherently time-aware  
- Smoothing techniques reveal macro trends more clearly  
- Next models should incorporate temporal structure more explicitly  
