class PresetPanel {
    constructor() {
        this.presets = [];
        this.currentPreset = null;
        this.container = document.querySelector('.preset-container');
        this.select = document.querySelector('.preset-select');
        this.submitBtn = document.querySelector('.preset-submit-btn');
        this.init();
    }

    init() {
        this.loadPresets();
        this.setupEventListeners();
    }

    async loadPresets() {
        try {
            const response = await fetch('/api/list-presets');
            if (!response.ok) {
                throw new Error('Failed to load presets');
            }
            const data = await response.json();
            this.presets = data.presets;
            this.renderPresetOptions();
        } catch (error) {
            console.error('Error loading presets:', error);
            alert('加载预设列表失败，请刷新页面重试');
        }
    }

    renderPresetOptions() {
        if (!this.select) return;

        this.select.innerHTML = '<option value="">选择预设...</option>';
        this.presets.forEach(preset => {
            const option = document.createElement('option');
            option.value = preset;
            option.textContent = preset.replace('.json', '');
            this.select.appendChild(option);
        });
    }

    setupEventListeners() {
        if (this.select) {
            this.select.addEventListener('change', () => {
                this.currentPreset = this.select.value;
                this.submitBtn.disabled = !this.currentPreset;
            });
        }

        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', () => this.handleSubmit());
        }
    }

    async handleSubmit() {
        if (!this.currentPreset) return;

        // 禁用按钮，防止重复点击
        this.submitBtn.disabled = true;
        this.submitBtn.textContent = '加载中...';

        try {
            const response = await fetch('/api/load-preset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    preset: this.currentPreset
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '加载预设失败');
            }

            if (data.success) {
                // 触发预设加载成功事件
                window.dispatchEvent(new CustomEvent('preset-loaded', {
                    detail: { preset: this.currentPreset }
                }));

                // 重新加载初始数据
                if (window.ws && window.ws.readyState === WebSocket.OPEN) {
                    // 先停止当前的故事生成
                    window.ws.send(JSON.stringify({
                        type: 'control',
                        action: 'stop'
                    }));

                    // 重新连接WebSocket以获取新的初始数据
                    const clientId = Date.now().toString();
                    const ws = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);
                    
                    ws.onopen = () => {
                        console.log('WebSocket重新连接成功');
                    };

                    ws.onmessage = (event) => {
                        const message = JSON.parse(event.data);
                        // 触发自定义事件，让其他面板更新数据
                        window.dispatchEvent(new CustomEvent('websocket-message', {
                            detail: message
                        }));
                    };

                    ws.onerror = (error) => {
                        console.error('WebSocket错误:', error);
                        alert('连接服务器失败，请刷新页面重试');
                    };

                    // 更新全局WebSocket实例
                    window.ws = ws;
                }

                alert('预设加载成功！');
            }
        } catch (error) {
            console.error('Error loading preset:', error);
            alert(error.message || '加载预设失败，请重试');
        } finally {
            // 恢复按钮状态
            this.submitBtn.disabled = false;
            this.submitBtn.textContent = '加载预设';
        }
    }
}

const presetPanel = new PresetPanel();