from flask import Flask, render_template
from utils import get_ai_data, get_plot_data
import os

STEP = 15
STUDENT_NUMBER = 9

app = Flask(__name__)

# Конфигурация
app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'patients.xlsx')

# Инициализация данных
plot_data = []
ai_data = []

if os.path.exists(app.config['DATA_PATH']):
    plot_data = get_plot_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)
    ai_data = get_ai_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)
else:
    raise Exception(f"Data file not found at {app.config['DATA_PATH']}")

@app.route('/')
def index():
    dataset = plot_data[['wavenumber', 'health']].copy()
    dataset['mean_values'] = plot_data.drop(columns=['wavenumber', 'health']).mean(axis=1)
    dataset['std'] = plot_data.drop(columns=['wavenumber', 'health']).std(axis=1)
    dataset = dataset.to_dict('records')
    return render_template('index.html', dataset=dataset)


if __name__ == '__main__':
    app.run()