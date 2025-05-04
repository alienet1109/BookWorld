class APIPanel {
    constructor() {
        // 强制单例模式
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
        
        // 绑定方法到实例，确保函数引用一致
        this.handleSubmit = this.handleSubmit.bind(this);
        this.updateModelOptions = this.updateModelOptions.bind(this);
        
        // 初始化模型选项
        this.updateModelOptions();
        
        // 设置单例
        window.apiPanelInstance = this;
        console.log('APIPanel: 新实例已创建，但尚未初始化事件');
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
        // 关键改变: 使用DOM元素的data属性作为标记
        if (this.submitButton) {
            // 检查按钮是否已有事件绑定标记
            if (this.submitButton.getAttribute('data-has-click-handler') === 'true') {
                console.log('APIPanel: 提交按钮已绑定事件，跳过');
            } else {
                // 首先移除可能存在的旧事件监听器
                this.submitButton.removeEventListener('click', this.handleSubmit);
                
                // 添加新的事件监听器
                this.submitButton.addEventListener('click', this.handleSubmit);
                
                // 使用DOM属性标记已绑定
                this.submitButton.setAttribute('data-has-click-handler', 'true');
                console.log('APIPanel: 提交按钮事件已绑定并标记到DOM元素');
            }
        }
        
        if (this.providerSelect) {
            // 同样处理下拉框
            if (this.providerSelect.getAttribute('data-has-change-handler') === 'true') {
                console.log('APIPanel: 下拉框已绑定事件，跳过');
            } else {
                this.providerSelect.removeEventListener('change', this.updateModelOptions);
                this.providerSelect.addEventListener('change', this.updateModelOptions);
                this.providerSelect.setAttribute('data-has-change-handler', 'true');
            }
        }
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
    }

    handleSubmit(event) {
        // 防止表单默认提交行为和事件冒泡
        event.preventDefault();
        event.stopPropagation();
        
        console.log('APIPanel: 提交处理开始 -', 
                   'ID:', Math.random().toString(36).substr(2, 9), 
                   '时间:', new Date().toISOString());
        
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
            const message = window.i18n && window.i18n.get ? 
                window.i18n.get('fillAllFields') : '请填写所有字段！';
            alert(message);
            APIPanel.isSubmitting = false;
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
                APIPanel.isSubmitting = false;
                if (response.ok) {
                    const message = window.i18n && window.i18n.get ? 
                        window.i18n.get('configSubmitted') : '配置已提交到服务器！';
                    alert(message);
                } else {
                    const message = window.i18n && window.i18n.get ? 
                        window.i18n.get('submitFailed') : '提交失败，请检查服务器状态。';
                    alert(message);
                }
            })
            .catch(error => {
                APIPanel.isSubmitting = false;
                console.error('APIPanel: HTTP请求失败:', error);
                const message = window.i18n && window.i18n.get ? 
                    window.i18n.get('networkError') : '提交失败，请检查网络连接。';
                alert(message);
            });
    }
}

// 防重复提交的静态标记
APIPanel.isSubmitting = false;

// 所有全局代码放在一个条件中，确保只执行一次
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
        
        return instance;
    };
    
    // 处理标签切换事件 - 修改为不再获取新实例
    if (window.apiPanelTabHandler) {
        document.removeEventListener('click', window.apiPanelTabHandler);
    }
    
    window.apiPanelTabHandler = function(event) {
        // 只处理API面板tab按钮的点击
        if (event.target.classList.contains('tab-btn') && 
            event.target.getAttribute('data-target') === 'api-panel') {
            
            console.log('APIPanel: Tab切换到API面板');
            
            // 关键修改：只在已经初始化的情况下更新模型选项
            if (window.apiPanelInstance) {
                window.apiPanelInstance.updateModelOptions();
                console.log('APIPanel: 使用现有实例更新模型选项');
            }
            // 不再调用getAPIPanel()，避免触发潜在的重复初始化
        }
    };
    
    // 添加标签切换事件处理
    document.addEventListener('click', window.apiPanelTabHandler);
    
    // 设置已初始化标记
    window.apiPanelJsInitialized = true;
    console.log('APIPanel: 脚本全局初始化完成');
}