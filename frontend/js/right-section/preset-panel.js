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
            alert('Error loading presets, please try again.');
        }
    }

    renderPresetOptions() {
        if (!this.select) return;

        this.select.innerHTML = '<option value="">Select a preset...</option>';
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
                throw new Error(data.detail || 'Failed to load preset');
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
                        console.log('WebSocket Reconnected:', clientId);
                    };

                    ws.onmessage = (event) => {
                        const message = JSON.parse(event.data);
                        // 触发自定义事件，让其他面板更新数据
                        window.dispatchEvent(new CustomEvent('websocket-message', {
                            detail: message
                        }));
                    };

                    ws.onerror = (error) => {
                        console.error('WebSocket Error:', error);
                        alert('WebSocket connection error, please try again later.');
                    };

                    // 更新全局WebSocket实例
                    window.ws = ws;
                }

                alert('Preset loaded successfully!');
            }
        } catch (error) {
            console.error('Error loading preset:', error);
            alert(error.message || 'Failed to load preset, please try again.');
        } finally {
            // 恢复按钮状态
            this.submitBtn.disabled = false;
        }
    }
}

const presetPanel = new PresetPanel();