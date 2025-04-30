# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 20:23:58 2025

@author: Aarya
"""
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import pickle

# Load data
df = pd.read_csv(r'housefinder\ml models\Mumbai_updated_realistic.csv')
#dropping irrelevant columns
df=df.drop(columns=['MaintenanceStaff', 'RainWaterHarvesting', 'IndoorGames', 'Intercom', 'SportsFacility', 'ATM', '24X7Security', 'PowerBackup', 'StaffQuarter', 'Cafeteria', 'MultipurposeRoom', 'WashingMachine', 'Gasconnection', 'AC', 'Wifi', 'Childrensplayarea', 'BED', 'VaastuCompliant', 'Microwave', 'GolfCourse', 'TV', 'DiningTable', 'Sofa', 'Wardrobe', 'Refrigerator', 'Society'])
# Preprocessing
df.fillna(0, inplace=True)  # simple missing value handling
df = pd.get_dummies(df, columns=['Location'])  # one-hot encode location

# Separate features and target
X = df.drop('Price', axis=1)
y = df['Price']
# Model
model = RandomForestRegressor()
model.fit(X, y)


# Save model and columns together
model_data = {
    'model': model,
    'columns': X.columns.tolist()
}

with open(r'housefinder\ml models\random_forest_model.pkl', 'wb') as file:
    pickle.dump(model_data, file)

print("Model and columns saved successfully!")