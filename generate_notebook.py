"""
Generates the complete Jupyter Notebook for the Capstone project.
"""

import json
import os

def create_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# 🌱 Capstone 5: AI-Based Smart Irrigation System Using Sensors\n",
                    "### Machine Learning for Precision Agriculture & Automated Water Conservation\n",
                    "\n",
                    "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)\n",
                    "\n",
                    "---\n",
                    "## 1. Project Overview & Problem Statement\n",
                    "Traditional agricultural irrigation relies on static timers or manual schedules, which causes either over-irrigation (water waste, soil nutrient leaching, root rot) or under-irrigation (crop dehydration and wilting).\n",
                    "\n",
                    "This capstone project implements an **end-to-end AI-powered smart irrigation solution** that:\n",
                    "1. Collects multi-sensor telemetry: Soil Moisture (%), Ambient Temperature (°C), Relative Humidity (%), Soil Temperature, Sunlight Illuminance (Lux), and Raindrop status.\n",
                    "2. Performs rigorous Data Preprocessing & Exploratory Data Analysis (EDA).\n",
                    "3. Trains and benchmarks multiple classification algorithms (**Logistic Regression**, **Decision Tree**, **Random Forest**, **Gradient Boosting**).\n",
                    "4. Trains regression models to predict exact water dosage (**Random Forest Regressor**).\n",
                    "5. Evaluates model performance via Accuracy, Precision, Recall, F1-Score, ROC-AUC, MAE, RMSE, and $R^2$.\n",
                    "6. Integrates the trained model with an automated pump actuation control pipeline."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Environment Setup & Dependency Installation"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Install dependencies if running in Google Colab\n",
                    "# !pip install numpy pandas matplotlib seaborn scikit-learn joblib\n",
                    "\n",
                    "import os\n",
                    "import json\n",
                    "import numpy as np\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "import joblib\n",
                    "\n",
                    "from sklearn.model_selection import train_test_split\n",
                    "from sklearn.preprocessing import StandardScaler, OneHotEncoder\n",
                    "from sklearn.compose import ColumnTransformer\n",
                    "from sklearn.linear_model import LogisticRegression, LinearRegression\n",
                    "from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor\n",
                    "from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier\n",
                    "from sklearn.metrics import (\n",
                    "    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,\n",
                    "    confusion_matrix, classification_report, roc_curve,\n",
                    "    mean_absolute_error, root_mean_squared_error, r2_score\n",
                    ")\n",
                    "\n",
                    "sns.set_theme(style=\"whitegrid\")\n",
                    "plt.rcParams['figure.dpi'] = 120\n",
                    "print(\"Libraries successfully imported!\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Dataset Loading & Inspection"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load the agronomic sensor dataset\n",
                    "df = pd.read_csv('dataset/smart_irrigation_data.csv')\n",
                    "print(f\"Dataset Shape: {df.shape[0]} samples x {df.shape[1]} columns\\n\")\n",
                    "display(df.head())\n",
                    "print(\"\\n--- Data Types & Non-Null Values ---\")\n",
                    "df.info()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Exploratory Data Analysis (EDA)\n",
                    "Let's explore the relationships between environmental conditions (soil moisture, temperature, humidity) and irrigation requirements."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Target Class Distribution\n",
                    "print(\"Target Class Distribution (0: No Irrigation, 1: Irrigation Required):\")\n",
                    "print(df['irrigation_required'].value_counts(normalize=True).round(3))\n",
                    "\n",
                    "# Correlation Heatmap\n",
                    "plt.figure(figsize=(9, 6))\n",
                    "num_cols = ['soil_moisture', 'temperature', 'humidity', 'soil_temperature', 'sunlight_lux', 'rain_sensor', 'irrigation_required']\n",
                    "sns.heatmap(df[num_cols].corr(), annot=True, fmt='.2f', cmap='Blues', linewidths=0.5)\n",
                    "plt.title('Sensor Correlation Matrix', fontsize=13, weight='bold')\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Soil Moisture vs Irrigation Requirement\n",
                    "plt.figure(figsize=(10, 5))\n",
                    "sns.histplot(data=df, x='soil_moisture', hue='irrigation_required', kde=True, bins=30, palette=['#2b8a3e', '#e03131'])\n",
                    "plt.title('Soil Moisture Distribution Stratified by Irrigation Need', fontsize=13, weight='bold')\n",
                    "plt.xlabel('Soil Moisture (%)')\n",
                    "plt.ylabel('Observation Frequency')\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Data Preprocessing & Feature Engineering\n",
                    "- Impute missing values with feature medians.\n",
                    "- Engineer domain features: `temp_moisture_ratio` and `vapor_deficit`.\n",
                    "- Scale numerical features and One-Hot Encode categorical features (`crop_type`, `soil_type`)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 1. Handle missing values\n",
                    "for col in ['temperature', 'humidity']:\n",
                    "    if df[col].isnull().sum() > 0:\n",
                    "        median_val = df[col].median()\n",
                    "        df[col] = df[col].fillna(median_val)\n",
                    "        print(f\"Imputed {col} with median: {median_val:.2f}\")\n",
                    "\n",
                    "# 2. Feature Engineering\n",
                    "df['temp_moisture_ratio'] = df['temperature'] / (df['soil_moisture'] + 1.0)\n",
                    "df['vapor_deficit'] = (100.0 - df['humidity']) * (df['temperature'] / 50.0)\n",
                    "\n",
                    "num_features = ['soil_moisture', 'temperature', 'humidity', 'soil_temperature', 'sunlight_lux', 'rain_sensor', 'temp_moisture_ratio', 'vapor_deficit']\n",
                    "cat_features = ['crop_type', 'soil_type']\n",
                    "\n",
                    "X = df[num_features + cat_features]\n",
                    "y_class = df['irrigation_required']\n",
                    "y_reg = df['water_requirement_ml']\n",
                    "\n",
                    "# 3. Train-Test Split (80% Train, 20% Test)\n",
                    "X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(\n",
                    "    X, y_class, y_reg, test_size=0.20, random_state=42, stratify=y_class\n",
                    ")\n",
                    "\n",
                    "# 4. Preprocessing Pipeline\n",
                    "preprocessor = ColumnTransformer(\n",
                    "    transformers=[\n",
                    "        ('num', StandardScaler(), num_features),\n",
                    "        ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features)\n",
                    "    ]\n",
                    ")\n",
                    "\n",
                    "X_train_proc = preprocessor.fit_transform(X_train)\n",
                    "X_test_proc = preprocessor.transform(X_test)\n",
                    "\n",
                    "print(f\"Training set samples: {X_train_proc.shape[0]} | Processed Features: {X_train_proc.shape[1]}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 6. Machine Learning Model Training (Classification)\n",
                    "We train and benchmark 4 algorithms:\n",
                    "1. Logistic Regression (Baseline linear model)\n",
                    "2. Decision Tree Classifier (Rule-based tree)\n",
                    "3. Random Forest Classifier (Ensemble bagging)\n",
                    "4. Gradient Boosting Classifier (Ensemble boosting)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "classifiers = {\n",
                    "    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),\n",
                    "    'Decision Tree': DecisionTreeClassifier(max_depth=6, min_samples_leaf=5, random_state=42),\n",
                    "    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_leaf=3, random_state=42),\n",
                    "    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)\n",
                    "}\n",
                    "\n",
                    "results = []\n",
                    "fitted_clfs = {}\n",
                    "\n",
                    "for name, clf in classifiers.items():\n",
                    "    clf.fit(X_train_proc, y_class_train)\n",
                    "    y_pred = clf.predict(X_test_proc)\n",
                    "    y_proba = clf.predict_proba(X_test_proc)[:, 1] if hasattr(clf, 'predict_proba') else y_pred\n",
                    "    \n",
                    "    results.append({\n",
                    "        'Model': name,\n",
                    "        'Accuracy': accuracy_score(y_class_test, y_pred),\n",
                    "        'Precision': precision_score(y_class_test, y_pred),\n",
                    "        'Recall': recall_score(y_class_test, y_pred),\n",
                    "        'F1-Score': f1_score(y_class_test, y_pred),\n",
                    "        'ROC-AUC': roc_auc_score(y_class_test, y_proba)\n",
                    "    })\n",
                    "    fitted_clfs[name] = clf\n",
                    "\n",
                    "results_df = pd.DataFrame(results).set_index('Model')\n",
                    "display(results_df.style.highlight_max(axis=0, color='#86efac'))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 7. Model Evaluation & Confusion Matrix"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Confusion matrix for best model (Random Forest)\n",
                    "rf_model = fitted_clfs['Random Forest']\n",
                    "y_rf_pred = rf_model.predict(X_test_proc)\n",
                    "cm = confusion_matrix(y_class_test, y_rf_pred)\n",
                    "\n",
                    "plt.figure(figsize=(6, 5))\n",
                    "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', annot_kws={'size': 14, 'weight': 'bold'},\n",
                    "            xticklabels=['No Water (0)', 'Irrigate (1)'], yticklabels=['No Water (0)', 'Irrigate (1)'])\n",
                    "plt.title('Random Forest Confusion Matrix', fontsize=13, weight='bold')\n",
                    "plt.xlabel('Predicted Class')\n",
                    "plt.ylabel('True Class')\n",
                    "plt.tight_layout()\n",
                    "plt.show()\n",
                    "\n",
                    "print(\"\\n--- Detailed Classification Report ---\")\n",
                    "print(classification_report(y_class_test, y_rf_pred, target_names=['No Water', 'Irrigate']))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 8. Regression Modeling: Water Dosage Prediction (ml)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "reg = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)\n",
                    "reg.fit(X_train_proc, y_reg_train)\n",
                    "y_reg_pred = reg.predict(X_test_proc)\n",
                    "\n",
                    "mae = mean_absolute_error(y_reg_test, y_reg_pred)\n",
                    "rmse = root_mean_squared_error(y_reg_test, y_reg_pred)\n",
                    "r2 = r2_score(y_reg_test, y_reg_pred)\n",
                    "\n",
                    "print(f\"Random Forest Regressor Performance:\")\n",
                    "print(f\"  Mean Absolute Error (MAE): {mae:.2f} ml\")\n",
                    "print(f\"  Root Mean Squared Error (RMSE): {rmse:.2f} ml\")\n",
                    "print(f\"  R² Score: {r2:.4f}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 9. Live Sensor Prediction Test"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Test hypothetical field reading:\n",
                    "test_reading = pd.DataFrame([{\n",
                    "    'soil_moisture': 22.0,\n",
                    "    'temperature': 35.5,\n",
                    "    'humidity': 32.0,\n",
                    "    'soil_temperature': 31.0,\n",
                    "    'sunlight_lux': 55000.0,\n",
                    "    'rain_sensor': 0,\n",
                    "    'temp_moisture_ratio': 35.5 / 23.0,\n",
                    "    'vapor_deficit': (100.0 - 32.0) * (35.5 / 50.0),\n",
                    "    'crop_type': 'Tomato',\n",
                    "    'soil_type': 'Sandy'\n",
                    "}])\n",
                    "\n",
                    "test_proc = preprocessor.transform(test_reading)\n",
                    "pred_action = rf_model.predict(test_proc)[0]\n",
                    "pred_water = reg.predict(test_proc)[0]\n",
                    "\n",
                    "print(\"=== AI DECISION ENGINE OUTPUT ===\")\n",
                    "print(f\"Irrigation Required: {'YES (PUMP ON)' if pred_action == 1 else 'NO (PUMP OFF)'}\")\n",
                    "print(f\"Recommended Water Dosage: {pred_water:.1f} ml\")\n",
                    "print(f\"Pump Runtime @ 35ml/s: {pred_water / 35.0:.1f} seconds\")"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    out_path = 'smart_irrigation_analysis_and_training.ipynb'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    print(f"Jupyter Notebook generated at: {out_path}")

if __name__ == '__main__':
    create_notebook()
