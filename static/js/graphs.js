    // Проверка существования элемента
    function getElementOrThrow(id) {
        const element = document.getElementById(id);
        if (!element) {
            throw new Error(`Элемент с ID ${id} не найден`);
        }
        return element;
    }

    // Валидация ввода
    function validateInput(inputId, errorId) {
        try {
            const input = getElementOrThrow(inputId);
            const errorElement = getElementOrThrow(errorId);
            const button = getElementOrThrow('update-btn');

            const value = input.value.trim();
            const numValue = parseInt(value);
            const isValid = value !== '' && numValue > 0 && numValue.toString() === value;

            if (!isValid) {
                input.classList.add('invalid');
                errorElement.style.display = 'block';
                button.disabled = true;
                return false;
            } else {
                input.classList.remove('invalid');
                errorElement.style.display = 'none';
                button.disabled = false;
                return true;
            }
        } catch (error) {
            console.error('Ошибка валидации:', error);
            return false;
        }
    }

    // Создание основного графика с анимацией
function createPlot(data) {
try {
    // Исходное состояние (все линии на нуле)
    const initialTraces = [
        {
            x: data.wavenumbers,
            y: new Array(data.wavenumbers.length).fill(data.ranges.y[0]),
            name: 'Здоровые (среднее)',
            line: { color: 'green', width: 3 },
            mode: 'lines'
        },
        {
            x: data.wavenumbers,
            y: new Array(data.wavenumbers.length).fill(data.ranges.y[0]),
            name: 'Здоровые +СКО',
            line: { color: 'green', width: 1, dash: 'dot' },
            mode: 'lines',
            hoverinfo: 'none'
        },
        {
            x: data.wavenumbers,
            y: new Array(data.wavenumbers.length).fill(data.ranges.y[0]),
            line: { color: 'green', width: 1, dash: 'dot' },
            mode: 'lines',
            fill: 'tonexty',
            fillcolor: 'rgba(0, 128, 0, 0.15)',
            hoverinfo: 'none',
            showlegend: false
        },
        {
            x: data.wavenumbers,
            y: new Array(data.wavenumbers.length).fill(data.ranges.y[0]),
            name: 'Больные (среднее)',
            line: { color: 'red', width: 3 },
            mode: 'lines'
        },
        {
            x: data.wavenumbers,
            y: new Array(data.wavenumbers.length).fill(data.ranges.y[0]),
            name: 'Больные +СКО',
            line: { color: 'red', width: 1, dash: 'dot' },
            mode: 'lines',
            hoverinfo: 'none'
        },
        {
            x: data.wavenumbers,
            y: new Array(data.wavenumbers.length).fill(data.ranges.y[0]),
            line: { color: 'red', width: 1, dash: 'dot' },
            mode: 'lines',
            fill: 'tonexty',
            fillcolor: 'rgba(255, 0, 0, 0.15)',
            hoverinfo: 'none',
            showlegend: false
        }
    ];

    const layout = {
        title: 'Среднее значение волнового числа у пациентов',
        xaxis: {
            title: 'Волновое число (cm⁻¹)',
            range: data.ranges.x,
            showgrid: true,
            gridcolor: '#eee'
        },
        yaxis: {
            title: 'Интенсивность',
            range: data.ranges.y,
            showgrid: true,
            gridcolor: '#eee'
        },
        legend: {
            orientation: 'h',
            y: -0.2
        },
        margin: { t: 60, l: 60, r: 40, b: 60 },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        clickmode: 'event+select'
    };

    // Создаем график с начальным состоянием
    Plotly.newPlot('graph', initialTraces, layout);

    // Анимация графика
    animatePlot(data, initialTraces);

    // Добавляем обработчик клика
    document.getElementById('graph').on('plotly_click', function(data) {
        if (data.points && data.points.length > 0) {
            const point = data.points[0];
            selectedWavenumber = point.x;
            getElementOrThrow('selected-wavenumber').textContent = selectedWavenumber.toFixed(2);
            getElementOrThrow('selected-point-info').style.display = 'block';
            updateBoxplot(selectedWavenumber);
        }
    });
} catch (error) {
    console.error('Ошибка при создании графика:', error);
    alert('Ошибка при отображении графика');
}
}

// Функция анимации графика
function animatePlot(data, initialTraces) {
    const totalDuration = 2500; // 2.5 секунды общее время анимации
    const startTime = Date.now();
    let currentTraces = JSON.parse(JSON.stringify(initialTraces));

    // Функция плавного изменения
    function exponentialEasing(t) {
        return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    }

    function animateFrame() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(1, elapsed / totalDuration);
        const easedProgress = exponentialEasing(progress);

        // Разделяем анимацию на фазы
        if (progress <= 0.5) {
            // Фаза 1: Построение средних линий (0-1.25s)
            const phaseProgress = progress * 2;
            const easedPhaseProgress = exponentialEasing(phaseProgress);

            for (let i = 0; i < data.wavenumbers.length; i++) {
                // Здоровые
                currentTraces[0].y[i] = data.ranges.y[0] +
                    (data.healthy.means[i] - data.ranges.y[0]) * easedPhaseProgress;

                // Больные
                currentTraces[3].y[i] = data.ranges.y[0] +
                    (data.unhealthy.means[i] - data.ranges.y[0]) * easedPhaseProgress;
            }
        } else {
            // Фаза 2: Построение СКО (1.25-2.5s)
            const phaseProgress = (progress - 0.5) * 2;
            const easedPhaseProgress = exponentialEasing(phaseProgress);

            for (let i = 0; i < data.wavenumbers.length; i++) {
                // Здоровые +СКО
                currentTraces[1].y[i] = data.healthy.means[i] +
                    data.healthy.stds[i] * easedPhaseProgress;

                // Здоровые -СКО
                currentTraces[2].y[i] = data.healthy.means[i] -
                    data.healthy.stds[i] * easedPhaseProgress;

                // Больные +СКО (с небольшой задержкой)
                if (phaseProgress > 0.2) {
                    const patientProgress = (phaseProgress - 0.2) / 0.8;
                    const easedPatientProgress = exponentialEasing(patientProgress);

                    currentTraces[4].y[i] = data.unhealthy.means[i] +
                        data.unhealthy.stds[i] * easedPatientProgress;

                    currentTraces[5].y[i] = data.unhealthy.means[i] -
                        data.unhealthy.stds[i] * easedPatientProgress;
                }
            }
        }

        // Обновляем график
        Plotly.animate('graph', {
            data: currentTraces,
            traces: [0, 1, 2, 3, 4, 5],
            layout: {}
        }, {
            transition: { duration: 0 },
            frame: { duration: 0, redraw: true }
        });

        if (progress < 1) {
            requestAnimationFrame(animateFrame);
        }
    }

    animateFrame();
}

// Создание ящика с усами
function createBoxplot(data) {
    try {
        const traces = [
            {
                y: data.healthy,
                name: 'Здоровые',
                type: 'box',
                boxpoints: 'all',
                jitter: 0.3,
                pointpos: -1.8,
                marker: {
                    color: 'green',
                    size: 5,
                    opacity: 0.5
                },
                line: {
                    color: 'green',
                    width: 2
                }
            },
            {
                y: data.unhealthy,
                name: 'Больные',
                type: 'box',
                boxpoints: 'all',
                jitter: 0.3,
                pointpos: -1.8,
                marker: {
                    color: 'red',
                    size: 5,
                    opacity: 0.5
                },
                line: {
                    color: 'red',
                    width: 2
                }
            }
        ];

        const layout = {
            title: `Распределение значений при<br> ${data.wavenumber.toFixed(2)} cm⁻¹`,
            yaxis: {
                title: 'Интенсивность',
                showgrid: true,
                gridcolor: '#eee'
            },
            margin: { t: 60, l: 60, r: 40, b: 60 },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            showlegend: false
        };

        Plotly.react('boxplot', traces, layout);
    } catch (error) {
        console.error('Ошибка при создании ящика с усами:', error);
        alert('Ошибка при отображении ящика с усами');
    }
}

// Функция обновления графика
async function updateGraph() {
    try {
        const isStudentValid = validateInput('student-input', 'student-error');
        const isStepValid = validateInput('step-input', 'step-error');

        if (!isStudentValid || !isStepValid) {
            return;
        }

        const button = getElementOrThrow('update-btn');
        const loadingOverlay = getElementOrThrow('graph-loading');

        // Показываем индикаторы загрузки
        button.classList.add('loading');
        button.disabled = true;
        loadingOverlay.style.display = 'flex';

        const studentNum = parseInt(getElementOrThrow('student-input').value);
        const stepVal = parseInt(getElementOrThrow('step-input').value);

        const response = await fetch(`/get_new_data?student_number=${studentNum}&step=${stepVal}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            currentData = data;

            // Сначала создаем график с начальным состоянием
            createPlot(data);

            // Сбрасываем выбранную точку
            selectedWavenumber = null;
            getElementOrThrow('selected-point-info').style.display = 'none';
            Plotly.purge('boxplot');
        } else {
            throw new Error(data.message || 'Неизвестная ошибка сервера');
        }
    } catch (error) {
        console.error('Ошибка при обновлении графика:', error);
        alert(`Ошибка: ${error.message}`);
    } finally {
        // Скрываем индикаторы загрузки в любом случае
        const button = getElementOrThrow('update-btn');
        const loadingOverlay = getElementOrThrow('graph-loading');

        button.classList.remove('loading');
        button.disabled = false;
        loadingOverlay.style.display = 'none';
    }
}

// Функция обновления ящика с усами
async function updateBoxplot(wavenumber) {
    try {
        const loadingOverlay = getElementOrThrow('boxplot-loading');
        loadingOverlay.style.display = 'flex';

        const response = await fetch(`/get_new_boxplot_data?wavenumber=${wavenumber}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            createBoxplot(data);
        } else {
            throw new Error(data.message || 'Неизвестная ошибка сервера');
        }
    } catch (error) {
        console.error('Ошибка при обновлении ящика с усами:', error);
        alert(`Ошибка: ${error.message}`);
    } finally {
        const loadingOverlay = getElementOrThrow('boxplot-loading');
        loadingOverlay.style.display = 'none';
    }
}

