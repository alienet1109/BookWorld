class ScenesPanel {
    constructor() {
        this.scenes = new Set();
        this.currentScene = null;
        this.container = document.querySelector('.scene-buttons');
        this.clearBtn = document.querySelector('.clear-selection-btn');
        this.init();
    }

    init() {
        // this.initEventListeners();
        
        // 监听消息中的场景更新
        window.addEventListener('scene-update', (event) => {
            const sceneNumber = event.detail.scene;
            if (sceneNumber !== undefined) {
                this.addScene(sceneNumber);
            }
        });

        // 监听WebSocket消息
        window.addEventListener('websocket-message', (event) => {
            const message = event.detail;
            
            // 如果是初始数据，获取已有场景
            if (message.type === 'initial_data' && message.data.history_messages) {
                message.data.history_messages.forEach(message => this.addScene(message.scene));
            }
            
            // 从状态更新中获取场景信息
            if (message.type === 'message' && message.data.scene !== undefined) {
                this.addScene(message.data.scene);
            }
        });
    }

    addScene(sceneNumber) {
        // 只添加已经结束的场景
        if (!this.scenes.has(sceneNumber) && sceneNumber !== undefined) {
            console.log(`Adding scene ${sceneNumber}`);
            this.scenes.add(sceneNumber);
            this.renderSceneButtons();
            console.log('Current scenes:', Array.from(this.scenes));
        }
    }

    initEventListeners() {
        // 清除选择按钮事件
        this.clearBtn.addEventListener('click', () => {
            this.clearSelection();
        });
    }


    renderSceneButtons() {
        this.container.innerHTML = '';
        
        // 将场景号排序
        const sortedScenes = Array.from(this.scenes).sort((a, b) => a - b);
        
        sortedScenes.forEach(scene => {
            const button = document.createElement('button');
            button.className = 'scene-btn';
            if (this.currentScene === scene) {
                button.classList.add('active');
            }
            button.textContent = `Scene ${scene}`;
            
            button.addEventListener('click', () => {
                this.selectScene(scene);
            });
            
            this.container.appendChild(button);
        });
    }

    selectScene(sceneNumber) {
        const buttons = this.container.querySelectorAll('.scene-btn');
        buttons.forEach(btn => btn.classList.remove('active'));
        
        if (this.currentScene === sceneNumber) {
            // 如果点击当前选中的场景，取消选择
            this.currentScene = null;
            console.log('Scene selection cleared');
        } else {
            // 选中新场景
            this.currentScene = sceneNumber;
            buttons.forEach(btn => {
                if (btn.textContent === `场景 ${sceneNumber}`) {
                    btn.classList.add('active');
                }
            });
            console.log('Scene selected:', sceneNumber);
        }
        
        // 触发场景选择事件
        window.dispatchEvent(new CustomEvent('scene-selected', {
            detail: { scene: this.currentScene }
        }));

        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            // 添加发送 WebSocket 消息
            window.ws.send(JSON.stringify({
                type: 'request_scene_characters',
                scene: this.currentScene
            }));
        }
    }

    clearSelection() {
        this.currentScene = null;
        const buttons = this.container.querySelectorAll('.scene-btn');
        buttons.forEach(btn => btn.classList.remove('active'));
        
        // 确保清除选择时也触发事件
        const sceneEvent = new CustomEvent('scene-selected', {
            detail: { scene: null }
        });
        window.dispatchEvent(sceneEvent);

        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            // 添加发送 WebSocket 消息
            window.ws.send(JSON.stringify({
                type: 'request_scene_characters',
                scene: null
            }));
        }
    }
}
const scenesPanel = new ScenesPanel();