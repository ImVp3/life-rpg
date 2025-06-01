# Discord Bot

Một Discord bot được xây dựng bằng Python với nhiều tính năng thú vị, bao gồm hệ thống RPG và tích hợp AI.

## Tính năng

- Hệ thống RPG (Life RPG)
- Tích hợp AI thông qua Google AI
- Quản lý cơ sở dữ liệu SQLite
- Hệ thống cogs mở rộng
- Các tiện ích và công cụ hỗ trợ

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package manager)

## Cài đặt

1. Clone repository:
```bash
git clone [repository-url]
cd discord-bot
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

4. Tạo file `.env` và cấu hình các biến môi trường cần thiết:
```
DISCORD_TOKEN=your_discord_bot_token
GOOGLE_API_KEY=your_google_api_key
```

## Cấu trúc dự án

```
discord-bot/
├── src/
│   ├── agent/         # AI agent và các tính năng AI
│   ├── cogs/          # Các module mở rộng của bot
│   ├── database/      # Quản lý cơ sở dữ liệu
│   ├── utils/         # Các tiện ích và công cụ
│   ├── data/          # Dữ liệu và tài nguyên
│   └── bot.py         # File chính của bot
├── requirements.txt   # Danh sách dependencies
└── README.md         # Tài liệu dự án
```

## Sử dụng

1. Đảm bảo bạn đã cấu hình đúng các biến môi trường trong file `.env`
2. Chạy bot:
```bash
python src/bot.py
```

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request để đóng góp vào dự án.
