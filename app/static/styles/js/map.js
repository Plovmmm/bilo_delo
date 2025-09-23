let map;
let tempMarker = null;
let selectedCoords = null;

function initMap() {
    map = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 10,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']
    });

    // Обработчик клика по карте
    map.events.add('click', function (e) {
        const coords = e.get('coords');
        showTempMarker(coords);
    });

    loadPlaces();
}

function showTempMarker(coords) {
    selectedCoords = coords;
    
    // Убираем предыдущую временную метку
    if (tempMarker) {
        tempMarker.remove();
    }

    // Создаем временную метку
    tempMarker = new ymaps.Placemark(coords, {}, {
        preset: 'islands#redIcon',
        draggable: true
    });

    map.geoObjects.add(tempMarker);

    // Показываем кнопку "Добавить место"
    showAddButton(coords);

    // Получаем адрес для выбранных координат
    getAddressByCoords(coords).then(address => {
        document.getElementById('placeAddress').value = address;
    });

    // Обработчик перемещения метки
    tempMarker.events.add('dragend', function () {
        const newCoords = tempMarker.geometry.getCoordinates();
        selectedCoords = newCoords;
        showAddButton(newCoords);
        getAddressByCoords(newCoords).then(address => {
            document.getElementById('placeAddress').value = address;
        });
    });
}

function showAddButton(coords) {
    const tempMarkerElement = document.getElementById('tempMarker');
    const markerBtn = tempMarkerElement.querySelector('.marker-btn');
    
    // Позиционируем кнопку относительно координат
    const pixelCoords = map.convertToPagePixels(coords);
    tempMarkerElement.style.left = (pixelCoords[0] + 20) + 'px';
    tempMarkerElement.style.top = (pixelCoords[1] - 40) + 'px';
    tempMarkerElement.classList.remove('hidden');
}

function hideAddButton() {
    document.getElementById('tempMarker').classList.add('hidden');
}

function openAddPanel() {
    document.getElementById('addPlacePanel').classList.remove('hidden');
    hideAddButton();
}

function closeAddPanel() {
    document.getElementById('addPlacePanel').classList.add('hidden');
    
    // Убираем временную метку
    if (tempMarker) {
        map.geoObjects.remove(tempMarker);
        tempMarker = null;
    }
    
    clearForm();
}

function clearForm() {
    document.getElementById('placeForm').reset();
    document.getElementById('placeDate').value = window.APP_CONFIG.TODAY;
    
    // Очищаем превью фото
    clearPhotoPreviews();
}

// Остальные функции остаются как были...
ymaps.ready(initMap);

window.MapManager = {
    initMap,
    showTempMarker,
    openAddPanel,
    closeAddPanel
};