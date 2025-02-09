$(document).ready(function() {
    // Обновляем доступные места при изменении тура
    $('#id_tour_id').change(function() {
        var tourId = $(this).val();
        if (tourId) {
            $.ajax({
                url: urls.getFreeSeatsUrl,  // Используем переданный URL
                data: {
                    'tour_id': tourId
                },
                dataType: 'json',
                success: function(data) {
                    $('#freeSeats').text('Свободных мест: ' + data.free_seats);
                }
            });
        } else {
            $('#freeSeats').text('Свободных мест: ');
        }
    });

    // Обновляем итоговую цену при изменении числа участников
    $('#id_participants').on('input', function() {
        var participants = $(this).val();
        var tourId = $('#id_tour_id').val();

        if (participants && tourId) {
            // Получаем цену тура и обновляем итоговую цену
            $.ajax({
                url: urls.getTourPriceUrl,  // Используем переданный URL
                data: {
                    'tour_id': tourId
                },
                dataType: 'json',
                success: function(data) {
                    var totalPrice = data.price * participants;
                    $('#totalPrice').text(totalPrice);
                }
            });
        } else {
            $('#totalPrice').text(0);
        }
    });
});