const token = "052023136503f863f31f61be60059bb5563a3bcf"

$(document).ready(function () {
    const savedCity = $('#selectedCity').val();
    if (savedCity) {
        $('#cityInput').val(savedCity);
    }

    $('#cityInput').on('input', function () {
        const query = $(this).val();

        if (query.length < 2) {
            $('#suggestions').empty();
            return;
        }

        $.ajax({
            method: "POST",
            url: "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address",
            contentType: "application/json",
            headers: {
                "Authorization": "Token " + token
            },
            data: JSON.stringify({
                query: query,
                count: 5,
                locations: [{ "country": "Россия" }],
                from_bound: { value: "city" },
                to_bound: { value: "city" }
            }),
            success: function (data) {
                $('#suggestions').empty();

                data.suggestions.forEach(suggestion => {
                    const city = suggestion.data.city;
                    $('#suggestions').append(`<div class="suggest-item">${city}</div>`);
                });

                $('.suggest-item').on('click', function () {
                    const selectedCity = $(this).text();
                    $('#cityInput').val(selectedCity);
                    $('#selectedCity').val(selectedCity);
                    $('#city').text(selectedCity);
                    $('#suggestions').empty();
                });
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Инициализация календаря
    initDatepicker();
    
    // Инициализация города
    initCity();
    
    // Обработчик отправки формы
    document.getElementById("filterForm").addEventListener("submit", function(e) {
        // Убедимся, что скрытые поля обновлены
        updateHiddenFields();
    });
});

function formatDateForInput(date) {
    // Формат YYYY-MM-DD для input value
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDateForDisplay(date) {
    // Формат DD.MM.YYYY для отображения
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
}

function initDatepicker() {
    const dateStart = document.getElementById("dateStart").value;
    const dateEnd = document.getElementById("dateEnd").value;
    let defaultDate = [];
    
    if (dateStart && dateEnd) {
        defaultDate = [dateStart, dateEnd];
    }

    flatpickr("#calendarRange", {
        mode: "range",
        minDate: "today",
        dateFormat: "Y-m-d",
        locale: "ru",
        defaultDate: defaultDate,
        onChange: function(selectedDates) {
            if (selectedDates.length === 2) {
                document.getElementById("dateStart").value = formatDateForInput(selectedDates[0]);
                document.getElementById("dateEnd").value = formatDateForInput(selectedDates[1]);
                document.getElementById("calendarRange").value = 
                    `${formatDateForDisplay(selectedDates[0])} — ${formatDateForDisplay(selectedDates[1])}`;
            }
        }
    });

    if (dateStart && dateEnd) {
        document.getElementById("calendarRange").value = 
            `${formatDate(dateStart)} — ${formatDate(dateEnd)}`;
    }
}

function initCity() {
    const selectedCity = document.getElementById("selectedCity").value;
    if (selectedCity) {
        document.getElementById("city").textContent = selectedCity;
    }
    
    document.getElementById("city").addEventListener("click", showModalCity);
    document.getElementById("closeModalCity").addEventListener("click", closeModalCity);
}

function updateHiddenFields() {
    // Для города - убедимся, что значение сохранено
    const cityInput = document.getElementById("cityInput");
    if (cityInput && cityInput.value.trim()) {
        document.getElementById("selectedCity").value = cityInput.value.trim();
    }
    
    // Для дат - flatpickr уже обновляет скрытые поля
}

// Вспомогательная функция для форматирования даты
function formatDate(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}.${month}.${year}`;
}

function showModalCity() {
    const modal = document.getElementById('modal-city');
    const selectedCity = document.getElementById("selectedCity").value;
    
    // Устанавливаем сохранённое значение города
    if (selectedCity) {
        document.getElementById("cityInput").value = selectedCity;
        document.getElementById("city").textContent = selectedCity;
    }
    
    modal.style.display = "block";

    if (!window.suggestViewInitialized) {
        ymaps.ready(function () {
            window.suggestView = new ymaps.SuggestView('cityInput');
            window.suggestView.events.add('select', function (e) {
                console.log("Выбран город:", e.get('item').value);
            });
            window.suggestViewInitialized = true;
        });
    }
}


function closeModalCity() {
    const cityInput = document.getElementById("cityInput");
    const selectedCity = cityInput.value.trim();
    
    if (selectedCity) {
        document.getElementById("selectedCity").value = selectedCity;
        document.getElementById("city").textContent = selectedCity;
    }
    
    document.getElementById("modal-city").style.display = "none";
}

document.getElementById("city").addEventListener("click", () => showModalCity());

document.getElementById("closeModalCity").addEventListener("click", function () {
    const selectedCity = document.getElementById("cityInput").value.trim();
    document.getElementById("selectedCity").value = selectedCity;
    closeModalCity();
});

function openModal(roomId) {
    document.getElementById('deleteModal-' + roomId).style.display = 'block';
}

function closeModal(roomId) {
    document.getElementById('deleteModal-' + roomId).style.display = 'none';
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    // Получаем все модальные окна на странице
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
}
