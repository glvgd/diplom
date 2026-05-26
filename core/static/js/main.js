// Глобальные функции для всего сайта

// Получение CSRF токена для AJAX запросов
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

// Универсальная функция для AJAX запросов
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Ошибка при выполнении запроса', 'error');
        throw error;
    }
}

// Уведомления
function showNotification(message, type = 'info') {
    // Создаем контейнер для уведомлений если его нет
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        animation: slideIn 0.3s ease;
        cursor: pointer;
        ${type === 'success' ? 'background: #4caf50;' : 
          type === 'error' ? 'background: #f44336;' : 
          type === 'warning' ? 'background: #ff9800;' : 
          'background: #2196f3;'}
    `;
    notification.textContent = message;
    
    // Добавляем анимацию
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    container.appendChild(notification);
    
    // Автоматическое удаление через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
    
    // Удаление по клику
    notification.onclick = () => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    };
}

// Форматирование даты
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Валидация форм
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#f44336';
            isValid = false;
            showNotification(`Пожалуйста, заполните поле "${input.previousElementSibling?.textContent || 'поле'}"`, 'error');
        } else {
            input.style.borderColor = '#e0e0e0';
        }
    });
    
    return isValid;
}

// Загрузка с индикатором
function showLoading(buttonId, text = 'Загрузка...') {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = text;
    }
}

function hideLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button && button.dataset.originalText) {
        button.disabled = false;
        button.textContent = button.dataset.originalText;
    }
}

// Плавная прокрутка
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Обработка ошибок
function handleError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    
    let message = 'Произошла ошибка';
    if (error.message) {
        message += `: ${error.message}`;
    }
    
    showNotification(message, 'error');
}

// Инициализация всех компонентов при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем класс active для текущей страницы в навигации
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath === href) {
            link.classList.add('active');
        }
    });
    
    // Автоматическая валидация форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form.id)) {
                e.preventDefault();
            }
        });
    });
    
    // Автоматическое скрытие сообщений об ошибках через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Экспорт функций в глобальный объект
window.showNotification = showNotification;
window.formatDate = formatDate;
window.validateForm = validateForm;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.smoothScrollTo = smoothScrollTo;
window.apiRequest = apiRequest;
window.getCSRFToken = getCSRFToken;