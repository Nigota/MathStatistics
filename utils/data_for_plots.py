import pandas as pd

SHEET1 = 'health'
SHEET2 = 'heart disease'


def get_plot_data(file_path, student_number, step):
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
