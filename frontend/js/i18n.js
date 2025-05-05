const translations = {
    en: {
        start: "Start",
        pause: "Pause",
        stop: "Stop",
        exportStory: "Export Story",
        switchLang: "中/EN",
        inputPlaceholder: "Enter your message",
        status: "Status",
        settings: "Settings",
        scenes: "Scenes",
        scenesList: "Scenes",
        currentEvent: "Current Event",
        currentLocation: "Current Location",
        currentGroup: "Current Group",
        map: "Map",
        characterProfiles: "Character Profiles",
        apiProvider: "API Provider:",
        model: "Model:",
        saveSettings: "Save Settings",
        submit: "Submit",
        fillAllFields: "Please fill in all fields!",
        configSubmitted: "Configuration has been submitted to the server!",
        submitFailed: "Submission failed. Please check server status.",
        networkError: "Submission failed. Please check network connection.",
        APIsettings: "API Setting"
    },
    zh: {
        start: "开始",
        pause: "暂停",
        stop: "停止",
        exportStory: "输出故事",
        switchLang: "中/EN",
        inputPlaceholder: "输入你的消息",
        status: "状态",
        settings: "设定",
        scenes: "场景",
        scenesList: "场景列表",
        currentEvent: "当前事件",
        currentLocation: "当前地点",
        currentGroup: "当前分组",
        map: "地图",
        characterProfiles: "角色档案",
        apiProvider: "API提供商:",
        model: "模型:",
        saveSettings: "保存设置",
        submit: "提交",
        fillAllFields: "请填写所有字段！",
        configSubmitted: "配置已提交到服务器！",
        submitFailed: "提交失败，请检查服务器状态。",
        networkError: "提交失败，请检查网络连接。",
        APIsettings: "API设置"
    }
};

class I18nManager {
    constructor() {
        this.currentLang = 'zh';
        this.init();
    }

    init() {
        this.bindLanguageButton();
        this.updateTexts();
    }

    bindLanguageButton() {
        const langBtn = document.getElementById('languageBtn');
        langBtn.addEventListener('click', () => {
            this.currentLang = this.currentLang === 'zh' ? 'en' : 'zh';
            this.updateTexts();
            this.saveLanguagePreference();
        });
    }

    updateTexts() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[this.currentLang][key]) {
                element.textContent = translations[this.currentLang][key];
            }
        });
        // 更新输入框占位符
        const textarea = document.querySelector('.input-area textarea');
        textarea.placeholder = translations[this.currentLang].inputPlaceholder;
        
        // 触发语言变更事件
        window.dispatchEvent(new CustomEvent('language-changed'));
    }

    saveLanguagePreference() {
        localStorage.setItem('preferredLanguage', this.currentLang);
    }

    loadLanguagePreference() {
        const savedLang = localStorage.getItem('preferredLanguage');
        if (savedLang) {
            this.currentLang = savedLang;
            this.updateTexts();
        }
    }
    
    // 新增方法：获取特定翻译文本
    get(key) {
        if (translations[this.currentLang] && translations[this.currentLang][key]) {
            return translations[this.currentLang][key];
        }
        // 回退到中文
        return translations['zh'][key] || key;
    }
}

// 初始化语言管理器
document.addEventListener('DOMContentLoaded', () => {
    window.i18n = new I18nManager();
    window.i18n.loadLanguagePreference();
});
