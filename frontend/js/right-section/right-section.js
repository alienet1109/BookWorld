// right-section.js
class RightSection {
    // 修改构造函数中的部分代码
    constructor() {
        this.currentTab = 'status-panel'; // 默认激活的标签
        
        // 确保APIPanel只被初始化一次
        setTimeout(() => {
            if (typeof window.initializeAPIPanel === 'function') {
                console.log('从right-section.js引用APIPanel实例');
                this.apiPanel = window.apiPanelInstance || window.initializeAPIPanel();
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
