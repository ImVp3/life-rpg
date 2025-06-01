import os
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain import LLMChain
from langchain.llms import GooglePalm
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
import re
from typing import List, Union, Tuple
import json
import aiosqlite
import asyncio
from database.db import get_user, add_user, get_all_quests, get_user_quests, add_user_quests, claim_quest, reward_user, add_habit, get_user_habits, mark_habit_done, reward_stat_from_habit, try_level_up, exp_needed_for_level


# Định nghĩa các tools cho Agent
tools = [
    Tool(
        name="get_user",
        func=lambda user_id: asyncio.run(get_user(user_id)),
        description="Lấy thông tin người dùng từ database."
    ),
    Tool(
        name="add_user",
        func=lambda user_id, username: asyncio.run(add_user(user_id, username)),
        description="Thêm người dùng mới vào database."
    ),
    Tool(
        name="get_all_quests",
        func=lambda: asyncio.run(get_all_quests()),
        description="Lấy danh sách tất cả nhiệm vụ."
    ),
    Tool(
        name="get_user_quests",
        func=lambda user_id: asyncio.run(get_user_quests(user_id)),
        description="Lấy danh sách nhiệm vụ của người dùng."
    ),
    Tool(
        name="add_user_quests",
        func=lambda user_id, quest_ids: asyncio.run(add_user_quests(user_id, quest_ids)),
        description="Thêm nhiệm vụ cho người dùng."
    ),
    Tool(
        name="claim_quest",
        func=lambda user_id, quest_id: asyncio.run(claim_quest(user_id, quest_id)),
        description="Nhận thưởng nhiệm vụ."
    ),
    Tool(
        name="reward_user",
        func=lambda user_id, exp, gold: asyncio.run(reward_user(user_id, exp, gold)),
        description="Thưởng EXP và Gold cho người dùng."
    ),
    Tool(
        name="add_habit",
        func=lambda user_id, habit_id, name, stat_gain, base_exp: asyncio.run(add_habit(user_id, habit_id, name, stat_gain, base_exp)),
        description="Thêm thói quen mới cho người dùng."
    ),
    Tool(
        name="get_user_habits",
        func=lambda user_id: asyncio.run(get_user_habits(user_id)),
        description="Lấy danh sách thói quen của người dùng."
    ),
    Tool(
        name="mark_habit_done",
        func=lambda user_id, habit_id: asyncio.run(mark_habit_done(user_id, habit_id)),
        description="Đánh dấu thói quen đã hoàn thành."
    ),
    Tool(
        name="reward_stat_from_habit",
        func=lambda user_id, stat_gain, exp: asyncio.run(reward_stat_from_habit(user_id, stat_gain, exp)),
        description="Thưởng chỉ số và EXP từ thói quen."
    ),
    Tool(
        name="try_level_up",
        func=lambda user_id: asyncio.run(try_level_up(user_id)),
        description="Kiểm tra và thực hiện lên cấp cho người dùng."
    ),
    Tool(
        name="exp_needed_for_level",
        func=lambda level: exp_needed_for_level(level),
        description="Tính EXP cần thiết để lên cấp."
    )
]

# Định nghĩa prompt template cho Agent
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""

class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("agent_scratchpad")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += f"\nAction: {action}\nAction Input: {action.input}\nObservation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)

prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    input_variables=["input", "agent_scratchpad"]
)

# Định nghĩa output parser cho Agent
def output_parser(llm_output: str) -> Union[AgentAction, AgentFinish]:
    if "Final Answer:" in llm_output:
        return AgentFinish(
            return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
            log=llm_output,
        )
    regex = r"Action: (.*?)[\n]*Action Input: (.*)"
    match = re.search(regex, llm_output, re.DOTALL)
    if not match:
        return AgentFinish(
            return_values={"output": "I could not determine the next action."},
            log=llm_output,
        )
    action = match.group(1).strip()
    action_input = match.group(2).strip()
    return AgentAction(tool=action, tool_input=action_input, log=llm_output)

class Agent():
    def __init__(self, llm ):
        agent = LLMSingleActionAgent(
            llm_chain=LLMChain(llm=llm, prompt=prompt),
            allowed_tools=[tool.name for tool in tools],
            stop=["\nObservation:"],
            handle_parsing_errors=True
        )

        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    def chat(self, message):
        response = self.agent_executor.invoke({"input": message})
        return response
    