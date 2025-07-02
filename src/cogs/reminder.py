import discord
from discord.ext import commands
from database.db import get_user, get_user_reminder_mode, set_user_reminder_mode

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reminder")
    async def reminder(self, ctx, mode: str = None, *, custom_hours: str = None):
        """
        Cài đặt chế độ nhắc nhở thói quen
        
        Các chế độ có sẵn:
        - `OFF`: Không nhắc nhở
        - `AFTER_WORK`: Nhắc nhở sau mỗi 1 giờ từ 18h (mặc định)
        - `ALL`: Nhắc nhở sau mỗi 1 giờ từ 6h sáng đến 23h
        - `CUSTOM`: Nhắc nhở theo giờ tùy chỉnh
        
        Ví dụ:
        - `!reminder OFF` - Tắt nhắc nhở
        - `!reminder AFTER_WORK` - Chế độ sau giờ làm
        - `!reminder ALL` - Nhắc nhở cả ngày
        - `!reminder CUSTOM 8,12,18,22` - Nhắc nhở lúc 8h, 12h, 18h, 22h
        """
        # Kiểm tra user đã đăng ký chưa
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("❌ Bạn chưa đăng ký. Dùng `!register` trước.")
            return
        
        # Nếu không có mode, hiển thị thông tin hiện tại
        if not mode:
            current_settings = await get_user_reminder_mode(ctx.author.id)
            if not current_settings:
                await ctx.send("❌ Không tìm thấy cài đặt nhắc nhở.")
                return
            
            embed = discord.Embed(
                title="🔔 Cài Đặt Nhắc Nhở Hiện Tại",
                color=0x3498db
            )
            
            mode_descriptions = {
                'OFF': '❌ Không nhắc nhở',
                'AFTER_WORK': '🏢 Nhắc nhở sau mỗi 1 giờ từ 18h đến 23h',
                'ALL': '🌞 Nhắc nhở sau mỗi 1 giờ từ 6h sáng đến 23h',
                'CUSTOM': '⚙️ Nhắc nhở theo giờ tùy chỉnh'
            }
            
            embed.add_field(
                name="Chế Độ",
                value=mode_descriptions.get(current_settings['mode'], current_settings['mode']),
                inline=False
            )
            
            if current_settings['mode'] == 'CUSTOM' and current_settings['custom_hours']:
                embed.add_field(
                    name="Giờ Tùy Chỉnh",
                    value=f"Lúc: {', '.join(map(str, current_settings['custom_hours']))}h",
                    inline=False
                )
            
            embed.add_field(
                name="💡 Cách Sử Dụng",
                value="`!reminder <mode> [giờ_tùy_chỉnh]`\n"
                      "Ví dụ: `!reminder CUSTOM 8,12,18,22`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        # Kiểm tra mode hợp lệ
        valid_modes = ['OFF', 'AFTER_WORK', 'ALL', 'CUSTOM']
        mode_descriptions = {
            'OFF': '❌ Không nhắc nhở',
            'AFTER_WORK': '🏢 Nhắc nhở sau mỗi 1 giờ từ 18h đến 23h',
            'ALL': '🌞 Nhắc nhở sau mỗi 1 giờ từ 6h sáng đến 23h',
            'CUSTOM': '⚙️ Nhắc nhở theo giờ tùy chỉnh'
        }
        
        if mode.upper() not in valid_modes:
            embed = discord.Embed(
                title="❌ Chế Độ Không Hợp Lệ",
                description="Các chế độ có sẵn:",
                color=0xe74c3c
            )
            for valid_mode in valid_modes:
                embed.add_field(
                    name=valid_mode,
                    value=mode_descriptions.get(valid_mode, valid_mode),
                    inline=False
                )
            await ctx.send(embed=embed)
            return
        
        mode = mode.upper()
        custom_hours_list = []
        
        # Xử lý custom hours nếu mode là CUSTOM
        if mode == 'CUSTOM':
            if not custom_hours:
                await ctx.send("❌ Chế độ CUSTOM cần có danh sách giờ. Ví dụ: `!reminder CUSTOM 8,12,18,22`")
                return
            
            try:
                # Parse custom hours
                hours_str = custom_hours.replace(' ', '')
                custom_hours_list = [int(h) for h in hours_str.split(',')]
                
                # Kiểm tra giờ hợp lệ
                for hour in custom_hours_list:
                    if not (0 <= hour <= 23):
                        await ctx.send("❌ Giờ phải từ 0-23. Ví dụ: `!reminder CUSTOM 8,12,18,22`")
                        return
                
                # Sắp xếp và loại bỏ trùng lặp
                custom_hours_list = sorted(list(set(custom_hours_list)))
                
            except ValueError:
                await ctx.send("❌ Định dạng giờ không đúng. Ví dụ: `!reminder CUSTOM 8,12,18,22`")
                return
        
        # Cập nhật cài đặt
        await set_user_reminder_mode(ctx.author.id, mode, custom_hours_list)
        
        # Tạo thông báo thành công
        embed = discord.Embed(
            title="✅ Cài Đặt Nhắc Nhở Thành Công",
            color=0x2ecc71
        )
        
        mode_descriptions = {
            'OFF': '❌ Đã tắt nhắc nhở',
            'AFTER_WORK': '🏢 Nhắc nhở sau mỗi 1 giờ từ 18h đến 23h',
            'ALL': '🌞 Nhắc nhở sau mỗi 1 giờ từ 6h sáng đến 23h',
            'CUSTOM': '⚙️ Nhắc nhở theo giờ tùy chỉnh'
        }
        
        embed.add_field(
            name="Chế Độ Mới",
            value=mode_descriptions.get(mode, mode),
            inline=False
        )
        
        if mode == 'CUSTOM' and custom_hours_list:
            embed.add_field(
                name="Giờ Tùy Chỉnh",
                value=f"Lúc: {', '.join(map(str, custom_hours_list))}h",
                inline=False
            )
        
        embed.set_footer(text="Dùng !reminder để xem cài đặt hiện tại")
        await ctx.send(embed=embed)

    @commands.command(name="reminder_test")
    async def reminder_test(self, ctx):
        """Test gửi nhắc nhở ngay lập tức"""
        # Kiểm tra user đã đăng ký chưa
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("❌ Bạn chưa đăng ký. Dùng `!register` trước.")
            return
        
        # Kiểm tra cài đặt nhắc nhở
        current_settings = await get_user_reminder_mode(ctx.author.id)
        if not current_settings or current_settings['mode'] == 'OFF':
            await ctx.send("❌ Bạn chưa bật nhắc nhở. Dùng `!reminder` để cài đặt.")
            return
        
        # Gửi nhắc nhở test
        from utils.reminder_scheduler import ReminderScheduler
        test_scheduler = ReminderScheduler(self.bot)
        
        test_user = {
            'user_id': ctx.author.id,
            'username': ctx.author.name,
            'mode': current_settings['mode'],
            'custom_hours': current_settings['custom_hours']
        }
        
        await test_scheduler.send_reminder_to_user(test_user)
        await ctx.send("✅ Đã gửi nhắc nhở test!")

async def setup(bot):
    await bot.add_cog(ReminderCog(bot)) 