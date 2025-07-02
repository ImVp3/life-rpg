# 🤖 LifeRPG Agent

## Tổng Quan
LifeRPG Agent là một AI assistant thông minh được tích hợp vào Discord bot, có khả năng tương tác tự nhiên và quản lý hệ thống Life RPG một cách thông minh.

## Tính Năng Chính

### 🎮 Quản Lý RPG
- **User Management**: Đăng ký, xem profile, quản lý nhân vật
- **Level System**: Theo dõi cấp độ, Tu Vi, Ngộ Tính, Sinh Lực
- **Realm System**: Hệ thống cảnh giới tu luyện

### 🧠 Quản Lý Thói Quen
- **Smart Habit Management**: Đánh dấu hoàn thành thông minh
- **Shared Habits**: Quản lý thói quen chung
- **Streak Tracking**: Theo dõi chuỗi thói quen
- **Reward Calculation**: Tính toán thưởng tự động

### 🎯 Quản Lý Nhiệm Vụ
- **Quest Management**: Xem và nhận thưởng nhiệm vụ
- **Auto Rewards**: Tự động thưởng khi hoàn thành

### 🔔 Quản Lý Nhắc Nhở
- **Reminder Settings**: Cài đặt chế độ nhắc nhở
- **Incomplete Tracking**: Theo dõi thói quen chưa hoàn thành

### 🔍 System Introspection (Mới)
- **Command Discovery**: Lấy danh sách tất cả lệnh có sẵn
- **Feature Information**: Thông tin chi tiết về tính năng hệ thống
- **System Status**: Kiểm tra trạng thái hoạt động
- **Command Help**: Hướng dẫn sử dụng lệnh cụ thể

## Các Tools Có Sẵn

### User Management Tools
- `check_user_registered` - Kiểm tra hồ sơ tồn tại
- `get_user_info_formatted` - Thông tin người dùng

### Habit Management Tools
- `get_user_habits_formatted` - Danh sách thói quen
- `mark_habit_done_smart` - Hoàn thành thông minh
- `toggle_habit_enabled` - Bật/tắt thói quen
- `get_incomplete_habits_for_user` - Thói quen chưa hoàn thành

### Quest Management Tools
- `get_all_quests` - Danh sách nhiệm vụ
- `get_user_quests` - Nhiệm vụ của user
- `claim_quest` - Nhận thưởng nhiệm vụ

### Shared Habits Tools
- `get_shared_habits_info` - Thông tin thói quen chung
- `handle_shared_habits_toggle` - Toggle thói quen chung
- `handle_shared_habits_enable` - Bật thói quen chung
- `handle_shared_habits_disable` - Tắt thói quen chung

### Reminder Tools
- `get_user_reminder_mode` - Cài đặt nhắc nhở
- `set_user_reminder_mode` - Thiết lập nhắc nhở
- `get_users_with_reminders` - Users có nhắc nhở

### System Introspection Tools (Mới)
- `get_available_commands` - Danh sách lệnh
- `get_system_features` - Tính năng hệ thống
- `get_system_status` - Trạng thái hệ thống
- `get_command_help` - Hướng dẫn lệnh

## Cách Sử Dụng

### Tương Tác Tự Nhiên
Agent có thể hiểu và phản hồi các câu hỏi tự nhiên như:
- "Tôi có thể làm gì với hệ thống này?"
- "Hãy cho tôi biết danh sách lệnh"
- "Làm thế nào để thêm thói quen?"
- "Trạng thái hệ thống hiện tại như thế nào?"

### Hướng Dẫn Lệnh
Agent có thể giải thích chi tiết cách sử dụng bất kỳ lệnh nào:
- "Làm thế nào để sử dụng lệnh habit_add?"
- "Giải thích về lệnh reminder"
- "Cách sử dụng quest_claim"

### Kiểm Tra Hệ Thống
Agent có thể cung cấp thông tin về hệ thống:
- "Hệ thống có những tính năng gì?"
- "Trạng thái hoạt động hiện tại"
- "Danh sách tất cả lệnh có sẵn"

## Prompt System

### System Prompt
Agent sử dụng prompt phong cách "Hệ Thống Tu Tiên" với:
- Ngữ khí khách quan, nghiêm túc
- Thuật ngữ tu tiên: Tu Vi, Ngộ Tính, Sinh Lực, Cảnh Giới
- Phản hồi ngắn gọn, đầy đủ
- Tính chỉ đạo mạnh mẽ

### Examples
Có sẵn các examples cho các tình huống phổ biến:
- User chưa đăng ký
- Thông tin thói quen chung
- Quản lý thói quen
- Chúc mừng level up
- Động viên
- System introspection

## Cấu Hình

### Model
- **Model**: Gemini 2.0 Flash
- **Temperature**: 0.7
- **Memory**: Conversation Buffer

### Tools
- Tổng cộng 25+ tools
- Hỗ trợ async operations
- Tích hợp với database
- System introspection capabilities

## Testing

### Test Scripts
- `test_agent_introspection.py` - Test chức năng introspection
- Có thể test từng tool riêng lẻ
- Test tương tác tự nhiên

### Test Cases
- Lấy danh sách commands
- Thông tin tính năng hệ thống
- Trạng thái hệ thống
- Help cho lệnh cụ thể
- Chat với câu hỏi về hệ thống

## Lưu Ý

- Agent luôn kiểm tra trạng thái đăng ký trước khi thực hiện hành động
- Tự động xử lý các workflow phức tạp
- Cung cấp thông tin chính xác và cập nhật
- Hỗ trợ introspection để hiểu rõ khả năng của chính mình 