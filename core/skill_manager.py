import importlib
import pkgutil
import inspect
import sys
import os
import json
from typing import Dict, Any

from NOVA.core.llm import LLMHandler
from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
from NOVA.core.logger import logger

from NOVA.core.nlp import NLPHandler
try:
    from NOVA.core.semantic_router import SemanticRouter
except ImportError:
    SemanticRouter = None

class SkillManager:
    def __init__(self, features_pkg="features"):
        self.features_pkg = features_pkg
        self.skills: Dict[str, BaseSkill] = {} # Map intent -> Skill Instance
        self.llm = LLMHandler()
        self.nlp = NLPHandler()
        self.semantic_router = SemanticRouter() if SemanticRouter else None
        self._load_skills()

    def _load_skills(self):
        # loads skills from features pkg
        try:
            # Import the features package to locate it
            package = importlib.import_module(self.features_pkg)
            
            # Walk through modules in the features directory
            for _, name, _ in pkgutil.iter_modules(package.__path__):
                full_name = f"{self.features_pkg}.{name}"
                try:
                    module = importlib.import_module(full_name)
                    # Force reload if already loaded (for Hot Reload)
                    module = importlib.reload(module)
                    
                    # Inspect for BaseSkill subclasses
                    for member_name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) 
                            and issubclass(obj, BaseSkill) 
                            and obj is not BaseSkill):
                            
                            # Instantiate and register
                            skill_instance = obj()
                            logger.info(f"Registering Skill: {skill_instance.name}")
                            
                            for intent in skill_instance.intents:
                                self.skills[intent] = skill_instance
                                logger.debug(f"  -> Bound intent '{intent}' to {skill_instance.name}")
                                
                                # Register intent with semantic router
                                if self.semantic_router:
                                    self.semantic_router.register_intent(intent, skill_instance.description)
                                
                except Exception as e:
                    logger.error(f"Failed to load module {full_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to init features package: {e}")

    def reload_skills(self):
        # reloads all skills
        logger.info("Reloading skills...")
        self.skills.clear()
        self._load_skills()
        logger.info("Skills reloaded.")


    def get_skill(self, class_name):
        for intent, instance in self.skills.items():
             if instance.__class__.__name__ == class_name:
                 return instance
        return None

    def execute_skill(self, intent: str, entities: Dict[str, Any]) -> SkillResponse:
        # runs intent
        logger.info(f"Executing intent: {intent}")
        
        # 1. Check Registry
        if intent in self.skills:
            skill = self.skills[intent]
            try:
                # TODO: Permission Check Here
                return skill.execute(entities)
            except Exception as e:
                logger.error(f"Error executing skill {skill.name}: {e}")
                return SkillResponse(text=f"Error executing skill: {e}", success=False)
                
        # 2. Built-in Handlers (Legacy/Hardcoded or Meta)
        elif intent == "greet":
             return SkillResponse(text="Hello! How can I help you? [Legacy]")
        elif intent == "exit":
             return SkillResponse(text="Goodbye! Shutting down.", success=True)
             
        # 3. LLM Fallback
        else:
            user_msg = entities.get("raw_text", "Hello")
            logger.info("Intent unknown. Delegating to LLM.")
            llm_text = self.llm.generate(f"The user said: '{user_msg}'. Respond as NOVA/Jarvis.")
            return SkillResponse(text=llm_text, success=True)

    def route_request(self, text: str) -> SkillResponse:
        # routes input via nlp or llm
        import time
        start_time = time.time()
        
        # 1. Fast NLP Processing (Regex/Pattern)
        # Note: We assume Main passes us the raw text, but Main currently uses 'nlp'.
        # For this refactor, SkillManager will now own the NLP instance or we pass it?
        # Ideally SkillManager owns it or uses a passed one. 
        # For now, I'll instantiate NLP if not present, OR Main calls nlp.process first?
        # User requested: "route_input(text)" which implies Manager handles it.
        # But `SkillManager` currently doesn't have `self.nlp`.
        # I should assume Main.py might still own NLP or pass it. 
        # BUT, the cleaner architecture is SkillManager has NLP.
        # I'll rely on Main.py passing intent/entities? No, the prompt specifically says "route_input(user_text)".
        # So I will IMPORT NLPHandler here.
        
        nlp = self.nlp # Use the NLPHandler instance from __init__
        
        intent, entities, confidence = nlp.process(text)
        
        route_type = "UNKNOWN"
        response = None
        
        # 2. Logic Dispatcher
        if confidence > 0.7 and intent in self.skills:
            route_type = "SKILL"
            logger.info(f"Routing to Skill: {intent} (Conf: {confidence})")
            try:
                response = self.skills[intent].execute(entities)
            except Exception as e:
                logger.error(f"Skill Error: {e}")
                response = None

        # 2a. Semantic Routing (Vector Search)
        if not response and self.semantic_router:
            try:
                sem_intent, sem_score = self.semantic_router.route(text)
                # Threshold of 0.65 (tune based on all-MiniLM)
                if sem_intent and sem_score > 0.65: 
                    if sem_intent in self.skills:
                        logger.info(f"Semantic Routing: '{text}' -> {sem_intent} ({sem_score:.2f})")
                        route_type = f"SEMANTIC[{sem_intent}]"
                        # We lack entities. We can try blank execute or delegate to LLM with hint?
                        # For now, let's treat it as a strong hint for the LLM Router or execute if simple.
                        # Simple skills (like 'set_alarm') need entities.
                        # Complex skills (like 'weather') can handle defaults.
                        # Strategy: If Semantic match is strong, use LLM to EXTRACT slots for that intent.
                        # Use LLM-TOOL route logic but forced intent.
                        
                        # FORCE LLM ROUTER with Hint?
                        # ACTUALLY, sticking to the Implementation Plan: 
                        # "Semantic Routing... Return top Skill."
                        # If I execute `self.skills[sem_intent].execute({})`:
                        # Weather -> IP Weather (Works)
                        # Scheduler -> "When?" (Works)
                        # Google -> "What search?" (Works)
                        # So it's safe to execute with empty entities!
                        response = self.skills[sem_intent].execute({})
            except Exception as e:
                logger.error(f"Semantic Router Error: {e}")
        
        # 3. Fallback / Low Confidence
        # 3. Fallback / Low Confidence -> LLM Tool Router
        if not response:
            route_type = "LLM-ROUTER"
            logger.info(f"Routing to GPT Router (Intent: {intent}, Conf: {confidence})")
            
            # Prepare Tool List for Prompt
            tool_list = []
            seen_intents = set()
            for s_intent, skill in self.skills.items():
                if s_intent not in seen_intents:
                    tool_list.append({
                        "tool": s_intent,
                        "desc": getattr(skill, 'description', 'No desc'),
                        "args": getattr(skill, 'slots', {})
                    })
                    seen_intents.add(s_intent)
            
            prompt = f"""You are NOVA. Decide if you should use a tool or chat. 
Tools: {json.dumps(tool_list)}

User: {text}

Output JSON ONLY:
{{
  "tool": "intent_name" or null,
  "args": {{ "arg_name": "value" }} or null,
  "response": "Your conversational response here"
}}
"""
            model = "gpt-3.5-turbo" 
            
            try:
                llm_output = self.llm.generate(prompt, model=model)
                # Cleaning to ensure JSON
                if "```json" in llm_output:
                    llm_output = llm_output.split("```json")[1].split("```")[0].strip()
                elif "```" in llm_output:
                    llm_output = llm_output.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(llm_output)
                
                tool_name = parsed.get("tool")
                tool_args = parsed.get("args") or {}
                conversational_text = parsed.get("response") or ""
                
                if tool_name and tool_name in self.skills:
                    route_type = f"LLM-TOOL[{tool_name}]"
                    logger.info(f"LLM Selected Tool: {tool_name}")
                    # Execute
                    skill_res = self.skills[tool_name].execute(tool_args)
                    
                    # SYNTHESIS STEP
                    # Instead of returning raw skill text, use LLM to synthesize answer
                    # This enables "Should I bring an umbrella?" -> (Weather Data) -> "Yes, because..."
                    tool_out = skill_res.text
                    synth_prompt = f"""User asked: "{text}"
Tool '{tool_name}' output: "{tool_out}"

Synthesize a helpful, conversational response based on the tool output. 
Do not explicitly mention using a tool.
"""
                    logger.info("Synthesizing response...")
                    gen = self.llm.generate(synth_prompt, model=model, stream=True)
                    
                    # Create new response with stream
                    response = SkillResponse(
                        text="", 
                        intent=tool_name, 
                        success=skill_res.success,
                        data=skill_res.data,
                        visual=skill_res.visual,
                        is_streaming=True,
                        iterator=gen
                    )
                else:
                    route_type = "LLM-CHAT"
                    # STREAMING ENABLED
                    llm_stream = self.llm.generate(conversational_text or text, model=model, stream=True)
                    # If conversational_text came from the JSON, it's just a string, not a stream
                    # But if we want to stream the CHAT generation, we must call generate AGAIN?
                    # Actually, if the Router gave us a response in JSON, it's already generated.
                    # To effectively stream, we should NOT ask the Router to generate the response text in the JSON,
                    # but only decide the tool. If no tool, then we ask LLM to generate chat response WITH streaming.
                    
                    if conversational_text:
                         # Using the pre-generated text (not streamed)
                         response = SkillResponse(text=conversational_text, success=True, intent="gpt_chat")
                    else:
                         # Re-generate with streaming since Router didn't give text
                         gen = self.llm.generate(f"User said: '{text}'. You are NOVA. Respond briefly.", model=model, stream=True)
                         response = SkillResponse(text="", success=True, intent="gpt_chat", is_streaming=True, iterator=gen)
            
            except Exception as e:
                logger.error(f"LLM Parsing Error: {e}")
                # Fallback to simple stream chat
                gen = self.llm.generate(f"User said: '{text}'. Respond.", model=model, stream=True)
                response = SkillResponse(text="", success=True, intent="gpt_chat", is_streaming=True, iterator=gen)
            
        # Ensure intent is set if the skill didn't set it (optional, but good practice)
        if hasattr(response, 'intent') and response.intent == "unknown" and intent != "unknown":
            response.intent = intent

        latency = (time.time() - start_time) * 1000
        logger.info(f"Request handled via {route_type} in {latency:.2f}ms")
        
        return response
