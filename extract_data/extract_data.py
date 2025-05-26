import sys
sys.path.append("../")
from bw_utils import *
from extract_utils import *
import os
import json

config = load_json_file("./extract_config.json")


target_character_names = config["target_character_names"] if "target_character_names" in config else []
target_location_names = config["target_location_names"] if "target_location_names" in config else []
book_path = config["book_path"]
book_name = os.path.basename(book_path).split(".")[0]
language = config["language"] if config["language"] else lang_detect(book_name)
book_source = config["book_source"] if config["book_source"] else book_name
print(language,book_source)
for key in config:
    if "API_KEY" in key and config[key]:
        os.environ[key] = config[key]

llm = get_models(config["llm_model_name"])
data = get_chapters(book_path) # chapters = [{"idx":"","title":"","content":""}]

def get_default_character_info(role_name,language,other_role_names):
    default_character_info = {
    "role_name": role_name,
    "role_code": convert_name_to_code(role_name,language),
    "source": book_source,
    "profile": "",
    "activity":1,
    "nickname": role_name,
    "relation": {convert_name_to_code(role_name,language):{
        "relation":[], 
        "detail":"" } for role_name in other_role_names}
    }
    return default_character_info

def get_defaule_location_info(location_name,language):
    default_location_info = {
        "location_name": location_name,
        "location_code": convert_name_to_code(location_name,language),
        "description": "",
        "detail": "",
    }
    return default_location_info

def process_character_chunk(chunk, character_name, language):
    prompt = f"""Analyze the following text and extract information about {character_name}. 
    Focus on their personality, background, and key characteristics.
    If the text doesn't contain relevant information about {character_name}, respond with 'NO_INFO'.
    
    Text:
    {chunk}
    
    Provide a concise summary of the character's profile."""
    
    response = llm.chat(prompt)
    if response.strip() != 'NO_INFO':
        return response.strip()
    return None

def process_character_relation(chunk, char1, char2, language):
    prompt = f"""Analyze the relationship between {char1} and {char2} in the following text.
    Focus on their interaction, feelings towards each other, and relationship dynamics.
    If the text doesn't contain relevant information about their relationship, respond with 'NO_INFO'.
    
    Text:
    {chunk}
    
    Provide a concise description of their relationship."""
    
    response = llm.chat(prompt)
    if response.strip() != 'NO_INFO':
        return response.strip()
    return None

def process_location_chunk(chunk, location_name, language):
    prompt = f"""Analyze the following text and extract information about {location_name}.
    Focus on its physical description, significance, and key features.
    If the text doesn't contain relevant information about {location_name}, respond with 'NO_INFO'.
    
    Text:
    {chunk}
    
    Provide a concise description of the location."""
    
    response = llm.chat(prompt)
    if response.strip() != 'NO_INFO':
        return response.strip()
    return None

def update_character_info(character_name, new_profile):
    if character_name not in target_characters_info:
        target_characters_info[character_name] = get_default_character_info(
            character_name, language, [name for name in target_character_names if name != character_name]
        )
    
    if new_profile:
        current_profile = target_characters_info[character_name]["profile"]
        if current_profile:
            target_characters_info[character_name]["profile"] = current_profile + "\n" + new_profile
        else:
            target_characters_info[character_name]["profile"] = new_profile

def update_character_relation(char1, char2, new_relation):
    if new_relation:
        char1_code = convert_name_to_code(char1, language)
        char2_code = convert_name_to_code(char2, language)
        
        if char1 not in target_characters_info:
            target_characters_info[char1] = get_default_character_info(
                char1, language, [name for name in target_character_names if name != char1]
            )
        
        current_relation = target_characters_info[char1]["relation"][char2_code]["detail"]
        if current_relation:
            target_characters_info[char1]["relation"][char2_code]["detail"] = current_relation + "\n" + new_relation
        else:
            target_characters_info[char1]["relation"][char2_code]["detail"] = new_relation

def update_location_info(location_name, new_description):
    if location_name not in target_locations_info:
        target_locations_info[location_name] = get_defaule_location_info(location_name, language)
    
    if new_description:
        current_description = target_locations_info[location_name]["description"]
        if current_description:
            target_locations_info[location_name]["description"] = current_description + "\n" + new_description
        else:
            target_locations_info[location_name]["description"] = new_description



def ensure_dir(path):
    """Ensure directory exists, create if not"""
    if not os.path.exists(path):
        os.makedirs(path)

def save_role_info(role_info):
    """Save individual role information to specified path"""
    role_code = role_info["role_code"]
    role_dir = f"./data/roles/{book_source}/{role_code}"
    ensure_dir(role_dir)
    
    role_path = f"{role_dir}/role_info.json"
    save_json_file(role_path, role_info)
    return role_path

def save_location_info(locations_info):
    """Save all location information to specified path"""
    location_dir = f"./data/locations"
    ensure_dir(location_dir)
    
    location_path = f"{location_dir}/{book_source}.json"
    save_json_file(location_path, locations_info)
    return location_path



def save_json_file(path, data):
    """Save data as JSON file"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_main_characters(text, language):
    """Extract main characters from the text using LLM"""
    prompt = f"""Analyze the following text and identify the main characters.
    Focus on characters who:
    1. Appear frequently throughout the story
    2. Have significant impact on the plot
    3. Are central to the narrative
    
    For each character, provide their name and a brief reason why they are important.
    Format: name: reason
    
    Text:
    {text}
    
    List the main characters (maximum 10):"""
    
    response = llm.chat(prompt)
    characters = []
    for line in response.strip().split('\n'):
        if ':' in line:
            name = line.split(':')[0].strip()
            characters.append(name)
    return characters

def extract_key_locations(text, language):
    """Extract key locations from the text using LLM"""
    prompt = f"""Analyze the following text and identify the key locations.
    Focus on places that:
    1. Are frequently mentioned
    2. Have significant importance to the story
    3. Are central to the plot
    
    For each location, provide its name and a brief reason why it is important.
    Format: name: reason
    
    Text:
    {text}
    
    List the key locations (maximum 10):"""
    
    response = llm.chat(prompt)
    locations = []
    for line in response.strip().split('\n'):
        if ':' in line:
            name = line.split(':')[0].strip()
            locations.append(name)
    return locations

def process_large_text(text, max_length=10000):
    """Process large text by splitting into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        if end >= len(text):
            chunks.append(text[start:])
            break
        # Find the last period or newline before max_length
        last_period = text.rfind('.', start, end)
        last_newline = text.rfind('\n', start, end)
        split_point = max(last_period, last_newline)
        if split_point == -1:
            split_point = end
        chunks.append(text[start:split_point + 1])
        start = split_point + 1
    return chunks

def auto_extract_targets():
    """Automatically extract target characters and locations from the book"""
    print("Starting automatic extraction of main characters and locations...")
    
    # Combine all chapter contents
    full_text = ""
    for chapter in data:
        full_text += chapter['content'] + "\n"
    
    # Process text in chunks to handle context limits
    text_chunks = process_large_text(full_text)
    
    # Extract characters and locations from each chunk
    all_characters = set()
    all_locations = set()
    
    for chunk in text_chunks:
        characters = extract_main_characters(chunk, language)
        locations = extract_key_locations(chunk, language)
        all_characters.update(characters)
        all_locations.update(locations)
    
    # Convert sets to lists
    target_character_names = list(all_characters)
    target_location_names = list(all_locations)
    
    print(f"Extracted {len(target_character_names)} main characters and {len(target_location_names)} key locations")
    return target_character_names, target_location_names


if __name__ == "__main__":
    target_characters_info = {}
    target_locations_info = {}
    # default character and location info
    if not target_character_names or not target_location_names:
        print("No target characters or locations specified. Starting automatic extraction...")
        target_character_names, target_location_names = auto_extract_targets()
        
        # Update config with extracted targets
        config["target_character_names"] = target_character_names
        config["target_location_names"] = target_location_names
        save_json_file("./extract_config.json", config)
        
        print("Updated config file with extracted targets")
        print(target_character_names,target_location_names)
    
    # main
    for chapter in data:
        text = chapter['content']
        if language == 'en':
            chunks = split_text_by_max_words(text, max_words=2000)
        else:
            chunks = split_text_by_max_words(text, max_words=4000)
        
        for chunk in chunks:
            # Profile
            for character in target_character_names:
                if character in chunk:
                    new_profile = process_character_chunk(chunk, character, language)
                    update_character_info(character, new_profile)
            # Relation
            for i, char1 in enumerate(target_character_names):
                for char2 in target_character_names[i+1:]:
                    if char1 in chunk and char2 in chunk:
                        char1_pos = chunk.find(char1)
                        char2_pos = chunk.find(char2)
                        if abs(char1_pos - char2_pos) <= 100:
                            new_relation = process_character_relation(chunk, char1, char2, language)
                            update_character_relation(char1, char2, new_relation)
            # Location
            for location in target_location_names:
                if location in chunk:
                    new_description = process_location_chunk(chunk, location, language)
                    update_location_info(location, new_description)
                    
    # Replace the original save results section
    print("Starting to save extracted data...")

    # Save role information
    for role_info in target_characters_info.values():
        role_path = save_role_info(role_info)
        print(f"Role information saved: {role_path}")

    # Save location information
    location_path = save_location_info(target_locations_info)
    print(f"Location information saved: {location_path}")

    print(f"Data extraction completed!")
    print(f"Role information saved to ./data/roles/{book_source}/")
    print(f"Location information saved to {location_path}")