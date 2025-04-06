
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (confusion_matrix, accuracy_score,
                             precision_score, recall_score,
                             f1_score, roc_curve, roc_auc_score)

def get_gaussian_model(data):

    X = data.drop(columns=['health'])
    y = data['health']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GaussianNB()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    conf_matrix = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    tn, fp, fn, tp = conf_matrix.ravel()
    specificity = tn / (tn + fp)

    y_probs = model.predict_proba(X_test)[:, 1]

    # Построение ROC-кривой
    fpr, tpr, thresholds = roc_curve(y_test, y_probs)
    roc_auc = roc_auc_score(y_test, y_probs)

    return {
        "model": model,
        "fpr": fpr,
        "tpr": tpr,
        "roc_thresholds": thresholds,
        "roc_auc": roc_auc,
        "accuracy": accuracy,
        "precision": precision,
        "sensitivity": recall,
        "specificity": specificity,
        "f1": f1,
        "conf_matrix": conf_matrix,
    }


