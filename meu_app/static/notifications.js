// Sistema de Notificações Personalizado
class NotificationSystem {
    constructor() {
        this.container = document.getElementById('notification-container');
        this.notifications = [];
    }

    show(type, title, message, duration = 5000) {
        const notification = this.createNotification(type, title, message);
        this.container.appendChild(notification);
        this.notifications.push(notification);

        // Animar entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto-remover após duração
        if (duration > 0) {
            setTimeout(() => {
                this.hide(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(type, title, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        notification.innerHTML = `
            <div class="notification-icon">${icons[type] || 'ℹ'}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="notificationSystem.hide(this.parentElement)">×</button>
        `;

        return notification;
    }

    hide(notification) {
        notification.classList.add('hide');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.parentElement.removeChild(notification);
            }
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    // Métodos de conveniência
    success(title, message, duration) {
        return this.show('success', title, message, duration);
    }

    error(title, message, duration) {
        return this.show('error', title, message, duration);
    }

    warning(title, message, duration) {
        return this.show('warning', title, message, duration);
    }

    info(title, message, duration) {
        return this.show('info', title, message, duration);
    }
}

// Inicializar sistema de notificações quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar sistema de notificações
    window.notificationSystem = new NotificationSystem();

    // Substituir alert() padrão
    window.originalAlert = window.alert;
    window.alert = function(message) {
        notificationSystem.error('Atenção', message, 5000);
    };

    // Função global para notificações
    window.showNotification = function(type, title, message, duration) {
        return notificationSystem.show(type, title, message, duration);
    };

    // Processar mensagens flash do Flask
    const flashMessages = document.querySelectorAll('[data-flash-message]');
    flashMessages.forEach(element => {
        const type = element.dataset.flashType || 'info';
        const title = element.dataset.flashTitle || 'Mensagem';
        const message = element.dataset.flashMessage;
        const duration = parseInt(element.dataset.flashDuration) || 5000;
        
        notificationSystem.show(type, title, message, duration);
        element.remove();
    });
});
