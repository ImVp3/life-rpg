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
                value=f"🎁 {quest['exp']} EXP, {quest['gold']} Gold\n🧩 ID dùng để claim: `{quest['id']}`\n✅ Trạng thái: {status}",
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
        await reward_user(ctx.author.id, quest["exp"], quest["gold"])
        await ctx.send(f"🎉 Bạn đã nhận {quest['exp']} EXP và {quest['gold']} Gold từ **{quest['name']}**!")
        result = await try_level_up(ctx.author.id)
        if result:
            embed = discord.Embed(
                title="🎉 Bạn đã lên cấp!",
                description=f"**{ctx.author.display_name}** đã đạt cấp độ **{result['new_level']}**!",
                color=0xffd700
            )
            embed.add_field(name="🏅 Cấp độ mới", value=result["new_level"])
            embed.add_field(name="✨ Điểm nâng cấp", value=f"+{result['level_point_gain']} điểm")
            embed.add_field(name="❤️ HP hồi phục", value=f"+{result['hp_gain']} HP")
            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(QuestCog(bot))
