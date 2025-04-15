setInterval(() => {
    updateAI();
}, 500);
let AI_data_loaded = false;

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Назначаем обработчики событий
        getElementOrThrow('student-input').addEventListener('input', () => {
            validateInput('student-input', 'student-error');
        });

        getElementOrThrow('step-input').addEventListener('input', () => {
            validateInput('step-input', 'step-error');
        });

        getElementOrThrow('update-btn').addEventListener('click', async () => {
            await updateGraph();
            AI_data_loaded = false;
        });

        // Первоначальная валидация
        validateInput('student-input', 'student-error');
        validateInput('step-input', 'step-error');

        // Инициализация графика
        updateGraph();
    } catch (error) {
        console.error('Ошибка инициализации:', error);
        alert('Произошла ошибка при загрузке страницы');
    }
});

async function updateAI() {
    if (AI_data_loaded) return;
    const name = 'gaussian';
    const response = await fetch(`/get_classifier_data?classifier_name=${name}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    if (data.status === 'success') {
        const loadingOverlay = getElementOrThrow('ai-loading');
        // Показываем индикаторы загрузки
        console.log(data.ai_loading)
        if (data.ai_loading) {
            loadingOverlay.style.display = 'flex';
            return;
        }
        loadingOverlay.style.display = 'none';
        AI_data_loaded = true;
    } else {
        throw new Error(data.message || 'Неизвестная ошибка сервера');
    }
}