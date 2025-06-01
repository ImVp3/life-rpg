import asyncio
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool

from database.db import (
    get_user, add_user, get_all_quests, get_user_quests, add_user_quests,
    claim_quest, reward_user, add_habit, get_user_habits, mark_habit_done,
    reward_stat_from_habit, try_level_up, exp_needed_for_level
)

class RPGChatbotAgent:
    def __init__(self,
                model_name: str = "gemini-2.0-flash",
                temperature: float = 0.7,
                verbose_mode: bool = True):
        self.model_name = model_name
        self.temperature = temperature
        self.verbose_mode = verbose_mode

        self.llm = self._initialize_llm()
        self.memory = self._initialize_memory()
        self.tools = self._initialize_tools()

        self.agent_prompt = self._initialize_agent_prompt()
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor()

    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature
        )

    def _initialize_memory(self) -> ConversationBufferMemory:
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="user_input"
        )

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool.from_function(
                name="get_user",
                func=get_user,
                coroutine=get_user,
                description="Lấy thông tin người dùng từ cơ sở dữ liệu."
            ),
            Tool.from_function(
                name="add_user",
                func=add_user,
                coroutine=add_user,
                description="Thêm người dùng mới."
            ),
            Tool.from_function(
                name="get_all_quests",
                func=get_all_quests,
                coroutine=get_all_quests,
                description="Lấy danh sách tất cả nhiệm vụ."
            ),
            Tool.from_function(
                name="get_user_quests",
                func=get_user_quests,
                coroutine=get_user_quests,
                description="Lấy nhiệm vụ của người dùng."
            ),
            Tool.from_function(
                name="add_user_quests",
                func=add_user_quests,
                coroutine=add_user_quests,
                description="Thêm nhiệm vụ cho người dùng."
            ),
            Tool.from_function(
                name="claim_quest",
                func=claim_quest,
                coroutine=claim_quest,
                description="Nhận thưởng nhiệm vụ."
            ),
            Tool.from_function(
                name="reward_user",
                func=reward_user,
                coroutine=reward_user,
                description="Thưởng EXP và vàng cho người dùng."
            ),
            Tool.from_function(
                name="add_habit",
                func=add_habit,
                coroutine=add_habit,
                description="Thêm thói quen cho người dùng."
            ),
            Tool.from_function(
                name="get_user_habits",
                func=get_user_habits,
                coroutine=get_user_habits,
                description="Lấy danh sách thói quen."
            ),
            Tool.from_function(
                name="mark_habit_done",
                func=mark_habit_done,
                coroutine=mark_habit_done,
                description="Đánh dấu thói quen hoàn thành."
            ),
            Tool.from_function(
                name="reward_stat_from_habit",
                func=reward_stat_from_habit,
                coroutine=reward_stat_from_habit,
                description="Thưởng chỉ số từ thói quen."
            ),
            Tool.from_function(
                name="try_level_up",
                func=try_level_up,
                coroutine=try_level_up,
                description="Kiểm tra và lên cấp."
            ),
            Tool.from_function(
                name="exp_needed_for_level",
                func=exp_needed_for_level,
                coroutine=exp_needed_for_level,
                description="Tính EXP cần để lên cấp."
            )
        ]


    def _initialize_agent_prompt(self) -> ChatPromptTemplate:
        system_template = (
            "Bạn là một trợ lý RPG tương tác, chuyên hỗ trợ người dùng trong việc quản lý nhiệm vụ, thói quen và phần thưởng như EXP, vàng, hoặc thăng cấp. "
            "Sử dụng các công cụ bạn có để thực hiện điều đó."
        )

        system_prompt = SystemMessagePromptTemplate.from_template(system_template)

        return ChatPromptTemplate.from_messages([
            system_prompt,
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{user_input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

    def _create_agent(self):
        return create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_prompt,
        )

    def _create_agent_executor(self) -> AgentExecutor:
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose_mode,
            handle_parsing_errors=True
        )

    async def chat(self, user_input: str) -> str:
        try:
            response = await self.agent_executor.ainvoke({"user_input": user_input})
            return response.get("output", "Xin lỗi, tôi không thể xử lý yêu cầu lúc này.")
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý của RPG Agent: {e}")
            return "Đã xảy ra lỗi. Vui lòng thử lại sau."
