// message.js
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.querySelector('.chat-messages');
    const textarea = document.querySelector('textarea');
    const sendButton = document.querySelector('.send-btn');
    const controlBtn = document.getElementById('controlBtn');
    const stopBtn = document.getElementById('stopBtn');
    const exportStoryBtn = document.getElementById('exportStoryBtn');
    
    // 生成随机的客户端ID
    const clientId = Math.random().toString(36).substring(7);
    
    // WebSocket连接
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${clientId}`);
    window.ws = ws

    let isPlaying = false;
    // 添加场景相关属性
    let currentSceneFilter = null;
    let startButtonText =  translations[window.i18n.currentLang]['start'];
    // 控制按钮点击事件
    controlBtn.addEventListener('click', function() {
        if (!isPlaying) {
            // 开始
            ws.send(JSON.stringify({
                type: 'control',
                action: 'start'
            }));
            startButtonText =  translations[window.i18n.currentLang]['pause']
            controlBtn.innerHTML = `<i class="fas fa-pause"></i><span data-i18n="pause">${startButtonText}</span>`;
            isPlaying = true;
        } else {
            // 暂停
            ws.send(JSON.stringify({
                type: 'control',
                action: 'pause'
            }));
            startButtonText =  translations[window.i18n.currentLang]['start']
            controlBtn.innerHTML = `<i class="fas fa-play"></i><span data-i18n="pause">${startButtonText}</span>`;
            isPlaying = false;
        }
    });

    // 停止按钮点击事件
    stopBtn.addEventListener('click', function() {
        ws.send(JSON.stringify({
            type: 'control',
            action: 'stop'
        }));
        controlBtn.innerHTML = '<i class="fas fa-play"></i><span>开始</span>';
        isPlaying = false;
    });

    // WebSocket事件处理
    ws.onopen = function() {
        console.log('WebSocket连接已建立');
        addSystemMessage('连接已建立');
    };
    
    ws.onclose = function() {
        console.log('WebSocket连接已关闭');
        addSystemMessage('连接已断开');
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket错误:', error);
        addSystemMessage('连接错误');
    };
    
    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);
        // 创建自定义事件来分发 WebSocket 消息
        const wsEvent = new CustomEvent('websocket-message', {
            detail: message
        });
        window.dispatchEvent(wsEvent);

        // 消息处理逻辑
        if (message.type === 'message') {
            // 从状态中获取当前场景编号
            const sceneNumber = message.data.scene; // 确保消息中包含场景信息
            if (sceneNumber !== undefined) {
                // 触发场景更新事件
                window.dispatchEvent(new CustomEvent('scene-update', {
                    detail: { scene: sceneNumber }
                }));
            }
            if (message.data.type === 'system') {
                addSystemMessage(message.data.text);
            } 
            else if (message.data.type === 'story') {
                // 为故事消息添加特殊样式
                const messageElement = document.createElement('div');
                messageElement.className = 'message story-message';
                messageElement.innerHTML = `
                    <div class="content">
                        <div class="header">
                            <span class="username">故事总结</span>
                            <span class="timestamp">${message.data.timestamp}</span>
                        </div>
                        <div class="text">${message.data.text}</div>
                    </div>
                `;
                chatMessages.appendChild(messageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            else {
                renderMessage(message.data);
            }
        }
        else if (message.type === 'initial_data') {
            // 清空现有消息，处理初始数据
            chatMessages.innerHTML = '';
            
            if (message.data.history_messages) {
                loadHistoryMessages(message.data.history_messages);
            }
            else {
                loadHistoryMessages([]);
            }
        }
    };

    function loadHistoryMessages(messages) {
        // 清空现有消息
        chatMessages.innerHTML = '';
        
        messages.forEach(message => {
            renderMessage(message);
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        console.log(`Loaded ${messages.length} historical messages`);
    }

    // 渲染消息
    function renderMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.dataset.timestamp = message.timestamp;
        messageElement.dataset.username = message.username;
        
        // 添加场景属性
        if (message.scene !== undefined) {
            messageElement.dataset.scene = message.scene;
            console.log(`Rendering message for scene ${message.scene}`);
        }
        
        messageElement.innerHTML = `
            <div class="icon">
                <img src="${message.icon}" alt="${message.username}">
            </div>
            <div class="content">
                <div class="header">
                    <span class="username">${message.username}</span>
                    <span class="timestamp">${message.timestamp}</span>
                </div>
                <div class="text-wrapper">
                    <div class="text">${message.text}</div>
                    <button class="edit-icon"><i class="fas fa-pen"></i></button>
                    <div class="edit-buttons" style="display: none;">
                        <button class="edit-btn save-btn">保存</button>
                        <button class="edit-btn cancel-btn">取消</button>
                    </div>
                </div>
            </div>
        `;
    
        // 获取元素引用
        const textElement = messageElement.querySelector('.text');
        const editButtons = messageElement.querySelector('.edit-buttons');
        const editIcon = messageElement.querySelector('.edit-icon');
        
        // 存储原始文本
        let originalText = message.text;
        let isEditing = false;
    
        // 移除文本元素的 focus 事件监听器，改为编辑图标的点击事件
        editIcon.addEventListener('click', () => {
            if (!isEditing) {
                isEditing = true;
                editButtons.style.display = 'flex';
                textElement.classList.add('editing');
                textElement.setAttribute('contenteditable', 'true');
                textElement.focus();
            }
        });
    
        // 保存按钮点击事件
        messageElement.querySelector('.save-btn').addEventListener('click', () => {
            const newText = textElement.textContent.trim();
            if (newText !== originalText) {
                // 发送编辑消息到服务器
                ws.send(JSON.stringify({
                    type: 'edit_message',
                    data: {
                        uuid: message.uuid,
                        text: newText,
                    }
                }));
                originalText = newText;
            }
            exitEditMode();
        });
    
        // 取消按钮点击事件
        messageElement.querySelector('.cancel-btn').addEventListener('click', () => {
            textElement.textContent = originalText;
            exitEditMode();
        });
    
        // 处理快捷键
        textElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                messageElement.querySelector('.save-btn').click();
            }
            if (e.key === 'Escape') {
                messageElement.querySelector('.cancel-btn').click();
            }
        });
    
        // 添加点击外部监听器
        document.addEventListener('click', function(event) {
            if (isEditing && !messageElement.contains(event.target)) {
                // 如果点击位置不在当前消息元素内，退出编辑模式
                exitEditMode();
                textElement.textContent = originalText;
            }
        });
    
        // 防止编辑区域的点击事件冒泡
        messageElement.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    
        function exitEditMode() {
            isEditing = false;
            editButtons.style.display = 'none';
            textElement.classList.remove('editing');
            textElement.blur();
        }
    
        // 根据当前场景筛选器决定是否显示
        if (currentSceneFilter !== null) {
            messageElement.style.display = 
                (String(message.scene) === String(currentSceneFilter)) ? '' : 'none';
        }

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    // 添加系统消息
    function addSystemMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message system';
        messageElement.innerHTML = `
            <div class="content">
                <div class="text">${text}</div>
            </div>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 发送消息
    function sendMessage() {
        const text = textarea.value.trim();
        if (text && ws.readyState === WebSocket.OPEN) {
            const message = {
                type: 'user_message',
                text: text,
                timestamp: new Date().toLocaleString()
            };
            ws.send(JSON.stringify(message));
            textarea.value = '';
        }
    }

    // 绑定发送按钮点击事件
    sendButton.addEventListener('click', sendMessage);

    // 绑定回车键发送
    textarea.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 监听场景选择事件
    window.addEventListener('scene-selected', (event) => {
        const selectedScene = event.detail.scene;
        currentSceneFilter = selectedScene;
        
        // 更新所有消息的显示状态
        document.querySelectorAll('.message').forEach(msg => {
            if (selectedScene === null) {
                msg.style.display = '';
            } else {
                msg.style.display = 
                    (msg.dataset.scene === String(selectedScene)) ? '' : 'none';
            }
        });
        
        // 滚动到可见的第一条消息
        const visibleMessages = document.querySelectorAll('.message[style=""]');
        if (visibleMessages.length > 0) {
            visibleMessages[0].scrollIntoView({ behavior: 'smooth' });
        }
    });

    // 添加导出故事按钮的点击事件
    exportStoryBtn.addEventListener('click', function() {
        ws.send(JSON.stringify({
            type: 'generate_story'
        }));
    });
});
