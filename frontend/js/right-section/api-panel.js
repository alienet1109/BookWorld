class APIPanel {
    constructor() {
        // 强制单例模式
        if (window.apiPanelInstance) {
            console.warn('APIPanel: Instance already exists, returning existing one.');
            return window.apiPanelInstance;
        }
        console.log('APIPanel: Creating new instance.');

        // 初始化DOM元素引用
        this.providerSelect = document.getElementById('api-provider');
        this.modelSelect = document.getElementById('api-model');
        this.apiKeyInput = document.getElementById('api-key');
        // Use a more specific selector if multiple buttons might exist
        this.submitButton = document.querySelector('#api-panel .api-submit-btn');

        // Check if elements were found
        if (!this.providerSelect || !this.modelSelect || !this.apiKeyInput || !this.submitButton) {
            console.error("APIPanel: One or more required DOM elements not found during construction.");
        }

        this.initialized = false;

        this.handleSubmit = this.handleSubmit.bind(this);
        this.updateModelOptions = this.updateModelOptions.bind(this);
        if (this.providerSelect && this.modelSelect) {
            this.updateModelOptions();
        }

        window.apiPanelInstance = this;
        console.log('APIPanel: New instance created.');
    }

    init() {
        if (this.initialized) {
            console.log('APIPanel: Listeners already initialized, skipping.');
            return;
        }
        
        if (!this.providerSelect || !this.modelSelect || !this.apiKeyInput || !this.submitButton) {
             console.error("APIPanel: Cannot init listeners, required DOM elements missing.");
             return;
        }

        console.log('APIPanel: Initializing event listeners.');
        this.setupEventListeners();
        this.initialized = true; 
        console.log('APIPanel: Event listeners initialized successfully.');
    }

    setupEventListeners() {
        // Submit Button Listener
        if (this.submitButton) {
            this.submitButton.removeEventListener('click', this.handleSubmit);
            // Add the listener
            this.submitButton.addEventListener('click', this.handleSubmit);
            console.log('APIPanel: Submit button listener attached.');
        }

        // Provider Select Listener
        if (this.providerSelect) {
            this.providerSelect.removeEventListener('change', this.updateModelOptions);
            this.providerSelect.addEventListener('change', this.updateModelOptions);
            console.log('APIPanel: Provider select listener attached.');
        }
    }

    updateModelOptions() {
        if (!this.providerSelect || !this.modelSelect) {
            console.warn('APIPanel: DOM elements missing for updateModelOptions.');
            return;
        }

        const provider = this.providerSelect.value;
        const models = {
            openai: ['gpt-3.5-turbo', 'gpt-4'],
            anthropic: ['claude-3-opus', 'claude-3-sonnet'],
            alibaba: ['qwen-turbo', 'qwen-max'],
            openrouter: ['gpt-4o-mini']
        };

        const currentModelValue = this.modelSelect.value;
        this.modelSelect.innerHTML = ''; // Clear existing

        if (models[provider] && models[provider].length > 0) {
            models[provider].forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                this.modelSelect.appendChild(option);
            });
            // Restore selection if possible
            if (models[provider].includes(currentModelValue)) {
                this.modelSelect.value = currentModelValue;
            }
        } else {
            // Add placeholder if no models
            const option = document.createElement('option');
            option.textContent = 'No models available';
            option.disabled = true;
            this.modelSelect.appendChild(option);
        }
    }

    handleSubmit(event) {
        // 防止表单默认提交行为和事件冒泡
        event.preventDefault();
        event.stopPropagation();

        if (APIPanel.isSubmitting) {
            console.log('APIPanel: Submission in progress, ignoring duplicate click.');
            return;
        }

        // Check elements exist before proceeding
        if (!this.providerSelect || !this.modelSelect || !this.apiKeyInput || !this.submitButton) {
             console.error("APIPanel: Cannot handle submit, critical elements missing.");
             alert(window.i18n?.get('internalError') ?? '内部错误，无法提交。');
             return;
        }


        // 设置标记，防止短时间内重复提交
        APIPanel.isSubmitting = true;
        this.submitButton.disabled = true; // Disable button
        // Use setTimeout for debounce, not for resetting the flag immediately after fetch starts
        const resetButton = () => {
             APIPanel.isSubmitting = false;
             if (this.submitButton) { // Check if button still exists
                 this.submitButton.disabled = false;
             }
             console.log('APIPanel: Submit button re-enabled.');
        };


        // 获取表单值
        const provider = this.providerSelect.value;
        const model = this.modelSelect.value;
        const apiKey = this.apiKeyInput.value.trim(); // Trim whitespace

        // 检查字段是否填写完整
        if (!provider || !model || !apiKey) {
            const message = window.i18n?.get('fillAllFields') ?? '请填写所有字段！';
            alert(message);
            resetButton(); // Re-enable button on validation failure
            return;
        }

        const requestData = {
            provider: provider,
            model: model,
            apiKey: apiKey
        };

        console.log('APIPanel: Sending config data (key hidden):', { provider, model, apiKey: '***' });

        // 发送HTTP请求
        fetch('/api/save-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (response.ok) {
                const message = window.i18n?.get('configSubmitted') ?? '配置已提交到服务器！';
                alert(message);
            } else {
                 // Try to get more specific error
                 response.text().then(text => {
                     console.error('APIPanel: Submit failed.', response.status, text);
                     const message = (window.i18n?.get('submitFailed') ?? '提交失败，请检查服务器状态。') + ` (Status: ${response.status})`;
                     alert(message);
                 }).catch(() => {
                      console.error('APIPanel: Submit failed.', response.status);
                      const message = (window.i18n?.get('submitFailed') ?? '提交失败，请检查服务器状态。') + ` (Status: ${response.status})`;
                      alert(message);
                 });
            }
        })
        .catch(error => {
            console.error('APIPanel: HTTP request failed:', error);
            const message = window.i18n?.get('networkError') ?? '提交失败，请检查网络连接。';
            alert(message);
        })
        .finally(() => {
            // Always re-enable the button after fetch completes (success or error)
            resetButton();
        });
    }
}

APIPanel.isSubmitting = false;
window.APIPanel = APIPanel;
