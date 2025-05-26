from datetime import datetime
from tqdm import tqdm 
import json 
import os
import warnings
import random
from typing import Any, Dict, List, Optional, Literal
from collections import defaultdict
import uuid

from bw_utils import *
from modules.main_role_agent import RPAgent
from modules.world_agent import WorldAgent
from modules.history_manager import HistoryManager
import argparse

warnings.filterwarnings('ignore')

class Server():
    def __init__(self,
                 preset_path: str,
                 world_llm_name: str,
                 role_llm_name: str,
                 embedding_name:str = "bge-m3") :
        """
        The initialization function of the system.
        
        Args:
            preset_path (str): The path to config file of this experiment.
            world_llm_name (str, optional): The base model of the world agent. Defaults to 'gpt-4o'.
            role_llm_name (str, optional): The base model of all the role agents. Defaults to 'gpt-4o'.
            mode (str, optional): If set to be 'script', the role agents will act according to the given script. 
                                  If set to be 'free', the role agents will act freely based on their backround.
                                  Defaults to 'free'.
        """
        
        self.role_llm_name: str = role_llm_name
        self.world_llm_name: str = world_llm_name
        self.embedding_name:str = embedding_name
        config = load_json_file(preset_path)
        self.preset_path = preset_path
        self.config: Dict = config
        self.experiment_name: str = os.path.basename(preset_path).replace(".json","") + "/" + config["experiment_subname"] + "_" + role_llm_name
        
        role_agent_codes: List[str] = config['role_agent_codes']
        world_file_path: str = config["world_file_path"]
        map_file_path: str = config["map_file_path"] if "map_file_path" in config else ""
        role_file_dir: str = config["role_file_dir"] if "role_file_dir" in config else "./data/roles/"
        loc_file_path: str = config["loc_file_path"]
        self.intervention: str = config["intervention"] if "intervention" in config else ""
        self.event = self.intervention
        self.script: str = config["script"] if "script" in config else ""
        self.language: str = config["language"] if "language" in config else "zh"
        self.source:str = config["source"] if "source" in config else ""
        
        self.idx: int = 0
        self.cur_round: int = 0
        self.progress: str = "剧本刚刚开始，还什么都没有发生" if self.language == 'zh' else "The story has just begun, nothing happens yet."
        self.moving_roles_info: Dict[str, Any] = {}   
        self.history_manager = HistoryManager()
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.current_status = {
            "location_code":"",
            "group":role_agent_codes,
        }
        self.scene_characters = {}
        self.event_history = []
        
        self.role_llm = get_models(role_llm_name)
        self.logger = get_logger(self.experiment_name)
        self.init_role_agents(role_agent_codes = role_agent_codes,
                            role_file_dir = role_file_dir,
                            world_file_path=world_file_path,
                            llm = self.role_llm)
        
        if world_llm_name == role_llm_name:
            self.world_llm = self.role_llm
        else:
            self.world_llm = get_models(world_llm_name)
        self.init_world_agent_from_file(world_file_path = world_file_path,
                                        map_file_path = map_file_path,
                                        loc_file_path = loc_file_path,
                                        llm = self.world_llm)
    
    # Init
    def init_role_agents(self, 
                         role_agent_codes: List[str], 
                         role_file_dir:str, 
                         world_file_path:str,
                         llm) -> None:
        self.role_codes: List[str] = role_agent_codes
        self.role_agents: Dict[str, RPAgent] = {}
        
        for role_code in role_agent_codes:
            if check_role_code_availability(role_code,role_file_dir):
                self.role_agents[role_code] = RPAgent(role_code=role_code, 
                                                      role_file_dir=role_file_dir,
                                                      world_file_path=world_file_path,
                                                      source = self.source, 
                                                      language=self.language,
                                                      llm_name = self.role_llm_name,
                                                      llm = llm,
                                                      embedding_name=self.embedding_name,
                                                      )
                # print(f"{role_code} Initialized.")
            else:
                print(f"Warning: The specified role `{role_code}` does not exist.")
    
    def init_world_agent_from_file(self, 
                                   world_file_path: str, 
                                   map_file_path: str,
                                   loc_file_path: str,
                                   llm) -> None:
        self.world_agent: WorldAgent = WorldAgent(world_file_path = world_file_path, 
                                                  location_file_path = loc_file_path,
                                                  map_file_path = map_file_path, 
                                                  llm_name=self.world_llm_name,
                                                  llm = llm,
                                                  language=self.language)
        for role_code in self.role_agents:
            self.role_agents[role_code].world_db = self.world_agent.db
            self.role_agents[role_code].world_db_name = self.world_agent.db_name
        
    def init_role_locations(self, random_allocate: bool = True):
        """
        Set initial positions of the roles.
        
        Args:
            random_allocate (bool, optional): if set to be True, the initial positions of the roles are randomly assigned. Defaults to True.
        """
        init_locations_code = random.choices(self.world_agent.locations, k = len(self.role_codes))
        for i,role_code in enumerate(self.role_codes):
            self.role_agents[role_code].set_location(init_locations_code[i], self.world_agent.find_location_name(init_locations_code[i]))
            info_text = f"{self.role_agents[role_code].nickname} 现在位于 {self.world_agent.find_location_name(init_locations_code[i])}" \
                if self.language == "zh" else f"{self.role_agents[role_code].nickname} is now located at {self.world_agent.find_location_name(init_locations_code[i])}"
            self.log(info_text)
    
    def reset_llm(self, role_llm_name, world_llm_name):
        self.role_llm = get_models(role_llm_name)
        for role_code in self.role_codes:
            self.role_agents[role_code].llm = self.role_llm
            self.role_agents[role_code].llm_name = role_llm_name
        if world_llm_name == role_llm_name:
            self.world_llm = self.role_llm
        else:
            self.world_llm = get_models(world_llm_name)
        self.world_agent.llm = self.world_llm
        self.role_llm_name = role_llm_name
        self.world_llm_name = world_llm_name
        
    # Simulation        
    def simulate_generator(self, 
                 rounds: int = 10, 
                 save_dir: str = "", 
                 if_save: Literal[0,1] = 0,
                 mode: Literal["free", "script"] = "free",
                 scene_mode: Literal[0,1] = 1,):
        """
        The main function of the simulation.

        Args:
            rounds (int, optional): The max rounds of simulation. Defaults to 10.
            save_dir (str, optional): _description_. Defaults to "".
            if_save (Literal[0,1], optional): _description_. Defaults to 0.
        """
        self.mode = mode 
        meta_info: Dict[str, Any] = self.continue_simulation_from_file(save_dir)            
        self.if_save: int = if_save
        start_round: int = meta_info["round"]
        sub_start_round:int = meta_info["sub_round"] if "sub_round" in meta_info else 0
        if start_round == rounds: return 
        
        # Setting Locations
        if not meta_info["location_setted"]:
            self.log("========== Start Location Setting ==========")
            self.init_role_locations()
            self._save_current_simulation("location")
            
        # Setting Goals
        if not meta_info["goal_setted"]:
            yield ("system","","-- Setting Goals --",None) 
            self.log("========== Start Goal Setting ==========")
            
            if self.mode == "free":
                self.get_event()
                self.log(f"--------- Free Mode: Current Event ---------\n{self.event}\n")
                yield ("system","",f"--------- Current Event ---------\n{self.event}\n", None) 
                self.event_history.append(self.event)
            elif self.mode == "script":
                self.get_script()
                self.log(f"--------- Script Mode: Setted Script ---------\n{self.script}\n")
                yield ("system","",f"--------- Setted Script ---------\n{self.script}\n", None) 
                self.event_history.append(self.event)
            if self.mode == "free":
                for role_code in self.role_codes:
                    motivation = self.role_agents[role_code].set_motivation(
                        world_description = self.world_agent.description, 
                        other_roles_info = self._get_group_members_info_dict(self.role_agents),
                        intervention = self.event,
                        script = self.script
                        )
                    info_text = f"{self.role_agents[role_code].nickname} 设立了动机: {motivation}" \
                        if self.language == "zh" else f"{self.role_agents[role_code].nickname} has set the motivation: {motivation}"
                    
                    record_id = str(uuid.uuid4())
                    self.log(info_text)
                    self.record(role_code=role_code,
                                detail=info_text,
                                actor = role_code,
                                group = [role_code],
                                actor_type = 'role',
                                act_type="goal setting",
                                record_id = record_id)
                    yield ("role",role_code,info_text,record_id)
                    
            self._save_current_simulation("goal")
            
        yield ("system","","-- Simulation Started --",None)
        selected_role_codes = []
        # Simulating
        for current_round in range(start_round, rounds):
            self.cur_round = current_round
            self.log(f"========== Round {current_round+1} Started ==========")
            if self.event and current_round >= 1:
                self.log(f"--------- Current Event ---------\n{self.event}\n")
                yield ("world","","-- Current Event --\n"+self.event, None)
                self.event_history.append(self.event)
                
            if len(self.moving_roles_info) == len(self.role_codes):
                self.settle_movement()
                continue
            
            # Characters in next scene
            if scene_mode:
                group = self._name2code(
                    self.world_agent.decide_scene_actors(
                        self._get_locations_info(False),
                        self.history_manager.get_recent_history(5),
                        self.event,
                        list(set(selected_role_codes + list(self.moving_roles_info.keys())))))
                selected_role_codes += group
                if len(selected_role_codes) > len(self.role_codes):
                    selected_role_codes = []
            else:
                group = self.role_codes
            self.current_status['group'] = group
            self.current_status['location_code'] = self.role_agents[group[0]].location_code
            self.scene_characters[str(current_round)] = group
            # Prologue 
            # if current_round == 0 and len(group) > 0 
            #     prologue = self.world_agent.generate_location_prologue(location_code=self.role_agents[group[0]].location_code, history_text=self._get_history_text(group),event=self.event,location_info_text=self._find_roles_at_location(self.role_agents[group[0]].location_code,name=True))
            #     self.log("--Prologue--: "+prologue)
            #     self.record(role_code="None",detail=prologue,act_type="prologue")
            start_idx = len(self.history_manager)

            sub_round = sub_start_round
            for sub_round in range(sub_start_round,3):
                if self.mode == "script":    
                    self.script_instruct(self.progress)
                else:
                    for role_code in group:
                        self.role_agents[role_code].update_goal(other_roles_status=self._get_status_text(self.role_codes))

                for role_code in group:
                    if scene_mode:
                        role_code =  self._name2code(self.world_agent.decide_next_actor("\n".join(self.history_manager.get_recent_history(3)),self._get_group_members_info_text(group,status=True),self.script)) if scene_mode else role_code
                    
                    yield from self.implement_next_plan(role_code = role_code,
                                            group = group)
                    self._save_current_simulation("action", current_round, sub_round)

                if_end,epilogue = self.world_agent.judge_if_ended("\n".join(self.history_manager.get_recent_history(len(self.history_manager)-start_idx)))
                if if_end:
                    record_id = str(uuid.uuid4())
                    self.log("--Epilogue--: "+epilogue)
                    self.record(role_code = "None",
                                detail = epilogue, 
                                actor_type="world",
                                act_type="epilogue", 
                                actor = "world",
                                group = [],
                                record_id = record_id)
                    yield ("world","","--Epilogue--: "+epilogue, record_id)
                    
                    break
            
                
            for role_code in group:
                yield from self.decide_whether_to_move(role_code = role_code,
                                            group = self._find_group(role_code))
                self.role_agents[role_code].update_status()
                
            self.settle_movement()
            self.update_event(group)    
                
            sub_start_round = 0 
            self._save_current_simulation("action", current_round + 1,sub_round + 1)
            
    # Main functions using llm    
    def implement_next_plan(self,role_code: str, group: List[str]):
        other_roles_info = self._get_group_members_info_dict(group)
        plan = self.role_agents[role_code].plan(
            other_roles_info = other_roles_info,
            available_locations = self.world_agent.locations,
            world_description = self.world_agent.description,
            intervention = self.event,
        )
        
        info_text = plan["detail"]
        if plan["target_role_codes"]:
            plan["target_role_codes"] = self._name2code(plan["target_role_codes"])
            
            
        record_id = str(uuid.uuid4())
        self.log(f"-Action-\n{self.role_agents[role_code].role_name}: "+ info_text)
        self.record(role_code = role_code,
                    detail = plan["detail"],
                    actor_type = 'role',
                    act_type = "plan",
                    actor = role_code,
                    group = plan["target_role_codes"] + [role_code],
                    plan = plan,
                    record_id = record_id
                        )
        yield ("role", role_code, info_text, record_id)

        if plan["interact_type"] == "single" and len(plan["target_role_codes"]) == 1 and plan["target_role_codes"][0] in group:
            yield from self.start_single_role_interaction(plan, record_id)
        elif plan["interact_type"] == "multi" and len(plan["target_role_codes"]) > 1 and set(plan["target_role_codes"]).issubset(set(group))  :
            yield from self.start_multi_role_interaction(plan, record_id)
        elif plan["interact_type"] == "enviroment":
            yield from self.start_enviroment_interaction(plan,role_code, record_id)
        elif plan["interact_type"] == "npc" and plan["target_npc_name"]:
            yield from self.start_npc_interaction(plan,role_code,target_name=plan["target_npc_name"], record_id = record_id)
        return info_text         
    
    def decide_whether_to_move(self, 
                          role_code: str, 
                          group: List[str]):
        if len(self.world_agent.locations) <= 1:
            return False
        if_move, move_detail, destination_code = self.role_agents[role_code].move(locations_info_text = self._get_locations_info(), 
                                                                                  locations_info = self.world_agent.locations_info)
        if if_move:
            self.log(move_detail)
            print(f"角色选择移动。{self.role_agents[role_code].role_name}正在前往{self.world_agent.find_location_name(destination_code)}" if self.language == "zh" else f"The role decides to move. {self.role_agents[role_code].role_name} is heading to {self.world_agent.find_location_name(destination_code)}.")
            self.record(role_code = role_code,
                    detail = move_detail,
                    actor_type = 'role',
                    act_type = "move",
                    actor = role_code,
                    group = [role_code],
                    destinatiion_code = destination_code
                        )
            yield ("role",role_code,move_detail,None)
            
            distance = self.world_agent.get_distance(self.role_agents[role_code].location_code, destination_code)
            self.role_agents[role_code].set_location(location_code=None, location_name=None)
            self.moving_roles_info[role_code] = {
                "location_code":destination_code,
                "distance":distance
            }
        return if_move
          
    def start_enviroment_interaction(self,
                                     plan: Dict[str, Any], 
                                     role_code: str,
                                     record_id: str):
        """
        Handles the role's interaction with the environment. 
        It gets interaction results from agents in the world, record the result and update the status of the role.

        Args:
            plan (Dict[str, Any]): The details of the action.
            role_code (str): The action maker.

        Returns:
            (str): The enviroment response.
        """
        if "action" not in plan:
            plan["action"] = ""
        self.current_status['group'] = [role_code]
        location_code = self.role_agents[role_code].location_code
        result = self.world_agent.enviroment_interact(action_maker_name = self.role_agents[role_code].role_name,
                                                            action  = plan["action"],
                                                            action_detail = conceal_thoughts(self.history_manager.search_record_detail(record_id)),
                                                            location_code = location_code)
        env_record_id = str(uuid.uuid4())
        self.log(f"(Enviroment):{result}")
        self.record(role_code = role_code,
                    detail = result,
                    actor_type = 'world',
                    act_type = "enviroment",
                    initiator = role_code,
                    actor = "world",
                    group = [role_code],
                    record_id = env_record_id)
        yield ("world","","(Enviroment):" + result, env_record_id)
        
        return conceal_thoughts(self.history_manager.search_record_detail(record_id)) + self.history_manager.search_record_detail(env_record_id)
    
    def start_npc_interaction(self,
                              plan: Dict[str, Any], 
                              role_code: str, 
                              target_name: str,
                              record_id: str,
                              max_rounds: int = 3):
        """
        Handles the role's interaction with the environment. 
        It gets interaction results from agents in the world, record the result and update the status of the role.

        Args:
            plan (Dict[str, Any]): The details of the action.
            role_code (str): The action maker.
            target_name (str): The target npc.

        Returns:
            (str): The enviroment response.
        """
        interaction = plan
        start_idx = len(self.history_manager)
        
        self.log(f"----------NPC Interaction----------\n")
        self.current_status['group'] = [role_code,target_name]
        for round in range(max_rounds):
            npc_interaction = self.world_agent.npc_interact(action_maker_name=self.role_agents[role_code].role_name,
                                                    action_detail=self.history_manager.search_record_detail(record_id),
                                                    location_name=self.role_agents[role_code].location_name,
                                                    target_name=target_name)
            npc_detail = npc_interaction["detail"]
            
            npc_record_id = str(uuid.uuid4())
            self.log(f"{target_name}: " + npc_detail)
            self.record(role_code = role_code,
                        detail = npc_detail,
                        actor_type = 'world',
                        act_type = "npc",
                        actor = "world",
                        group = [role_code],
                        npc_name = target_name,
                        record_id = npc_record_id
                        )
            yield ("world","",f"(NPC-{target_name}):" + npc_detail, npc_record_id)
            
            if npc_interaction["if_end_interaction"]:
                break
            
            interaction = self.role_agents[role_code].npc_interact(
                npc_name = target_name,
                npc_response = self.history_manager.search_record_detail(npc_record_id),
                history = self.history_manager.get_subsequent_history(start_idx = start_idx),
                intervention = self.event
            )
            detail = interaction["detail"]
            
            record_id = str(uuid.uuid4())
            self.log(f"{self.role_agents[role_code].role_name}: " + detail)
            self.record(role_code = role_code,
                        detail = detail,
                        actor_type = 'role',
                        act_type = "npc",
                        actor = role_code,
                        group = [role_code],
                        npc_name = target_name,
                        record_id = record_id)
            yield ("role",role_code,detail,record_id)
            
            if interaction["if_end_interaction"]:
                break
            if_end,epilogue = self.world_agent.judge_if_ended("\n".join(self.history_manager.get_subsequent_history(start_idx)))
            if if_end:
                break
                
        return "\n".join(self.history_manager.get_subsequent_history(start_idx = start_idx))
    
    def start_single_role_interaction(self,
                                      plan: Dict[str, Any],
                                      record_id: str,
                                      max_rounds: int = 8):
        interaction = plan
        acted_role_code = interaction["role_code"]
        acting_role_code = interaction["target_role_codes"][0]
        if acting_role_code not in self.role_codes:
            print(f"Warning: Role {acting_role_code} does not exist.")
            return
        self.current_status['group'] = [acted_role_code,acting_role_code]
        
        start_idx = len(self.history_manager)
        for round in range(max_rounds):
            interaction = self.role_agents[acting_role_code].single_role_interact(
                action_maker_code = acted_role_code, 
                action_maker_name = self.role_agents[acted_role_code].role_name,
                action_detail = conceal_thoughts(self.history_manager.search_record_detail(record_id)), 
                action_maker_profile = self.role_agents[acted_role_code].role_profile, 
                intervention = self.event
            )
            
            detail = interaction["detail"]
            
            record_id = str(uuid.uuid4())
            self.log(f"{self.role_agents[acting_role_code].role_name}: " + detail)
            self.record(role_code = acting_role_code,
                        detail = detail,
                        actor_type = 'role',
                        act_type = "single",
                        group = [acted_role_code,acting_role_code],
                        target_role_code = acting_role_code,
                        planning_role_code = plan["role_code"],
                        round = round,
                        record_id = record_id
                        )
            yield ("role",acting_role_code,detail,record_id)
            
            if interaction["if_end_interaction"]:
                return
            if interaction["extra_interact_type"] == "npc":
                print("---Extra NPC Interact---")
                result = yield from self.start_npc_interaction(plan=interaction,
                                                               role_code=acted_role_code,
                                                               target_name=interaction["target_npc_name"],
                                                               record_id=record_id)
                interaction["detail"] = result
                
            elif interaction["extra_interact_type"] == "enviroment":
                print("---Extra Env Interact---")
                result = yield from self.start_enviroment_interaction(plan=interaction,role_code=acted_role_code,record_id=record_id)
                interaction["detail"] = result
                
            if_end,epilogue = self.world_agent.judge_if_ended("\n".join(self.history_manager.get_subsequent_history(start_idx)))
            if if_end:
                break
            acted_role_code,acting_role_code = acting_role_code,acted_role_code
        return
    
    def start_multi_role_interaction(self, 
                                     plan: Dict[str, Any], 
                                     record_id: str,
                                     max_rounds: int = 8):

        interaction = plan
        acted_role_code = interaction["role_code"]
        group = interaction["target_role_codes"]
        group.append(acted_role_code)
        
        for code in group:
            if code not in self.role_codes:
                print(f"Warning: Role {code} does not exist.")
                return
        self.current_status['group'] = group
        
        start_idx = len(self.history_manager)
        other_roles_info = self._get_group_members_info_dict(group)
        
        for round in range(max_rounds):
            acting_role_code = self._name2code(self.world_agent.decide_next_actor(history_text = "\n".join(self.history_manager.get_recent_history(3)),
                                                                  roles_info_text = self._get_group_members_info_text(remove_list_elements(group,acted_role_code),status=True)))

            
            interaction = self.role_agents[acting_role_code].multi_role_interact(
                action_maker_code = acted_role_code, 
                action_maker_name = self.role_agents[acted_role_code].role_name,
                action_detail = conceal_thoughts(self.history_manager.search_record_detail(record_id)), 
                action_maker_profile = self.role_agents[acted_role_code].role_profile, 
                other_roles_info = other_roles_info,
                intervention = self.event
            )
            
            detail = interaction["detail"]
            
            record_id = str(uuid.uuid4())
            self.log(f"{self.role_agents[acting_role_code].role_name}: "+ detail)
            self.record(role_code = acting_role_code,
                        detail = detail,
                        actor_type = 'role',
                        act_type = "multi",
                        group = group,
                        actor = acting_role_code,
                        planning_role_code = plan["role_code"],
                        round = round,
                        record_id = record_id
                        )
            yield ("role",acting_role_code,detail,record_id)
            
                
            if interaction["if_end_interaction"]:
                break
            result = ""
            if interaction["extra_interact_type"] == "npc":
                print("---Extra NPC Interact---")
                result = yield from self.start_npc_interaction(plan=interaction,role_code=acting_role_code,target_name=interaction["target_npc_name"],record_id = record_id)
            elif interaction["extra_interact_type"] == "enviroment":
                print("---Extra Env Interact---")
                result = yield from self.start_enviroment_interaction(plan=interaction,role_code=acting_role_code,record_id = record_id)
            interaction["detail"] = self.history_manager.search_record_detail(record_id) + result
            acted_role_code = acting_role_code
            if_end,epilogue = self.world_agent.judge_if_ended("\n".join(self.history_manager.get_subsequent_history(start_idx)))
            if if_end:
                break
            
            return
    
    # Sub functions using llm
    def script_instruct(self, 
                        last_progress: str, 
                        top_k: int = 5):
        """
        Under the script mode, generate instruction for the roles at the beginning of each round.

        Args:
            last_progress (str): Where the script went in the last round.
            top_k (int, optional): The number of action history of each role to refer. Defaults to 1.

        Returns:
            Dict[str, Any]: Instruction for each role.
        """
        roles_info_text = self._get_group_members_info_text(self.role_codes,status=True)
        history_text = self.history_manager.get_recent_history(top_k)
    
        instruction = self.world_agent.get_script_instruction(
                                roles_info_text=roles_info_text, 
                                event = self.event, 
                                history_text=history_text,
                                script=self.script,
                                last_progress = last_progress)
        
        for code in instruction:
            if code == "progress":
                self.log("剧本进度："+ instruction["progress"]) if self.language == "zh" else self.log("Current Stage:"+ instruction["progress"])
            elif code in self.role_codes:
                # self.role_agents[code].update_goal(instruction = instruction[code])
                self.role_agents[code].goal = instruction[code]
            else:
                print("Instruction failed, role code:",code)
        return instruction
       
    def get_event(self,):
        if self.intervention == "" and not self.script:
            roles_info_text = self._get_group_members_info_text(self.role_codes,profile=True)
            status_text = self._get_status_text(self.role_codes)
            event = self.world_agent.generate_event(roles_info_text=roles_info_text,event=self.intervention,history_text=status_text)
            self.intervention = event
        elif self.intervention == "" and self.script:
            self.intervention = self.script
        self.event = self.intervention
        return self.intervention
    
    def get_script(self,):
        if self.script == "":
            roles_info_text = self._get_group_members_info_text(self.role_codes,profile=True)
            status = "\n".join([self.role_agents[role_code].status for role_code in self.role_codes])
            script = self.world_agent.generate_script(roles_info_text=roles_info_text,event=self.intervention,history_text=status)
            self.script = script
        return self.script
    
    def update_event(self, group: List[str], top_k: int = 1):
        if self.intervention == "":
            self.event = ""
        else:
            status_text = self._get_status_text(group)
            self.event = self.world_agent.update_event(self.event, self.intervention, status_text, script = self.script)
    
    # other
    def record(self,
               role_code: str, 
               detail: str, 
               actor_type: str,
               act_type: str,
               group: List[str] = [],
               actor: str = "",
               record_id = None,
               **kwargs):
        if act_type == "plan" and "plan" in kwargs:
            detail = f"{self.role_agents[role_code].nickname}: {detail}"
            interact_type = kwargs["plan"]["interact_type"]
            target = ", ".join(kwargs["plan"]["target_role_codes"])
            other_info = f"Interact type: {interact_type}, Target: {target}"
        elif act_type == "move" and "destination_code" in kwargs:
            destination = kwargs["destination_code"]
            other_info = f"Desitination:{destination}"
        elif act_type == "single":
            detail = f"{self.role_agents[role_code].nickname}: {detail}"
            target, planning_role, round = kwargs["target_role_code"],kwargs["planning_role_code"],kwargs["round"]
            other_info = f"Target: {target}, Planning Role: {planning_role}, Round: {round}"
        elif act_type == "multi": 
            detail = f"{self.role_agents[role_code].nickname}: {detail}"
            planning_role, round = kwargs["planning_role_code"],kwargs["round"]
            other_info = f"Group member:{group}, Planning Role: {planning_role}, Round:{round},"
        elif act_type == "npc":
            name = kwargs["npc_name"]
            other_info = f"Target: {name}"
        elif act_type == "enviroment":
            other_info = ""
        else:
            other_info = ""
        record = {
            "cur_round":self.cur_round,
            "role_code":role_code,
            "detail":detail,
            "actor":actor,
            "group":group,      # visible group
            "actor_type":actor_type,
            "act_type":act_type,
            "other_info":other_info,
            "record_id":record_id
        }
        self.history_manager.add_record(record)
        for code in group:
            self.role_agents[code].record(record)
    
    def settle_movement(self,):
        for role_code in self.moving_roles_info.copy():
            if not self.moving_roles_info[role_code]["distance"]:
                location_code = self.moving_roles_info[role_code]["location_code"]
                self.role_agents[role_code].set_location(location_code, self.world_agent.find_location_name(location_code))
                self.log(f"{self.role_agents[role_code].role_name} 已到达 【{self.world_agent.find_location_name(location_code)}】" if self.language == "zh" else
                         f"{self.role_agents[role_code].role_name} has reached [{self.world_agent.find_location_name(location_code)}]")
                del self.moving_roles_info[role_code]
            else:
                self.moving_roles_info[role_code]["distance"] -= 1
    
    def _find_group(self,role_code):
        return [code for code in self.role_codes if self.role_agents[code].location_code==self.role_agents[role_code].location_code]
    
    def _find_roles_at_location(self,location_code,name = False):
        if name:
            return [self.role_agents[code].nickname for code in self.role_codes if self.role_agents[code].location_code==location_code]
        else:
            return [code for code in self.role_codes if self.role_agents[code].location_code==location_code]

    def _get_status_text(self,group):
        return "\n".join([self.role_agents[role_code].status for role_code in group])
    
    def _get_group_members_info_text(self,group, profile = False,status = False):
        roles_info_text = ""
        for i, role_code in enumerate(group):
            name = self.role_agents[role_code].role_name
            roles_info_text += f"{i+1}. {name}\n(role_code:{role_code})\n"
            if profile:
                profile =  self.role_agents[role_code].role_profile
                roles_info_text += f"{profile}\n"
            if status:
                status =  self.role_agents[role_code].status
                roles_info_text += f"{status}\n"
        return roles_info_text
    
    def _get_group_members_info_dict(self,group: List[str]):
        info = {
                role_code: {
                    "nickname": self.role_agents[role_code].nickname,
                    "profile": self.role_agents[role_code].role_profile
                }
                for role_code in group
            }
        return info
    
    def _get_locations_info(self,detailed = True):
        location_info_text = "---当前各角色位置---\n" if self.language == "zh" else "---Current Location of Roles---\n"
        if detailed:
            for i,location_code in enumerate(self.world_agent.locations_info):
                location_name = self.world_agent.find_location_name(location_code)
                description = self.world_agent.locations_info[location_code]["description"]
                location_info_text += f"\n{i+1}. {location_name}\nlocation_code:{location_code}\n{description}\n\n"
                role_names = [f"{self.role_agents[code].role_name}({code})" for code in self.role_codes if self.role_agents[code].location_code == location_code]
                role_names = ", ".join(role_names)
                location_info_text += "目前在这里的角色有：" + role_names if self.language == "zh" else "Roles located here: " + role_names
        else:
            for i,location_code in enumerate(self.world_agent.locations_info):
                location_name = self.world_agent.find_location_name(location_code)
                role_names = [f"{self.role_agents[code].role_name}({code})" for code in self.role_codes if self.role_agents[code].location_code == location_code]
                if len(role_names) == 0:continue
                role_names = ", ".join(role_names)
                location_info_text += f"【{location_name}】：" + role_names +"；"
        return location_info_text
    
    def _name2code(self,roles):
        name_dic = {self.role_agents[code].role_name:code for code in self.role_codes}
        name_dic.update({self.role_agents[code].nickname:code for code in self.role_codes})
        if isinstance(roles, list):
            processed_roles = []
            for role in roles:
                if role in self.role_codes:
                    processed_roles.append(role)
                elif role in name_dic:
                    processed_roles.append(name_dic[role])
                elif "-" in role and role.split("-")[0] in name_dic:
                    processed_roles.append(name_dic[role.split("-")[0]])
                elif role.replace("_","·") in self.role_codes:
                    processed_roles.append(role.replace("_","·"))
                else:
                    processed_roles.append(role)
            return processed_roles
        elif isinstance(roles, str) :
            roles = roles.replace("\n","")
            if roles in self.role_codes:
                return roles
            elif roles in name_dic:
                return name_dic[roles]
            elif f"{roles}-{self.language}" in self.role_codes:
                return f"{roles}-{self.language}"
            elif "-" in roles and roles.split("-")[0] in name_dic:
                return name_dic[roles.split("-")[0]]
            elif roles.replace("_","·") in self.role_codes:
                return roles.replace("_","·")
        return roles
    
    def log(self,text):
        self.logger.info(text)
        print(text)
    
    def _save_current_simulation(self, 
                                 stage: Literal["location", "goal", "action"], 
                                 current_round: int = 0,
                                 sub_round:int = 0):
        """
        Save the current simulation progress. 

        Args:
            stage (Literal["location", "goal", "action"]): The stage in which the simulation has been carried out
            current_round (int, optional): If the stage is "action", specify the number of rounds that have been completed. Defaults to 0.
        """
        if not self.if_save:
            return
        save_dir = f"./experiment_saves/{self.experiment_name}/{self.role_llm_name}_{self.start_time}"
        create_dir(save_dir)
        location_setted, goal_setted = False,False
        if stage in ["location","goal","action"]:
            location_setted = True
        if stage in ["goal","action"]:
            goal_setted = True
        meta_info = {
                "location_setted":location_setted,
                "goal_setted": goal_setted,
                "round": current_round,   
                "sub_round": sub_round,    
            }

        save_json_file(os.path.join(save_dir, "meta_info.json"), meta_info)
        name = self.experiment_name.split("/")[0]
        save_json_file(os.path.join(save_dir, f"{name}.json"), self.config)
        
        filename = os.path.join(save_dir, f"./server_info.json")
        save_json_file(filename, self.__getstate__() )
        
        self.history_manager.save_to_file(save_dir)
        if hasattr(self, 'role_agents'):
            for role_code in self.role_codes:
                self.role_agents[role_code].save_to_file(save_dir)
            self.world_agent.save_to_file(save_dir)
        
    def continue_simulation_from_file(self, save_dir: str):
        """
        Restore the record of the last simulation.
        
        Args:
            save_dir (str): The path where the last simulation record was saved.

        Returns:
            Dict[str, Any]: The meta information recording the progress of the simulation
        """
        if os.path.exists(save_dir):
            meta_info = load_json_file(os.path.join(save_dir, "./meta_info.json"))
            filename = os.path.join(save_dir, f"./server_info.json")
            states = load_json_file(filename)
            self.__setstate__(states)   
            for role_code in self.role_codes:
                self.role_agents[role_code].load_from_file(save_dir) 
            self.world_agent.load_from_file(save_dir)
            self.history_manager.load_from_file(save_dir)
            
            for record in self.history_manager.detailed_history:
                for code in record["group"]:
                    if code in self.role_codes:
                        self.role_agents[code].record(record)
        else:
            meta_info = {
                "location_setted":False,
                "goal_setted": False,
                "round": 0,
                "sub_round": 0,
            }
        return meta_info
    
    def __getstate__(self):
        states = {key: value for key, value in self.__dict__.items() \
            if isinstance(value, (str, int, list, dict, bool, type(None))) \
                and key not in ['role_agents','world_agent','logger']}
        
        return states

    def __setstate__(self, states):
        self.__dict__.update(states)


class BookWorld():
    def __init__(self,
                 preset_path: str,
                 world_llm_name: str,
                 role_llm_name: str,
                 embedding_name:str = "bge-m3") :
        self.server = Server(preset_path, 
                        world_llm_name=world_llm_name, 
                        role_llm_name=role_llm_name, 
                        embedding_name=embedding_name)
        self.selected_scene = None
        
    def set_generator(self, 
                      rounds:int = 10, 
                      save_dir:str = "", 
                      if_save: Literal[0,1] = 0,
                      mode: Literal["free", "script"] = "free",
                      scene_mode: Literal[0,1] = 0,):
        self.server.continue_simulation_from_file(save_dir)
        self.generator = self.server.simulate_generator(rounds = rounds,
                                                        save_dir = save_dir,
                                                        if_save = if_save,
                                                        mode = mode,
                                                        scene_mode = scene_mode)
    def get_map_info(self):
        location_codes = self.server.world_agent.locations
        location_names = [self.server.world_agent.find_location_name(location_code) for location_code in location_codes]
        n = len(location_codes)
        distances = []
        for i in range(n):
            for j in range(i+1,n):
                if self.server.world_agent.get_distance(location_codes[i], location_codes[j]):
                    distances.append({
                        "source": location_names[i],
                        "target": location_names[j],
                        "distance": self.server.world_agent.get_distance(location_codes[i], location_codes[j])
                    })
            
        return {
            "places": location_names,
            "distances": distances
        }
    def select_scene(self,scene_number):
        if scene_number == None:
            self.selected_scene = scene_number
        else:
            self.selected_scene = str(scene_number)
        
    def get_characters_info(self):
        characters_info = []
        if self.selected_scene == None:
            codes = self.server.role_codes
        else:
            codes = self.server.scene_characters[str(self.selected_scene)]
        for (i, code) in enumerate(codes):
            agent = self.server.role_agents[code]
            location = agent.location_name
            if code in self.server.moving_roles_info:
                location_name = self.server.world_agent.find_location_name(self.server.moving_roles_info[code]["location_code"])
                distance = self.server.moving_roles_info[code]['distance']
                location = f"Reaching {location_name}... ({distance})"
            chara_info = {
                "id": i,
                "name": agent.nickname,
                "icon": agent.icon_path,
                "description": agent.role_profile,
                "goal": agent.goal if agent.goal else agent.motivation,
                "state": agent.status,
                "location": location
            }
            characters_info.append(chara_info)
        return characters_info

    def generate_next_message(self):
        message_type, code, text,message_id = next(self.generator)
        if message_type == "role":
            username = self.server.role_agents[code].role_name
            icon_path = self.server.role_agents[code].icon_path
        else:
            username = message_type
            icon_path = ""
        message = {
            'username': username,
            'type': message_type, # role, world, system
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'text': text,
            'icon': icon_path,
            "uuid": message_id,
            "scene": self.server.cur_round
        }
        return message
        
    def get_settings_info(self):
        return self.server.world_agent.world_settings
    
    def get_current_status(self):
        status = self.server.current_status
        status['event'] = self.server.event
        group = []
        for code in status['group']:
            if code in self.server.role_codes:
                group.append(self.server.role_agents[code].nickname)
            else:
                group.append(code)
        status['group'] = group
        location_code = self.server.current_status['location_code']
        if location_code not in self.server.world_agent.locations_info:
            location_name,location_description = "Undefined","Undefined"
        else:
            location_name,location_description = self.server.world_agent.find_location_name(location_code),self.server.world_agent.locations_info[location_code]["description"]
        status['location'] = {'name': location_name, 'description': location_description}
        status['characters'] = self.get_characters_info()
        return status
    
    def handle_message_edit(self,record_id,new_text):
        group = self.server.history_manager.modify_record(record_id,new_text)
        for code in group:
            self.server.role_agents[code].history_manager.modify_record(record_id,new_text)
        return

    def get_history_messages(self,save_dir):
        
        messages = []
        for record in self.server.history_manager.detailed_history:
            message_type = record["actor_type"]
            code = record["role_code"]
            if message_type == "role":
                username = self.server.role_agents[code].role_name
                icon_path = self.server.role_agents[code].icon_path
            else:
                username = message_type
                icon_path = "./frontend/assets/images/default-icon.jpg"
            messages.append({
                'username': username,
                'type': message_type, # role, world, system
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'text': record["detail"],
                'icon': icon_path,
                "uuid": record["record_id"],
                "scene": record["cur_round"]
            })
        return messages
    
    def generate_story(self,):
        logs = self.server.history_manager.get_complete_history()
        story = self.server.world_agent.log2story(logs)
        return story
    

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--world_llm', type=str, default='gpt-4o-mini')
    parser.add_argument('--role_llm', type=str, default='gpt-4o-mini')
    parser.add_argument('--genre', type=str, default='mgdv2')
    parser.add_argument('--preset_path', type=str, default='')

    parser.add_argument('--if_save', type=int, default=1, choices=[0,1])
    parser.add_argument('--scene_mode', type=int, default=0, choices=[0,1])
    parser.add_argument('--rounds', type=int, default=10)
    parser.add_argument('--save_dir', type=str, default='')
    parser.add_argument('--mode', type=str, default='free', choices=['free','script'])
    args = parser.parse_args()
    world_llm_name = args.world_llm
    role_llm_name = args.role_llm
    rounds = args.rounds
    genre = args.genre
    preset_path = args.preset_path
    save_dir = args.save_dir
    if_save = args.if_save
    scene_mode = args.scene_mode
    mode = args.mode
    if not preset_path:
        preset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),f"./config/experiment_{genre}.json")
    
    bw = BookWorld(preset_path, world_llm_name=world_llm_name, role_llm_name=role_llm_name)
    bw.set_generator(rounds = rounds, save_dir = save_dir, if_save = if_save, scene_mode = scene_mode,mode = mode)
    
    for i in range(100):
        try:
            bw.generate_next_message()
        except StopIteration:
            break