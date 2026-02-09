### Stream Thought Process

To stream your agent's thought process and tool calls in real-time, use 

stream=True with stream_events=True:
```python
from agno.agent import Agent, RunEvent
from agno.models.openai import OpenAIResponses
from agno.tools.hackernews import HackerNewsTools

agent = Agent(
    model=OpenAIResponses(id="gpt-4o"),
    tools=[HackerNewsTools()],
)

stream = agent.run("What's trending?", stream=True, stream_events=True)

for chunk in stream:
    if chunk.event == RunEvent.run_content:
        print(f"Content: {chunk.content}")
    elif chunk.event == RunEvent.tool_call_started:
        print(f"Tool started: {chunk.tool.tool_name}")
    elif chunk.event == RunEvent.tool_call_completed:
        print(f"Tool completed")
    elif chunk.event == RunEvent.reasoning_step:
        print(f"Reasoning: {chunk.reasoning_content}")
```



### Debug Mode
Enable debug_mode=True to inspect messages, tool calls, and metrics:

```python
agent = Agent(
    model=OpenAIResponses(id="gpt-4o"),
    tools=[HackerNewsTools()],
    debug_mode=True,  # Shows execution flow
    # debug_level=2,  # More detailed logs
)
```