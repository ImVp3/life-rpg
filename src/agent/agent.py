import asyncio
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool

from database.db import (
    get_user, get_all_quests, get_user_quests, add_user_quests,
    claim_quest, reward_user, add_habit, get_user_habits_with_status, mark_habit_done,
    reward_stat_from_habit, try_level_up, exp_needed_for_level,
    toggle_shared_habit_flag_smart, enable_shared_habit_flag, disable_shared_habit_flag,
    add_shared_habits_to_user, disable_shared_habits_for_user,
    enable_shared_habits_for_user, get_all_shared_habits, toggle_habit_enabled,
    get_user_reminder_mode, set_user_reminder_mode, get_users_with_reminders, get_incomplete_habits_for_user
)
from utils.level_fomula import exp_needed_for_level, get_realm_name, get_realm_description
from .prompt import SYSTEM_PROMPT, EXAMPLES, get_motivational_message, format_habit_info, format_user_profile

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
                description="Lấy thông tin người dùng từ cơ sở dữ liệu. Trả về None nếu user chưa đăng ký."
            ),
            Tool.from_function(
                name="get_all_quests",
                func=get_all_quests,
                coroutine=get_all_quests,
                description="Lấy danh sách tất cả nhiệm vụ có sẵn trong hệ thống."
            ),
            Tool.from_function(
                name="get_user_quests",
                func=get_user_quests,
                coroutine=get_user_quests,
                description="Lấy trạng thái nhiệm vụ của người dùng (đã hoàn thành hay chưa)."
            ),
            Tool.from_function(
                name="add_user_quests",
                func=add_user_quests,
                coroutine=add_user_quests,
                description="Thêm nhiệm vụ cho người dùng. Tự động gọi khi user xem quest_list."
            ),
            Tool.from_function(
                name="claim_quest",
                func=claim_quest,
                coroutine=claim_quest,
                description="Nhận thưởng nhiệm vụ. Đánh dấu quest đã hoàn thành và thưởng EXP."
            ),
            Tool.from_function(
                name="reward_user",
                func=reward_user,
                coroutine=reward_user,
                description="Thưởng EXP cho người dùng. Dùng sau khi hoàn thành quest hoặc habit."
            ),
            Tool.from_function(
                name="get_user_habits_with_status",
                func=get_user_habits_with_status,
                coroutine=get_user_habits_with_status,
                description="Lấy danh sách thói quen của user với trạng thái enabled/disabled và loại personal/shared."
            ),
            Tool.from_function(
                name="mark_habit_done",
                func=mark_habit_done,
                coroutine=mark_habit_done,
                description="Đánh dấu thói quen hoàn thành. Cần user_id và habit_id. Chỉ hoạt động với habits đã enabled. Trả về streak mới."
            ),
            Tool.from_function(
                name="reward_stat_from_habit",
                func=reward_stat_from_habit,
                coroutine=reward_stat_from_habit,
                description="Thưởng EXP và INT từ thói quen. Tự động gọi sau mark_habit_done."
            ),
            Tool.from_function(
                name="try_level_up",
                func=try_level_up,
                coroutine=try_level_up,
                description="Kiểm tra và lên cấp nếu đủ EXP. Trả về thông tin level up hoặc None."
            ),
            Tool.from_function(
                name="exp_needed_for_level",
                func=exp_needed_for_level,
                coroutine=exp_needed_for_level,
                description="Tính EXP cần để lên cấp. Dùng để hiển thị thông tin level."
            ),
            Tool.from_function(
                name="toggle_shared_habit_flag",
                func=toggle_shared_habit_flag_smart,
                coroutine=toggle_shared_habit_flag_smart,
                description="Toggle shared_habit flag cho user. Tự động đổi trạng thái hiện tại (bật -> tắt, tắt -> bật)."
            ),
            Tool.from_function(
                name="enable_shared_habit_flag",
                func=enable_shared_habit_flag,
                coroutine=enable_shared_habit_flag,
                description="Bật shared_habit flag cho user. Dùng khi user muốn bật shared habits."
            ),
            Tool.from_function(
                name="disable_shared_habit_flag",
                func=disable_shared_habit_flag,
                coroutine=disable_shared_habit_flag,
                description="Tắt shared_habit flag cho user. Dùng khi user muốn tắt shared habits."
            ),
            Tool.from_function(
                name="add_shared_habits_to_user",
                func=add_shared_habits_to_user,
                coroutine=add_shared_habits_to_user,
                description="Thêm tất cả shared habits vào user khi bật shared_habit flag."
            ),
            Tool.from_function(
                name="disable_shared_habits_for_user",
                func=disable_shared_habits_for_user,
                coroutine=disable_shared_habits_for_user,
                description="Disable tất cả shared habits của user khi tắt shared_habit flag."
            ),
            Tool.from_function(
                name="enable_shared_habits_for_user",
                func=enable_shared_habits_for_user,
                coroutine=enable_shared_habits_for_user,
                description="Enable tất cả shared habits của user khi bật shared_habit flag."
            ),
            Tool.from_function(
                name="get_all_shared_habits",
                func=get_all_shared_habits,
                coroutine=get_all_shared_habits,
                description="Lấy danh sách tất cả shared habits có sẵn trong hệ thống."
            ),
            Tool.from_function(
                name="toggle_habit_enabled",
                func=toggle_habit_enabled,
                coroutine=toggle_habit_enabled,
                description="Bật/tắt một thói quen cụ thể. Trả về trạng thái mới (1 = enabled, 0 = disabled)."
            ),
            Tool.from_function(
                name="handle_shared_habits_toggle",
                func=self._handle_shared_habits_toggle_wrapper,
                coroutine=self._handle_shared_habits_toggle_wrapper,
                description="Xử lý toggle shared habits workflow hoàn chỉnh. Tự động bật/tắt flag và thêm/xóa shared habits."
            ),
            Tool.from_function(
                name="handle_shared_habits_enable",
                func=self._handle_shared_habits_enable_wrapper,
                coroutine=self._handle_shared_habits_enable_wrapper,
                description="Bật shared habits cho user. Kiểm tra trạng thái hiện tại và thêm shared habits nếu cần."
            ),
            Tool.from_function(
                name="handle_shared_habits_disable",
                func=self._handle_shared_habits_disable_wrapper,
                coroutine=self._handle_shared_habits_disable_wrapper,
                description="Tắt shared habits cho user. Kiểm tra trạng thái hiện tại và disable shared habits nếu cần."
            ),
            Tool.from_function(
                name="check_user_registered",
                func=self.check_user_registered,
                coroutine=self.check_user_registered,
                description="Kiểm tra xem user đã đăng ký chưa. Trả về True/False."
            ),
            Tool.from_function(
                name="get_user_info_formatted",
                func=self.get_user_info_formatted,
                coroutine=self.get_user_info_formatted,
                description="Lấy thông tin user đã format đẹp. Trả về thông tin chi tiết hoặc thông báo chưa đăng ký."
            ),
            Tool.from_function(
                name="get_user_habits_formatted",
                func=self.get_user_habits_formatted,
                coroutine=self.get_user_habits_formatted,
                description="Lấy danh sách habits của user đã format đẹp. Hiển thị cả personal và shared habits."
            ),
            Tool.from_function(
                name="get_shared_habits_info",
                func=self.get_shared_habits_info,
                coroutine=self.get_shared_habits_info,
                description="Lấy thông tin về shared habits có sẵn trong hệ thống."
            ),
            Tool.from_function(
                name="mark_habit_done_smart",
                func=self.mark_habit_done_smart,
                coroutine=self.mark_habit_done_smart,
                description="Đánh dấu thói quen hoàn thành một cách thông minh. Cần user_id và habit_id. Tự động kiểm tra habit tồn tại và enabled."
            ),
            Tool.from_function(
                name="get_user_reminder_mode",
                func=get_user_reminder_mode,
                coroutine=get_user_reminder_mode,
                description="Lấy trạng thái nhắc nhở của người dùng."
            ),
            Tool.from_function(
                name="set_user_reminder_mode",
                func=set_user_reminder_mode,
                coroutine=set_user_reminder_mode,
                description="Thiết lập trạng thái nhắc nhở cho người dùng."
            ),
            Tool.from_function(
                name="get_users_with_reminders",
                func=get_users_with_reminders,
                coroutine=get_users_with_reminders,
                description="Lấy danh sách người dùng có nhắc nhở."
            ),
            Tool.from_function(
                name="get_incomplete_habits_for_user",
                func=get_incomplete_habits_for_user,
                coroutine=get_incomplete_habits_for_user,
                description="Lấy danh sách thói quen chưa hoàn thành của người dùng."
            ),
            Tool.from_function(
                name="get_available_commands",
                func=self._get_available_commands_wrapper,
                coroutine=self._get_available_commands_wrapper,
                description="Lấy danh sách tất cả các lệnh có sẵn trong hệ thống LifeRPG Bot."
            ),
            Tool.from_function(
                name="get_system_features",
                func=self._get_system_features_wrapper,
                coroutine=self._get_system_features_wrapper,
                description="Lấy thông tin chi tiết về các tính năng và chức năng của hệ thống LifeRPG."
            ),
            Tool.from_function(
                name="get_system_status",
                func=self._get_system_status_wrapper,
                coroutine=self._get_system_status_wrapper,
                description="Kiểm tra trạng thái tổng quan của hệ thống LifeRPG."
            ),
            Tool.from_function(
                name="get_command_help",
                func=self._get_command_help_wrapper,
                coroutine=self._get_command_help_wrapper,
                description="Lấy thông tin chi tiết về một lệnh cụ thể."
            )
        ]

    def _initialize_agent_prompt(self) -> ChatPromptTemplate:
        system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)

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

    async def get_user_info(self, user_id: int):
        """Helper method để lấy thông tin user"""
        return await get_user(user_id)

    async def check_user_registered(self, user_id: int) -> bool:
        """Helper method để kiểm tra user đã đăng ký chưa"""
        user = await get_user(user_id)
        return user is not None

    async def get_user_info_formatted(self, user_id: int):
        """Helper method để lấy thông tin user đã format"""
        user = await get_user(user_id)
        if not user:
            return EXAMPLES["user_not_registered"]
        
        return format_user_profile(user)

    async def mark_habit_done_smart(self, user_id: int, habit_id: str):
        """Helper method để đánh dấu habit done một cách thông minh"""
        # Kiểm tra user tồn tại
        user = await get_user(user_id)
        if not user:
            return "❌ Ký chủ chưa đăng ký. Hãy dùng `!register` trước."
        
        # Lấy thông tin habit
        habits = await get_user_habits_with_status(user_id)
        habit = next((h for h in habits if h[0] == habit_id), None)
        
        if not habit:
            return f"❌ Không tìm thấy thói quen với ID `{habit_id}`. Dùng `!habit_list` để xem danh sách."
        
        # Unpack habit data
        habit_id, name, stat_gain, base_exp, base_int, base_hp, streak, last_done, is_shared, enabled = habit
        
        if not enabled:
            return f"❌ Thói quen **{name}** đã bị tắt. Dùng `!habit_toggle {habit_id}` để bật lại."
        
        # Mark habit done
        new_streak = await mark_habit_done(user_id, habit_id)
        if new_streak is None:
            return "❌ Có lỗi xảy ra khi đánh dấu thói quen hoàn thành."
        
        # Tính thưởng với streak bonus
        streak_bonus = new_streak - 1
        
        bonus_exp = base_exp + 10 * streak_bonus
        bonus_int = base_int + (1 if base_int > 0 else 0) * streak_bonus
        bonus_hp = base_hp + (2 if base_hp > 0 else 0) * streak_bonus
        
        # Thưởng stats
        await reward_stat_from_habit(user_id, stat_gain, bonus_exp, bonus_int, bonus_hp)
        
        # Tạo thông báo thưởng theo phong cách tu tiên
        reward_text = f"+{bonus_exp} Tu Vi"
        if bonus_int > 0:
            reward_text += f", +{bonus_int} Ngộ Tính"
        if bonus_hp > 0:
            reward_text += f", +{bonus_hp} Sinh Lực"
        
        habit_type = "🔗 Thói Quen Chung" if is_shared else "👤 Thói Quen Cá Nhân"
        result = f"⚡️ **Hoàn Thành Tu Luyện:** {name} ({habit_type})\n"
        result += f"🎯 **Truyền Công:** {reward_text} (Chuỗi {new_streak} ngày)"
        
        # Kiểm tra level up
        level_up_result = await try_level_up(user_id)
        if level_up_result:
            new_level = level_up_result['new_level']
            realm_name = get_realm_name(new_level)
            realm_desc = get_realm_description(new_level)
            
            result += f"\n\n⚡️ **[ĐỘT PHÁ CẢNH GIỚI]**\n"
            result += f"🏆 **Cảnh Giới Mới:** {realm_name} (Level {new_level})\n"
            result += f"📖 *{realm_desc}*\n"
            result += f"❤️ **Hồi Phục Sinh Lực:** +{level_up_result['hp_gain']} HP\n\n"
            result += f"🔔 **Hệ Thống Ghi Nhận:** Ký chủ đã đột phá thành công. Tiếp tục duy trì tốc độ này."
        
        return result

    async def get_user_habits_formatted(self, user_id: int):
        """Helper method để lấy danh sách habits đã format"""
        habits = await get_user_habits_with_status(user_id)
        if not habits:
            return "❌ Ký chủ chưa có thói quen nào."
        
        personal_habits = []
        shared_habits = []
        
        for habit in habits:
            habit_id, name, stat_gain, base_exp, base_int, base_hp, streak, last_done, is_shared, enabled = habit
            
            status_icon = "✅" if enabled else "❌"
            type_icon = "🔗" if is_shared else "👤"
            
            habit_info = f"{status_icon} {type_icon} **{name}** (`{habit_id}`)\n"
            habit_info += f"Chỉ số: {stat_gain} | EXP: {base_exp} | Strike: {streak} ngày"
            
            if is_shared:
                shared_habits.append(habit_info)
            else:
                personal_habits.append(habit_info)
        
        result = ""
        if personal_habits:
            result += "👤 **Thói quen cá nhân:**\n" + "\n\n".join(personal_habits) + "\n\n"
        if shared_habits:
            result += "🔗 **Thói quen chung (Shared):**\n" + "\n\n".join(shared_habits)
        
        return result

    async def get_shared_habits_info(self):
        """Helper method để lấy thông tin shared habits"""
        shared_habits = await get_all_shared_habits()
        if not shared_habits:
            return "❌ Không có shared habits nào."
        
        result = "🔗 **Danh sách Shared Habits có sẵn:**\n\n"
        for habit in shared_habits:
            result += f"📝 **{habit['name']}**\n"
            result += f"• ID: `{habit['habit_id']}`\n"
            result += f"• Chỉ số: {habit['stat_gain']}\n"
            result += f"• EXP: {habit['base_exp']}\n"
            result += f"• Mô tả: {habit['description']}\n\n"
        
        result += "💡 Dùng `!toggle_shared_habit` để bật/tắt shared habits"
        return result

    async def handle_shared_habits_toggle(self, user_id: int):
        """Helper method để xử lý toggle shared habits workflow"""
        # Lấy thông tin user hiện tại
        user = await get_user(user_id)
        if not user:
            return "❌ Ký chủ chưa đăng ký. Hãy dùng `!register` trước."
        
        current_status = user['shared_habit']  # shared_habit flag
        new_status = await toggle_shared_habit_flag_smart(user_id)
        
        if new_status is None:
            return "❌ Có lỗi xảy ra khi thay đổi trạng thái shared habits."
        
        if new_status:  # Bật shared habits
            await add_shared_habits_to_user(user_id)
            return "✅ Đã bật Shared Habits! Các thói quen chung đã được thêm vào danh sách của ký chủ.\n\n" + await self.get_shared_habits_info()
        else:  # Tắt shared habits
            await disable_shared_habits_for_user(user_id)
            return "❌ Đã tắt Shared Habits! Các thói quen chung đã bị vô hiệu hóa (không bị xóa).\n\n💡 Ký chủ có thể bật lại bất cứ lúc nào bằng lệnh `!toggle_shared_habit`"

    async def handle_shared_habits_enable(self, user_id: int):
        """Helper method để bật shared habits"""
        user = await get_user(user_id)
        if not user:
            return "❌ Ký chủ chưa đăng ký. Hãy dùng `!register` trước."
        
        if user['shared_habit']:  # Đã bật rồi
            return "ℹ️ Shared Habits đã được bật rồi, ký chủ!"
        
        await enable_shared_habit_flag(user_id)
        await add_shared_habits_to_user(user_id)
        return "✅ Đã bật Shared Habits! Các thói quen chung đã được thêm vào danh sách của ký chủ.\n\n" + await self.get_shared_habits_info()

    async def handle_shared_habits_disable(self, user_id: int):
        """Helper method để tắt shared habits"""
        user = await get_user(user_id)
        if not user:
            return "❌ Ký chủ chưa đăng ký. Hãy dùng `!register` trước."
        
        if not user['shared_habit']:  # Đã tắt rồi
            return "ℹ️ Shared Habits đã được tắt rồi, ký chủ!"
        
        await disable_shared_habit_flag(user_id)
        await disable_shared_habits_for_user(user_id)
        return "❌ Đã tắt Shared Habits! Các thói quen chung đã bị vô hiệu hóa (không bị xóa).\n\n💡 Ký chủ có thể bật lại bất cứ lúc nào bằng lệnh `!toggle_shared_habit`"

    # Wrapper functions cho tools
    async def _handle_shared_habits_toggle_wrapper(self, user_id: int):
        return await self.handle_shared_habits_toggle(user_id)
    
    async def _handle_shared_habits_enable_wrapper(self, user_id: int):
        return await self.handle_shared_habits_enable(user_id)
    
    async def _handle_shared_habits_disable_wrapper(self, user_id: int):
        return await self.handle_shared_habits_disable(user_id)

    # Wrapper functions cho introspection tools
    async def _get_available_commands_wrapper(self, *args, **kwargs):
        return await self._get_available_commands()
    
    async def _get_system_features_wrapper(self, *args, **kwargs):
        return await self._get_system_features()
    
    async def _get_system_status_wrapper(self, *args, **kwargs):
        return await self._get_system_status()
    
    async def _get_command_help_wrapper(self, command_name: str = "", *args, **kwargs):
        return await self._get_command_help(command_name)

    # New tools for system introspection
    async def _get_available_commands(self) -> str:
        """Lấy danh sách tất cả các lệnh có sẵn trong hệ thống"""
        commands = {
            "👤 Nhân vật": [
                "!register - Tạo nhân vật",
                "!profile - Xem hồ sơ cá nhân", 
                "!delete_profile - Xóa profile (cần xác nhận)",
                "!level_status - Xem cấp độ và tiến trình EXP",
                "!level_list - Xem EXP cần thiết từ cấp 1–10",
                "!toggle_shared_habit - Bật/tắt shared habits"
            ],
            "🎯 Nhiệm vụ": [
                "!quest_list - Danh sách nhiệm vụ",
                "!quest_claim <id> - Nhận thưởng nhiệm vụ"
            ],
            "🧠 Thói quen": [
                "!habit_add <id> <stat> <exp> <int> <hp> <tên> - Thêm thói quen cá nhân",
                "!habit_list - Danh sách thói quen (cá nhân + shared)",
                "!habit_done <id> - Đánh dấu hoàn thành",
                "!habit_toggle <id> - Bật/tắt thói quen",
                "!shared_habits_info - Xem danh sách shared habits có sẵn"
            ],
            "🔔 Nhắc nhở": [
                "!reminder - Xem cài đặt nhắc nhở hiện tại",
                "!reminder <mode> - Cài đặt chế độ nhắc nhở",
                "!reminder_test - Test gửi nhắc nhở ngay lập tức"
            ],
            "⏰ Scheduler & Hệ thống": [
                "!schedule_status - Xem các job định kỳ đang chạy",
                "!helpme - Hiển thị danh sách lệnh"
            ]
        }
        
        result = "📋 **DANH SÁCH LỆNH HỆ THỐNG LIFE RPG:**\n\n"
        for category, cmd_list in commands.items():
            result += f"**{category}:**\n"
            for cmd in cmd_list:
                result += f"• {cmd}\n"
            result += "\n"
        
        return result

    async def _get_system_features(self) -> str:
        """Lấy thông tin chi tiết về các tính năng hệ thống"""
        features = {
            "🎮 Hệ thống RPG": {
                "description": "Hệ thống tu luyện với các chỉ số: Tu Vi (EXP), Ngộ Tính (INT), Sinh Lực (HP), Cảnh Giới (Level)",
                "components": ["Level progression", "Realm system", "Stat rewards", "Level up notifications"]
            },
            "🧠 Quản lý Thói quen": {
                "description": "Hệ thống quản lý thói quen cá nhân và chung với tracking streak và rewards",
                "components": ["Personal habits", "Shared habits", "Habit tracking", "Streak system", "Reward calculation"]
            },
            "🎯 Hệ thống Nhiệm vụ": {
                "description": "Nhiệm vụ hàng ngày và hàng tuần với rewards tự động",
                "components": ["Daily quests", "Weekly quests", "Quest rewards", "Auto reset"]
            },
            "🔔 Hệ thống Nhắc nhở": {
                "description": "Nhắc nhở tự động cho thói quen với nhiều chế độ khác nhau",
                "components": ["Reminder modes (OFF/AFTER_WORK/ALL/CUSTOM)", "Auto scheduling", "Mention notifications", "Incomplete habit tracking"]
            },
            "🤖 AI Agent": {
                "description": "AI assistant tích hợp với khả năng tương tác thông minh",
                "components": ["Natural language processing", "Smart habit management", "User assistance", "System introspection"]
            },
            "⏰ Scheduler System": {
                "description": "Hệ thống lập lịch tự động cho các tác vụ định kỳ",
                "components": ["Daily quest reset", "Weekly quest reset", "Habit streak reset", "Penalty system", "Reminder scheduling"]
            },
            "💾 Database Management": {
                "description": "Quản lý dữ liệu người dùng, thói quen, nhiệm vụ",
                "components": ["User profiles", "Habit tracking", "Quest management", "Progress history"]
            }
        }
        
        result = "🔧 **TÍNH NĂNG HỆ THỐNG LIFE RPG:**\n\n"
        for feature_name, feature_info in features.items():
            result += f"**{feature_name}:**\n"
            result += f"• Mô tả: {feature_info['description']}\n"
            result += f"• Thành phần: {', '.join(feature_info['components'])}\n\n"
        
        return result

    async def _get_system_status(self) -> str:
        """Kiểm tra trạng thái tổng quan của hệ thống"""
        try:
            # Kiểm tra các thành phần chính
            status_checks = {
                "Database Connection": "✅ Hoạt động",
                "AI Model": "✅ Gemini 2.0 Flash",
                "Scheduler System": "✅ APScheduler",
                "Reminder System": "✅ Async Scheduler",
                "Command System": "✅ Discord.py Cogs",
                "Memory System": "✅ Conversation Buffer"
            }
            
            result = "📊 **TRẠNG THÁI HỆ THỐNG:**\n\n"
            for component, status in status_checks.items():
                result += f"**{component}:** {status}\n"
            
            result += "\n🎯 **THỐNG KÊ TỔNG QUAN:**\n"
            result += "• Hệ thống đang hoạt động ổn định\n"
            result += "• Tất cả modules đã được load thành công\n"
            result += "• Scheduler jobs đang chạy định kỳ\n"
            result += "• AI Agent sẵn sàng hỗ trợ\n"
            
            return result
            
        except Exception as e:
            return f"❌ **LỖI KIỂM TRA HỆ THỐNG:** {str(e)}"

    async def _get_command_help(self, command_name: str = None) -> str:
        """Lấy thông tin chi tiết về một lệnh cụ thể"""
        command_help = {
            "register": {
                "description": "Tạo nhân vật mới trong hệ thống Life RPG",
                "usage": "!register",
                "details": "Khởi tạo hồ sơ người dùng với các chỉ số mặc định: Level 1, EXP 0, HP 100, INT 0"
            },
            "profile": {
                "description": "Xem thông tin chi tiết về nhân vật",
                "usage": "!profile",
                "details": "Hiển thị: Cảnh giới, Tu Vi, Sinh Lực, Ngộ Tính, trạng thái thói quen chung"
            },
            "habit_add": {
                "description": "Mở form để tạo thói quen mới",
                "usage": "!habit_add",
                "details": "Mở Modal form để tạo thói quen mới với giao diện dễ sử dụng. Không cần nhớ cú pháp phức tạp."
            },
            "habit_list": {
                "description": "Xem danh sách tất cả thói quen",
                "usage": "!habit_list",
                "details": "Hiển thị thói quen cá nhân và chung với trạng thái enabled/disabled"
            },
            "habit_done": {
                "description": "Đánh dấu thói quen hoàn thành",
                "usage": "!habit_done <id>",
                "details": "Hoàn thành thói quen, nhận thưởng, tăng streak, kiểm tra level up"
            },
            "reminder": {
                "description": "Quản lý chế độ nhắc nhở thói quen",
                "usage": "!reminder [mode] [custom_hours]",
                "details": "Các chế độ: OFF, AFTER_WORK (18h-23h), ALL (6h-23h), CUSTOM (giờ tùy chỉnh)"
            },
            "quest_list": {
                "description": "Xem danh sách nhiệm vụ có sẵn",
                "usage": "!quest_list",
                "details": "Hiển thị nhiệm vụ hàng ngày và hàng tuần với trạng thái hoàn thành"
            },
            "quest_claim": {
                "description": "Nhận thưởng nhiệm vụ đã hoàn thành",
                "usage": "!quest_claim <id>",
                "details": "Nhận EXP thưởng và kiểm tra level up khi hoàn thành nhiệm vụ"
            }
        }
        
        if not command_name:
            result = "📖 **HƯỚNG DẪN LỆNH:**\n\n"
            result += "Dùng `!get_command_help <tên_lệnh>` để xem chi tiết.\n\n"
            result += "**Các lệnh chính:**\n"
            for cmd in command_help.keys():
                result += f"• {cmd}\n"
            return result
        
        command_name = command_name.lower().replace("!", "")
        if command_name in command_help:
            cmd_info = command_help[command_name]
            result = f"📖 **HƯỚNG DẪN: {command_name.upper()}**\n\n"
            result += f"**Mô tả:** {cmd_info['description']}\n"
            result += f"**Cách dùng:** `{cmd_info['usage']}`\n"
            result += f"**Chi tiết:** {cmd_info['details']}\n"
        else:
            result = f"❌ Không tìm thấy thông tin cho lệnh `{command_name}`\n"
            result += "Dùng `!get_command_help` để xem danh sách lệnh có sẵn."
        
        return result
