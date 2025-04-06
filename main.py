import os
import pickle

from multiprocessing import Process
from flask import Flask, render_template, request, jsonify

from utils import get_plot_data, get_ai_data, get_boxplot_data
from utils import get_gaussian_model

app = Flask(__name__)

# Конфигурация
app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'patients.xlsx')
app.config['CSS_PATH'] = os.path.join(os.path.dirname(__file__), 'templates', 'styles.css')

# Глобальные переменные состояния
STUDENT_NUMBER = 1  # Переименовано из CURRENT_STUDENT
STEP = 15  # Переименовано из CURRENT_STEP
AI_PROCESS = Process(target=None)
CURRENT_CLASSIFIER = None


@app.route('/get_classifier_data', methods=['GET'])
def get_classifier_data():
    """Получение данных с именного классификатора (проверка завершения обучения)"""
    global AI_PROCESS, CURRENT_CLASSIFIER
    try:
        ai_data = []
        if not AI_PROCESS.is_alive():
            classifier_name = request.args.get('classifier_name')
            if classifier_name == 'gaussian':
                pass
            elif classifier_name == 'lightgbm':
                pass
            # elif classifier_name == '...':
            #     pass
            else:
                raise Exception(f"Invalid classifier name {CURRENT_CLASSIFIER}")

            CURRENT_CLASSIFIER = classifier_name
        return jsonify({
            'status': 'success',
            'ai_loading': AI_PROCESS.is_alive(),
            'ai_data': ai_data,
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f"Invalid input: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Server error: {str(e)}"
        }), 500


def create_classifiers():
    """Обучение классификаторов и сохранение в директорию для дальнейшей работы"""
    global STEP, STUDENT_NUMBER
    print("Обучение началось")
    AI = get_ai_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)

    # Гауссовский классификатор
    with open("data/temp_classifiers/gaussian.pickle", "wb") as file:
        pickle.dump(get_gaussian_model(AI), file)

    # ...
    # with open( ..., "wb") as file:
    #     pickle.dump( ..., file)

    print("Обучение завершено")


def load_boxplot_data(wavenumber):
    """Подготовка данных для boxplot'ов по конкретной длине волны"""
    boxplot_data = get_boxplot_data(app.config['DATA_PATH'], wavenumber)

    healthy = boxplot_data[boxplot_data['health'] == 1].drop(
        columns=['health', 'wavenumber']).values.flatten().tolist()
    unhealthy = boxplot_data[boxplot_data['health'] == 0].drop(
        columns=['health', 'wavenumber']).values.flatten().tolist()
    return {
        'healthy': healthy,
        'unhealthy': unhealthy,
        'wavenumber': wavenumber
    }


@app.route('/')
def index():
    """Основная страница с формой ввода"""
    global STUDENT_NUMBER, STEP
    initial_data = get_plot_data(app.config['DATA_PATH'], STUDENT_NUMBER, STEP)
    print(initial_data)
    return render_template('index.html', initial_data=initial_data)


@app.route('/get_new_data', methods=['GET'])
def get_new_data():
    """API для получения новых данных и обновления глобальных переменных"""
    global STUDENT_NUMBER, STEP, AI_PROCESS

    try:
        # Получаем новые значения из запроса
        new_student = int(request.args.get('student_number', STUDENT_NUMBER))
        new_step = int(request.args.get('step', STEP))

        # Валидация входных данных
        if new_student < 1 or new_step < 1:
            raise ValueError("Values must be positive integers")

        # Загружаем данные с новыми параметрами
        stats = get_plot_data(app.config['DATA_PATH'], new_student, new_step)

        # Обновляем глобальные переменные только после успешной загрузки
        STUDENT_NUMBER = new_student
        STEP = new_step

        # Обучение нейронок
        AI_PROCESS = Process(target=create_classifiers)
        AI_PROCESS.start()

        if stats['status'] == 'error':
            return jsonify(stats), 400

        return jsonify(stats)

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f"Invalid input: {str(e)}",
            'student_number': STUDENT_NUMBER,
            'step': STEP
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Server error: {str(e)}",
            'student_number': STUDENT_NUMBER,
            'step': STEP
        }), 500


@app.route('/get_new_boxplot_data', methods=['GET'])
def get_new_boxplot_data():
    """API для получения данных boxplot'ов"""
    try:
        wavenumber = float(request.args.get('wavenumber'))
        print(wavenumber)
        if wavenumber <= 0:
            raise ValueError("Wavenumber must be positive")

        boxplot_data = load_boxplot_data(wavenumber)

        return jsonify({
            'status': 'success',
            **boxplot_data
        })

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f"Invalid input: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Server error: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run()
