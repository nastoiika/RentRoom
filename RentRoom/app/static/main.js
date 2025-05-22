const token = "052023136503f863f31f61be60059bb5563a3bcf"

$(document).ready(function () {
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
          const city = suggestion.value;
          $('#suggestions').append(`<div class="suggest-item">${city}</div>`);
        });

        $('.suggest-item').on('click', function () {
          $('#cityInput').val($(this).text());
          $('#suggestions').empty();
        });
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
    flatpickr("#calendarRange", {
    mode: "range",
    minDate: "today",       
    dateFormat: "Y-m-d",   
    locale: "ru",
    onChange: function(selectedDates, dateStr) {
        if (selectedDates.length === 2) {
            document.getElementById("dateStart").value = selectedDates[0].toISOString().split('T')[0];
            document.getElementById("dateEnd").value = selectedDates[1].toISOString().split('T')[0];
        }
    }                
    });
});

function showModalCity() {
    const modal = document.getElementById('modal-city');
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
    document.getElementById("modal-city").style.display = "none";
}

document.getElementById("city").addEventListener("click", () => showModalCity());

document.getElementById("closeModalCity").addEventListener("click", function () {
    const selectedCity = document.getElementById("cityInput").value.trim();
    document.getElementById("selectedCity").value = selectedCity;
    closeModalCity();
});