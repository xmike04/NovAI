import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

from NOVA.core.persona import persona_manager

class LLMHandler:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.local_llm_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
        self.local_model = os.getenv("LOCAL_LLM_MODEL", "llama3") 
        
        if self.openai_key:
            openai.api_key = self.openai_key
            print("LLM: OpenAI API Key found. Online mode enabled.")
        else:
            print("LLM: No OpenAI API Key found. Defaulting to Offline mode.")

    def is_online(self):
        # checks internet
        try:
            requests.get("https://www.google.com", timeout=2)
            return True
        except requests.ConnectionError:
            return False

    def generate(self, prompt, model="gpt-3.5-turbo", max_tokens=150, system_prompt=None, stream=False):
        # runs llm
        if self.is_online() and self.openai_key:
            return self._generate_openai(prompt, model, max_tokens, system_prompt, stream)
        else:
            return self._generate_local(prompt, system_prompt, stream)

    def _generate_openai(self, prompt, model="gpt-3.5-turbo", max_tokens=150, system_prompt=None, stream=False):
        try:
            client = openai.OpenAI(api_key=self.openai_key)
            
            # Use provided prompt OR global persona
            sys_msg = system_prompt if system_prompt else persona_manager.get_prompt()
            
            response = client.chat.completions.create(
                model=model, 
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Wrap the OpenAI stream to yield strings
                def generator():
                    for chunk in response:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
                return generator()
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI Error: {e}. Falling back to local.")
            return self._generate_local(prompt, system_prompt, stream)

    def _generate_local(self, prompt, system_prompt=None, stream=False):
        # runs local llm
        print(f"LLM: Using Local Fallback ({self.local_model})...")
        sys_msg = system_prompt if system_prompt else persona_manager.get_prompt()
        
        # Prepend system prompt to user prompt for local models (basic concatenation)
        full_prompt = f"System: {sys_msg}\nUser: {prompt}"
        
        try:
            payload = {
                "model": self.local_model,
                "prompt": full_prompt,
                "stream": stream
            }
            # If streaming, we return a generator wrapper
            if stream:
                 # Note: requests.post with stream=True returns raw chunks
                 # Ollama returns valid JSON chunks per line
                 response = requests.post(self.local_llm_url, json=payload, stream=True, timeout=10)
                 def generator():
                     if response.status_code == 200:
                         for line in response.iter_lines():
                             if line:
                                 try:
                                     json_chunk = requests.utils.json.loads(line)
                                     yield json_chunk.get("response", "") 
                                 except:
                                     pass
                     else:
                        yield f"Error: {response.status_code}"
                 return generator()

            response = requests.post(self.local_llm_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                return f"Local LLM Error: {response.status_code}"
        except requests.ConnectionError:
            return "NOVA: I am offline and cannot reach the Local LLM (Ollama). Please ensure it is running."
        except Exception as e:
            return f"Local LLM Failed: {e}"
