"""
Machine Learning Training, Comparative Benchmarking & Model Serialization Pipeline
For Smart Irrigation Capstone System
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve,
    mean_absolute_error, root_mean_squared_error, r2_score
)

from eda_and_preprocess import load_data, preprocess_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
EDA_DIR = os.path.join(os.path.dirname(__file__), '..', 'eda_plots')

def train_and_evaluate():
    print("=" * 70)
    print("STEP 1: PREPARING TRAINING AND TESTING SPLITS")
    print("=" * 70)
    df = load_data()
    splits = preprocess_data(df)
    
    X_train = splits['X_train_proc']
    X_test = splits['X_test_proc']
    y_class_train = splits['y_class_train']
    y_class_test = splits['y_class_test']
    y_reg_train = splits['y_reg_train']
    y_reg_test = splits['y_reg_test']
    preprocessor = splits['preprocessor']
    
    # Retrieve feature names from ColumnTransformer
    cat_feature_names = list(preprocessor.named_transformers_['cat'].get_feature_names_out(splits['cat_cols']))
    all_feature_names = splits['num_cols'] + cat_feature_names
    
    print(f"\nTotal Features after Encoding & Engineering: {len(all_feature_names)}")
    print("Feature list:", all_feature_names)
    
    print("\n" + "=" * 70)
    print("STEP 2: TRAINING CLASSIFICATION MODELS (IRRIGATION REQUIREMENT)")
    print("=" * 70)
    
    classifiers = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=6, min_samples_leaf=5, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_leaf=3, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }
    
    classification_metrics = {}
    fitted_classifiers = {}
    
    for name, clf in classifiers.items():
        print(f"\n>>> Training {name}...")
        clf.fit(X_train, y_class_train)
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred
        
        acc = accuracy_score(y_class_test, y_pred)
        prec = precision_score(y_class_test, y_pred)
        rec = recall_score(y_class_test, y_pred)
        f1 = f1_score(y_class_test, y_pred)
        auc = roc_auc_score(y_class_test, y_proba)
        cm = confusion_matrix(y_class_test, y_pred).tolist()
        
        classification_metrics[name] = {
            'accuracy': round(float(acc), 4),
            'precision': round(float(prec), 4),
            'recall': round(float(rec), 4),
            'f1_score': round(float(f1), 4),
            'roc_auc': round(float(auc), 4),
            'confusion_matrix': cm
        }
        fitted_classifiers[name] = clf
        
        print(f"    Accuracy:  {acc*100:.2f}% | Precision: {prec*100:.2f}% | Recall: {rec*100:.2f}% | F1: {f1:.4f} | AUC: {auc:.4f}")
        
    print("\n" + "=" * 70)
    print("STEP 3: TRAINING REGRESSION MODELS (WATER REQUIREMENT VOLUME ml)")
    print("=" * 70)
    
    regressors = {
        'Linear Regression': LinearRegression(),
        'Decision Tree Regressor': DecisionTreeRegressor(max_depth=6, random_state=42),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    }
    
    regression_metrics = {}
    fitted_regressors = {}
    
    for name, reg in regressors.items():
        print(f"\n>>> Training {name}...")
        reg.fit(X_train, y_reg_train)
        y_pred_reg = reg.predict(X_test)
        
        mae = mean_absolute_error(y_reg_test, y_pred_reg)
        rmse = root_mean_squared_error(y_reg_test, y_pred_reg)
        r2 = r2_score(y_reg_test, y_pred_reg)
        
        regression_metrics[name] = {
            'mae': round(float(mae), 2),
            'rmse': round(float(rmse), 2),
            'r2_score': round(float(r2), 4)
        }
        fitted_regressors[name] = reg
        print(f"    MAE: {mae:.2f} ml | RMSE: {rmse:.2f} ml | R² Score: {r2:.4f}")
        
    print("\n" + "=" * 70)
    print("STEP 4: GENERATING COMPREHENSIVE PERFORMANCE PLOTS")
    print("=" * 70)
    
    # 1. Classification Metrics Comparison Bar Chart
    clf_df = pd.DataFrame(classification_metrics).T[['accuracy', 'precision', 'recall', 'f1_score']]
    plt.figure(figsize=(10, 6))
    ax = clf_df.plot(kind='bar', figsize=(11, 5.5), colormap='viridis', edgecolor='black', alpha=0.9)
    plt.title("Comparative Performance of Classification Models", fontsize=14, weight='bold', pad=15)
    plt.ylabel("Score (0.0 to 1.0)", fontsize=11)
    plt.xlabel("Model Architecture", fontsize=11)
    plt.ylim(0.7, 1.02)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'model_comparison_bar.png'))
    plt.close()
    
    # 2. Confusion Matrices for all Classifiers
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    axes = axes.flatten()
    for idx, (name, clf) in enumerate(fitted_classifiers.items()):
        cm = np.array(classification_metrics[name]['confusion_matrix'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                    cbar=False, annot_kws={"size": 14, "weight": "bold"})
        axes[idx].set_title(f"{name}\nAcc: {classification_metrics[name]['accuracy']*100:.1f}%", fontsize=12, weight='bold')
        axes[idx].set_xlabel("Predicted Label (0=OFF, 1=ON)")
        axes[idx].set_ylabel("True Label")
        axes[idx].set_xticklabels(['No Water', 'Irrigate'])
        axes[idx].set_yticklabels(['No Water', 'Irrigate'])
    plt.suptitle("Confusion Matrix Across Algorithms", fontsize=15, weight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'confusion_matrices.png'))
    plt.close()
    
    # 3. ROC Curves
    plt.figure(figsize=(8, 6))
    for name, clf in fitted_classifiers.items():
        if hasattr(clf, "predict_proba"):
            y_proba = clf.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_class_test, y_proba)
            plt.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {classification_metrics[name]['roc_auc']:.3f})")
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random Chance')
    plt.title("Receiver Operating Characteristic (ROC) Curves", fontsize=13, weight='bold')
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity / Recall)")
    plt.legend(loc='lower right')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'roc_curves.png'))
    plt.close()
    
    # 4. Feature Importance (Random Forest Classifier)
    rf_best = fitted_classifiers['Random Forest']
    importances = rf_best.feature_importances_
    feat_df = pd.DataFrame({
        'Feature': all_feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=True)
    
    plt.figure(figsize=(10, 6))
    plt.barh(feat_df['Feature'], feat_df['Importance'], color='#1098ad', edgecolor='black', alpha=0.85)
    plt.title("Random Forest Feature Importance for Irrigation Prediction", fontsize=13, weight='bold')
    plt.xlabel("Gini Feature Importance")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'feature_importances.png'))
    plt.close()
    
    # 5. Regression Actual vs Predicted Scatter
    rf_reg = fitted_regressors['Random Forest Regressor']
    y_reg_pred = rf_reg.predict(X_test)
    plt.figure(figsize=(8, 6))
    plt.scatter(y_reg_test, y_reg_pred, alpha=0.4, color='#7048e8', edgecolors='none')
    plt.plot([0, 1200], [0, 1200], 'r--', lw=2, label='Perfect Fit (y = x)')
    plt.title(f"Water Requirement: Actual vs Predicted\n(R² = {regression_metrics['Random Forest Regressor']['r2_score']:.3f}, MAE = {regression_metrics['Random Forest Regressor']['mae']} ml)", fontsize=13, weight='bold')
    plt.xlabel("Actual Water Requirement (ml)")
    plt.ylabel("Predicted Water Requirement (ml)")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_DIR, 'regression_predictions.png'))
    plt.close()
    
    print("\n" + "=" * 70)
    print("STEP 5: PERSISTING TRAINED MODELS & METRICS")
    print("=" * 70)
    
    # Save the models
    joblib.dump(fitted_classifiers['Random Forest'], os.path.join(MODELS_DIR, 'irrigation_classifier.pkl'))
    joblib.dump(fitted_classifiers['Decision Tree'], os.path.join(MODELS_DIR, 'decision_tree_classifier.pkl'))
    joblib.dump(fitted_classifiers['Logistic Regression'], os.path.join(MODELS_DIR, 'logistic_regression.pkl'))
    joblib.dump(fitted_regressors['Random Forest Regressor'], os.path.join(MODELS_DIR, 'water_regressor.pkl'))
    
    # Save feature names list
    with open(os.path.join(MODELS_DIR, 'feature_names.json'), 'w') as f:
        json.dump({
            'all_features': all_feature_names,
            'numeric_features': splits['num_cols'],
            'categorical_features': splits['cat_cols']
        }, f, indent=4)
        
    # Save evaluation metrics
    all_metrics = {
        'classification': classification_metrics,
        'regression': regression_metrics,
        'best_classification_model': 'Random Forest',
        'best_regression_model': 'Random Forest Regressor'
    }
    with open(os.path.join(MODELS_DIR, 'model_metrics.json'), 'w') as f:
        json.dump(all_metrics, f, indent=4)
        
    print(f"[SUCCESS] Trained models and evaluation JSON successfully saved in: {MODELS_DIR}")
    print(f"[SUCCESS] Evaluation graphs saved in: {EDA_DIR}")
    return all_metrics

if __name__ == '__main__':
    train_and_evaluate()
