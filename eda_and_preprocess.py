"""
Exploratory Data Analysis (EDA) and Preprocessing Pipeline
For Smart Irrigation Capstone System
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

# Set aesthetic styling for plots
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 200

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'smart_irrigation_data.csv')
EDA_DIR = os.path.join(os.path.dirname(__file__), '..', 'eda_plots')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

os.makedirs(EDA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def load_data(filepath=DATA_PATH):
    print(f"[1/5] Loading sensor dataset from: {filepath}")
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def perform_eda(df):
    print("[2/5] Performing Exploratory Data Analysis (EDA) and generating plots...")
    
    # Summary info
    print("\n--- Dataset Summary Info ---")
    print(df.info())
    print("\n--- Statistical Overview ---")
    print(df.describe().round(2))
    print("\n--- Missing Values Count ---")
    print(df.isnull().sum())
    
    # 1. Correlation Heatmap (numeric columns only)
    plt.figure(figsize=(10, 7))
    num_cols = ['soil_moisture', 'temperature', 'humidity', 'soil_temperature', 
                'sunlight_lux', 'rain_sensor', 'irrigation_required', 'water_requirement_ml']
    corr = df[num_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap, mask=mask, 
                vmin=-1, vmax=1, square=True, linewidths=.5, cbar_kws={"shrink": .8})
    plt.title("Environmental & Sensor Correlation Matrix", fontsize=14, weight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'correlation_matrix.png'))
    plt.close()
    
    # 2. Soil Moisture Distribution by Irrigation Status
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.histplot(data=df, x='soil_moisture', hue='irrigation_required', kde=True, 
                 palette=['#2b8a3e', '#e03131'], ax=axes[0], bins=30, alpha=0.6)
    axes[0].set_title("Soil Moisture Distribution by Irrigation Requirement", fontsize=12, weight='bold')
    axes[0].set_xlabel("Soil Moisture (%)")
    
    sns.boxplot(data=df, x='irrigation_required', y='soil_moisture', hue='irrigation_required',
                palette=['#2b8a3e', '#e03131'], ax=axes[1], boxprops=dict(alpha=0.8), legend=False)
    axes[1].set_title("Moisture Range for Irrigation Need", fontsize=12, weight='bold')
    axes[1].set_xticks([0, 1])
    axes[1].set_xticklabels(['No Irrigation Needed (0)', 'Irrigation Required (1)'])
    axes[1].set_ylabel("Soil Moisture (%)")
    
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'soil_moisture_distribution.png'))
    plt.close()
    
    # 3. Temperature vs Humidity Scatter with Rain overlay
    plt.figure(figsize=(9, 6))
    scatter = sns.scatterplot(
        data=df, x='temperature', y='humidity', 
        hue='irrigation_required', style='rain_sensor',
        palette=['#20c997', '#fa5252'], alpha=0.75, s=60
    )
    plt.title("Temperature vs Relative Humidity (Stratified by Irrigation & Rain)", fontsize=13, weight='bold')
    plt.xlabel("Ambient Temperature (°C)")
    plt.ylabel("Relative Humidity (%)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'temp_vs_humidity.png'))
    plt.close()
    
    # 4. Crop and Soil Irrigation Rates
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    crop_stats = df.groupby('crop_type')['irrigation_required'].mean().reset_index()
    crop_stats = crop_stats.sort_values(by='irrigation_required', ascending=False)
    sns.barplot(data=crop_stats, x='crop_type', y='irrigation_required', hue='crop_type',
                palette='viridis', ax=axes[0], legend=False)
    axes[0].set_title("Irrigation Probability by Crop Type", fontsize=12, weight='bold')
    axes[0].set_ylabel("Fraction Requiring Irrigation")
    axes[0].set_xlabel("Crop Type")
    for p in axes[0].patches:
        axes[0].annotate(f"{p.get_height()*100:.1f}%", 
                         (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                         ha='center', va='center', color='white', weight='bold')
        
    soil_stats = df.groupby('soil_type')['irrigation_required'].mean().reset_index()
    soil_stats = soil_stats.sort_values(by='irrigation_required', ascending=False)
    sns.barplot(data=soil_stats, x='soil_type', y='irrigation_required', hue='soil_type',
                palette='magma', ax=axes[1], legend=False)
    axes[1].set_title("Irrigation Probability by Soil Type", fontsize=12, weight='bold')
    axes[1].set_ylabel("Fraction Requiring Irrigation")
    axes[1].set_xlabel("Soil Type")
    for p in axes[1].patches:
        axes[1].annotate(f"{p.get_height()*100:.1f}%", 
                         (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                         ha='center', va='center', color='white', weight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'crop_irrigation_rates.png'))
    plt.close()
    
    # 5. Diurnal Sensor Trends (24-hour cycle)
    df['hour'] = df['timestamp'].dt.hour
    hourly_means = df.groupby('hour')[['temperature', 'humidity', 'soil_temperature']].mean()
    
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_means.index, hourly_means['temperature'], marker='o', label='Ambient Temp (°C)', color='#e03131', linewidth=2.2)
    plt.plot(hourly_means.index, hourly_means['soil_temperature'], marker='s', label='Soil Temp (°C)', color='#f59f00', linewidth=2.2)
    plt.plot(hourly_means.index, hourly_means['humidity'], marker='^', label='Humidity (%)', color='#1971c2', linewidth=2.2)
    plt.title("Diurnal 24-Hour Cycle of Environmental Sensors", fontsize=13, weight='bold')
    plt.xlabel("Hour of the Day (0-23)")
    plt.ylabel("Sensor Readings (°C / %)")
    plt.xticks(range(0, 24, 2))
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'diurnal_sensor_trends.png'))
    plt.close()
    
    print(f"[EDA Complete] Visualizations saved in: {EDA_DIR}")

def preprocess_data(df):
    print("[3/5] Handling missing values and data preprocessing...")
    
    # Impute missing numeric values with column medians
    numeric_features = ['soil_moisture', 'temperature', 'humidity', 'soil_temperature', 'sunlight_lux', 'rain_sensor']
    categorical_features = ['crop_type', 'soil_type']
    
    for col in numeric_features:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            print(f"  -> Imputing {df[col].isnull().sum()} missing values in '{col}' with median: {median_val:.2f}")
            df[col] = df[col].fillna(median_val)
            
    # Engineer synthetic derived features:
    # 1. Heat-Moisture Stress Index
    df['temp_moisture_ratio'] = df['temperature'] / (df['soil_moisture'] + 1.0)
    # 2. Vapor Deficit approximation
    df['vapor_deficit'] = (100.0 - df['humidity']) * (df['temperature'] / 50.0)
    
    extended_numeric = numeric_features + ['temp_moisture_ratio', 'vapor_deficit']
    
    feature_columns = extended_numeric + categorical_features
    X = df[feature_columns]
    y_class = df['irrigation_required']
    y_reg = df['water_requirement_ml']
    
    # Build scikit-learn preprocessing ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), extended_numeric),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
        ]
    )
    
    print("[4/5] Fitting preprocessor and splitting train/test sets...")
    X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
        X, y_class, y_reg, test_size=0.20, random_state=42, stratify=y_class
    )
    
    preprocessor.fit(X_train)
    
    # Save the fitted preprocessor
    preprocessor_path = os.path.join(MODELS_DIR, 'preprocessor.pkl')
    joblib.dump(preprocessor, preprocessor_path)
    print(f"  -> Saved fitted preprocessor to: {preprocessor_path}")
    
    # Return structured splits
    return {
        'X_train_raw': X_train,
        'X_test_raw': X_test,
        'X_train_proc': preprocessor.transform(X_train),
        'X_test_proc': preprocessor.transform(X_test),
        'y_class_train': y_class_train,
        'y_class_test': y_class_test,
        'y_reg_train': y_reg_train,
        'y_reg_test': y_reg_test,
        'preprocessor': preprocessor,
        'feature_columns': feature_columns,
        'num_cols': extended_numeric,
        'cat_cols': categorical_features
    }

if __name__ == '__main__':
    df = load_data()
    perform_eda(df)
    splits = preprocess_data(df)
    print("[5/5] Preprocessing and EDA pipeline executed successfully!")
