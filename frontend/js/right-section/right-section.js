// right-section.js
class RightSection {
    constructor() {
        this.currentTab = 'status-panel'; // 默认激活的标签
        
        // 初始化SettingsPanel，但不处理APIPanel
        setTimeout(() => {
            this.settingsPanel = new SettingsPanel();
            console.log('RightSection: SettingsPanel初始化完成');
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
                
                // 让专门的tab事件处理器去处理API面板初始化
                // 不在这里做任何API面板相关的操作
            });
        });
    }
}

// 移除这个DOMContentLoaded事件监听器，避免重复初始化
// 改为导出类供index.html使用
window.RightSection = RightSection;

// 删除以下代码，避免重复初始化
// document.addEventListener('DOMContentLoaded', () => {
//     const rightSection = new RightSection();
// });