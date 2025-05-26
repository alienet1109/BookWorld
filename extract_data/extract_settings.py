import sys
sys.path.append("../")
from bw_utils import *
from extract_utils import *
import os

config = load_json_file("./extract_config.json")

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

lis_settings = [] 
# [{'term':...,'nature':[..],'detail':..,'source':...}]
dic_settings = {}

EXTRACT_SETTINGS_PROMPT = """
Identify the world-building elements and facts reflected in the given text from {source}, 
focusing on unique aspects such as magical systems in fantasy works, levels of technological advancement in science fiction, 
pivotal historical events, cultural consensus... 
Utilize your reasoning skills to uncover the underlying facts hidden beneath the surface.
** Make sure the settings you extract are common to most people in the world **

- Target text:
{text}

Notice that:
1.**Don't include any name, action, status of certain characters**. 
If the character's actions reflect certain social norms or settings, keep only the reflected part.
2.Don't include temporary event or seasonal description like 'It's raining...' or 'It's winter...'
3.Avoid using ambiguous or trival pronouns like 'their','The room'. 
4.Avoid describing specific environment, such as 'The room's small and shabby condition...', 

- If the fact is about an infrequent term or terms, write the extracted fat following this format:
[term](nature):detail
- If the fact contains no certain term, write it with natural language. 
Each extracted fact should be separated by a newline.
"""
if language == 'zh':
    EXTRACT_SETTINGS_PROMPT += """
==Example output(use the same language with the Target text)==
[多斯拉克](民族):多斯拉克文化中，马是重要的象征，战士的地位和成就与他们的骑术密切相关。
[黑暗森林法则](理论):黑暗森林法则是对人类未能发现外星文明的一种假想解释。该假说认为宇宙中存在许多外星文明，但它们都沉默而多疑。该假说假设任何航天文明都会将其他智能生命视为不可避免的威胁，并因此摧毁任何暴露其行踪的新生文明。
在这个世界，在室内打伞被视为一种不吉利的行为。
"""
else:
    EXTRACT_SETTINGS_PROMPT += """
==Example output(use the same language with the Target text)==
[Invisibility Cloak](artifact):Invisibility Cloak grants the wearer complete invisibility by concealing them from sight, making it an invaluable tool for stealth and evasion.
In this world, throwing stones into rivers is considered an unlucky symbol.
    """


    
def update_settings(dic,lis,settings,source):
    settings = clear_blank_row(settings)
    for row in settings.split("\n"):
        parsed = parse_fact(row)
        if parsed:
            term,nature,detail = parsed
            if not term:
                lis.append({'term':term,'nature':[nature],'detail':[detail],'source':[source]})
                continue
            if term not in dic:
                dic[term] = {"nature":[nature],
                            "detail":[detail],
                            "source":[source]}
            else:
                if nature not in dic[term]["nature"]:
                    dic[term]["nature"].append(nature)
                if source not in dic[term]["source"]:
                    dic[term]["source"].append(source)
                dic[term]["detail"].append(detail)
        else:
            lis.append({'term':"",'nature':"",'detail':[row],'source':[source]})
        
    return dic,lis


for chapter in data:
    text = chapter['content']
    title = chapter['title']
    idx = chapter["idx"]
    print(idx)
    if language == 'en':
        chunks = split_text_by_max_words(text,max_words=2000)
    else:
        chunks = split_text_by_max_words(text,max_words=4000)
    for chunk in chunks:
        prompt = EXTRACT_SETTINGS_PROMPT.format(**{
            "text":chunk,
            "source":book_source
        })
        output = clear_blank_row(llm.chat(prompt))
        print(output)
        dic_settings,lis_settings = update_settings(dic_settings, lis_settings, output,f"{idx}_{title}")

dic_settings2 = dict(sorted(dic_settings.items(), key=lambda x:x[0]))
lis_settings2 = lis_settings
for term in dic_settings2:
    value = dic_settings2[term]
    nature = value["nature"]
    detail = value["detail"]
    source = value["source"]
    lis_settings2.append({'term':term, 'nature':nature, 'detail':detail,'source':source})
    
    
path = f"./worlds/{book_source}/world_details/{book_source}.jsonl"
save_jsonl_file(path,lis_settings2)
print(f"Extaction on {book_source} has finished. The extracted settings have been saved to", path)