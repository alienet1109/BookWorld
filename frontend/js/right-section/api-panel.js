class APIPanel {
    constructor() {
        // 初始化时绑定 DOM 元素
        this.providerSelect = document.getElementById('api-provider');
        this.modelSelect = document.getElementById('api-model');
        this.apiKeyInput = document.getElementById('api-key');
        this.submitButton = document.querySelector('.api-submit-btn');

        // 绑定方法到当前实例，确保函数引用一致
        this.handleSubmit = this.handleSubmit.bind(this); // 确保 remove/add 监听器一致
        this.updateModelOptions = this.updateModelOptions.bind(this);

        // 设置初始事件监听器
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.submitButton) {
            // 确保移除已有监听器，防止重复绑定
            this.submitButton.removeEventListener('click', this.handleSubmit);
            this.submitButton.addEventListener('click', this.handleSubmit);
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

        const provider = this.providerSelect.value;
        const model = this.modelSelect.value;
        const apiKey = this.apiKeyInput.value;

        // 检查字段是否填写完整
        if (!provider || !model || !apiKey) {
            alert('请填写所有字段！');
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
                    alert('配置已提交到服务器！');
                } else {
                    alert('提交失败，请检查服务器状态。');
                }
            })
            .catch(error => {
                console.error('HTTP 请求失败:', error);
                alert('提交失败，请检查网络连接。');
            });
    }
}

// 初始化 API 面板
document.addEventListener('DOMContentLoaded', () => {
    new APIPanel();
});
