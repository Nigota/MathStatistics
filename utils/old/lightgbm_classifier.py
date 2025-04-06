import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, roc_auc_score

FILE = 'roman_spectre.xlsx'
SHEET1 = 'health'
SHEET2 = 'heart disease'
STUDENT_NUMBER = 9
BINS = 5
STEP = 15
N_SPLITS = 5  # Количество фолдов в KFold

def main():
    healthy_df = pd.read_excel(FILE, SHEET1)
    unhealthy_df = pd.read_excel(FILE, SHEET2)

    # Выбираем нужные данные
    length = min(len(healthy_df['wavenumber']), len(unhealthy_df['wavenumber']))
    list_number = STUDENT_NUMBER
    step = length // STEP
    start = step * (list_number - 1)
    end = step * list_number
    healthy_df = healthy_df[start:end].reset_index(drop=True)
    unhealthy_df = unhealthy_df[start:end].reset_index(drop=True)

    healthy_df['health'] = 1
    unhealthy_df['health'] = 0

    # Разворачиваем данные через NumPy
    wavenumbers1 = np.repeat(healthy_df['wavenumber'].values, healthy_df.shape[1] - 2)
    wavenumbers2 = np.repeat(unhealthy_df['wavenumber'].values, unhealthy_df.shape[1] - 2)
    intensities1 = healthy_df.iloc[:, 1:-1].values.flatten()
    intensities2 = unhealthy_df.iloc[:, 1:-1].values.flatten()
    health_labels1 = np.repeat(healthy_df['health'].values, healthy_df.shape[1] - 2)
    health_labels2 = np.repeat(unhealthy_df['health'].values, unhealthy_df.shape[1] - 2)

    # Создаем DataFrame
    df = pd.DataFrame({
        'wavenumber': np.concatenate((wavenumbers1, wavenumbers2)),
        'intensity': np.concatenate((intensities1, intensities2)),
        'health': np.concatenate((health_labels1, health_labels2))
    })

    # === Обучаем LightGBM ===
    X = df.drop(columns=['health'])  # Признаки
    y = df['health']  # Целевая переменная

    # === K-Fold валидация ===
    skf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=42)

    acc_scores, precision_scores, recall_scores, f1_scores, roc_auc_scores = [], [], [], [], []

    plt.figure()
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = lgb.LGBMClassifier(boosting_type='gbdt', num_leaves=31, learning_rate=0.05, n_estimators=100,
                                   force_row_wise=True, verbosity=-1)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_probs = model.predict_proba(X_test)[:, 1]

        # Метрики
        acc_scores.append(accuracy_score(y_test, y_pred))
        precision_scores.append(precision_score(y_test, y_pred))
        recall_scores.append(recall_score(y_test, y_pred))
        f1_scores.append(f1_score(y_test, y_pred))
        roc_auc_scores.append(roc_auc_score(y_test, y_probs))
        fpr, tpr, thresholds = roc_curve(y_test, y_probs)
        plt.plot(fpr, tpr, color='darkorange', lw=2)

    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')

    # === Средние значения метрик ===
    print(f"Средняя Accuracy: {np.mean(acc_scores):.2f}")
    print(f"Средняя Precision: {np.mean(precision_scores):.2f}")
    print(f"Средняя Recall: {np.mean(recall_scores):.2f}")
    print(f"Средняя F1-score: {np.mean(f1_scores):.2f}")
    print(f"Средняя ROC AUC: {np.mean(roc_auc_scores):.2f}")

    plt.show()


if __name__ == '__main__':
    main()
