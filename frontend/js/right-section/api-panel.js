class APIPanel {
    constructor() {
        // 初始化时绑定 DOM 元素
        this.providerSelect = document.getElementById('api-provider');
        this.modelSelect = document.getElementById('api-model');
        this.apiKeyInput = document.getElementById('api-key');
        this.submitButton = document.querySelector('.api-submit-btn');

        // 标记这个实例已经初始化
        this.initialized = false;

        // 绑定方法到当前实例，确保函数引用一致
        this.handleSubmit = this.handleSubmit.bind(this);
        this.updateModelOptions = this.updateModelOptions.bind(this);
        
        // 初始化模型选项
        this.updateModelOptions();
        
        console.log('APIPanel 实例已创建, 等待初始化事件绑定');
    }

    init() {
        // 只初始化一次
        if (this.initialized) {
            console.log('APIPanel 已经初始化过，跳过');
            return;
        }
        
        // 设置事件监听器
        this.setupEventListeners();
        this.initialized = true;
        console.log('APIPanel 实例已完成初始化');
    }

    setupEventListeners() {
        if (this.submitButton) {
            // 为安全起见，先移除可能存在的事件监听器
            this.submitButton.removeEventListener('click', this.handleSubmit);
            
            // 直接在原始按钮上添加事件，不替换DOM
            this.submitButton.addEventListener('click', this.handleSubmit);
            console.log('Submit 事件监听器已绑定到原始按钮');
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
        // 防止表单默认提交行为和事件冒泡
        event.preventDefault();
        event.stopPropagation();
        
        // 使用静态标记防止重复提交
        if (APIPanel.isSubmitting) {
            console.log('提交操作正在处理中，忽略重复点击');
            return;
        }
        
        // 设置标记，防止1秒内重复提交
        APIPanel.isSubmitting = true;
        setTimeout(() => { APIPanel.isSubmitting = false; }, 1000);
        
        console.log('提交事件触发 - event target:', event.target.tagName);

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

// 静态属性，用于防止重复提交
APIPanel.isSubmitting = false;

// 创建一个全局单例工厂函数
window.getAPIPanel = function() {
    if (!window.apiPanelInstance) {
        window.apiPanelInstance = new APIPanel();
    }
    return window.apiPanelInstance;
};

// 专门用于初始化的函数，确保只初始化一次
window.initializeAPIPanel = function() {
    const instance = window.getAPIPanel();
    // 确保只初始化一次
    instance.init();
    return instance;
};

// 移除原来的事件监听器
if (window.apiPanelTabHandler) {
    document.removeEventListener('click', window.apiPanelTabHandler);
}

// 创建新的、只处理tab切换的事件监听器
window.apiPanelTabHandler = function(event) {
    // 只处理tab按钮的点击，不关心其他元素
    if (event.target.classList.contains('tab-btn') && 
        event.target.getAttribute('data-target') === 'api-panel') {
        
        console.log('Tab切换到API面板');
        // 确保实例存在，但不涉及事件处理
        const instance = window.getAPIPanel();
        // 只更新模型选项
        instance.updateModelOptions();
    }
};

// 添加tab切换处理
document.addEventListener('click', window.apiPanelTabHandler);

// 静态标记，避免重复监听
window.apiPanelJsInitialized = true;
console.log('api-panel.js 加载完成');