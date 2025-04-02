from flask import Flask, render_template
from utils.data_for_plots import get_plot_data
import os

STEP = 15
STUDENT_NUMBER = 9

app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = 'qzwxecrv12345'
app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'patients.csv')
app.config['MODEL_PATH'] = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')

if os.path.exists(app.config['DATA_PATH']):
    data = get_plot_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)
    print(data)

@app.route('/')
def index():
    """Главная страница"""
    print(data)
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API для предсказаний (пример)"""
    # Здесь должен быть код для обработки входящих данных
    # и возврата предсказания от модели
    # prediction = classifier.predict(data)
    return {"prediction": "sample_prediction"}

if __name__ == '__main__':
    app.run(debug=True)