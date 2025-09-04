import sys
from collections import defaultdict
sys.path.append("../")
import os
from typing import Any, Dict, List, Optional, Literal
from modules.embedding import get_embedding_model
from modules.memory import build_role_agent_memory
from modules.history_manager import HistoryManager
from bw_utils import *
import random
import warnings
warnings.filterwarnings("ignore")



class RPAgent:
    def __init__(self, 
                 role_code: str,
                 role_file_dir: str,
                 world_file_path: str,
                 source: str = "",
                 language: str = "en",
                 db_type: str = "chroma",
                 llm_name: str = "gpt-4o-mini",
                 llm = None,
                 embedding_name: str = "bge-small",
                 embedding = None
                 ):
        super(RPAgent, self).__init__()
        self.language: str  = language
        self.role_code: str = role_code
        
        self.history_manager = HistoryManager()
        self.prompts: List[Dict] = []
        self.acted: bool = False
        self.status: str = ""
        self.goal: str = ""
        self.location_code: str = ""
        self.location_name: str = ""
        self.motivation: str = ""
        
        self._init_from_file(role_code, role_file_dir, world_file_path, source)
        self._init_prompt()
        
        self.llm_name = llm_name
        if llm == None:
            llm = get_models(llm_name)
        self.llm = llm
        
        if embedding is None:
            embedding = get_embedding_model(embedding_name, language=self.language)
        
        self.db_name = clean_collection_name(f"role_{role_code}_{embedding_name}")
        self.db = build_db(data = self.role_data,
                           db_name = self.db_name,
                           db_type = db_type,
                           embedding = embedding)
        self.world_db = None
        self.world_db_name = ""
        self.memory = build_role_agent_memory(llm_name=llm_name,
                                              embedding_name = embedding_name,
                                              embedding = embedding,
                                              db_name = self.db_name.replace("role","memory"),
                                              language = self.language,
                                              type="naive"
                                              )
        
    def _init_prompt(self):
        if self.language == 'zh':
            from modules.prompt.role_agent_prompt_zh \
                import ROLE_PLAN_PROMPT,ROLE_SINGLE_ROLE_RESPONSE_PROMPT,ROLE_MULTI_ROLE_RESPONSE_PROMPT,ROLE_SET_GOAL_PROMPT,INTERVENTION_PROMPT,UPDATE_GOAL_PROMPT,UPDATE_STATUS_PROMPT,ROLE_SET_MOTIVATION_PROMPT,SCRIPT_ATTENTION_PROMPT,ROLE_MOVE_PROMPT,SUMMARIZE_PROMPT,ROLE_NPC_RESPONSE_PROMPT
            
        else:
            from modules.prompt.role_agent_prompt_en \
                import ROLE_PLAN_PROMPT,ROLE_SINGLE_ROLE_RESPONSE_PROMPT,ROLE_MULTI_ROLE_RESPONSE_PROMPT,ROLE_SET_GOAL_PROMPT,INTERVENTION_PROMPT,UPDATE_GOAL_PROMPT,UPDATE_STATUS_PROMPT,ROLE_SET_MOTIVATION_PROMPT,SCRIPT_ATTENTION_PROMPT,ROLE_MOVE_PROMPT,SUMMARIZE_PROMPT,ROLE_NPC_RESPONSE_PROMPT
        self._ROLE_SET_GOAL_PROMPT = ROLE_SET_GOAL_PROMPT
        self._ROLE_PLAN_PROMPT = ROLE_PLAN_PROMPT
        self._ROLE_SINGLE_ROLE_RESPONSE_PROMPT = ROLE_SINGLE_ROLE_RESPONSE_PROMPT
        self._ROLE_MULTI_ROLE_RESPONSE_PROMPT = ROLE_MULTI_ROLE_RESPONSE_PROMPT
        self._INTERVENTION_PROMPT = INTERVENTION_PROMPT
        self._UPDATE_GOAL_PROMPT = UPDATE_GOAL_PROMPT
        self._UPDATE_STATUS_PROMPT = UPDATE_STATUS_PROMPT
        self._ROLE_SET_MOTIVATION_PROMPT = ROLE_SET_MOTIVATION_PROMPT
        self._SCRIPT_PROMPT = SCRIPT_ATTENTION_PROMPT
        self._ROLE_MOVE_PROMPT = ROLE_MOVE_PROMPT
        self._SUMMARIZE_PROMPT = SUMMARIZE_PROMPT
        self._ROLE_NPC_RESPONSE_PROMPT = ROLE_NPC_RESPONSE_PROMPT
            
    def _init_from_file(self, 
                        role_code: str, 
                        role_file_dir: str, 
                        world_file_path: str,
                        source:str):
        if source and os.path.exists(os.path.join(role_file_dir, source)):
            for path in get_child_folders(os.path.join(role_file_dir, source)):
                if role_code in path:
                    role_path = path
                    break
        else:
            for path in get_grandchild_folders(role_file_dir):
                if role_code in path:
                    role_path = path
                    break
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        role_profile_path = os.path.join(base_dir, role_path,"role_info.json")
        
        role_info = load_json_file(role_profile_path)
        # self.role_info = role_info
        self.role_profile: str = role_info['profile']
        self.nickname: str = role_info["nickname"]
        self.role_name: str = role_info["role_name"]
        self.relation: str = role_info["relation"]
        self.motivation: str = role_info["motivation"] if "motivation" in role_info else ""
        
        self.activity: float = float(role_info["activity"]) if "activity" in role_info else 1.0
        self.icon_path: str = os.path.join(base_dir, role_path,"icon.png")
        self.avatar_path: str = os.path.join(base_dir, role_path,"avatar.png")
        for image_type in ['jpg','png','bmp']:
            if os.path.exists(os.path.join(base_dir, role_path,f"./avatar.{image_type}")):
                self.avatar_path: str = os.path.join(base_dir, role_path,f"avatar.{image_type}")
            if os.path.exists(os.path.join(base_dir, role_path,f"./icon.{image_type}")):
                self.icon_path: str = os.path.join(base_dir, role_path,f"icon.{image_type}")

        self.role_data: List[str] = build_role_agent_data(os.path.join(base_dir, role_path))
        
    # Agent
    def set_motivation(self, 
                       world_description: str, 
                       other_roles_info: Dict[str, Any], 
                       intervention: str = "", 
                       script: str = ""):
        if self.motivation:
            return self.motivation
        other_roles_info_text = self.get_other_roles_info_text(other_roles_info)
        prompt = self._ROLE_SET_MOTIVATION_PROMPT.format(**
            {
                "role_name": self.role_name,
                "profile":self.role_profile,
                "world_description": world_description,
                "other_roles_description": other_roles_info_text,
                "location": self.location_name
            })  
        if script:
            script = self._SCRIPT_PROMPT.format(**
                {"script": script}
            )  
            prompt = prompt + script
        elif intervention:
            intervention = self._INTERVENTION_PROMPT.format(**
                {"intervention": intervention}
            )
            prompt = intervention + prompt + "\n**注意: 在你的动机中考虑全局事件的影响**" if self.language == "zh" else intervention + prompt + "\n**Notice that: You should take the global event into consideration.**"
        
        motivation = self.llm.chat(prompt)
        self.save_prompt(prompt = prompt, detail = motivation)
        self.motivation = motivation
        return motivation
    
    def plan(self, 
             other_roles_info: Dict[str, Any], 
             available_locations: List[str], 
             world_description: str, 
             intervention: str = ""):
        action_history_text = self.retrieve_history(query = "", retrieve=False)
        references = self.retrieve_references(query = action_history_text)
        knowledges = self.retrieve_knowledges(query = action_history_text)
        
        if len(other_roles_info) == 1:
            other_roles_info_text = "没有人在这里。你不能进行涉及角色的互动。" if self.language == "zh" else "No one else is here. You can not interact with roles."
        else:
            other_roles_info_text = self.get_other_roles_info_text(other_roles_info, if_profile = False)
        
        if intervention:
            intervention = self._INTERVENTION_PROMPT.format(**
                {"intervention": intervention}
            )
        prompt = self._ROLE_PLAN_PROMPT.format(**
            {
                "role_name": self.role_name,
                "nickname": self.nickname,
                "profile": self.role_profile,
                "goal": self.goal,
                "status": self.status,
                "history": action_history_text,
                "other_roles_info": other_roles_info_text,
                "world_description": world_description,
                "location": self.location_name,
                "references": references,
                "knowledges":knowledges,
            }
        )
        prompt = intervention + prompt
        max_tries = 3
        plan = {"action": "待机" if self.language == "zh" else "Stay", 
                "destination": None,
                "interact_type":'no',
                "target_role_codes": [],
                "target_npc_name":None,
                "detail": f"{self.role_name}原地不动，观察情况。" if self.language == "zh" else f"{self.role_name} stays put."
                }
        
        for i in range(max_tries):
            response = self.llm.chat(prompt)
            try:
                plan.update(json_parser(response))
                break
            except Exception as e:
                print(self.role_name)
                print(f"Parsing failure! {i+1}th tries. Error:", e)   
                print(response)
        plan["role_code"] = self.role_code
        self.save_prompt(detail=plan["detail"],
                      prompt=prompt)
        return plan
    
    def npc_interact(self,
                     npc_name:str,
                     npc_response:str,
                     history:str,
                     intervention:str = ""
                     ):
        references = self.retrieve_references(npc_response)
        knowledges = self.retrieve_knowledges(query = npc_response)
        
        if intervention:
            intervention = self._INTERVENTION_PROMPT.format(**
                {"intervention": intervention}
            )
        prompt = self._ROLE_NPC_RESPONSE_PROMPT.format(**
            {
                "role_name": self.role_name,
                "nickname": self.nickname,
                "profile": self.role_profile,
                "goal": self.goal,
                "npc_name":npc_name,
                "npc_response":npc_response,
                "references": references,
                "knowledges":knowledges,
                "dialogue_history": history
            }
            )
        prompt = intervention + prompt
        interaction = {
                    "if_end_interaction": True,
                    "detail": "",
                    }
        response = self.llm.chat(prompt)
        interaction.update(json_parser(response))
        self.save_prompt(detail = interaction["detail"], 
                      prompt = prompt)
        return interaction
    
    def single_role_interact(self, 
                             action_maker_code: str, 
                             action_maker_name: str,
                             action_detail: str, 
                             action_maker_profile: str, 
                             intervention: str = ""):
        references = self.retrieve_references(action_detail)
        history = self.retrieve_history(query = action_detail)
        knowledges = self.retrieve_knowledges(query = action_detail)
        
        relation = f"role_code:{action_maker_code}\n" + self.search_relation(action_maker_code)
        
        if intervention:
            intervention = self._INTERVENTION_PROMPT.format(**
                {"intervention": intervention}
            )
        prompt = self._ROLE_SINGLE_ROLE_RESPONSE_PROMPT.format(**
            {
                "role_name": self.role_name,
                "nickname": self.nickname,
                "action_maker_name": action_maker_name,
                "action_detail": action_detail, 
                "profile": self.role_profile,
                "action_maker_profile": action_maker_profile,
                "relation": relation,
                "goal": self.goal,
                "status": self.status,
                "references": references,
                "knowledges":knowledges,
                "history": history
            }
            )
        prompt = intervention + prompt
        
        max_tries = 3
        interaction = {
                    "if_end_interaction": True,
                    "extra_interact_type":"no",
                    "target_npc_name":"",
                    "detail": "",
                    }
        
        for i in range(max_tries):
            response = self.llm.chat(prompt) 
            try:
                interaction.update(json_parser(response))
                break
            except Exception as e:
                print(f"Parsing failure! {i}th tries. Error:", e)    
                print(response)
        
        self.save_prompt(detail = interaction["detail"], 
                      prompt = prompt)
        return interaction
    
    def multi_role_interact(self, 
                            action_maker_code: str, 
                            action_maker_name: str, 
                            action_detail: str, 
                            action_maker_profile: str, 
                            other_roles_info: Dict[str, Any], 
                            intervention: str = ""):
        references = self.retrieve_references(query = action_detail)
        history = self.retrieve_history(query = action_detail)
        knowledges = self.retrieve_knowledges(query = action_detail)
        
        other_roles_info_text = self.get_other_roles_info_text(other_roles_info, if_profile = False)

        if intervention:
            intervention = self._INTERVENTION_PROMPT.format(**
                {"intervention": intervention}
            )
        prompt = self._ROLE_MULTI_ROLE_RESPONSE_PROMPT.format(**
            {
                "role_name": self.role_name,
                "nickname": self.nickname,
                "action_maker_name": action_maker_name,
                "action_detail": action_detail, 
                "profile": self.role_profile,
                "action_maker_profile": action_maker_profile,
                "other_roles_info":other_roles_info_text,
                "goal":self.goal,
                "status": self.status,
                "references": references,
                "knowledges":knowledges,
                "history": history
            }
            )
        prompt = intervention + prompt
        max_tries = 3
        interaction = {
                    "if_end_interaction": True,
                    "extra_interact_type":"no",
                    "target_role_code":"",
                    "target_npc_name":"",
                    "visible_role_codes":[],
                    "detail": "",
                    }
        
        for i in range(max_tries):
            response = self.llm.chat(prompt) 
            try:
                interaction.update(json_parser(response))
                break
            except Exception as e:
                print(f"Parsing failure! {i}th tries. Error:", e)    
                print(response)
        self.save_prompt(detail = interaction["detail"], prompt=prompt)
        return interaction
    
    def update_status(self,):
        prompt = self._UPDATE_STATUS_PROMPT.format(**{
            "role_name":self.role_name,
            "status":self.status,
            "history_text":self.retrieve_history(query=""),
            "activity":self.activity
        })
        max_tries = 3
        for i in range(max_tries):
            response = self.llm.chat(prompt) 
            try:
                status = json_parser(response)
                self.status = status["updated_status"]
                self.activity = float(status["activity"])
                break
            except Exception as e:
                print(f"Parsing failure! {i}th tries. Error:", e)    
                print(response)
        
        return
    
    def update_goal(self,other_roles_status: str,instruction: str = ""):
        motivation = self.motivation
        if instruction:
            motivation = instruction
        history = self.retrieve_history(self.motivation)
        if len(history) == 0:
            self.goal = motivation
            return motivation
        
        prompt = self._UPDATE_GOAL_PROMPT.format(**{
            "history":history,
            "motivation":motivation,
            "goal":self.goal,
            "other_roles_status":other_roles_status,
            "location":self.location_name
        })
        response = self.llm.chat(prompt) 
        try:
            new_plan = json_parser(response)
            if new_plan["if_change_goal"]:
                goal = new_plan["updated_goal"]
                self.save_prompt(prompt,response)
                self.goal = goal
                return goal
        except Exception as e:
            print(self.role_name)
            print(f"Parsing failure! Error:", e)    
            print(response)
        return ""
    
    def move(self, 
             locations_info_text: str, 
             locations_info: Dict[str, Any]):
        history_text = self.retrieve_history(query="")
        prompt = self._ROLE_MOVE_PROMPT.format(**{
            "role_name":self.role_name,
            "profile": self.role_profile,
            "goal":self.goal,
            "status":self.status,
            "history":history_text,
            "location":self.location_name,
            "locations_info_text":locations_info_text
            
        })
        response= self.llm.chat(prompt)
        try:
            result = json_parser(response)
            if result["if_move"] and "destination_code" in result and result["destination_code"] in locations_info and result["destination_code"] != self.location_code:
                destination_code = result["destination_code"]
                self.save_prompt(detail = result["detail"],
                              prompt = prompt)
                return True, result["detail"], destination_code
        except Exception as e:
            print(f"Parsing failure! Error:", e)    
            print(response)
        return False, "",self.location_code
    
    def record(self, 
                record):
        self.history_manager.add_record(record)
        
    def save_prompt(self,prompt,detail):
        if prompt:
            self.prompts.append({"prompt":prompt,
                                 "response":detail})
    # Other
    def action_check(self,):
        if self.acted == False:
            self.acted = True
            return True
        dice = random.uniform(0,1)
        if dice > self.activity:
            self.acted = False
            return False
        return True
    
    def retrieve_knowledges(self, query:str, top_k:int=1, max_words = 100):
        if self.world_db is None:
            return ""
        knowledges = "\n".join(self.world_db.search(query, top_k,self.world_db_name))
        knowledges = knowledges[:max_words]
        return knowledges
    
    def retrieve_references(self, query: str, top_k: int = 1):
        if self.db is None:
            return ""
        references = "\n".join(self.db.search(query, top_k,self.db_name))
        return references
    
    def retrieve_history(self, query: str, top_k: int = 5, retrieve: bool = False):
        if len(self.history_manager) == 0: return ""
        if len(self.history_manager) >= top_k and retrieve:
            history = "\n" + "\n".join(self.memory.search(query, top_k)) + "\n"
        else:
            history = "\n" + "\n".join(self.history_manager.get_recent_history(top_k))
        return history
        
    def get_other_roles_info_text(self, other_roles: List[str], if_relation: bool = True, if_profile: bool = True):
        roles_info_text = ""
        for i, role_code in enumerate(other_roles):
            if role_code == self.role_code :continue
            name = other_roles[role_code]["nickname"]
            profile = other_roles[role_code]["profile"]  if if_profile else ""
            relation = self.search_relation(role_code) if if_relation else ""
            roles_info_text += f"\n{i+1}. {name}\nrole_code:{role_code}\n{relation}\n{profile}\n\n"

        return roles_info_text
    
    def search_relation(self, other_role_code: str):
        if self.language == 'en':
            if other_role_code in self.relation:
                relation_text = ",".join(self.relation[other_role_code]["relation"])
                detail_text = self.relation[other_role_code]["detail"]
                return f"This is your {relation_text}. {detail_text}\n"
            else:
                return ""
        elif self.language == 'zh':
            if other_role_code in self.relation:
                relation_text = ",".join(self.relation[other_role_code]["relation"])
                detail_text = self.relation[other_role_code]["detail"]
                return f"这是你的{relation_text}. {detail_text}\n"
            else:
                return ""
    def set_location(self, location_code, location_name):
        self.location_code: Optional[str] = location_code
        self.location_name: Optional[str] = location_name
            
    def __getstate__(self):
        states = {key: value for key, value in self.__dict__.items() \
            if isinstance(value, (str, int, list, dict, bool, type(None))) \
                and key not in ['role_info','role_data','llm','embedding','db',"memory"]
                and "PROMPT" not in key}
        return states

    def __setstate__(self, states):
        self.__dict__.update(states)
        self._init_prompt()

    def save_to_file(self, root_dir):
        filename = os.path.join(root_dir, f"./roles/{self.role_code}.json")
        save_json_file(filename, self.__getstate__() )

    def load_from_file(self, root_dir):
        filename = os.path.join(root_dir, f"./roles/{self.role_code}.json")
        states = load_json_file(filename)
        self.__setstate__(states)     
        self.memory.init_from_data(self.history_manager.get_complete_history())

def build_role_agent_data(role_dir: str):
    role_data: List[str] = []
    for path in get_child_paths(role_dir):
        if os.path.splitext(path)[-1] == ".txt":
            text = load_text_file(path)
            role_data += split_text_by_max_words(text)
        elif os.path.splitext(path)[-1] == ".jsonl":
            role_data += [line["text"] for line in load_jsonl_file(path)]
    return role_data      


if __name__ == "__main__":
    agent = RPAgent(role_code='Harry-en')
    agent.single_role_interact("Hi,Harry, Who is Ron?")


    