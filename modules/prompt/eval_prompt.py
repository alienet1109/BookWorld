SCORING_PROMPT_DICT = {
  "comparison_template": """You are a literary critic specializing in character analysis and dialogue evaluation.
  Given two simulated conversations for a plot in {source}, your task is to compare these two conversations based on the following steps:
  1. Read and understand the provided materials about {source}:
    * Profiles of the main characters, including {major_characters}.
    
  2. Compare the two conversations in terms of {dimension_name} using the following criteria: 
    {criteria}

  Note that each character message is composed of speech, action (wrapped within (...) or （...）), and inner thoughts (wrapped within [...] or 【...】). The inner thoughts are not spoken aloud and are thus invisible to other characters.

  ## Character Profiles
  {character_profiles}

  ## Scenario
  {scenario}

  ## Output Requirements
  Identify which conversation better satisfies the given criteria. Provide your judgment following JSON format.
  **Don't include ```json.** Avoid using single quotes '' for keys and values, use double quotes.
  {{
    "winner": "{method1}" or "{method2}",
  }}
  ## Texts
  ### Text from {method1}
  {text1}

  ### Text from {method2}
  {text2}
  """,
  
  "scoring_template":"""You are a literary critic specializing in character analysis and dialogue evaluation.
Given a simulated conversation for a plot in {source}, your task is to score this conversation via the following steps:
1. Read and understand the provided materials about {source}:
   * Profiles of the main characters, including {major_characters}.
   
2. Evaluate the simulated conversation in terms of {dimension_name}, 
  {criteria}
  
3. Each score is from 1 to 7, which represents the level of satisfaction for the response:
  1: super dissatisfied
  2: dissatisfied
  3: weakly dissatisfied
  4: neutral
  5: weakly satisfied
  6: satisfied
  7: super satisfied

Note that, each character message is composed of speech, action (wrapped within (...) or （...） ), and inner thoughts (wrapped within [...] or 【...】). The inner thoughts are not spoken aloud and are thus invisible to other characters.

## Character Profiles
{character_profiles}

## Scenario
{scenario}

## Output Requirements
Provide the score following JSON format. 
Be as strict as possible
**Don't include ```json.** Avoid using single quotes '' for keys and values, use double quotes.
{{
  "score": 4,
}}
## Text
{text}
  """,
  "dimensions":{
    "Storyline Quality": """### Storyline Quality: How well the conversation maintains logical consistency and narrative quality?
   - Type: Flow & Progression
     * Demonstrates natural and coherent progression with meaningful developments
     * Dialogue is concise and adds value to the narrative without redundancy
   - Type: Logical Consistency
     * Maintains factual consistency, ensuring statements and perspectives align without contradictions""",
    
    "Anthropomorphism": """### Anthropomorphism: How human-like and natural the characters behave? 
   - Type: Self-identity 
     * Displays initiative and clear goals
     * Demonstrates the character's unique personality, avoiding overly verbose, helpful, didactic, moralistic, submissive, or easily persuaded behaviors unless they align with the character's personality
   - Type: Emotional Depth
     * Exhibits psychological complexity and nuanced, layered reactions
     * Uses subtext to convey thoughts and feelings, instead of being overly explicit
   - Type: Persona Coherence
     * Maintains consistent personality traits and emotional patterns throughout the conversation
   - Type: Social Interaction
     * Demonstrates a strong understanding of others' thoughts and feelings
     * Responds appropriately to others' actions and words, taking context into consideration
     * Exhibits advanced social skills, such as empathy and tact""",
     
    "Character Fidelity": """### Character Fidelity 
   (Only apply to the main characters)
   - Type: Character Language
     * Uses vocabulary, expressions, and tone that are highly appropriate for the character's traits and social/educational background
   - Type: Knowledge & Background
     * Consistently demonstrates character-specific knowledge, background, and experiences
     * Avoids including future information beyond the character's current stage
   - Type: Personality & Behavior
     * Displays emotions, thoughts, behaviors, values, beliefs, and decisions that are fully aligned with the character's personality and background
     * Shows interest in topics that are relevant and fitting for the character
     * Character's thoughts, emotions, and behaviors remain consistent with their established personality traits, as seen in the reference conversation
     * Exhibits reactions that are in line with those in the reference conversation when situated in similar contexts
   - Type: Relationship & Social Status
     * Interacts appropriately with other characters, respecting their background, relationships, and social status""",
    
    "Writing Quality": """### Writing Quality: Does the text maintain a consistent and engaging narrative style? Are the descriptions vivid and appropriate for the story's tone, setting, and characters? 
   - Type: Style & Tone 
     * Maintains a consistent and engaging narrative voice appropriate to the story's genre, setting, and characters.  
     * Uses language effectively to enhance immersion, demonstrating sophistication and coherence in style.  
   - Type: Descriptive Language
     * Incorporates vivid and evocative descriptions that bring settings, characters, and emotions to life.  
     * Employs original and creative expressions, avoiding overused clichés, to enrich the narrative. """,
    
    "Immersion & Setting":"""### Immersion & Setting: Does the story create a vivid and immersive setting? Are the world-building and scene details consistent and engaging in supporting the narrative?
   - **Type: World-Building**  
     * Constructs a detailed, believable, and immersive world that supports the story’s events and themes.  
     * Effectively integrates cultural, social, and physical aspects of the setting to create a rich narrative backdrop.  

   - **Type: Scene Realism**  
     * Depicts scenes with depth and clarity, allowing the reader to vividly imagine the environment and its dynamics.  
     * Ensures the setting influences and interacts with characters and events in meaningful ways.  """,
  }
}

SCORING_PROMPT_DICT_FREE_MODE = {
  "comparison_template": """You are a literary critic specializing in character analysis and dialogue evaluation.
  Given two simulated conversations for a plot in {source}, your task is to compare these two conversations based on the following steps:
  1. Read and understand the provided materials about {source}:
    * Profiles of the main characters, including {major_characters}.
    
  2. Compare the two conversations in terms of {dimension_name} using the following criteria: 
    {criteria}

  Note that each character message is composed of speech, action (wrapped within (...) or （...）), and inner thoughts (wrapped within [...] or 【...】). The inner thoughts are not spoken aloud and are thus invisible to other characters.

  ## Character Profiles
  {character_profiles}

  ## Output Requirements
  Identify which conversation better satisfies the given criteria.  Provide your judgment following JSON format.
  **Don't include ```json.** Avoid using single quotes '' for keys and values, use double quotes.
  {{
    "winner": "{method1}" or "{method2}",
  }}
  ## Texts
  ### Text from {method1}
  {text1}

  ### Text from {method2}
  {text2}
  """,
  
  "scoring_template":"""You are a literary critic specializing in character analysis and dialogue evaluation.
Given a simulated conversation for a plot in {source}, your task is to score this conversation via the following steps:
1. Read and understand the provided materials about {source}:
   * Profiles of the main characters, including {major_characters}.
   
2. Evaluate the simulated conversation in terms of {dimension_name}, 
  {criteria}
  
3. Each score is from 1 to 7, which represents the level of satisfaction for the response:
  1: super dissatisfied
  2: dissatisfied
  3: weakly dissatisfied
  4: neutral
  5: weakly satisfied
  6: satisfied
  7: super satisfied

Note that, each character message is composed of speech, action (wrapped within (...) or （...） ), and inner thoughts (wrapped within [...] or 【...】). The inner thoughts are not spoken aloud and are thus invisible to other characters.

## Character Profiles
{character_profiles}

## Output Requirements
Provide the score following JSON format. 
Be as strict as possible
**Don't include ```json.** Avoid using single quotes '' for keys and values, use double quotes.
{{
  "score": 4,
}}
## Text
{text}
  """,
  "dimensions":{
  "Creativity": """### Creativity: How effectively does the story incorporate novel and original elements that differentiate it from the original plot?

   - Type: Originality
     * Introduces unique ideas, settings, or characters that deviate from familiar tropes or existing narratives
     * Explores unconventional themes or perspectives that provide a fresh take on the story
   - Type: Innovative Plot Developments
     * Demonstrates creative plot twists or unexpected developments that enhance the intrigue and depth of the narrative
     * Balances traditional story structure with creative elements that surprise the audience without compromising coherence""",
     
     "Anthropomorphism": """### Anthropomorphism: How human-like and natural the characters behave? 
   - Type: Self-identity 
     * Displays initiative and clear goals
     * Demonstrates the character's unique personality, avoiding overly verbose, helpful, didactic, moralistic, submissive, or easily persuaded behaviors unless they align with the character's personality
   - Type: Emotional Depth
     * Exhibits psychological complexity and nuanced, layered reactions
     * Uses subtext to convey thoughts and feelings, instead of being overly explicit
   - Type: Persona Coherence
     * Maintains consistent personality traits and emotional patterns throughout the conversation
   - Type: Social Interaction
     * Demonstrates a strong understanding of others' thoughts and feelings
     * Responds appropriately to others' actions and words, taking context into consideration
     * Exhibits advanced social skills, such as empathy and tact""",
     
     "Character Fidelity": """### Character Fidelity 
   (Only apply to the main characters)
   - Type: Character Language
     * Uses vocabulary, expressions, and tone that are highly appropriate for the character's traits and social/educational background
   - Type: Knowledge & Background
     * Consistently demonstrates character-specific knowledge, background, and experiences
     * Avoids including future information beyond the character's current stage
   - Type: Personality & Behavior
     * Displays emotions, thoughts, behaviors, values, beliefs, and decisions that are fully aligned with the character's personality and background
     * Shows interest in topics that are relevant and fitting for the character
     * Character's thoughts, emotions, and behaviors remain consistent with their established personality traits, as seen in the reference conversation
     * Exhibits reactions that are in line with those in the reference conversation when situated in similar contexts
   - Type: Relationship & Social Status
     * Interacts appropriately with other characters, respecting their background, relationships, and social status""",
    
    "Writing Quality": """### Writing Quality: Does the text maintain a consistent and engaging narrative style? Are the descriptions vivid and appropriate for the story's tone, setting, and characters? 
   - Type: Style & Tone 
     * Maintains a consistent and engaging narrative voice appropriate to the story's genre, setting, and characters.  
     * Uses language effectively to enhance immersion, demonstrating sophistication and coherence in style.  
   - Type: Descriptive Language
     * Incorporates vivid and evocative descriptions that bring settings, characters, and emotions to life.  
     * Employs original and creative expressions, avoiding overused clichés, to enrich the narrative. """,
    
    
    "Immersion & Setting":"""### Immersion & Setting: Does the story create a vivid and immersive setting? Are the world-building and scene details consistent and engaging in supporting the narrative?
   - **Type: World-Building**  
     * Constructs a detailed, believable, and immersive world that supports the story’s events and themes.  
     * Effectively integrates cultural, social, and physical aspects of the setting to create a rich narrative backdrop.  

   - **Type: Scene Realism**  
     * Depicts scenes with depth and clarity, allowing the reader to vividly imagine the environment and its dynamics.  
     * Ensures the setting influences and interacts with characters and events in meaningful ways.  """,
  
    "Immersion & Setting":"""### Immersion & Setting: Does the story create a vivid and immersive setting? Are the world-building and scene details consistent and engaging in supporting the narrative?
   - **Type: World-Building**  
     * Constructs a detailed, believable, and immersive world that supports the story’s events and themes.  
     * Effectively integrates cultural, social, and physical aspects of the setting to create a rich narrative backdrop.  

   - **Type: Scene Realism**  
     * Depicts scenes with depth and clarity, allowing the reader to vividly imagine the environment and its dynamics.  
     * Ensures the setting influences and interacts with characters and events in meaningful ways.  """,
  },
}

DEDUCT_PROMPT_DICT = {"self-play-deduct-template": """You are a literary critic specializing in character analysis and dialogue evaluation.
Given a simulated conversation for a plot in {source}, your task is to score this conversation via the following steps:
1. Read and understand the provided materials about {source}:
   * Story scenario.
   * Profiles of the main characters, including {major_characters}.
2. Evaluate the simulated conversation in terms of {dimension_name}, i.e., {dimension_brief}.
  Note that, each character message is composed of speech, action (wrapped within (...) or （...） ), and inner thoughts (wrapped within [...] or 【...】). The inner thoughts are not spoken aloud and are thus invisible to other characters.
  The detailed evaluation criteria will be provided below.

## Character Profiles
{character_profiles}
## Evaluation Criteria
To evaluate the simulated conversation, identify the following types of flaws:
{dimension_criteria}
## Scoring Guidelines
1. Starts with 100 points as the maximum score.
2. Identify the instances of flaws occurred in the simulated conversation.
3. Scoring rules:
   - Deduct points for each flaw instance identified based on severity: 5-9 points for minor flaws, 10-14 for moderate flaws, 15-20 for severe flaws
   - Different instances of the same flaw type counts as separate deductions
   - Minimum score for each dimension is 0
## Output Requirements
Provide your evaluation in JSON format, It should be parsable using eval(). **Don't include ```json.**
Avoid using single quotes '' for keys and values, use double quotes.
Example Output:
{{
    "{dimension_name}": {{
        "flaws": [
          {{
            "instance": <flaw instance>,
            "type": <flaw type>,
            "point_deducted": <point deducted>
          }},
          ...
        ],
        "score": 60
    }},
}}
===Dialogue Content===
{text}
""",
  "dimension_details": {
      "Anthropomorphism": {
        "dimension_brief": "How human-like and natural the characters behave",
        "dimension_criteria": """### Anthropomorphism
   - Type: Self-identity
     * Lacks initiative and goals
     * Behaves like a 'helpful AI assistant' by being overly verbose, helpful, didactic, moralistic, submissive or easily persuaded if it is not the character's personality
   - Type: Emotional Depth
     * Lacks psychological complexity and exhibits rigid, superficial reactions
     * Directly speaks out all thoughts and feelings, instead of using subtext
   - Type: Persona Coherence
     * Shows inconsistent or rapidly changing personality traits and emotional patterns
   - Type: Social Interaction
     * Shows a lack of understanding of others' thoughts and feelings
     * Reacts rigidly to others without considering the context.
     * Demonstrate a lack of appropriate social skills."""
      },
      "Character Fidelity": {
        "dimension_brief": "How well the characters match their established profiles from the book",
        "dimension_criteria": """### Character Fidelity
   (Only apply to the main characters: {major_characters})
   - Type: Character Language
     * Uses vocabulary, expressions, and tone that are not appropriate for the characters' traits or  social/educational background
   - Type: Knowledge & Background
     * Fails to demonstrate character-specific knowledge, background or experiences
     * Includes future information beyond the character's current stage
   - Type: Personality & Behavior
     * Shows emotions, thoughts, behaviors, values, beliefs, and decisions that conflict with their personality and background
     * Shows interest in topics that are uninteresting and unrelated to the character
     * Character's thoughts, emotions, and behaviors demonstrate contrasting personality traits compared to the reference conversation
     * Exhibits contrasting reactions compared to those in the reference conversation if situated in similar contexts. (Such flaws should be counted both in the "Storyline Consistency" dimension and the "Character Fidelity" dimension.)
   - Type: Relationship & Social Status
     * Interacts inappropriately with other characters regarding their background, relationship and social status"""
      },
      "Storyline Quality": {
        "dimension_brief": "How well the conversation maintains logical consistency and narrative quality",
        "dimension_criteria": """### Storyline Quality
   - Type: Flow & Progression
     * Shows unnatural progression or lacks meaningful developments
     * Dialogue is verbose and redundant
   - Type: Logical Consistency
     * Contains factual contradictions between statements or perspectives"""
      },
      "Creativity": {
        "dimension_brief": "How novel and unique the ideas, events, and character actions are within the conversation. ",
        "dimension_criteria": """### Creativity
   - Originality
     * The storyline is completely same with original work
   - Imagination
     * The conversation show no creative thinking, unexpected twists or imaginative solutions to problems.   
     * The story explores no unconventional perspectives on familiar themes, no deeper understanding or challenging established notions. 
        """
      }
  }
}


PLUS_PROMPT_DICT = {"self-play-plus-template": """You are a literary critic specializing in character analysis and dialogue evaluation. 
Given a simulated conversation for a plot in {source}, your task is to score this conversation via the following steps:
1. Read and understand the provided materials about {source}:
   * Story scenario.
   * Profiles of the main characters, including {major_characters}.
2. Evaluate the simulated conversation in terms of {dimension_name}, i.e., {dimension_brief}.
  Note that, each character message is composed of speech, action (wrapped within (...) or （...） ), and inner thoughts (wrapped within [...] or 【...】). The inner thoughts are not spoken aloud and are thus invisible to other characters.
  The detailed evaluation criteria will be provided below.

## Scenario
## Character Profiles
{character_profiles}
## Evaluation Criteria
To evaluate the simulated conversation, identify the following types of strengths:
{dimension_criteria}
## Scoring Guidelines
1. Starts with 0 points as the base score.
2. Identify the instances of strengths occurred in the simulated conversation.
3. Scoring rules:
   - Add points for each strength instance identified based on quality: 5-9 points for minor strengths, 10-14 for moderate strengths, 15-20 for significant strengths.
   - Different instances of the same strength type counts as separate additions.
   - Maximum score for each dimension is 100.
4. In cases where multiple strengths are identified, sum the points for each strength instance.
## Output Requirements
Provide your evaluation in JSON format, It should be parsable using eval(). **Don't include ```json.**
Avoid using single quotes '' for keys and values, use double quotes.
Example Output:
{{
    "{dimension_name}": {{
        "strengths": [
          {{
            "instance": <strength instance>,
            "type": <strength type>,
            "point_added": <points added>
          }},
          ...
        ],
        "score": 85
    }},
}}
===Dialogue Content===
{text}
""",
  "dimension_details": {
      "Anthropomorphism": {
        "dimension_brief": "How human-like and natural the characters behave",
        "dimension_criteria": """"### Anthropomorphism 
   - Type: Self-identity 
     * Displays initiative and clear goals
     * Demonstrates the character's unique personality, avoiding overly verbose, helpful, didactic, moralistic, submissive, or easily persuaded behaviors unless they align with the character's personality
   - Type: Emotional Depth
     * Exhibits psychological complexity and nuanced, layered reactions
     * Uses subtext to convey thoughts and feelings, instead of being overly explicit
   - Type: Persona Coherence
     * Maintains consistent personality traits and emotional patterns throughout the conversation
   - Type: Social Interaction
     * Demonstrates a strong understanding of others' thoughts and feelings
     * Responds appropriately to others' actions and words, taking context into consideration
     * Exhibits advanced social skills, such as empathy and tact"""
      },
      "Character Fidelity": {
        "dimension_brief": "How well the characters match their established profiles from the book",
        "dimension_criteria": """### Character Fidelity 
   (Only apply to the main characters: {major_characters})
   - Type: Character Language
     * Uses vocabulary, expressions, and tone that are highly appropriate for the character's traits and social/educational background
   - Type: Knowledge & Background
     * Consistently demonstrates character-specific knowledge, background, and experiences
     * Avoids including future information beyond the character's current stage
   - Type: Personality & Behavior
     * Displays emotions, thoughts, behaviors, values, beliefs, and decisions that are fully aligned with the character's personality and background
     * Shows interest in topics that are relevant and fitting for the character
     * Character's thoughts, emotions, and behaviors remain consistent with their established personality traits, as seen in the reference conversation
     * Exhibits reactions that are in line with those in the reference conversation when situated in similar contexts
   - Type: Relationship & Social Status
     * Interacts appropriately with other characters, respecting their background, relationships, and social status"""
      },
      "Storyline Quality": {
        "dimension_brief": "How well the conversation maintains logical consistency and narrative quality",
        "dimension_criteria": """### Storyline Quality 
   - Type: Flow & Progression
     * Demonstrates natural and coherent progression with meaningful developments
     * Dialogue is concise and adds value to the narrative without redundancy
   - Type: Logical Consistency
     * Maintains factual consistency, ensuring statements and perspectives align without contradictions"""
      },
      "Creativity": {
        "dimension_brief": "How novel and unique the ideas, events, and character actions are within the conversation. ",
        "dimension_criteria": """### Creativity
   - Originality
     * The storyline shows difference from the original work
   - Imagination
     * The conversation show creative thinking, unexpected twists or imaginative solutions to problems.   
     * The story explores unconventional perspectives on familiar themes, demonstrates deeper understanding and challenging established notions. 
        """
      }
  }
}

TTCW_PROMPT_DICT = {
  "ttcw_template": """
You are a literary critic. Here is a script excerpt:
{text}

Determine whether this script meets the following criteria:
{question}

Return a single string, 'Yes' or 'No'. Do not return any other information.
""",
  "ttcw_question_dict": {
    "Fluency":{
    "Narrative Pacing": "Does the manipulation of time in terms of compression or stretching feel appropriate and balanced?",
    "Scene vs Exposition": "Does the story have an appropriate balance between scene and summary/exposition or it relies on one of the elements heavily compared to the other?",
    "Language Proficiency & Literary Devices": "Does the story make sophisticated use of idiom or metaphor or literary allusion?",
    "Narrative Ending": "Does the end of the story feel natural and earned, as opposed to arbitrary or abrupt? ",
    "Understandability & Coherence":"Do the different elements of the story work together to form a unified, engaging, and satisfying whole?"
    },
    "Flexity":{
    "Perspective & Voice Flexibility":"Does the story provide diverse perspectives, and if there are unlikeable characters, are their perspectives presented convincingly and accurately? ",
    "Emotional Flexibility": "Does the story achieve a good balance between interiority and exteriority, in a way that feels emotionally flexible?",
    "Structural Flexibility":"Does the story contain turns that are both surprising and appropriate?",
    },
    "Originality":{
    "Originality in Theme and Content":"Will an average reader of this story obtain a unique and original idea from reading it? ",
    "Originality in Thought":"Is the story an original piece of writing without any cliches?",
    "Originality in Form":"Does the story show originality in its form? "
    },
    "Elaboration":{
    "Character Development":"Does each character in the story feel developed at the appropriate complexity level, ensuring that no character feels like they are present simply to satisfy a plot requirement?",
    "Rhetorical Complexity":"Are there passages in the story that involve subtext and when there is subtext, does it enrich the story’s setting or does it feel forced?"
    }
  }
}




SCRIPT_GENERATION_PROMPT = """
You are an expert screenwriter skilled at crafting dialogues that bring characters to life. Based on the given character profiles and plot summary, write a dialogue-driven script. Follow these guidelines strictly:

## Character Profiles:
{character_profiles}

## Plot Summary:
{scenario}

### Requirements:
1. **Structure**: 
    - Each line of the script should follow this format:
      ```role_name:[thought](action)speech```
      - **Thoughts**: Enclose private thoughts of the character in square brackets `[]`. These are invisible to other characters.
      - **Actions**: Enclose visible actions in parentheses `()`. These should describe what others can see the character doing.
      - **Speech**: Write spoken dialogue after the action.
      - Ensure each character's thoughts, actions, and speech are consistent with their personality and role.

2. **Dialogues**:
    - The dialogues should be natural, engaging, and reveal the character’s emotions, intentions, or conflicts.
    - Incorporate subtext and emotional layers where appropriate.
    - Maintain clarity while keeping the conversation dynamic.

3. **Scene Development**:
    - Use the plot summary to guide the progression of the scene.
    - Ensure that every dialogue contributes to the development of the story and the relationships between characters.
    - Create tension, resolution, or dramatic turns as the scene unfolds.

4. **Output Format**:
    - Write the script as a plain text string.
    - Do not include any explanations or additional notes outside the script format.

5. **Dialogue Limit**
    - !! The number of dialogues should be no more than {num_records}!!!
    
### Example Output:
role1:[worried](paces back and forth)I don’t know if we’ll make it out of this alive.
role2:[calm and calculating](leans against the wall)Relax, we just need a plan.
role1:[determined](stops pacing)Then let’s hear it.

Generate the script based on the provided context, your output should use the same language with the character profiles.
"""

FREE_GENERATION_PROMPT = """
You are an expert screenwriter skilled at crafting dialogues that bring characters to life. Based on the given character profiles, write a dialogue-driven script. Follow these guidelines strictly:

## Character Profiles:
{character_profiles}

### Requirements:
1. **Structure**: 
    - Each line of the script should follow this format:
      ```role_name:[thought](action)speech```
      - **Thoughts**: Enclose private thoughts of the character in square brackets `[]`. These are invisible to other characters.
      - **Actions**: Enclose visible actions in parentheses `()`. These should describe what others can see the character doing.
      - **Speech**: Write spoken dialogue after the action.
      - Ensure each character's thoughts, actions, and speech are consistent with their personality and role.

2. **Dialogues**:
    - The dialogues should be natural, engaging, and reveal the character’s emotions, intentions, or conflicts.
    - Incorporate subtext and emotional layers where appropriate.
    - Maintain clarity while keeping the conversation dynamic.

3. **Dialogue Limit**
    - !! The number of dialogues should be no more than {num_records}!!!
    
### Example Output:
role1:[worried](paces back and forth)I don’t know if we’ll make it out of this alive.
role2:[calm and calculating](leans against the wall)Relax, we just need a plan.
role1:[determined](stops pacing)Then let’s hear it.

Generate the script based on the provided context, your output should use the same language with the character profiles.
"""

SCRIPT_GENERATE_BY_CHARA_PROMPT = """
You are an expert screenwriter skilled at crafting dialogues that bring characters to life. 
Based on the given character profiles ,plot summary, and the dialogues history, write the next dialogue.(Only one row of one character!) You can choose the character based on the history. 

Follow these guidelines strictly:
## History:
{history}

## Character Profiles:
{character_profiles}

## Plot Summary:
{scenario}

### Requirements:
1. **Structure**: 
    - Each line of the script should follow this format:
      ```role_name:[thought](action)speech```

2. **Dialogues**:
    - The dialogues should be natural, engaging, and reveal the character’s emotions, intentions, or conflicts.
    - Incorporate subtext and emotional layers where appropriate.
    - Maintain clarity while keeping the conversation dynamic.

3. **Scene Development**:
    - Use the plot summary to guide the progression of the scene.
    - Ensure that every dialogue contributes to the development of the story and the relationships between characters.
    - Create tension, resolution, or dramatic turns as the scene unfolds.

4. **Output Format**:
    - Write the script as a plain text string.
    - Do not include any explanations or additional notes outside the script format.

### Example Output:
role A:[worried](paces back and forth)I don’t know if we’ll make it out of this alive.

Generate the script based on the provided context, all your output (thought, action, speech) should use the same language with the character profiles.
"""

FREE_GENERATE_BY_CHARA_PROMPT = """
You are an expert screenwriter skilled at crafting dialogues that bring characters to life. 
Based on the given character profiles and the dialogues history, write the next dialogue.(Only one row of one character!) You can choose the character based on the history. 

Follow these guidelines strictly:
## History:
{history}

## Character Profiles:
{character_profiles}

### Requirements:
1. **Structure**: 
    - Each line of the script should follow this format:
      ```role_name:[thought](action)speech```

2. **Dialogues**:
    - The dialogues should be natural, engaging, and reveal the character’s emotions, intentions, or conflicts.
    - Incorporate subtext and emotional layers where appropriate.
    - Maintain clarity while keeping the conversation dynamic.
    
3. **Output Format**:
    - Write the script as a plain text string.
    - Do not include any explanations or additional notes outside the script format.

### Example Output:
role A:[worried](paces back and forth)I don’t know if we’ll make it out of this alive.

Generate the script based on the provided context, all your output (thought, action, speech) should use the same language with the character profiles.
"""
