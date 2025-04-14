import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# === Фильтрация ===
def mex_hat_filter(y, sigma):
    x = np.linspace(-5, 5, 100)
    mex_hat = (1 - (x ** 2 / sigma ** 2)) * np.exp(-x ** 2 / (2 * sigma ** 2))
    # Делаем зеркальное отражение спектра, чтобы убрать выбросы на концах
    y_filtered = np.pad(y,
                        pad_width=len(y) // 2,
                        mode='reflect')
    # Делаем свертку и возвращаем исходную длину спектра
    y_filtered = np.convolve(y_filtered, mex_hat, mode='same')
    y_filtered = y_filtered[len(y) // 2: -len(y) // 2]
    return y_filtered


# === Стандартизация ===
def standard(df, columns):
    for col in columns:
        df[col] = (df[col] - df['mean']) / df['std']
    df['mean'] = df.drop(columns=["wavenumber", 'mean', 'std']).mean(axis=1)
    df['std'] = df.drop(columns=["wavenumber", 'mean', 'std']).mean(axis=1)
    print(df.head(3))
    return df


# === Обработка датафрейма ===
def process_data(df, prefix):
    columns = [f'{prefix}{i}' for i in range(1, 51)]
    for col in columns:
        df[col] = mex_hat_filter(df[col], 3)
    df['mean'] = df.drop(columns=["wavenumber"]).mean(axis=1)
    df['std'] = df.drop(columns=["wavenumber", 'mean']).std(axis=1)

    # df = standard(df, columns)
    return df


# === Загрузка данных ===
healthy_raw = pd.read_excel('data/patients.xlsx', sheet_name='health')
unhealthy_raw = pd.read_excel('data/patients.xlsx', sheet_name='heart disease')


# === Визуализация для каждого метода отдельно ===
def plot_normalization(title):
    healthy = process_data(healthy_raw, 'healthy')
    unhealthy = process_data(unhealthy_raw, 'heart_patient')

    plt.figure(figsize=(10, 5))
    plt.plot(healthy['wavenumber'], healthy['mean'], label='Здоровые', color='green')
    plt.plot(unhealthy['wavenumber'], unhealthy['mean'], label='Больные', color='red')
    plt.title(f'{title}')
    plt.xlabel('Волновое число (см⁻¹)')
    plt.ylabel('Интенсивность (норм.)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === Вызов графиков ===
plot_normalization("Нормализация на максимум")
