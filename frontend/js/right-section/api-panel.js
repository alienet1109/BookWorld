class APIPanel {
    constructor() {
        // 强制单例模式 - 如果实例已存在，直接返回
        if (window.apiPanelInstance) {
            console.warn('APIPanel已存在实例，返回现有实例');
            return window.apiPanelInstance;
        }
        
        // 初始化DOM元素引用
        this.providerSelect = document.getElementById('api-provider');
        this.modelSelect = document.getElementById('api-model');
        this.apiKeyInput = document.getElementById('api-key');
        this.submitButton = document.querySelector('.api-submit-btn');

        // 初始化标记
        this.initialized = false;
        this.eventsBound = false;

        // 绑定方法到实例，确保函数引用一致
        this.handleSubmit = this.handleSubmit.bind(this);
        this.updateModelOptions = this.updateModelOptions.bind(this);
        
        // 初始化模型选项
        this.updateModelOptions();
        
        // 将实例保存到全局
        window.apiPanelInstance = this;
        console.log('APIPanel: 新实例已创建');
    }

    init() {
        // 只初始化一次
        if (this.initialized) {
            console.log('APIPanel: 已初始化，跳过重复初始化');
            return;
        }
        
        // 确保DOM元素已加载
        if (!document.getElementById('api-panel')) {
            console.warn('APIPanel: DOM未准备好，100ms后重试');
            setTimeout(() => this.init(), 100);
            return;
        }
        
        // 设置事件监听器
        this.setupEventListeners();
        this.initialized = true;
        console.log('APIPanel: 初始化完成');
    }

    setupEventListeners() {
        // 防止重复绑定事件
        if (this.eventsBound) {
            console.log('APIPanel: 事件已绑定，跳过');
            return;
        }
        
        // 处理提交按钮
        if (this.submitButton) {
            // 完全替换按钮以清除所有之前可能绑定的事件
            const newButton = this.submitButton.cloneNode(true);
            this.submitButton.parentNode.replaceChild(newButton, this.submitButton);
            this.submitButton = newButton;
            
            // 为克隆后的新按钮添加事件监听器
            this.submitButton.addEventListener('click', this.handleSubmit);
            console.log('APIPanel: 提交按钮事件监听器已绑定到克隆按钮');
        }
    
        // 处理供应商选择下拉框
        if (this.providerSelect) {
            // 同样替换元素以清除事件
            const newSelect = this.providerSelect.cloneNode(true);
            this.providerSelect.parentNode.replaceChild(newSelect, this.providerSelect);
            this.providerSelect = newSelect;
            this.providerSelect.addEventListener('change', this.updateModelOptions);
            console.log('APIPanel: 供应商选择框事件已绑定到克隆元素');
        }
        
        this.eventsBound = true;
    }

    updateModelOptions() {
        if (!this.providerSelect || !this.modelSelect) {
            console.warn('APIPanel: DOM引用无效，无法更新模型选项');
            return;
        }
        
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
            
        console.log(`APIPanel: 已更新模型列表为${provider}供应商的选项`);
    }

    handleSubmit(event) {
        // 防止表单默认提交行为和事件冒泡
        event.preventDefault();
        event.stopPropagation();
        
        // 详细日志，帮助调试
        console.log('APIPanel: 提交处理开始 -', 
                    '元素:', event.target.tagName,
                    '事件类型:', event.type,
                    '时间戳:', new Date().toISOString());
        
        // 使用静态标记防止重复提交
        if (APIPanel.isSubmitting) {
            console.log('APIPanel: 提交操作正在处理中，忽略重复点击');
            return;
        }
        
        // 设置标记，防止短时间内重复提交
        APIPanel.isSubmitting = true;
        setTimeout(() => { APIPanel.isSubmitting = false; }, 1000);

        // 获取表单值
        const provider = this.providerSelect.value;
        const model = this.modelSelect.value;
        const apiKey = this.apiKeyInput.value;

        // 检查字段是否填写完整
        if (!provider || !model || !apiKey) {
            // 使用 i18n 获取国际化文本
            const message = window.i18n && window.i18n.get ? 
                window.i18n.get('fillAllFields') : '请填写所有字段！';
            alert(message);
            APIPanel.isSubmitting = false; // 重置提交状态
            return;
        }

        const requestData = {
            provider: provider,
            model: model,
            apiKey: apiKey
        };

        // 发送HTTP请求
        fetch('/api/save-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        })
            .then(response => {
                APIPanel.isSubmitting = false; // 重置提交状态
                if (response.ok) {
                    // 使用 i18n 获取国际化文本
                    const message = window.i18n && window.i18n.get ? 
                        window.i18n.get('configSubmitted') : '配置已提交到服务器！';
                    alert(message);
                    console.log('APIPanel: 配置已成功提交');
                } else {
                    // 使用 i18n 获取国际化文本
                    const message = window.i18n && window.i18n.get ? 
                        window.i18n.get('submitFailed') : '提交失败，请检查服务器状态。';
                    alert(message);
                    console.error('APIPanel: 服务器响应失败', response.status);
                }
            })
            .catch(error => {
                APIPanel.isSubmitting = false; // 重置提交状态
                console.error('APIPanel: HTTP请求失败:', error);
                // 使用 i18n 获取国际化文本
                const message = window.i18n && window.i18n.get ? 
                    window.i18n.get('networkError') : '提交失败，请检查网络连接。';
                alert(message);
            });
    }
}

// 防重复提交的静态标记
APIPanel.isSubmitting = false;

// 下面的代码只执行一次，防止多次引入脚本时重复执行
if (!window.apiPanelJsInitialized) {
    // 单例获取函数
    window.getAPIPanel = function() {
        if (!window.apiPanelInstance) {
            window.apiPanelInstance = new APIPanel();
        }
        return window.apiPanelInstance;
    };
    
    // 初始化函数 - 只执行一次
    window.initializeAPIPanel = function() {
        if (window.apiPanelInitialized) {
            console.log('APIPanel: 已初始化，跳过重复初始化');
            return window.apiPanelInstance;
        }
        
        const instance = window.getAPIPanel();
        instance.init();
        
        // 标记为已初始化
        window.apiPanelInitialized = true;
        console.log('APIPanel: 首次全局初始化完成');
        
        return instance;
    };
    
    // 确保只有一个tab事件处理器
    if (window.apiPanelTabHandler) {
        document.removeEventListener('click', window.apiPanelTabHandler);
    }
    
    // 定义tab切换处理函数
    window.apiPanelTabHandler = function(event) {
        // 只处理API面板tab按钮的点击
        if (event.target.classList.contains('tab-btn') && 
            event.target.getAttribute('data-target') === 'api-panel') {
            
            console.log('APIPanel: Tab切换到API面板');
            
            // 获取实例但不做额外初始化，只更新模型选项
            const instance = window.apiPanelInstance || window.getAPIPanel();
            instance.updateModelOptions();
        }
    };
    
    // 注册全局tab切换事件
    document.addEventListener('click', window.apiPanelTabHandler);
    
    // 设置已初始化标记
    window.apiPanelJsInitialized = true;
    console.log('APIPanel: 脚本初始化标记已设置，防止重复执行');
}

console.log('APIPanel: api-panel.js 文件已完成加载');