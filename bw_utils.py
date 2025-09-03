import os
import pickle
import json
import logging
import datetime
import re
import random
import base64

MODEL_NAME_DICT = {
    "gpt-3.5":"openai/gpt-3.5-turbo",
    "gpt-4":"openai/gpt-4",
    "gpt-4o":"openai/gpt-4o",
    "gpt-4o-mini":"openai/gpt-4o-mini",
    "gpt-3.5-turbo":"openai/gpt-3.5-turbo",
    "deepseek-r1":"deepseek/deepseek-r1",
    "deepseek-v3":"deepseek/deepseek-chat",
    "gemini-2.0-flash":"google/gemini-2.0-flash-001",
    "gemini-1.5-flash":"google/gemini-flash-1.5",
    "llama3-70b": "meta-llama/llama-3.3-70b-instruct",
    "qwen-turbo":"qwen/qwen-turbo",
    "qwen-plus":"qwen/qwen-plus",
    "qwen-max":"qwen/qwen-max",
    "qwen-2.5-72b":"qwen/qwen-2.5-72b-instruct",
    "claude-3.5-haiku": "anthropic/claude-3.5-haiku",
    "claude-3.5-sonnet":"anthropic/claude-3.5-sonnet",
    "claude-3.7-sonnet":"anthropic/claude-3.7-sonnet",
    "phi-4":"microsoft/phi-4",
}

def get_models(model_name):
    if os.getenv("OPENROUTER_API_KEY", default="") and model_name in MODEL_NAME_DICT:
        from modules.llm.OpenRouter import OpenRouter
        return OpenRouter(model=MODEL_NAME_DICT[model_name])
    elif model_name.startswith('gpt'):
        from modules.llm.LangChainGPT import LangChainGPT
        if model_name.startswith('gpt-3.5'):
            return LangChainGPT(model="gpt-3.5-turbo")
        elif model_name == 'gpt-4' or model_name == 'gpt-4-turbo':
            return LangChainGPT(model="gpt-4")
        elif model_name == 'gpt-4o':
            return LangChainGPT(model="gpt-4o")
        elif model_name == "gpt-4o-mini":
            return LangChainGPT(model="gpt-4o-mini")
    elif model_name.startswith("claude"):
        from modules.llm.Claude import Claude
        if model_name.startswith("claude-3.5-sonnet"):
            return Claude(model="claude-3-5-sonnet-latest")
        elif model_name.startswith("claude-3.7-sonnet"):
            return Claude(model="claude-3-7-sonnet-latest")
        elif model_name.startswith("claude-3.5-haiku"):
            return Claude(model="claude-3-5-haiku-latest")
        return Claude()
    elif model_name.startswith('qwen'):
        from modules.llm.Qwen import Qwen
        return Qwen(model = model_name)
    elif model_name.startswith('deepseek'):
        from modules.llm.DeepSeek import DeepSeek
        return DeepSeek(model = model_name)
    elif model_name.startswith('doubao'):
        from modules.llm.Doubao import Doubao
        return Doubao()
    elif model_name.startswith('gemini'):
        from modules.llm.Gemini import Gemini
        if model_name.startswith('gemini-2.0'):
            return Gemini(model="gemini-2.0-flash")
        elif model_name.startswith('gemini-1.5'):
            return Gemini(model="gemini-1.5-flash")
        elif model_name.startswith('gemini-2.5-flash'):
            return Gemini(model="gemini-2.5-flash-preview-04-17")
        elif model_name.startswith('gemini-2.5-pro'):
            return Gemini(model="gemini-2.5-pro-preview-05-06")
        return Gemini()
    else:
        print(f'Warning! undefined model {model_name}, use gpt-4o-mini instead.')
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT()
    
def build_world_agent_data(world_file_path,max_words = 30):
    world_dir = os.path.dirname(world_file_path)
    details_dir = os.path.join(world_dir,"./world_details")
    data = []
    settings = []
    if os.path.exists(details_dir):
        for path in get_child_paths(details_dir):
            if os.path.splitext(path)[-1] == ".txt":
                text = load_text_file(path)
                data += split_text_by_max_words(text,max_words)
            if os.path.splitext(path)[-1] == ".jsonl":
                jsonl = load_jsonl_file(path)
                data += [f"{dic['term']}:{dic['detail']}" for dic in jsonl]
                settings += jsonl
    return data,settings

def build_db(data, db_name, db_type, embedding, save_type="persistent"):
    if not data or not db_name:
        return None
    if True:
        from modules.db.ChromaDB import ChromaDB
        db = ChromaDB(embedding,save_type)
        db_name = db_name
        db.init_from_data(data,db_name)
    return db

def get_root_dir():
    current_file_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(current_file_path)
    return root_dir

def create_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def get_logger(experiment_name):
    logger = logging.getLogger(experiment_name)
    logger.setLevel(logging.INFO)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    create_dir(f"{get_root_dir()}/log/{experiment_name}")
    file_handler = logging.FileHandler(os.path.join(get_root_dir(),f"./log/{experiment_name}/{current_time}.log"),encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    # Avoid logging duplication
    logger.propagate = False

    return logger

def merge_text_with_limit(text_list, max_words, language = 'en'):
    """
    Merge a list of text strings into one, stopping when adding another text exceeds the maximum count.

    Args:
        text_list (list): List of strings to be merged.
        max_count (int): Maximum number of characters (for Chinese) or words (for English).
        is_chinese (bool): If True, count Chinese characters; if False, count English words.

    Returns:
        str: The merged text, truncated as needed.
    """
    merged_text = ""
    current_count = 0

    for text in text_list:
        if language == 'zh':
            # Count Chinese characters
            text_length = len(text)
        else:
            # Count English words
            text_length = len(text.split(" "))

        if current_count + text_length > max_words:
            break

        merged_text += text + "\n"
        current_count += text_length

    return merged_text

def normalize_string(text):
    # 去除空格并将所有字母转为小写
    import re
    return re.sub(r'[\s\,\;\t\n]+', '', text).lower()

def fuzzy_match(str1, str2, threshold=0.8):
    str1_normalized = normalize_string(str1)
    str2_normalized = normalize_string(str2)

    if str1_normalized == str2_normalized:
        return True

    return False

def load_character_card(path):
    from PIL import Image
    import PIL.PngImagePlugin
    
    image = Image.open(path)
    if isinstance(image, PIL.PngImagePlugin.PngImageFile):
        for key, value in image.text.items():
            try:
                character_info = json.loads(decode_base64(value))
                if character_info:
                    return character_info
            except:
                continue
    return None

def decode_base64(encoded_string):
    # Convert the string to bytes if it's not already
    if isinstance(encoded_string, str):
        encoded_bytes = encoded_string.encode('ascii')
    else:
        encoded_bytes = encoded_string

    # Decode the Base64 bytes
    decoded_bytes = base64.b64decode(encoded_bytes)

    # Try to convert the result to a string, assuming UTF-8 encoding
    try:
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except UnicodeDecodeError:
        # If it's not valid UTF-8 text, return the raw bytes
        return decoded_bytes
    
def remove_list_elements(list1, *args):
    for target in args:
        if isinstance(target,list) or isinstance(target,dict):
            list1 = [i for i in list1 if i not in target]
        else:
            list1 = [i for i in list1 if i != target]
    return list1

def extract_html_content(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    content_div = soup.find("div", {"id": "content"})
    if not content_div:
        return ""

    paragraphs = []
    for div in content_div.find_all("div"):
        paragraphs.append(div.get_text(strip=True))
    
    main_content = "\n\n".join(paragraphs)
    return main_content

def load_text_file(path):
    with open(path,"r",encoding="utf-8") as f:
        text = f.read()
    return text

def save_text_file(path,target):
    with open(path,"w",encoding="utf-8") as f:
        text = f.write(target)

def load_json_file(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)
    
def save_json_file(path,target):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(target, f, ensure_ascii=False,indent=True)
        
def load_jsonl_file(path):
    data = []
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data
        
def save_jsonl_file(path,target):
    with open(path, "w",encoding="utf-8") as f:
        for row in target:
            print(json.dumps(row, ensure_ascii=False), file=f)

def split_text_by_max_words(text: str, max_words: int = 30):
    segments = []
    current_segment = []
    current_length = 0
    
    lines = text.splitlines()

    for line in lines:
        words_in_line = len(line)
        current_segment.append(line + '\n')
        current_length += words_in_line
        
        if current_length + words_in_line > max_words:
            segments.append(''.join(current_segment))
            current_segment = []
            current_length = 0

    if current_segment:
        segments.append(''.join(current_segment))

    return segments

def lang_detect(text):
    import re
    def count_chinese_characters(text):
        # 使用正则表达式匹配所有汉字字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars)
            
    if count_chinese_characters(text) > len(text) * 0.05:
        lang = 'zh'
    else:
        lang = 'en'
    return lang

def dict_to_str(dic):
    res = ""
    for key in dic:
        res += f"{key}: {dic[key]};"
    return res

def count_tokens_num(string, encoding_name = "cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

 
def json_parser(output):
    output = output.replace("\n", "")
    output = output.replace("\t", "")
    if "{" not in output:
        output = "{" + output
    if "}" not in output:
        output += "}"  
    pattern = r'\{.*\}'
    matches = re.findall(pattern, output, re.DOTALL)
    try:
        parsed_json = eval(matches[0])
    except:
        try:
            parsed_json = json.loads(matches[0])
            
        except json.JSONDecodeError:
            try:
                detail = re.search(r'"detail":\s*(.+?)\s*}', matches[0]).group(1)
                detail = f"\"{detail}\"" 
                new_output = re.sub(r'"detail":\s*(.+?)\s*}', f"\"detail\":{detail}}}", matches[0])
                parsed_json = json.loads(new_output)
            except Exception as e:
                raise ValueError("No valid JSON found in the input string")
    return parsed_json

def action_detail_decomposer(detail):
    thoughts = re.findall(r'【(.*?)】', detail)
    actions = re.findall(r'（(.*?)）', detail)
    dialogues = re.findall(r'「(.*?)」', detail)
    return thoughts,actions,dialogues

def conceal_thoughts(detail):
    text = re.sub(r'【.*?】', '', detail)
    text = re.sub(r'\[.*?\]', '', text)
    return text

def extract_first_number(text):
    match = re.search(r'\b\d+(?:\.\d+)?\b', text)
    return int(match.group()) if match else None

def check_role_code_availability(role_code,role_file_dir):
    for path in get_grandchild_folders(role_file_dir):
        if role_code in path:
            return True
    return False
    
def get_grandchild_folders(root_folder, if_full = True):
    folders = []
    for resource in os.listdir(root_folder):
        subpath = os.path.join(root_folder,resource)
        for folder_name in os.listdir(subpath):
            folder_path = os.path.join(subpath, folder_name)
            if if_full:
                folders.append(folder_path)
            else:
                folders.append(folder_name)
    
    return folders

def get_child_folders(root_folder, if_full = True):
    folders = []
    for resource in os.listdir(root_folder):
        if if_full:
            path = os.path.join(root_folder,resource)
            if os.path.isdir(path):
                folders.append(path)
        else:
            path = resource
            if os.path.isdir(os.path.join(root_folder, path)):
                folders.append(path)
    return folders

def get_child_paths(root_folder, if_full = True):
    paths = []
    for resource in os.listdir(root_folder):
        if if_full:
            path = os.path.join(root_folder,resource)
            if os.path.isfile(path):
                paths.append(path)
        else:
            path = resource
            if os.path.isfile(os.path.join(root_folder, path)):
                paths.append(path)
    return paths

def get_first_directory(path):
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                return full_path
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def find_files_with_suffix(directory, suffix):
    matched_files = []
    for root, dirs, files in os.walk(directory):  # 遍历目录及其子目录
        for file in files:
            if file.endswith(suffix):  # 检查文件后缀
                matched_files.append(os.path.join(root, file))  # 将符合条件的文件路径加入列表

    return matched_files

def remove_element_with_probability(lst, threshold=3, probability=0.2):
    # 确保列表不为空
    if len(lst) > threshold and random.random() < probability:
        # 随机选择一个元素的索引
        index = random.randint(0, len(lst) - 1)
        # 删除该索引位置的元素
        lst.pop(index)
    return lst
  
def count_token_num(text):
    from transformers import GPT2TokenizerFast
    tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
    return len(tokenizer.encode(text))

def get_cost(model_name,prompt,output):
    input_price=0
    output_price=0
    if model_name.startswith("gpt-4"):
        input_price=10
        output_price=30
    elif model_name.startswith("gpt-3.5"):
        input_price=0.5
        output_price=1.5
    
    return input_price*count_token_num(prompt)/1000000 + output_price * count_token_num(output)/1000000

def is_image(filepath):
    if not os.path.isfile(filepath):
        return False

    valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff','.webp']
    file_extension = os.path.splitext(filepath)[1].lower()

    # 判断扩展名是否在有效图片扩展名列表中
    if file_extension in valid_image_extensions:
        return True

    return False

def clean_collection_name(name: str) -> str:
    cleaned_name = name.replace(' ', '_')
    cleaned_name = cleaned_name.replace('.', '_')
    if not all(ord(c) < 128 for c in cleaned_name):
        encoded = base64.b64encode(cleaned_name.encode('utf-8')).decode('ascii')
        encoded = encoded[:60] if len(encoded) > 60 else encoded
        valid_name = f"mem_{encoded}"
    else:
        valid_name = cleaned_name
    valid_name = re.sub(r'[^a-zA-Z0-9_-]', '-', valid_name)
    valid_name = re.sub(r'\.\.+', '-', valid_name)
    valid_name = re.sub(r'^[^a-zA-Z0-9]+', '', valid_name)  # 移除开头非法字符
    valid_name = re.sub(r'[^a-zA-Z0-9]+$', '', valid_name)
    valid_name = valid_name[:60]
    return valid_name
    
cache_sign = True
cache = None 
def cached(func):
    def wrapper(*args,**kwargs):
        global cache
        cache_path = "bw_cache.pkl"
        if cache == None:
            if not os.path.exists(cache_path):
                cache = {}
            else:
                cache = pickle.load(open(cache_path, 'rb'))
        key = (func.__name__, str([args[0].role_code, args[0].__class__, args[0].llm_name , args[0].history]), str(kwargs.items()))
        if (cache_sign and key in cache and cache[key] not in [None, '[TOKEN LIMIT]']) :
            return cache[key]
        else:
            result = func(*args, **kwargs)
            if result != 'busy' and result != None:
                cache[key] = result
                pickle.dump(cache, open(cache_path, 'wb'))
            return result
    return wrapper