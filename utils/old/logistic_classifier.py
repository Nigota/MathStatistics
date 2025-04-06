import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_curve, roc_auc_score

FILE = 'roman_spectre.xlsx'
SHEET1 = 'health'
SHEET2 = 'heart disease'
STUDENT_NUMBER = 9
BINS = 5
STEP = 15


def main():
    healthy_df = pd.read_excel(FILE, SHEET1)
    unhealthy_df = pd.read_excel(FILE, SHEET2)

    # отбираем нужные данные
    length = min(len(healthy_df['wavenumber']), len(unhealthy_df['wavenumber']))
    list_number = STUDENT_NUMBER  # Номер студента в списке группы
    step = length // STEP
    start = step * (list_number - 1)
    end = step * list_number
    healthy_df = healthy_df[start:end].reset_index(drop=True)
    unhealthy_df = unhealthy_df[start:end].reset_index(drop=True)

    healthy_df['health'] = 1
    unhealthy_df['health'] = 0

    # Повторяем wavenumber столько раз, сколько столбцов healthy
    wavenumbers1 = np.repeat(healthy_df['wavenumber'].values, healthy_df.shape[1] - 2)
    wavenumbers2 = np.repeat(unhealthy_df['wavenumber'].values, unhealthy_df.shape[1] - 2)
    # Берем все значения интенсивностей и разворачиваем в 1D-массив
    intensities1 = healthy_df.iloc[:, 1:-1].values.flatten()
    intensities2 = unhealthy_df.iloc[:, 1:-1].values.flatten()
    # Дублируем значения health столько же раз
    health_labels1 = np.repeat(healthy_df['health'].values, healthy_df.shape[1] - 2)
    health_labels2 = np.repeat(unhealthy_df['health'].values, unhealthy_df.shape[1] - 2)

    # Создаем новый DataFrame
    df = pd.DataFrame({
        'wavenumber': np.concatenate((wavenumbers1, wavenumbers2)),
        'intensity': np.concatenate((intensities1, intensities2)),
        'health': np.concatenate((health_labels1, health_labels2))
    })

    # === 2. Обучаем логистическую регрессию ===
    # Определяем признаки и целевую переменную
    X = df.drop(columns=['health'])  # Признаки
    y = df['health']  # Целевая переменная
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    conf_matrix = confusion_matrix(y_test, y_pred)
    print("Матрица ошибок:\n", conf_matrix)

    # Расчет метрик
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Расчет специфичности
    tn, fp, fn, tp = conf_matrix.ravel()
    specificity = tn / (tn + fp)

    # Вывод метрик
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall (Sensitivity): {recall:.2f}")
    print(f"Specificity: {specificity:.2f}")
    print(f"F1-score: {f1:.2f}")

    y_probs = model.predict_proba(X_test)[:, 1]

    # Построение ROC-кривой
    fpr, tpr, thresholds = roc_curve(y_test, y_probs)
    roc_auc = roc_auc_score(y_test, y_probs)

    # Визуализация ROC-кривой
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.show()

    # Вывод ROC AUC
    print(f"ROC AUC: {roc_auc:.2f}")

if __name__ == '__main__':
    main()
