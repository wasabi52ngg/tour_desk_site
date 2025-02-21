document.addEventListener('DOMContentLoaded', function () {
    ymaps.ready(initMap);
});

function initMap() {
    const apiKey = '{{ settings.YANDEX_MAPS_API_KEY }}';
    const address = '{{ location.address }}';
    const mapContainer = document.getElementById('location-map');

    if (!address) {
        console.error('Адрес не указан.');
        mapContainer.innerText = 'Не удалось загрузить карту. Проверьте адрес.';
        return;
    }

    ymaps.geocode(address, { apiKey: apiKey }).then(function (res) {
    const firstGeoObject = res.geoObjects.get(0);
    const coords = firstGeoObject.geometry.getCoordinates();
    console.log('Адрес:', address, 'Координаты:', coords);

    const myMap = new ymaps.Map(mapContainer, {
        center: coords,
        zoom: 12
    });

    const myPlacemark = new ymaps.Placemark(coords, {
        hintContent: '{{ location.name }}',
        balloonContent: '{{ location.name }}'
    });

    myMap.geoObjects.add(myPlacemark);
}).catch(function (error) {
    console.error('Ошибка при геокодировании:', error);
    mapContainer.innerText = 'Не удалось загрузить карту. Проверьте адрес.';
});
}