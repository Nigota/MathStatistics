from flask import Flask, render_template, request, jsonify
from utils import get_plot_data, get_ai_data, get_boxplot_data
import os
from typing import Dict, Any

app = Flask(__name__)

# Конфигурация
app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'patients.xlsx')

# Глобальные переменные состояния
STUDENT_NUMBER = 1  # Переименовано из CURRENT_STUDENT
STEP = 15  # Переименовано из CURRENT_STEP


def load_and_prepare_data(student_number: int, step: int) -> Dict[str, Any]:
    """Загрузка и подготовка данных"""
    try:
        if not os.path.exists(app.config['DATA_PATH']):
            raise FileNotFoundError(f"Data file not found at {app.config['DATA_PATH']}")

        # Загрузка данных
        plot_data = get_plot_data(app.config['DATA_PATH'], student_number, step)
        ai_data = get_ai_data(app.config['DATA_PATH'], student_number, step)

        # Разделение данных
        healthy = plot_data[plot_data['health'] == 1].reset_index(drop=True)
        unhealthy = plot_data[plot_data['health'] == 0].reset_index(drop=True)

        if len(healthy) == 0 or len(unhealthy) == 0:
            raise ValueError("Not enough data for both groups")

        # Проверка согласованности данных
        if not healthy['wavenumber'].equals(unhealthy['wavenumber']):
            raise ValueError("Wavenumbers differ between groups")

        # Формирование результата
        return {
            'wavenumbers': healthy['wavenumber'].tolist(),
            'healthy': {
                'means': healthy['mean_values'].tolist(),
                'stds': healthy['std'].tolist()
            },
            'unhealthy': {
                'means': unhealthy['mean_values'].tolist(),
                'stds': unhealthy['std'].tolist()
            },
            'ranges': {
                'x': calculate_x_range(plot_data['wavenumber']),
                'y': calculate_y_range(healthy, unhealthy)
            },
            'student_number': student_number,  # Переименовано
            'step': step,  # Переименовано
            'status': 'success'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'student_number': student_number,  # Переименовано
            'step': step  # Переименовано
        }


def calculate_x_range(wavenumbers) -> list:
    min_x = wavenumbers.min()
    max_x = wavenumbers.max()
    padding = (max_x - min_x) * 0.05
    return [min_x - padding, max_x + padding]


def calculate_y_range(healthy, unhealthy) -> list:
    max_val = max(
        (healthy['mean_values'] + healthy['std']).max(),
        (unhealthy['mean_values'] + unhealthy['std']).max()
    )
    min_val = min(
        (healthy['mean_values'] - healthy['std']).min(),
        (unhealthy['mean_values'] - unhealthy['std']).min()
    )
    padding = (max_val - min_val) * 0.1
    return [min_val - padding, max_val + padding]


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
    initial_data = load_and_prepare_data(STUDENT_NUMBER, STEP)
    print(initial_data)
    return render_template('index.html', initial_data=initial_data)


@app.route('/get_new_data', methods=['GET'])
def get_new_data():
    """API для получения новых данных и обновления глобальных переменных"""
    global STUDENT_NUMBER, STEP

    try:
        # Получаем новые значения из запроса
        new_student = int(request.args.get('student_number', STUDENT_NUMBER))
        new_step = int(request.args.get('step', STEP))

        # Валидация входных данных
        if new_student < 1 or new_step < 1:
            raise ValueError("Values must be positive integers")

        # Загружаем данные с новыми параметрами
        stats = load_and_prepare_data(new_student, new_step)

        if stats['status'] == 'error':
            return jsonify(stats), 400

        # Обновляем глобальные переменные только после успешной загрузки
        STUDENT_NUMBER = new_student
        STEP = new_step

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
