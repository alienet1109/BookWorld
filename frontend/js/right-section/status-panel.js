// status-panel.js
class StatusPanel {
    constructor() {
        this.defaultStatus = {
            event: "等待事件...",
            location: {
                name: "未知位置",
                description: "等待位置更新..."
            },
            group: []
        }
        this.currentStatus = this.defaultStatus;
        this.init();
    }

    init() {
        // 设置默认状态
        this.updateAllStatus(this.currentStatus);
        this.updateSettings([]);
        
        // 监听WebSocket消息
        window.addEventListener('websocket-message', (event) => {
            const message = event.detail;
            
            if (message.type === 'status_update') {
                this.updateAllStatus(message.data);
            }
            
            if (message.type === 'initial_data' && message.data.status) {
                this.updateAllStatus(message.data.status);
                this.updateSettings(message.data.settings);
            }
        });
    }

    updateEvent(eventText) {
        const eventContainer = document.querySelector('#current-event .module-content');
        if (eventContainer) {
            eventContainer.innerHTML = `
                <div class="event-text">
                    <span class="status-indicator ${eventText ? 'status-active' : 'status-inactive'}"></span>
                    ${eventText || 'No Event'}
                </div>
            `;
        }
    }

    updateLocation(locationData) {
        const locationContainer = document.querySelector('#current-location .module-content');
        if (locationContainer) {
            locationContainer.innerHTML = `
                <div class="location-name">${locationData.name}</div>
                <div class="location-description">${locationData.description}</div>
            `;
        }
    }

    updateGroup(members) {
        const groupContainer = document.querySelector('.group-members');
        if (groupContainer) {
            if (members && members.length > 0) {
                groupContainer.innerHTML = members.map(name => `
                    <div class="group-member">
                        <span class="member-name">${name}</span>
                    </div>
                `).join('');
            } else {
                groupContainer.innerHTML = '<div class="no-members">Empty Group</div>';
            }
        }
    }

    updateSettings(settings) {
        const settingsContainer = document.querySelector('.settings-content');
        if (settingsContainer) {
            if (settings && settings.length > 0) {
                settingsContainer.innerHTML = settings.map(setting => `
                    <div class="setting-item">
                        <div class="setting-term">${setting.term}</div>
                        <div class="setting-nature">${setting.nature}</div>
                        <div class="setting-detail">${setting.detail}</div>
                    </div>
                `).join('');
            } else {
                settingsContainer.innerHTML = '<div class="no-settings">暂无设定</div>';
            }
        }
    }

    updateAllStatus(statusData) {
        this.currentStatus = statusData;
        if (statusData.event !== undefined) this.updateEvent(statusData.event);
        if (statusData.location) this.updateLocation(statusData.location);
        if (statusData.group) this.updateGroup(statusData.group);
    }
}

const statusPanel = new StatusPanel();