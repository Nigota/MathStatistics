import pandas as pd
import numpy as np

SHEET1 = 'health'
SHEET2 = 'heart disease'


def get_ai_data(file_path, student_number, step):
    healthy_df = pd.read_excel(file_path, SHEET1)
    unhealthy_df = pd.read_excel(file_path, SHEET2)

    # Выбираем нужные данные
    length = min(len(healthy_df['wavenumber']), len(unhealthy_df['wavenumber']))
    list_number = student_number
    step = length // step
    start = step * (list_number - 1)
    end = step * list_number
    healthy_df = healthy_df[start:end].reset_index(drop=True)
    unhealthy_df = unhealthy_df[start:end].reset_index(drop=True)

    healthy_df['health'] = 1
    unhealthy_df['health'] = 0

    # Разворачиваем данные через NumPy
    wavenumbers1 = np.repeat(healthy_df['wavenumber'].values, healthy_df.shape[1] - 2)
    wavenumbers2 = np.repeat(unhealthy_df['wavenumber'].values, unhealthy_df.shape[1] - 2)
    intensities1 = healthy_df.iloc[:, 1:-1].values.flatten()
    intensities2 = unhealthy_df.iloc[:, 1:-1].values.flatten()
    health_labels1 = np.repeat(healthy_df['health'].values, healthy_df.shape[1] - 2)
    health_labels2 = np.repeat(unhealthy_df['health'].values, unhealthy_df.shape[1] - 2)

    # Создаем DataFrame
    df = pd.DataFrame({
        'wavenumber': np.concatenate((wavenumbers1, wavenumbers2)),
        'intensity': np.concatenate((intensities1, intensities2)),
        'health': np.concatenate((health_labels1, health_labels2))
    })

    return df
