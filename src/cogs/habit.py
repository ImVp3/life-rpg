import discord
from discord.ext import commands
from database.db import (
    get_user, add_habit, get_user_habits_with_status, mark_habit_done, reward_stat_from_habit, try_level_up,
    toggle_habit_enabled, get_all_shared_habits
)
from utils.level_fomula import get_realm_name, get_realm_description

class HabitAddModal(discord.ui.Modal, title="Tạo thói quen mới"):
    def __init__(self):
        super().__init__()
        
    habit_id = discord.ui.TextInput(
        label="ID thói quen",
        placeholder="Ví dụ: code_5h, read_30min",
        required=True,
        max_length=20,
        style=discord.TextStyle.short
    )
    
    habit_name = discord.ui.TextInput(
        label="Tên thói quen",
        placeholder="Ví dụ: Code ít nhất 5 giờ mỗi ngày",
        required=True,
        max_length=100,
        style=discord.TextStyle.short
    )
    
    rewards = discord.ui.TextInput(
        label="Thưởng (EXP INT HP)",
        placeholder="Ví dụ: 80 10 5 (80 EXP, 10 INT, 5 HP)",
        required=True,
        max_length=20,
        style=discord.TextStyle.short
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse rewards
            reward_parts = self.rewards.value.strip().split()
            if len(reward_parts) != 3:
                await interaction.response.send_message("❌ Vui lòng nhập đúng format: EXP INT HP (3 số cách nhau bởi dấu cách)", ephemeral=True)
                return
            
            exp = int(reward_parts[0])
            int_gain = int(reward_parts[1])
            hp_gain = int(reward_parts[2])
            
            # Auto determine stat type based on rewards
            if int_gain > 0 and hp_gain > 0:
                stat_type = "INT"  # Default to INT if both are positive
            elif int_gain > 0:
                stat_type = "INT"
            elif hp_gain > 0:
                stat_type = "HP"
            else:
                stat_type = "INT"  # Default to INT if no stat rewards
            
            # Add habit
            await add_habit(
                interaction.user.id, 
                self.habit_id.value, 
                self.habit_name.value, 
                stat_type, 
                exp, 
                int_gain, 
                hp_gain
            )
            
            embed = discord.Embed(
                title="✅ Thói quen đã được tạo thành công!",
                color=0x2ecc71
            )
            embed.add_field(name="Tên", value=self.habit_name.value, inline=True)
            embed.add_field(name="ID", value=f"`{self.habit_id.value}`", inline=True)
            embed.add_field(name="Chỉ số", value=stat_type, inline=True)
            embed.add_field(name="EXP thưởng", value=exp, inline=True)
            embed.add_field(name="Ngộ Tính", value=int_gain, inline=True)
            embed.add_field(name="Sinh Lực", value=hp_gain, inline=True)
            embed.set_footer(text="Dùng !habit_done <id> để đánh dấu hoàn thành")
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("❌ Vui lòng nhập số hợp lệ cho EXP, INT và HP!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Có lỗi xảy ra: {str(e)}", ephemeral=True)

class HabitAddButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="📝 Tạo thói quen mới", style=discord.ButtonStyle.primary)
    async def create_habit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = HabitAddModal()
        await interaction.response.send_modal(modal)

class HabitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="habit_add")
    async def habit_add(self, ctx):
        """Mở form để tạo thói quen mới (dễ sử dụng hơn command line)"""
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("❌ Bạn chưa đăng ký. Dùng `!register` trước.")
            return
        
        embed = discord.Embed(
            title="📝 Tạo thói quen mới",
            description="Nhấn nút bên dưới để mở form tạo thói quen mới.\n\n**Thông tin cần thiết:**\n• ID thói quen (ví dụ: code_5h)\n• Tên thói quen\n• Thưởng: 3 số cách nhau bởi dấu cách\n  - Ví dụ: `80 10 5` = 80 EXP, 10 INT, 5 HP\n  - Ví dụ: `50 0 0` = 50 EXP, 0 INT, 0 HP",
            color=0x3498db
        )
        embed.set_footer(text="Form sẽ mở trong 60 giây")
        
        view = HabitAddButton()
        await ctx.send(embed=embed, view=view)

    @commands.command(name="habit_list")
    async def habit_list(self, ctx):
        habits = await get_user_habits_with_status(ctx.author.id)
        if not habits:
            await ctx.send("❌ Bạn chưa có thói quen nào.")
            return

        embed = discord.Embed(title="📋 Danh sách thói quen", color=0x2ecc71)
        
        # Phân loại habits
        personal_habits = []
        shared_habits = []
        
        for habit in habits:
            habit_id, name, stat_gain, base_exp, base_int, base_hp, streak, last_done, is_shared, enabled = habit
            
            status_icon = "✅" if enabled else "❌"
            type_icon = "🔗" if is_shared else "👤"
            
            # Tạo thông tin thưởng
            reward_info = f"Tu Vi: {base_exp}"
            if base_int > 0:
                reward_info += f" | Ngộ Tính: +{base_int}"
            if base_hp > 0:
                reward_info += f" | Sinh Lực: +{base_hp}"
            
            habit_info = f"{status_icon} {type_icon} **{name}** (`{habit_id}`)\n"
            habit_info += f"Thưởng: {reward_info} | Strike: {streak} ngày"
            
            if is_shared:
                shared_habits.append(habit_info)
            else:
                personal_habits.append(habit_info)
        
        # Hiển thị personal habits
        if personal_habits:
            embed.add_field(
                name="👤 Thói quen cá nhân",
                value="\n\n".join(personal_habits),
                inline=False
            )
        
        # Hiển thị shared habits
        if shared_habits:
            embed.add_field(
                name="🔗 Thói quen chung (Shared)",
                value="\n\n".join(shared_habits),
                inline=False
            )
        
        embed.set_footer(text="✅ = Đang hoạt động | ❌ = Đã tắt | Dùng !habit_toggle <id> để bật/tắt")
        await ctx.send(embed=embed)

    @commands.command(name="habit_toggle")
    async def habit_toggle(self, ctx, habit_id: str):
        """Bật/tắt một thói quen cụ thể"""
        new_status = await toggle_habit_enabled(ctx.author.id, habit_id)
        
        if new_status is None:
            await ctx.send("❌ Không tìm thấy thói quen với ID này.")
            return
        
        status_text = "✅ Bật" if new_status else "❌ Tắt"
        await ctx.send(f"🔄 Đã {status_text} thói quen `{habit_id}`")

    @commands.command(name="shared_habits_info")
    async def shared_habits_info(self, ctx):
        """Xem thông tin về các shared habits có sẵn"""
        shared_habits = await get_all_shared_habits()
        
        embed = discord.Embed(title="🔗 Danh sách Shared Habits có sẵn", color=0x3498db)
        
        for habit in shared_habits:
            embed.add_field(
                name=f"📝 {habit['name']}",
                value=f"**ID:** `{habit['habit_id']}`\n"
                      f"**Chỉ số:** {habit['stat_gain']}\n"
                      f"**EXP:** {habit['base_exp']}\n"
                      f"**Mô tả:** {habit['description']}",
                inline=False
            )
        
        embed.set_footer(text="Dùng !toggle_shared_habit để bật/tắt shared habits")
        await ctx.send(embed=embed)

    @commands.command(name="habit_done")
    async def habit_done(self, ctx, habit_id: str):
        # Kiểm tra xem habit có enabled không
        habits = await get_user_habits_with_status(ctx.author.id)
        habit = next((h for h in habits if h[0] == habit_id), None)
        
        if not habit:
            await ctx.send("⚠️ Không tìm thấy thói quen.")
            return
        
        # Unpack habit data
        habit_id, name, stat_gain, base_exp, base_int, base_hp, streak, last_done, is_shared, enabled = habit
        
        if not enabled:  # enabled = False
            await ctx.send(f"❌ Thói quen này đã bị tắt. Dùng `!habit_toggle {habit_id}` để bật lại.")
            return
        
        streak = await mark_habit_done(ctx.author.id, habit_id)
        if streak is None:
            await ctx.send("⚠️ Không tìm thấy thói quen.")
            return

        # Tính thưởng với streak bonus
        streak_bonus = streak - 1
        
        bonus_exp = base_exp + 10 * streak_bonus
        bonus_int = base_int + (1 if base_int > 0 else 0) * streak_bonus
        bonus_hp = base_hp + (2 if base_hp > 0 else 0) * streak_bonus
        
        await reward_stat_from_habit(ctx.author.id, stat_gain, bonus_exp, bonus_int, bonus_hp)
        
        # Tạo thông báo thưởng
        reward_text = f"+{bonus_exp} Tu Vi"
        if bonus_int > 0:
            reward_text += f", +{bonus_int} Ngộ Tính"
        if bonus_hp > 0:
            reward_text += f", +{bonus_hp} Sinh Lực"
        
        habit_type = "🔗 Thói Quen Chung" if is_shared else "👤 Thói Quen Cá Nhân"
        await ctx.send(f"⚡️ Hoàn thành **{name}** ({habit_type})! {reward_text} (Chuỗi {streak})")
        
        result = await try_level_up(ctx.author.id)
        if result:
            new_level = result['new_level']
            realm_name = get_realm_name(new_level)
            realm_desc = get_realm_description(new_level)
            
            embed = discord.Embed(
                title="⚡️ [ĐỘT PHÁ CẢNH GIỚI]",
                description=f"**{ctx.author.display_name}** đã đột phá thành công!",
                color=0xffd700
            )
            embed.add_field(name="🏆 Cảnh Giới Mới", value=f"{realm_name} (Level {new_level})")
            embed.add_field(name="📖 Mô Tả", value=realm_desc, inline=False)
            embed.add_field(name="❤️ Hồi Phục Sinh Lực", value=f"+{result['hp_gain']} HP")
            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.set_footer(text="🔔 Hệ Thống Ghi Nhận: Tiếp tục duy trì tốc độ này.")
            await ctx.send(embed=embed)

    @commands.command(name="habit_all")
    async def habit_all(self, ctx):
        """Xem toàn bộ thói quen (cá nhân + shared) của bạn với đầy đủ thông tin."""
        habits = await get_user_habits_with_status(ctx.author.id)
        if not habits:
            await ctx.send("❌ Bạn chưa có thói quen nào.")
            return

        embed = discord.Embed(title="📋 Tất cả thói quen của bạn", color=0x8e44ad)
        for habit in habits:
            habit_id, name, stat_gain, base_exp, base_int, base_hp, streak, last_done, is_shared, enabled = habit
            status_icon = "✅" if enabled else "❌"
            type_icon = "🔗" if is_shared else "👤"
            reward_info = f"Tu Vi: {base_exp}"
            if base_int > 0:
                reward_info += f" | Ngộ Tính: +{base_int}"
            if base_hp > 0:
                reward_info += f" | Sinh Lực: +{base_hp}"
            streak_info = f"Chuỗi: {streak} ngày"
            last_done_info = f"Lần cuối: {last_done if last_done else 'Chưa hoàn thành'}"
            embed.add_field(
                name=f"{status_icon} {type_icon} {name} (ID: `{habit_id}`)",
                value=f"Chỉ số: {stat_gain}\n{reward_info}\n{streak_info}\n{last_done_info}",
                inline=False
            )
        embed.set_footer(text="✅ = Đang hoạt động | ❌ = Đã tắt | Dùng !habit_toggle <id> để bật/tắt")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HabitCog(bot))
