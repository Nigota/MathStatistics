import numpy as np


# === Мексиканская шляпа ===
def mex_hat_filter(y, sigma=3):
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


def moving_average_filter(y, window_size=10):
    """
    Применяет фильтр скользящего среднего к сигналу

    Параметры:
    y (array): Входной сигнал
    window_size (int): Размер окна усреднения (должен быть нечетным)

    Возвращает:
    array: Отфильтрованный сигнал
    """
    # Проверяем, что размер окна нечетный
    if window_size % 2 == 0:
        window_size += 1

    # Создаем ядро фильтра (равномерное распределение)
    kernel = np.ones(window_size) / window_size

    # Делаем зеркальное отражение спектра, чтобы убрать выбросы на концах
    pad_width = window_size // 2
    y_filtered = np.pad(y, pad_width=pad_width, mode='reflect')

    # Применяем свертку
    y_filtered = np.convolve(y_filtered, kernel, mode='valid')

    return y_filtered
