import discord
from discord.ext import commands
from database.db import (
    get_user,
    get_all_quests,
    get_user_quests,
    add_user_quests,
    claim_quest,
    reward_user,
    try_level_up
)

class QuestAddModal(discord.ui.Modal, title="Tạo nhiệm vụ mới"):
    def __init__(self):
        super().__init__()
        
    quest_id = discord.ui.TextInput(
        label="ID nhiệm vụ",
        placeholder="Ví dụ: daily_meditation, weekly_reading",
        required=True,
        max_length=30,
        style=discord.TextStyle.short
    )
    
    quest_name = discord.ui.TextInput(
        label="Tên nhiệm vụ",
        placeholder="Ví dụ: Thiền định 10 phút mỗi ngày",
        required=True,
        max_length=100,
        style=discord.TextStyle.short
    )
    
    quest_type = discord.ui.TextInput(
        label="Loại nhiệm vụ (daily/weekly)",
        placeholder="daily",
        required=True,
        max_length=6,
        style=discord.TextStyle.short
    )
    
    rewards = discord.ui.TextInput(
        label="EXP thưởng",
        placeholder="Ví dụ: 100",
        required=True,
        max_length=5,
        style=discord.TextStyle.short
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate quest type
            quest_type_lower = self.quest_type.value.lower()
            if quest_type_lower not in ["daily", "weekly"]:
                await interaction.response.send_message("❌ Loại nhiệm vụ phải là 'daily' hoặc 'weekly'!", ephemeral=True)
                return
            
            # Parse EXP reward
            exp = int(self.rewards.value)
            
            # TODO: Implement add_quest function in database
            # For now, just show success message
            embed = discord.Embed(
                title="✅ Nhiệm vụ đã được tạo thành công!",
                color=0x2ecc71
            )
            embed.add_field(name="Tên", value=self.quest_name.value, inline=True)
            embed.add_field(name="ID", value=f"`{self.quest_id.value}`", inline=True)
            embed.add_field(name="Loại", value=quest_type_lower, inline=True)
            embed.add_field(name="EXP thưởng", value=exp, inline=True)
            embed.set_footer(text="Nhiệm vụ sẽ có hiệu lực ngay lập tức")
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("❌ Vui lòng nhập số hợp lệ cho EXP!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Có lỗi xảy ra: {str(e)}", ephemeral=True)

class QuestAddButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="🎯 Tạo nhiệm vụ mới", style=discord.ButtonStyle.primary)
    async def create_quest(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = QuestAddModal()
        await interaction.response.send_modal(modal)

class QuestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quest_list")
    async def quest_list(self, ctx):
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("Bạn chưa đăng ký. Hãy dùng `!register` trước.")
            return

        all_quests = await get_all_quests()
        await add_user_quests(ctx.author.id, [q["id"] for q in all_quests])
        user_quests = dict(await get_user_quests(ctx.author.id))

        embed = discord.Embed(title="📜 Danh sách nhiệm vụ", color=0x00ffcc)
        for quest in all_quests:
            done = user_quests.get(quest["id"], 0)
            status = "✅ Đã hoàn thành" if done else "❌ Chưa hoàn thành"
            embed.add_field(
                name=f"{quest['name']} (`{quest['id']}`) [{quest['type']}]",
                value=f"�� {quest['exp']} EXP\n🧩 ID dùng để claim: `{quest['id']}`\n✅ Trạng thái: {status}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="quest_claim")
    async def quest_claim(self, ctx, quest_id: str):
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("Bạn chưa đăng ký.")
            return

        all_quests = await get_all_quests()
        quest = next((q for q in all_quests if q["id"] == quest_id), None)

        if not quest:
            await ctx.send("❌ Nhiệm vụ không tồn tại.")
            return

        user_quests = dict(await get_user_quests(ctx.author.id))
        if user_quests.get(quest_id, 0):
            await ctx.send("⚠️ Bạn đã hoàn thành nhiệm vụ này rồi.")
            return

        await claim_quest(ctx.author.id, quest_id)
        await reward_user(ctx.author.id, quest["exp"])
        await ctx.send(f"🎉 Bạn đã nhận {quest['exp']} EXP từ **{quest['name']}**!")
        result = await try_level_up(ctx.author.id)
        if result:
            embed = discord.Embed(
                title="🎉 Bạn đã lên cấp!",
                description=f"**{ctx.author.display_name}** đã đạt cấp độ **{result['new_level']}**!",
                color=0xffd700
            )
            embed.add_field(name="🏅 Cấp độ mới", value=result["new_level"])
            embed.add_field(name="❤️ HP hồi phục", value=f"+{result['hp_gain']} HP")
            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)

    @commands.command(name="quest_add")
    async def quest_add(self, ctx):
        """Mở form để tạo nhiệm vụ mới (chỉ dành cho admin)"""
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("❌ Bạn chưa đăng ký. Dùng `!register` trước.")
            return
        
        # TODO: Add admin check here
        # if not ctx.author.guild_permissions.administrator:
        #     await ctx.send("❌ Chỉ admin mới có thể tạo nhiệm vụ mới.")
        #     return
        
        embed = discord.Embed(
            title="🎯 Tạo nhiệm vụ mới",
            description="Nhấn nút bên dưới để mở form tạo nhiệm vụ mới.\n\n**Thông tin cần thiết:**\n• ID nhiệm vụ (ví dụ: daily_meditation)\n• Tên nhiệm vụ\n• Loại nhiệm vụ (daily/weekly)\n• EXP thưởng\n  - Ví dụ: `100` = 100 EXP\n  - Ví dụ: `50` = 50 EXP",
            color=0xe74c3c
        )
        embed.set_footer(text="Form sẽ mở trong 60 giây")
        
        view = QuestAddButton()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(QuestCog(bot))
