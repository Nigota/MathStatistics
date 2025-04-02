from flask import Flask, render_template, jsonify, request
from utils import get_ai_data, get_plot_data
import os
import logging

# Конфигурация
STEP = 15
STUDENT_NUMBER = 9

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация приложения
app.config.update(
    SECRET_KEY='qzwxecrv12345',
    DATA_PATH=os.path.join(os.path.dirname(__file__), 'data', 'patients.xlsx'),
    MODEL_PATH=os.path.join(os.path.dirname(__file__), 'models', 'model.pkl'),
    DEBUG=True
)


def load_data() -> tuple:
    """Загрузка и подготовка данных"""
    plot_data = []
    ai_data = []

    try:
        if os.path.exists(app.config['DATA_PATH']):
            logger.info("Loading plot data...")
            plot_data = get_plot_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)

            logger.info("Loading AI data...")
            ai_data = get_ai_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)
        else:
            logger.warning(f"Data file not found at {app.config['DATA_PATH']}")

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)

    return plot_data, ai_data


# Загрузка данных при старте приложения
plot_data, ai_data = load_data()


@app.route('/')
def index() -> str:
    """Главная страница с графиками"""
    try:
        dataset = plot_data.to_dict('records') if hasattr(plot_data, 'to_dict') else []
        return render_template('index.html', dataset=dataset)
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}", exc_info=True)
        return render_template('error.html', error="Ошибка загрузки данных")


@app.route('/api/data')
def get_data_api():
    """API для получения данных с параметрами"""
    try:
        student_number = request.args.get('student_number', default=STUDENT_NUMBER, type=int)
        step = request.args.get('step', default=STEP, type=int)

        # Перезагружаем данные с новыми параметрами
        plot_data = get_plot_data(app.config['DATA_PATH'], student_number, step)

        return jsonify({
            "status": "success",
            "data": plot_data.to_dict('records'),
            "student_number": student_number,
            "step": step
        })
    except Exception as e:
        logger.error(f"API data error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run()
