
## Specifying prompts for your agents
This documentation explains how to specify a reusable prompt using the dawgpyl library.

To specify a prompt for your agents, follow these steps:

1. Create a new prompt file or edit an existing one in your project directory.
2. Define the prompt content within the file. This can include instructions, questions, or any text that you want the agent to use.
3. Save the prompt file with a descriptive name that reflects its purpose.
4. In your agent's configuration, reference the prompt file by its filepath to load and use the prompt.

Example:

```python
from dawgpyl import Agent

# Load the prompt from a file
with open('path/to/your/prompt.txt', 'r') as file:
    prompt_content = file.read()

# Create an agent and set the prompt
agent = Agent(prompt=prompt_content)

# Use the agent with the specified prompt
response = agent.respond("Your input here")
print(response)
```

By following these steps, you can easily manage and reuse prompts across different agents in your project.


dawgpyl makes it easy to specify reusable prompts for your agents. Simply create 

Simply create an entry into the `PROMPTS` dictionary in the configs/core.py file.


``` 
-8<- "configs/core.py:prompts"

```