import os

import pandas as pd
import numpy as np

SHEET1 = 'health'
SHEET2 = 'heart disease'


# === Обработка датафрейма ===
def filter_data(df, prefix, filter_func):
    columns = [f'{prefix}{i}' for i in range(1, 51)]
    for col in columns:
        df[col] = filter_func(df[col])

    return df


# === Расчет оси х ===
def calculate_x_range(wavenumbers) -> list:
    min_x = wavenumbers.min()
    max_x = wavenumbers.max()
    padding = (max_x - min_x) * 0.05
    return [min_x - padding, max_x + padding]


# === Расчет оси y ===
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


# === Получение данных из файла ===
def get_data_from_exel(file_path, student_number, count):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}")

    healthy_df = pd.read_excel(file_path, SHEET1)
    unhealthy_df = pd.read_excel(file_path, SHEET2)
    # Выбираем нужные данные
    length = min(len(healthy_df['wavenumber']), len(unhealthy_df['wavenumber']))
    list_number = student_number
    step = length // count
    step += 1 if step % 2 != 0 else 0  # Данные должны быть четными для фильтра
    start = step * (list_number - 1)
    end = step * list_number

    healthy_df = healthy_df[start:end].reset_index(drop=True)
    unhealthy_df = unhealthy_df[start:end].reset_index(drop=True)

    # Проверка наличия данных
    if len(healthy_df) == 0 or len(unhealthy_df) == 0:
        raise ValueError("Not enough data for both groups")

    # Проверка согласованности данных
    if not healthy_df['wavenumber'].equals(unhealthy_df['wavenumber']):
        raise ValueError("Wavenumbers differ between groups")

    return healthy_df, unhealthy_df


def get_plot_data(file_path, student_number, count, filter_func=None):
    """Загрузка и подготовка данных"""
    try:
        # Получаем данные
        healthy_df, unhealthy_df = get_data_from_exel(file_path, student_number, count)

        # Фильтрация
        if filter_func is not None:
            healthy_df = filter_data(healthy_df, 'healthy', filter_func)
            unhealthy_df = filter_data(unhealthy_df, 'heart_patient', filter_func)

        healthy_df['mean_values'] = healthy_df.drop(columns=['wavenumber']).mean(axis=1)
        healthy_df['std'] = healthy_df.drop(columns=['wavenumber', 'mean_values']).std(axis=1)

        unhealthy_df['mean_values'] = unhealthy_df.drop(columns=['wavenumber']).mean(axis=1)
        unhealthy_df['std'] = unhealthy_df.drop(columns=['wavenumber', 'mean_values']).std(axis=1)

        return {
            'wavenumbers': healthy_df['wavenumber'].tolist(),
            'healthy': {
                'means': healthy_df['mean_values'].tolist(),
                'stds': healthy_df['std'].tolist()
            },
            'unhealthy': {
                'means': unhealthy_df['mean_values'].tolist(),
                'stds': unhealthy_df['std'].tolist()
            },
            'ranges': {
                'x': calculate_x_range(healthy_df['wavenumber']),
                'y': calculate_y_range(healthy_df, unhealthy_df)
            },
            'student_number': student_number,  # Переименовано
            'step': count,  # Переименовано
            'status': 'success'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'student_number': student_number,  # Переименовано
            'step': count  # Переименовано
        }


def get_boxplot_data(file_path, wavenumber):
    healthy_df = pd.read_excel(file_path, SHEET1)
    unhealthy_df = pd.read_excel(file_path, SHEET2)

    healthy_df = healthy_df[healthy_df['wavenumber'] == wavenumber].reset_index(drop=True)
    unhealthy_df = unhealthy_df[unhealthy_df['wavenumber'] == wavenumber].reset_index(drop=True)
    healthy_df['health'] = 1
    unhealthy_df['health'] = 0

    rename_dict = {
        col: col.replace('healthy', 'patient')
        for col in healthy_df.columns
        if col.startswith('healthy')
    }
    healthy_df = healthy_df.rename(columns=rename_dict)

    rename_dict = {
        col: col.replace('heart_patient', 'patient')
        for col in unhealthy_df.columns
        if col.startswith('heart_patient')
    }
    unhealthy_df = unhealthy_df.rename(columns=rename_dict)

    df = pd.concat((healthy_df, unhealthy_df)).reset_index(drop=True)
    return df
