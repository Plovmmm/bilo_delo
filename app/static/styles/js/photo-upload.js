// Управление загрузкой фотографий
class PhotoUploader {
    constructor() {
        this.maxFileSize = 5 * 1024 * 1024; // 5MB
        this.allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        this.init();
    }

    init() {
        this.setupPhotoUpload('mainPhoto', 'mainPhotoPreview');
        this.setupPhotoUpload('photo1', 'photo1Preview');
        this.setupPhotoUpload('photo2', 'photo2Preview');
        this.setupPhotoUpload('photo3', 'photo3Preview');
    }

    setupPhotoUpload(inputId, previewId) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        const uploadArea = input.parentElement;

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.validateAndPreviewFile(file, preview, uploadArea);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) {
                input.files = e.dataTransfer.files;
                this.validateAndPreviewFile(file, preview, uploadArea);
            }
        });

        // Клик по превью для удаления
        preview.addEventListener('click', () => {
            this.removePhoto(input, preview, uploadArea);
        });
    }

    validateAndPreviewFile(file, preview, uploadArea) {
        // Проверка типа файла
        if (!this.allowedTypes.includes(file.type)) {
            this.showError('Разрешены только JPG, PNG и WebP изображения');
            return;
        }

        // Проверка размера
        if (file.size > this.maxFileSize) {
            this.showError('Размер файла не должен превышать 5MB');
            return;
        }

        this.previewFile(file, preview, uploadArea);
    }

    previewFile(file, preview, uploadArea) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.classList.remove('hidden');
            
            // Скрываем иконку и текст
            uploadArea.querySelector('.photo-icon').classList.add('hidden');
            uploadArea.querySelector('.photo-text').classList.add('hidden');
        };

        reader.readAsDataURL(file);
    }

    removePhoto(input, preview, uploadArea) {
        input.value = '';
        preview.src = '';
        preview.classList.add('hidden');
        
        // Показываем иконку и текст
        uploadArea.querySelector('.photo-icon').classList.remove('hidden');
        uploadArea.querySelector('.photo-text').classList.remove('hidden');
    }

    getPhotosData() {
        const photos = {};
        const inputs = ['mainPhoto', 'photo1', 'photo2', 'photo3'];

        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input.files[0]) {
                photos[inputId] = input.files[0];
            }
        });

        return photos;
    }

    validateRequiredPhotos() {
        const mainPhoto = document.getElementById('mainPhoto').files[0];
        if (!mainPhoto) {
            this.showError('Главное фото обязательно для добавления');
            return false;
        }
        return true;
    }

    showError(message) {
        alert(message); // Можно заменить на красивые уведомления
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.photoUploader = new PhotoUploader();
});

// Обработчик формы
document.getElementById('placeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    savePlace();
});

function savePlace() {
    // Проверка обязательных полей
    const title = document.getElementById('placeTitle').value.trim();
    if (!title) {
        alert('Введите название места');
        return;
    }

    if (!selectedCoords) {
        alert('Выберите место на карте');
        return;
    }

    // Проверка фото
    if (!window.photoUploader.validateRequiredPhotos()) {
        return;
    }

    // Сбор данных формы
    const formData = new FormData();
    formData.append('user_id', window.APP_CONFIG.USER_ID);
    formData.append('title', title);
    formData.append('date_visited', document.getElementById('placeDate').value);
    formData.append('address', document.getElementById('placeAddress').value);
    formData.append('description', document.getElementById('placeDescription').value);
    formData.append('lat', selectedCoords[0]);
    formData.append('lon', selectedCoords[1]);

    // Добавляем фото
    const photos = window.photoUploader.getPhotosData();
    Object.keys(photos).forEach(key => {
        formData.append('photos', photos[key]);
    });

    // Отправка на сервер
    fetch('/api/places', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Место успешно добавлено!');
            window.MapManager.closeAddPanel();
            location.reload();
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка сети');
    });
}

function clearPhotoPreviews() {
    const previews = ['mainPhotoPreview', 'photo1Preview', 'photo2Preview', 'photo3Preview'];
    const inputs = ['mainPhoto', 'photo1', 'photo2', 'photo3'];

    previews.forEach(previewId => {
        const preview = document.getElementById(previewId);
        preview.src = '';
        preview.classList.add('hidden');
    });

    inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        input.value = '';
        
        const uploadArea = input.parentElement;
        uploadArea.querySelector('.photo-icon').classList.remove('hidden');
        uploadArea.querySelector('.photo-text').classList.remove('hidden');
    });
}