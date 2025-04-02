from flask import Flask, render_template
from utils import get_ai_data, get_plot_data
import os

STEP = 15
STUDENT_NUMBER = 9

app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = 'qzwxecrv12345'
app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'patients.xlsx')
app.config['MODEL_PATH'] = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')

plot_data = []
if os.path.exists(app.config['DATA_PATH']):
    plot_data = get_plot_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)

ai_data = []
if os.path.exists(app.config['DATA_PATH']):
    ai_data = get_ai_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)

@app.route('/')
def index():
    """Главная страница"""
    dataset = plot_data.to_dict('records')
    return render_template('index.html', dataset=dataset)

@app.route('/predict', methods=['POST'])
def predict():
    """API для предсказаний (пример)"""
    # Здесь должен быть код для обработки входящих данных
    # и возврата предсказания от модели
    # prediction = classifier.predict(data)
    return {"prediction": "sample_prediction"}

if __name__ == '__main__':
    app.run()