from flask import Flask
from utils import get_plot_data, get_ai_data
import os

STEP = 15
STUDENT_NUMBER = 9

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
