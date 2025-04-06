from flask import Flask
from utils import get_plot_data, get_ai_data, get_boxplot_data
import os
import numpy as np

STEP = 15
STUDENT_NUMBER = 1

app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = 'qzwxecrv12345'
app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'patients.xlsx')
app.config['MODEL_PATH'] = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')

data = []
print(app.config['DATA_PATH'])
if os.path.exists(app.config['DATA_PATH']):
    data = get_plot_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)

dataset = data[['wavenumber']].copy()
dataset['mean_values'] = data.drop(columns=['wavenumber', 'health']).mean(axis=1)
dataset['std'] = data.drop(columns=['wavenumber', 'health']).std(axis=1)
print(dataset)


def load_boxplot_data(wavenumber):
    """Подготовка данных для boxplot'ов по конкретной длине волны"""
    boxplot_data = get_boxplot_data(app.config['DATA_PATH'], wavenumber)

    healthy = boxplot_data[boxplot_data['health'] == 1].drop(columns=['health', 'wavenumber']).values.flatten().tolist()
    unhealthy = boxplot_data[boxplot_data['health'] == 0].drop(
        columns=['health', 'wavenumber']).values.flatten().tolist()

    return {
        'healthy': healthy,
        'unhealthy': unhealthy,
        'wavenumber': wavenumber
    }


print(load_boxplot_data(511.8803852224))
