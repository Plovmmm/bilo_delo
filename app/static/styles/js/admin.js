// Функции для администратора
let addPlaceListener = null;
let selectedCoords = null;
let editMode = false;
let editingPlaceId = null;

// Включение режима добавления
function enableAddMode() {
    if (editMode) {
        disableEditMode();
    }
    
    document.querySelector('.controls .btn-primary').classList.add('active');
    document.getElementById('addPlacePanel').classList.remove('hidden');
    
    addPlaceListener = window.MapManager.getMap().events.add('click', function (e) {
        selectedCoords = e.get('coords');
        updateAddressByCoords(selectedCoords);
    });
}

// Выключение режима добавления
function disableAddMode() {
    document.querySelector('.controls .btn-primary').classList.remove('active');
    document.getElementById('addPlacePanel').classList.add('hidden');
    
    if (addPlaceListener) {
        window.MapManager.getMap().events.remove(addPlaceListener);
        addPlaceListener = null;
    }
    
    clearForm();
}

// Переключение режима добавления
function toggleAddMode() {
    if (addPlaceListener) {
        disableAddMode();
    } else {
        enableAddMode();
    }
}

// Обновление адреса по координатам
function updateAddressByCoords(coords) {
    window.MapManager.getAddressByCoords(coords)
        .then(address => {
            document.getElementById('placeAddress').value = address;
        })
        .catch(error => {
            console.error('Ошибка получения адреса:', error);
            document.getElementById('placeAddress').value = 'Адрес не определен';
        });
}

// Сохранение места
function savePlace() {
    const title = document.getElementById('placeTitle').value.trim();
    
    if (!title) {
        showAlert('Введите название места', 'error');
        return;
    }
    
    if (!selectedCoords && !editMode) {
        showAlert('Выберите место на карте', 'error');
        return;
    }

    const placeData = {
        user_id: window.APP_CONFIG.USER_ID,
        title: title,
        description: document.getElementById('placeDescription').value.trim(),
        date_visited: document.getElementById('placeDate').value,
        address: document.getElementById('placeAddress').value.trim(),
        lat: selectedCoords ? selectedCoords[0] : null,
        lon: selectedCoords ? selectedCoords[1] : null
    };

    const url = editMode ? `/api/places/${editingPlaceId}` : '/api/places';
    const method = editMode ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(placeData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(editMode ? 'Место обновлено!' : 'Место добавлено!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка сохранения:', error);
        showAlert('Ошибка сети', 'error');
    });
}

// Редактирование места
function editPlace(placeId) {
    // Находим место по ID
    const place = userPlaces.find(p => p.id === placeId);
    if (!place) return;

    editingPlaceId = placeId;
    editMode = true;

    // Заполняем форму данными
    document.getElementById('placeTitle').value = place.title;
    document.getElementById('placeDescription').value = place.description || '';
    document.getElementById('placeDate').value = place.date_visited;
    document.getElementById('placeAddress').value = place.address || '';

    // Показываем панель редактирования
    document.getElementById('addPlacePanel').classList.remove('hidden');
    document.querySelector('.panel h3').textContent = 'Редактировать место';

    // Центрируем карту на месте
    window.MapManager.getMap().setCenter([place.lat, place.lon], 15);
}

// Отключение режима редактирования
function disableEditMode() {
    editMode = false;
    editingPlaceId = null;
    document.querySelector('.panel h3').textContent = 'Добавить новое место';
    disableAddMode();
}

// Отмена добавления/редактирования
function cancelAddPlace() {
    if (editMode) {
        disableEditMode();
    } else {
        disableAddMode();
    }
}

// Очистка формы
function clearForm() {
    document.getElementById('placeTitle').value = '';
    document.getElementById('placeDescription').value = '';
    document.getElementById('placeDate').value = window.APP_CONFIG.TODAY;
    document.getElementById('placeAddress').value = '';
    selectedCoords = null;
}

// Поделиться картой
function shareMap() {
    const shareUrl = `${window.location.origin}/guest/${window.APP_CONFIG.USER_ID}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Моя карта "Было дело"',
            text: 'Посмотрите мою карту посещенных мест',
            url: shareUrl
        });
    } else if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(() => {
            showAlert('Ссылка скопирована в буфер обмена!', 'success');
        });
    } else {
        // Fallback для старых браузеров
        prompt('Скопируйте ссылку:', shareUrl);
    }
}

// Всплывающие уведомления
function showAlert(message, type = 'info') {
    // Создаем элемент уведомления
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Стили для уведомлений
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        z-index: 1000;
        max-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    const bgColors = {
        success: '#28a745',
        error: '#dc3545',
        info: '#17a2b8',
        warning: '#ffc107'
    };
    
    alert.style.backgroundColor = bgColors[type] || bgColors.info;
    
    document.body.appendChild(alert);
    
    // Автоматическое скрытие
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

// Добавляем CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);