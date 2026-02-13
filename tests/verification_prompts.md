# NOVA System Verification Prompts

Here are 20 prompts to test every aspect of the NOVA system.
Run these via Voice (after "Jarvis") or type them into the debug/chat input.

## Core & Identity
1. **"Hello, who are you?"**
   *Expected*: "I am NOVA..." (Verifies System Prompt & Persona).
2. **"Tell me a joke."**
   *Expected*: A joke from OpenAI/Ollama. (Verifies LLM Connectivity).

## Profile & Memory
3. **"My name is [Your Name]."**
   *Expected*: "Okay, I'll call you [Name]..." (Verifies Profile Skill).
4. **"What is my name?"**
   *Expected*: "[Your Name]" (Verifies Profile Persistence).
5. **"I like coding in Python."**
   *Expected*: "Noted." (Verifies Fact Storage).
6. **"What programming language do I like?"**
   *Expected*: "Python." (Verifies Memory/Context Injection).

## External APIs
7. **"What is the weather in Tokyo?"**
   *Expected*: Current weather details. (Verifies Weather Skill).
8. **"Play Despacito on YouTube."**
   *Expected*: Opens YouTube in browser. (Verifies YouTube Skill).

## Agent Actions (Device & Schedule)
9. **"Open Calculator."**
   *Expected*: Calculator app opens. (Verifies AppControl Open).
10. **"Close Calculator."**
    *Expected*: Calculator app quits. (Verifies AppControl Close).
11. **"Close NOVA."**
    *Expected*: "I cannot close NOVA..." (Verifies Safety Sandbox).
12. **"Remind me to stretch in 10 seconds."**
    *Expected*: "Set reminder..." -> Wait 10s -> "Attention: stretch". (Verifies Scheduler).

## Knowledge (RAG)
13. **"Ingest document requirements.txt."**
    *Expected*: "Ingested..." (Verifies Knowledge Skill Ingestion).
14. **"What libraries are in the requirements file?"**
    *Expected*: Lists libraries like `openai`, `chromadb`. (Verifies Semantic Retrieval).

## Workflows & Reasoning
15. **"Create workflow Morning Test: Open Calculator, wait 2 seconds, What is the weather."**
    *Expected*: "Created workflow 'Morning Test'..." (Verifies Workflow Creation).
16. **"Run Morning Test."**
    *Expected*: Opens app -> waits -> speaks weather. (Verifies Workflow Execution).
17. **"Decompose task: Plan a dinner party."**
    *Expected*: "Broken down into 5 steps..." -> Executes steps. (Verifies Reasoning Engine).

## System & DX
18. **"Set log level to DEBUG."**
    *Expected*: "Log Level changed..." (View logs to see verbose output).
19. **"Reload skills."**
    *Expected*: "Skills reloaded." (Verifies Hot Reload).
20. **"Shutdown System."**
    *Expected*: Goodbye message and app exit (if implemented) or graceful stop.
