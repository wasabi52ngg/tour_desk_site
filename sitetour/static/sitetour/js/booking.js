document.addEventListener('DOMContentLoaded', function() {
    let currentTourId = null;
    let currentPrice = 0;
    let maxParticipants = 0;
    let selectedSession = null;
    const calendarContainer = document.getElementById('calendarContainer');
    const selectDateButton = document.getElementById('selectDateButton');
    const countElement = document.getElementById('participantCount'); // Добавляем элемент счетчика
    let flatpickrInstance = null;


    // Инициализация календаря
    function initCalendar(availableDates) {
        if (flatpickrInstance) flatpickrInstance.destroy();

        flatpickrInstance = flatpickr("#calendar", {
            inline: true,
            mode: "single",
            locale: "ru",
            minDate: "today",
            enable: availableDates,
            dateFormat: "Y-m-d",
            onChange: async (selectedDates) => {
                if (selectedDates.length > 0) {
                    await handleDateSelect(selectedDates[0]);
                    toggleCalendar(false);
                }
            }
        });
    }

    // Обработка выбора даты
     async function handleDateSelect(selectedDate) {
        try {
            const utcDate = selectedDate.toISOString().split('T')[0];
            const response = await fetch(
                `${urls.getAvailableSessionsUrl}?tour_id=${currentTourId}&date=${utcDate}`
            );

            if (!response.ok) throw new Error('Ошибка загрузки сессий');
            const data = await response.json();

            if (data.error || !data.sessions.length) {
                throw new Error(data.error || 'Нет доступных сеансов');
            }

            selectedSession = data.sessions[0];
            maxParticipants = selectedSession.free_seats;
            currentPrice = selectedSession.price;

            updateUI(selectedDate);
            updatePriceControls();
            validateForm();
        } catch (error) {
            showError(error.message);
            resetSessionData();
        }
    }

    // Обновление интерфейса
    function updateUI(date) {
         const utcDate = new Date(
            Date.UTC(
                date.getUTCFullYear(),
                date.getUTCMonth(),
                date.getUTCDate()
            )
        );
        document.getElementById('selectedDate').textContent = utcDate.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        document.getElementById('freeSeats').textContent = maxParticipants;
        document.getElementById('dateSelectionInfo').style.display = 'block';
    }

    // Обновление элементов управления
    function updatePriceControls() {
        let participants = parseInt(countElement.textContent);
        participants = Math.min(Math.max(participants, 1), maxParticipants);

        countElement.textContent = participants;
        document.getElementById('selectedParticipants').value = participants;
        document.getElementById('totalPrice').textContent =
            (participants * currentPrice).toLocaleString('ru-RU');

        if (selectedSession) {
            document.getElementById('selectedSessionId').value = selectedSession.id;
        }
    }


    // Валидация формы
    function validateForm() {
        const isValid = !!selectedSession && maxParticipants > 0;
        document.getElementById('submitButton').disabled = !isValid;
        return isValid; // Возвращаем результат валидации
    }

    // Сброс данных сессии
    function resetSessionData() {
        selectedSession = null;
        maxParticipants = 0;
        currentPrice = 0;

        document.getElementById('freeSeats').textContent = '0';
        document.getElementById('totalPrice').textContent = '0';
        // Убрано: document.getElementById('participantCount').textContent = '1';
        document.getElementById('dateSelectionInfo').style.display = 'none';
        validateForm();
    }

    // Обработчики событий
    document.getElementById('id_tour_id').addEventListener('change', async function() {
        currentTourId = this.value;
        document.getElementById('selectedTourId').value = currentTourId;
        resetSessionData();

        if (!currentTourId) {
            toggleCalendar(false);
            return;
        }

        try {
            const response = await fetch(`${urls.getAvailableSessionsUrl}?tour_id=${currentTourId}`);
            if (!response.ok) throw new Error('Ошибка загрузки данных');

            const data = await response.json();
            const availableDates = data.sessions.map(s => {
            const dateStr = s.start_datetime.split('T')[0];
            return dateStr;
        });

            initCalendar(availableDates);
            selectDateButton.disabled = false;
        } catch (error) {
            showError(error.message);
            this.value = '';
            currentTourId = null;
            selectDateButton.disabled = true;
        }
    });

    document.getElementById('increaseParticipants').addEventListener('click', () => {
        let current = parseInt(countElement.textContent);
        if (current < maxParticipants) {
            countElement.textContent = current + 1;
            updatePriceControls(); // Обновляем через единую функцию
        }
    });

    document.getElementById('decreaseParticipants').addEventListener('click', () => {
        let current = parseInt(countElement.textContent);
        if (current > 1) {
            countElement.textContent = current - 1;
            updatePriceControls(); // Обновляем через единую функцию
        }
    });

    selectDateButton.addEventListener('click', () => {
        if (!currentTourId) return showError('Сначала выберите тур');
        toggleCalendar(calendarContainer.style.display === 'none');
    });

    document.getElementById('bookingForm').addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            showError('Заполните все поля корректно');
        } else {
            // Убедитесь, что все данные актуальны перед отправкой
            document.getElementById('selectedParticipants').value = countElement.textContent;
            document.getElementById('selectedTourId').value = currentTourId;
        }
    });

    // Вспомогательные функции
    function toggleCalendar(show) {
        calendarContainer.style.display = show ? 'block' : 'none';
        selectDateButton.textContent = show ? 'Скрыть календарь' : 'Выбрать дату';
    }

    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        errorElement.textContent = message;

        const container = document.querySelector('.booking-container');
        container.insertBefore(errorElement, container.firstChild);

        setTimeout(() => errorElement.remove(), 5000);
    }
});