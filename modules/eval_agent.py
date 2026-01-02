import sys

from flask import Response
sys.path.append("../")
from typing import Any, Dict, List, Optional, Literal
from collections import defaultdict
from bw_utils import *
from modules.prompt.eval_prompt import DEDUCT_PROMPT_DICT,PLUS_PROMPT_DICT, TTCW_PROMPT_DICT, SCRIPT_GENERATION_PROMPT,SCORING_PROMPT_DICT,SCRIPT_GENERATE_BY_CHARA_PROMPT,SCORING_PROMPT_DICT_FREE_MODE,FREE_GENERATE_BY_CHARA_PROMPT,FREE_GENERATION_PROMPT
from modules.embedding import get_embedding_model

class EvalAgent:
    def __init__(self,
                 roles_info: Dict[str, Any],
                 summary: str,
                 source: str = "",
                 llm_name: str = "gpt-4o",
                 llm = None,
                 role_llm = None
                 ):
        super(EvalAgent, self).__init__()
        if llm == None:
            llm = get_models(llm_name)
        self.llm_name = llm_name
        self.llm = llm
        self.role_llm = role_llm
        self.summary = summary
        self.source = source
        self.eval_result = defaultdict(dict)
        self.generated_script = {}
        self.roles_info = roles_info
        
    def naive_generate(self,num_records: int, mode = "script"):
        if "naive" in self.generated_script and self.generated_script["naive"] and self.generated_script["naive"].strip():
            return self.generated_script["naive"]
        if mode == "script":
            prompt = SCRIPT_GENERATION_PROMPT.format(**{
                "source":self.source,
                "scenario": self.summary,
                "major_characters": self._get_roles_name(),
                "character_profiles": self._get_roles_info_text(),
                "num_records": num_records
            })
            text = self.role_llm.chat(prompt)
            self.generated_script["naive"] = text
            return self.generated_script["naive"]
        elif mode == "free":
            prompt = FREE_GENERATION_PROMPT.format(**{
                "source":self.source,
                "major_characters": self._get_roles_name(),
                "character_profiles": self._get_roles_info_text(),
                "num_records": num_records
            })
            text = self.role_llm.chat(prompt)
            self.generated_script["naive"] = text
            return self.generated_script["naive"]
    
    def naive_generate_multi_round(self,num_records: int , mode="script"):
        if "naive_multi" in self.generated_script and self.generated_script["naive_multi"] and self.generated_script["naive_multi"].strip():
            return self.generated_script["naive_multi"]
        lis = []
        num_records = min(num_records, 20)
        if mode == "script":
            for i in range(num_records):
                prompt = SCRIPT_GENERATE_BY_CHARA_PROMPT.format(**{
                    "history":"\n".join(lis),
                    "source":self.source,
                    "scenario": self.summary,
                    "major_characters": self._get_roles_name(),
                    "character_profiles": self._get_roles_info_text(),
                })
                for _ in range(3):
                    try:
                        text = self.role_llm.chat(prompt)
                        if text:
                            break
                    except Exception as e:
                        print(e)
                lis.append(text)
            self.generated_script["naive_multi"] = merge_text_with_limit(lis, 5000)
            return self.generated_script["naive_multi"]
        elif mode == "free":
            for i in range(num_records):
                prompt = FREE_GENERATE_BY_CHARA_PROMPT.format(**{
                    "history":"\n".join(lis),
                    "source":self.source,
                    "major_characters": self._get_roles_name(),
                    "character_profiles": self._get_roles_info_text(),
                })
                for _ in range(3):
                    text = self.role_llm.chat(prompt)
                    if text:
                        break
                lis.append(text)
            self.generated_script["naive_multi"] = merge_text_with_limit(lis, 5000)
            return self.generated_script["naive_multi"]
    
    def hollmwood_generate(self,root_dir,idx,num_records: int, default_text = ""):
        
        path = os.path.join(root_dir,idx,"Cleaned_Screenplay.json")
        if not os.path.exists(path):
            return default_text
        lis = load_json_file(path)[:num_records]
        text = merge_text_with_limit(lis, 5000)
        if not text: 
            text = default_text
        self.generated_script["hollmwood"] = text
        return text
    
    def naive_score(self,text,method, mode = "script"):
        result = {"score":{}}
        evaled_dims = []
        if method in self.eval_result and "scoring" in self.eval_result[method] and "score" in self.eval_result[method]["scoring"]:
            evaled_dims = list(self.eval_result[method]["scoring"]["score"].keys())
            result = self.eval_result[method]["scoring"]
        elif method not in self.eval_result:
            self.eval_result[method] = {}
        elif "scoring" not in self.eval_result[method]:
            self.eval_result[method]["scoring"] = {}

        if mode == "script":
            self.generated_script[method] = text
            dimensions = list(SCORING_PROMPT_DICT["dimensions"].keys())
            template = SCORING_PROMPT_DICT["scoring_template"]
            
            for dim in dimensions:
                if dim in evaled_dims:continue
                criteria = SCORING_PROMPT_DICT["dimensions"][dim]
                prompt = template.format(**{
                "dimension_name":dim,
                "criteria":criteria,
                "source":self.source,
                "scenario": self.summary,
                "major_characters": self._get_roles_name(),
                "character_profiles": self._get_roles_info_text(),
                "text":text,
                })
                for i in range(3):
                    try:
                        output = self.llm.chat(prompt)
                        response = json_parser(output)
                        score = response["score"]
                        result["score"][dim] = score
                        # result["explanation"][dim] = response["explanation"]
                        break
                    except Exception as e:
                        print(f"Parsing failure! {i+1}th tries. Error:", e)
            self.eval_result[method]["scoring"] = result
            return result["score"]
        elif mode == "free":
            self.generated_script[method] = text
            dimensions = list(SCORING_PROMPT_DICT_FREE_MODE["dimensions"].keys())
            template = SCORING_PROMPT_DICT_FREE_MODE["scoring_template"]
            for dim in dimensions:
                if dim in evaled_dims:continue
                criteria = SCORING_PROMPT_DICT_FREE_MODE["dimensions"][dim]
                prompt = template.format(**{
                "dimension_name":dim,
                "criteria":criteria,
                "source":self.source,
                "major_characters": self._get_roles_name(),
                "character_profiles": self._get_roles_info_text(),
                "text":text,
                })
                for i in range(3):
                    try:
                        output = self.llm.chat(prompt)
                        response = json_parser(output)
                        score = response["score"]
                        result["score"][dim] = score
                        # result["explanation"][dim] = response["explanation"]
                        break
                    except Exception as e:
                        print(f"Parsing failure! {i+1}th tries. Error:", e)
            self.eval_result[method]["scoring"] = result
            return result["score"]
    
    def score_all_dims(self, text,method,score_type = "deduct"):
        if method in self.eval_result and score_type in self.eval_result[method] and "score_detail" in self.eval_result[method][score_type]:
            return self.eval_result[method][score_type]["score_detail"], self.eval_result[method][score_type]["score"]
        self.generated_script[method] = text
        if score_type == "deduct":
            dimensions = list(DEDUCT_PROMPT_DICT["dimension_details"].keys())
        elif score_type == "plus":
            dimensions = list(PLUS_PROMPT_DICT["dimension_details"].keys())
        if method not in self.eval_result:
            self.eval_result[method] = {}
        if score_type not in self.eval_result[method]:
            self.eval_result[method][score_type] = {"score_detail":{},"score":0}
        sum_score = 0
        for dim in dimensions:
            result,score = self.score_single_dim(text,dim,score_type)
            self.eval_result[method][score_type]["score_detail"].update(result)
            sum_score += score
        self.eval_result[method][score_type]["score"] = sum_score / len(dimensions)
        return self.eval_result[method][score_type]["score_detail"], self.eval_result[method][score_type]["score"]

    def score_single_dim(self, text, dim, score_type = "deduct"):
        if score_type == "deduct":
            template = DEDUCT_PROMPT_DICT["self-play-deduct-template"]
            brief = DEDUCT_PROMPT_DICT["dimension_details"][dim]["dimension_brief"]
            criteria = DEDUCT_PROMPT_DICT["dimension_details"][dim]["dimension_criteria"]
        elif score_type == "plus":
            template = PLUS_PROMPT_DICT["self-play-plus-template"]
            brief = PLUS_PROMPT_DICT["dimension_details"][dim]["dimension_brief"]
            criteria = PLUS_PROMPT_DICT["dimension_details"][dim]["dimension_criteria"]
        prompt = template.format(**{
            "dimension_name":dim,
            "dimension_brief":brief,
            "dimension_criteria":criteria,
            "source":self.source,
            "scenario": self.summary,
            "major_characters": self._get_roles_name(),
            "character_profiles": self._get_roles_info_text(),
            "text":text,
        })
        max_tries = 5
        for i in range(max_tries):
            response = self.llm.chat(prompt)
            try:
                
                result = json_parser(response)
                result[dim]["score"] = int(result[dim]["score"])
                break
            except Exception as e:
                print(f"Parsing failure! {i+1}th tries. Error:", e)
                print(response)
        return result,result[dim]["score"]

    def naive_winner(self,method_text,method, mode = "script"):
        bookworld_text = self.generated_script["bookworld"]
        result = {"winner":{}}
        evaled_dims = []
        if method in self.eval_result and "winner" in self.eval_result[method]:
            evaled_dims = list(self.eval_result[method]["winner"]["winner"].keys())
            result = self.eval_result[method]["winner"]
        elif method not in self.eval_result:
            self.eval_result[method] = {}
        elif "winner" not in self.eval_result[method]:
            self.eval_result[method]["winner"] = {}
        if mode == "script":
            dimensions = list(SCORING_PROMPT_DICT["dimensions"].keys())
            template = SCORING_PROMPT_DICT["comparison_template"]
            
            for dim in dimensions:
                if dim in evaled_dims:continue
                criteria = SCORING_PROMPT_DICT["dimensions"][dim]
                prompt = template.format(**{
                "dimension_name":dim,
                "criteria":criteria,
                "source":self.source,
                "major_characters": self._get_roles_name(),
                "character_profiles": self._get_roles_info_text(),
                "scenario": self.summary,
                "text1":bookworld_text,
                "text2":method_text,
                "method1":"bookworld",
                "method2":method,
                })
                for i in range(3):
                    try:
                        response = json_parser(self.llm.chat(prompt))
                        winner = response["winner"]
                        result["winner"][dim] = winner
                        # result["explanation"][dim] = response["explanation"]
                        break
                    except Exception as e:
                        print(f"Parsing failure! {i+1}th tries. Error:", e)

            self.eval_result[method]["winner"] = result
            return self.eval_result[method]["winner"]["winner"]
        elif mode == "free":
            dimensions = list(SCORING_PROMPT_DICT_FREE_MODE["dimensions"].keys())
            template = SCORING_PROMPT_DICT_FREE_MODE["comparison_template"]
            for dim in dimensions:
                if dim in evaled_dims:continue
                criteria = SCORING_PROMPT_DICT_FREE_MODE["dimensions"][dim]
                prompt = template.format(**{
                "dimension_name":dim,
                "criteria":criteria,
                "source":self.source,
                "major_characters": self._get_roles_name(),
                "character_profiles": self._get_roles_info_text(),
                "text1":bookworld_text,
                "text2":method_text,
                "method1":"bookworld",
                "method2":method,
                })
                for i in range(3):
                    try:
                        response = json_parser(self.llm.chat(prompt))
                        winner = response["winner"]
                        result["winner"][dim] = winner
                        # result["explanation"][dim] = response["explanation"]
                        break
                    except Exception as e:
                        print(f"Parsing failure! {i+1}th tries. Error:", e)
                        print(response)

            self.eval_result[method]["winner"] = result
            return self.eval_result[method]["winner"]["winner"]
    
    def ttcw_test(self,text,method):
        if method in self.eval_result and "ttcw_detail" in self.eval_result[method]:
            return self.eval_result[method]["ttcw_detail"],self.eval_result[method]["ttcw_score"]
        ttcw_question_dict = TTCW_PROMPT_DICT["ttcw_question_dict"]
        TTCW_SYSTEM_PROMPT = TTCW_PROMPT_DICT["ttcw_template"]
        result_dic = {}
        score_dic = {}
        all_yes,all_no = 0,0
        for dim in ttcw_question_dict:
            num_yes,num_no = 0,0
            result_dic[dim] = {}
            for subdim in ttcw_question_dict[dim]:
                question = ttcw_question_dict[dim][subdim]
                prompt = TTCW_SYSTEM_PROMPT.format(**{
                    "text":text,
                    "question":question
                })
                result = self.llm.chat(prompt).lower()
                if "yes" in result :
                    result_dic[dim][subdim] = 'yes'
                    num_yes += 1
                elif "no" in result :
                    result_dic[dim][subdim] = 'no'
                    num_no += 1
            all_yes += num_yes
            all_no += num_no
            score_dic[dim] = num_yes / (num_yes + num_no)
        score_dic['all'] = all_yes / (all_yes + all_no)
        if not method in self.eval_result:
            self.eval_result[method] = {}
        self.eval_result[method]["ttcw_detail"] = result_dic
        self.eval_result[method]["ttcw_score"] = score_dic

        return self.eval_result[method]["ttcw_detail"],self.eval_result[method]["ttcw_score"]
    
    def save_generated_text(self, method, text):
        self.generated_script[method] = text
        
    def _get_roles_name(self,):

        return ", ".join([role_info["nickname"] for role_info in self.roles_info.values()])

    def _get_roles_info_text(self,):
        info_text = ""
        for role_code in self.roles_info:
            nickname = self.roles_info[role_code]["nickname"]
            profile = self.roles_info[role_code]["profile"]
            info_text += f"{nickname}: {profile}\n"
        return info_text
    
    def __getstate__(self):
        state = {key: value for key, value in self.__dict__.items() 
                if isinstance(value, (str, int, list, dict, float, bool, type(None)))
                and (key not in ['llm','embedding','db']
                and "PROMPT" not in key)
                }
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def save_to_file(self, root_dir):
        filename = os.path.join(root_dir, f"./eval_agent.json")
        save_json_file(filename, self.__getstate__() )

    def load_from_file(self, root_dir):
        print("Load eval results")
        filename = os.path.join(root_dir, f"./eval_agent.json")
        if os.path.exists(filename):
            state = load_json_file(filename)
            self.__setstate__(state)  
