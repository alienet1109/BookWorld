class APIPanel {
    constructor() {
        // 初始化时绑定 DOM 元素
        this.providerSelect = document.getElementById('api-provider');
        this.modelSelect = document.getElementById('api-model');
        this.apiKeyInput = document.getElementById('api-key');
        this.submitButton = document.querySelector('.api-submit-btn');

        // 绑定方法到当前实例，确保函数引用一致
        this.handleSubmit = this.handleSubmit.bind(this);
        this.updateModelOptions = this.updateModelOptions.bind(this);

        // 设置初始事件监听器
        this.setupEventListeners();
        
        // 初始化模型选项
        this.updateModelOptions();
        
        console.log('APIPanel 实例已创建');
    }

    setupEventListeners() {
        if (this.submitButton) {
            // 先完全移除所有点击事件监听器
            const newButton = this.submitButton.cloneNode(true);
            if (this.submitButton.parentNode) {
                this.submitButton.parentNode.replaceChild(newButton, this.submitButton);
            }
            this.submitButton = newButton;
            
            // 添加新的事件监听器
            this.submitButton.addEventListener('click', this.handleSubmit);
            console.log('Submit 事件监听器已绑定 (完全重置)');
        }
    
        if (this.providerSelect) {
            this.providerSelect.removeEventListener('change', this.updateModelOptions);
            this.providerSelect.addEventListener('change', this.updateModelOptions);
        }
    }

    updateModelOptions() {
        const provider = this.providerSelect.value;
        const models = {
            openai: ['gpt-3.5-turbo', 'gpt-4'],
            anthropic: ['claude-3-opus', 'claude-3-sonnet'],
            alibaba: ['qwen-turbo', 'qwen-max'],
            openrouter: ['gpt-4o-mini']
        };

        this.modelSelect.innerHTML = models[provider]
            .map(model => `<option value="${model}">${model}</option>`)
            .join('');
    }

    handleSubmit(event) {
        // 防止表单默认提交行为
        event.preventDefault();
        console.log('提交事件触发');

        const provider = this.providerSelect.value;
        const model = this.modelSelect.value;
        const apiKey = this.apiKeyInput.value;

        // 检查字段是否填写完整
        if (!provider || !model || !apiKey) {
            // 使用 i18n 获取国际化文本
            const message = window.i18n && window.i18n.get ? 
                window.i18n.get('fillAllFields') : '请填写所有字段！';
            alert(message);
            return;
        }

        const requestData = {
            provider: provider,
            model: model,
            apiKey: apiKey
        };

        // 直接通过 HTTP 提交
        fetch('/api/save-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        })
            .then(response => {
                if (response.ok) {
                    // 使用 i18n 获取国际化文本
                    const message = window.i18n && window.i18n.get ? 
                        window.i18n.get('configSubmitted') : '配置已提交到服务器！';
                    alert(message);
                } else {
                    // 使用 i18n 获取国际化文本
                    const message = window.i18n && window.i18n.get ? 
                        window.i18n.get('submitFailed') : '提交失败，请检查服务器状态。';
                    alert(message);
                }
            })
            .catch(error => {
                console.error('HTTP 请求失败:', error);
                // 使用 i18n 获取国际化文本
                const message = window.i18n && window.i18n.get ? 
                    window.i18n.get('networkError') : '提交失败，请检查网络连接。';
                alert(message);
            });
    }
}

// 在 DOMContentLoaded 事件之前移除之前可能存在的事件监听器
if (window.apiPanelTabSwitchHandler) {
    document.removeEventListener('click', window.apiPanelTabSwitchHandler);
}

// 创建一个全局初始化函数，确保只有一个实例
window.initializeAPIPanel = function() {
    // 检查之前创建的实例是否有效
    const existingInstance = window.apiPanelInstance;
    if (existingInstance) {
        console.log('复用已存在的APIPanel实例');
        // 更新实例
        existingInstance.setupEventListeners();
        return existingInstance;
    }
    
    // 创建新实例
    console.log('创建新的APIPanel实例');
    window.apiPanelInstance = new APIPanel();
    return window.apiPanelInstance;
};

// 创建新的事件处理函数并保存引用
window.apiPanelTabSwitchHandler = function(event) {
    if (event.target.classList.contains('tab-btn') && 
        event.target.getAttribute('data-target') === 'api-panel') {
        console.log('切换到API面板');
        if (window.apiPanelInstance) {
            // 切换面板时刷新模型选项，同时重置事件绑定
            window.apiPanelInstance.updateModelOptions();
            window.apiPanelInstance.setupEventListeners();
        }
    }
};

// 添加新的监听器
document.addEventListener('click', window.apiPanelTabSwitchHandler);