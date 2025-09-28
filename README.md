# BookWorld: Interactive Multi-Agent Story Creation System

<div align="center">

🖥️ [Project Page](https://bookworld2025.github.io/) | 📃 [Paper](https://arxiv.org/abs/2504.14538) | 🤗 [Demo](https://huggingface.co/spaces/alienet/BookWorld)

</div>




This is the official implementation of the paper "BOOKWORLD: From Novels to Interactive Agent Societies for Story Creation".

<a href="https://ibb.co/TBTf350n"><img src="https://i.ibb.co/tMhGr52N/Preview.png" alt="Preview" border="0"></a>
## Update
[2025-09-02]
#### ChromaDB Enhancements
Fixed several critical bugs in ChromaDB implementation, improving stability and reliability of database operations. The update focuses on better data persistence and retrieval functionality.

#### Flexible Embedding Configuration
You can now easily switch between different embedding models through configuration in `embedding.py`. The system supports both online API services and local models. Simply modify the model dictionary in the configuration file to use your preferred embedding solution.


## Introduction

BookWorld is a comprehensive system for social simulation in fictional worlds through multi-agent interactions. The system features:

- Scene-based story progression with multiple character agents
- Continuous updating of agent memories, status, and goals
- World agent orchestration of the simulation
- Support for human intervention and control
- LLM-based story generation and refinement

## Setup

### Step 1. Clone the repository
```bash
git clone https://github.com/your-repo/bookworld.git
cd bookworld
```

### Step 2.Install dependencies
Conda
```bash
conda create -n bookworld python=3.10
conda activate bookworld
pip install -r requirements.txt
```
Docker
```bash
docker build -t bookworld .
```

### Step 3. Configure Simulation Settings
Fill in the configuration parameters in `config.json`:
  - `role_llm_name`: LLM model for character roles
  - `world_llm_name`: LLM model for world simulation
  - `preset_path`: The path to the experiment preset
  - `if_save`: Enable/disable saving (1/0)
  - `scene_mode`: Scene progression mode
  - `rounds`: Number of simulation rounds
  - `mode`: Simulation mode ("free" or "script")

Then enter the API key of the LLM provider you're using either in `config.json` or through the frontend interface.

## Usage

### Step 1. Start the server
```bash
python server.py
```
or
```bash
uvicorn server:app --host 127.0.0.1 --port 8000  
```
Docker
```bash 
docker run -p 7860:7860 bookworld
```

### Step 2. Access the web interface
Open a browser and navigate to:
- Local Python: http://localhost:8000
- Local Docker: http://localhost:7860

### Step 3. Interact with the system
- Start/pause/stop story generation
- View character information and map details
- Monitor story progression and agent interactions
- Edit generated content if needed

### Step 4. Continue from previous simulation
1. Locate the directory of the previous simulation within `/experiment_saves/`
2. Set its path to the `save_dir` field in `config.json`. Ensure that the selected directory directly contains `server_info.json` and `world_agent.json`.

## Customization
### Construct Your Virtual World Manually
1. Create the roles, map, worldbuilding following the examples given in `/data/`. Additionally, you can place an image named `icon.(png/jpg)` inside the character's folder — this will be used as the avatar displayed in the interface.
2. You can improve the simulation quality by providing background settings about the world in `world_details/` or put character dialogue lines in `role_lines.jsonl`. 
3. Enter the preset path to `preset_path` in `config.json`.

### Extract Role, Location, and Setting Data Automatically

Utilize the script provided in `/extract_data/` to extract key story elements using LLMs.

<font color="red">
⚠️ Note: We are sorry that the extraction code is currently unstable and may not produce reliable results. We recommend manually entering the character profiles and descriptions, or using data from sources such as Wikipedia. You can quickly generate a template for location and character information by setting <code>if_auto_extract</code> to 0 in <code>extract_config.json</code>.
</font>
<br><br>

**1. Configure the extraction model and API key in `extract_config.json`:**

* `book_path`: Path to the input book file. We currently support `.epub` (recommended), `.pdf`, and `.txt` formats.
* `language`: The language of the book (e.g., `en`, `zh`). If not specified, the program will attempt to detect it automatically.
* `book_source`: The title or name of the book. If omitted, the program will try to infer it from the file.
* `target_character_names`: A list of characters to extract information about. It's best to use names or nicknames that appear most frequently in the text, rather than full formal names. If not provided, the program will attempt to extract them automatically. **For higher-quality results, we strongly recommend specifying this field.**
* `target_location_names`: A list of important locations. Again, using the most frequently occurring name or common synonym improves accuracy. If omitted, locations will be extracted automatically. **For higher-quality results, we strongly recommend specifying this field.**

**2. Run the script**

  Characters and Locations

  ```bash
  python extract_data.py
  ``` 

  Settings

  ```bash
  python extract_settings.py
  ```

### Convert SillyTavern Character Cards to Role Data

1. Put your character cards in `/data/sillytavern_cards/`.
2. Run the script. It will convert all the cards into the role data that BookWorld needs.
```bash
python convert_sillytavern_cards_to_data.py
```
3. Input role codes of all the characters participating in this simulation to `role_agent_codes` in the preset file.

## Directory Structure

```
.
├── data/
├── frontend/
│   ├── assets/
│   ├── css/
│   └── js/
├── modules/
│   ├── db/
│   ├── llm/
│   ├── prompt/
│   ├── main_role_agent.py
│   └── world_agent.py
├── experiment_configs/
├── BookWorld.py
├── server.py
├── config.json
└── index.html
```


## Authors and Citation
**Authors:** Yiting Ran, Xintao Wang, Tian Qiu,
Jiaqing Liang, Yanghua Xiao, Deqing Yang.

```bibtex
@inproceedings{ran2025bookworld,
  title={BOOKWORLD: From Novels to Interactive Agent Societies for Story Creation},
  author={Ran, Yiting and Wang, Xintao and Qiu, Tian and Liang, Jiaqing and Xiao, Yanghua and Yang, Deqing},
  booktitle={Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  pages={15898--15912},
  year={2025}
}
```
## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).


##  Acknowledgements

- Fantasy Map: The background of map panel used in the frontend is from [Free Fantasy Maps](https://freefantasymaps.org/epic-world-cinematic-landscapes/), created by Fantasy Map Maker. This map is free for non-commercial use.

## Contact

BookWorld is a foundational framework that we aim to continuously optimize and enrich with custom modules. We welcome and greatly appreciate your suggestions and contributions!

If you have any suggestions or would like to contribute, please contact us at: alienet1109@163.com

