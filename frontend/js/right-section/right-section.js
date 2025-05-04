// right-section.js
class RightSection {
    constructor() {
        this.currentTab = 'status-panel'; // 默认激活的标签
        
        // 确保不重复初始化
        setTimeout(() => {
            // 只引用实例，不初始化
            if (typeof window.getAPIPanel === 'function') {
                this.apiPanel = window.getAPIPanel();
                console.log('RightSection: 引用APIPanel实例');
            }
            this.settingsPanel = new SettingsPanel();
        }, 200);
        
        this.init();
    }

    init() {
        this.initTabSwitching();
        
        // WebSocket监听
        window.addEventListener('websocket-message', (event) => {
            const message = event.detail;
            if (message.type === 'initial_data' && message.data.settings) {
                this.settingsPanel.updateSettings(message.data.settings);
            }
        });
    }

    initTabSwitching() {
        const tabButtons = document.querySelectorAll('.right-toolbar .tab-btn');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const targetPanelId = button.getAttribute('data-target');
                
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                document.querySelectorAll('.tab-panel').forEach(panel => {
                    panel.classList.remove('active');
                });
                document.getElementById(targetPanelId).classList.add('active');
                
                this.currentTab = targetPanelId;
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const rightSection = new RightSection();
});
