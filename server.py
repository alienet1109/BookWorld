from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import json
import asyncio
import os
from pathlib import Path
from datetime import datetime
from bw_utils import is_image, load_json_file
from BookWorld import BookWorld

app = FastAPI()
default_icon_path = './frontend/assets/images/default-icon.jpg'
config = load_json_file('config.json')
for key in config:
    if "API_KEY" in key:
        os.environ[key] = config[key]

static_file_abspath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'frontend'))
app.mount("/frontend", StaticFiles(directory=static_file_abspath), name="frontend")

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  
        self.story_tasks: dict[str, asyncio.Task] = {}  
        if True:
            if "preset_path" in config and config["preset_path"] and os.path.exists(config["preset_path"]):
                preset_path = config["preset_path"]
            elif "genre" in config and config["genre"]:
                genre = config["genre"]
                preset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),f"./config/experiment_{genre}.json")
            else:
                raise ValueError("Please set the preset_path in `config.json`.")
            self.bw = BookWorld(preset_path = preset_path,
                    world_llm_name = config["world_llm_name"],
                    role_llm_name = config["role_llm_name"],
                    embedding_name = config["embedding_model_name"])
            self.bw.set_generator(rounds = config["rounds"], 
                        save_dir = config["save_dir"], 
                        if_save = config["if_save"],
                        mode = config["mode"],
                        scene_mode = config["scene_mode"],)
        else:
            from BookWorld_test import BookWorld_test
            self.bw = BookWorld_test()
          
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        self.stop_story(client_id)
            
    def stop_story(self, client_id: str):
        if client_id in self.story_tasks:
            self.story_tasks[client_id].cancel()
            del self.story_tasks[client_id]

    async def start_story(self, client_id: str):
        if client_id in self.story_tasks:
            # 如果已经有任务在运行，先停止它
            self.stop_story(client_id)
        
        # 创建新的故事任务
        self.story_tasks[client_id] = asyncio.create_task(
            self.generate_story(client_id)
        )

    async def generate_story(self, client_id: str):
        """持续生成故事的协程"""
        try:
            while True:
                if client_id in self.active_connections:
                    message,status = await self.get_next_message()
                    await self.active_connections[client_id].send_json({
                        'type': 'message',
                        'data': message
                    })
                    await self.active_connections[client_id].send_json({
                        'type': 'status_update',
                        'data': status
                    })
                    # 添加延迟，控制消息发送频率
                    await asyncio.sleep(1)  # 可以调整这个值
                else:
                    break
        except asyncio.CancelledError:
            # 任务被取消时的处理
            print(f"Story generation cancelled for client {client_id}")
        except Exception as e:
            print(f"Error in generate_story: {e}")

    async def get_initial_data(self):
        """获取初始化数据"""
        return {
            'characters': self.bw.get_characters_info(),
            'map': self.bw.get_map_info(),
            'settings': self.bw.get_settings_info(),
            'status': self.bw.get_current_status(),
            'history_messages':self.bw.get_history_messages(save_dir = config["save_dir"]),
        }
    
    async def get_next_message(self):
        """从BookWorld获取下一条消息"""
        message = self.bw.generate_next_message()
        if not os.path.exists(message["icon"]) or not is_image(message["icon"]):
            message["icon"] = default_icon_path
        status = self.bw.get_current_status()
        return message,status

manager = ConnectionManager()

@app.get("/")
async def get():
    html_file = Path("index.html")
    return HTMLResponse(html_file.read_text(encoding="utf-8"))

@app.get("/data/{full_path:path}")
async def get_file(full_path: str):
    # 可以设置多个基础路径
    base_paths = [
        Path("/data/")
    ]
    
    for base_path in base_paths:
        file_path = base_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        else:
            return FileResponse(default_icon_path)
    
    raise HTTPException(status_code=404, detail="File not found")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        initial_data = await manager.get_initial_data()
        await websocket.send_json({
            'type': 'initial_data',
            'data': initial_data
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'user_message':
                # 处理用户消息
                await websocket.send_json({
                    'type': 'message',
                    'data': {
                        'username': 'User',
                        'timestamp': message['timestamp'],
                        'text': message['text'],
                        'icon': default_icon_path,
                    }
                })
                
            elif message['type'] == 'control':
                # 处理控制命令
                if message['action'] == 'start':
                    await manager.start_story(client_id)
                elif message['action'] == 'pause':
                    manager.stop_story(client_id)
                elif message['action'] == 'stop':
                    manager.stop_story(client_id)
                    # 可以在这里添加额外的停止逻辑
                    
            elif message['type'] == 'edit_message':
                # 处理消息编辑
                edit_data = message['data']
                # 假设 BookWorld 类有一个处理编辑的方法
                manager.bw.handle_message_edit(
                    record_id=edit_data['uuid'],
                    new_text=edit_data['text']
                )
                
            elif message['type'] == 'request_scene_characters':
                manager.bw.select_scene(message['scene'])
                scene_characters = manager.bw.get_characters_info()
                await websocket.send_json({
                    'type': 'scene_characters',
                    'data': scene_characters
                })
                
            elif message['type'] == 'generate_story':
                # 生成故事文本
                story_text = manager.bw.generate_story()
                # 发送生成的故事作为新消息
                await websocket.send_json({
                    'type': 'message',
                    'data': {
                        'username': 'System',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'text': story_text,
                        'icon': default_icon_path,
                        'type': 'story'
                    }
                })
                
            elif message['type'] == 'request_api_configs':
                await websocket.send_json({
                    'type': 'api_configs',
                    'data': API_CONFIGS
                })
                
            elif message['type'] == 'api_settings':
                # 处理API设置
                settings = message['data']
                # 设置环境变量
                os.environ[settings['envKey']] = settings['apiKey']
                
                # 更新BookWorld的设置
                manager.bw.update_api_settings(
                    provider=settings['provider'],
                    model=settings['model']
                )
                
                # 发送确认消息
                await websocket.send_json({
                    'type': 'message',
                    'data': {
                        'username': 'System',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'text': f'已更新 {settings["provider"]} API设置',
                        'icon': default_icon_path,
                        'type': 'system'
                    }
                })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(client_id)

@app.post("/api/save-config")
async def save_config(request: Request):
    global config
    global manager
    try:
        config_data = await request.json()
        # 检查必要字段是否存在
        if 'provider' not in config_data or 'model' not in config_data or 'apiKey' not in config_data:
            raise HTTPException(status_code=400, detail="缺少必要的字段")

        llm_provider = config_data['provider']
        model = config_data['model']
        api_key = config_data['apiKey']
        config['role_llm_name'] = model
        config['world_llm_name'] = model
        if 'openai' in llm_provider.lower():
            os.environ['OPENAI_API_KEY'] = api_key
        elif 'anthropic' in llm_provider.lower():
            os.environ['ANTHROPIC_API_KEY'] = api_key
        elif 'alibaba' in llm_provider.lower():
            os.environ['DASHSCOPE_API_KEY'] = api_key
        elif 'openrouter' in llm_provider.lower():
            os.environ['OPENROUTER_API_KEY'] = api_key
            
        if "preset_path" in config and config["preset_path"] and os.path.exists(config["preset_path"]):
            preset_path = config["preset_path"]
        elif "genre" in config and config["genre"]:
            genre = config["genre"]
            preset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),f"./config/experiment_{genre}.json")
        else:
            raise ValueError("Please set the preset_path in `config.json`.")
        manager.bw = BookWorld(preset_path = preset_path,
                world_llm_name = config["world_llm_name"],
                role_llm_name = config["world_llm_name"])
        manager.bw.set_generator(rounds = config["rounds"], 
                    save_dir = config["save_dir"], 
                    if_save = config["if_save"],
                    mode = config["mode"],
                    scene_mode = config["scene_mode"],)
        return {"status": "success", "message": llm_provider + " 配置已保存"}
    except Exception as e:
        print(f"保存配置失败: {e}")
        raise HTTPException(status_code=500, detail="保存配置失败")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
