# 🔔 Chức Năng Nhắc Nhở Thói Quen

## Tổng Quan
Hệ thống nhắc nhở tự động cho các thói quen với nhiều chế độ khác nhau.

## Các Chế Độ Nhắc Nhở

### 1. OFF
- **Mô tả**: Không nhắc nhở
- **Cách dùng**: `!reminder OFF`

### 2. AFTER_WORK (Mặc định)
- **Mô tả**: Nhắc nhở sau mỗi 1 giờ từ 18h đến 23h
- **Cách dùng**: `!reminder AFTER_WORK`
- **Thời gian**: 18h, 19h, 20h, 21h, 22h, 23h

### 3. ALL
- **Mô tả**: Nhắc nhở sau mỗi 1 giờ từ 6h sáng đến 23h
- **Cách dùng**: `!reminder ALL`
- **Thời gian**: 6h, 7h, 8h, 9h, 10h, 11h, 12h, 13h, 14h, 15h, 16h, 17h, 18h, 19h, 20h, 21h, 22h, 23h

### 4. CUSTOM
- **Mô tả**: Nhắc nhở theo giờ tùy chỉnh
- **Cách dùng**: `!reminder CUSTOM 8,12,18,22`
- **Thời gian**: Tùy chỉnh (0-23h)

## Các Lệnh

### `!reminder`
- **Mô tả**: Xem cài đặt nhắc nhở hiện tại
- **Ví dụ**: `!reminder`

### `!reminder <mode>`
- **Mô tả**: Cài đặt chế độ nhắc nhở
- **Ví dụ**: 
  - `!reminder OFF`
  - `!reminder AFTER_WORK`
  - `!reminder ALL`
  - `!reminder CUSTOM 8,12,18,22`

### `!reminder_test`
- **Mô tả**: Test gửi nhắc nhở ngay lập tức
- **Ví dụ**: `!reminder_test`

## Cách Hoạt Động

1. **Scheduler**: Chạy mỗi giờ để kiểm tra và gửi nhắc nhở
2. **Kiểm tra**: Xem giờ hiện tại có phù hợp với chế độ nhắc nhở không
3. **Lọc thói quen**: Chỉ nhắc nhở những thói quen chưa hoàn thành hôm nay
4. **Gửi nhắc nhở**: Mention user và liệt kê thói quen cần làm

## Cấu Hình

### Biến Môi Trường
Thêm vào file `.env`:
```
GENERAL_CHANNEL=your_general_channel_id_here
```

### Database
Các cột mới trong bảng `users`:
- `reminder_mode`: Chế độ nhắc nhở (OFF/AFTER_WORK/ALL/CUSTOM)
- `reminder_custom_hours`: Danh sách giờ tùy chỉnh (JSON array)

## Tính Năng

- ✅ Mention user khi nhắc nhở
- ✅ Liệt kê thói quen chưa hoàn thành
- ✅ Phân loại thói quen cá nhân và chung
- ✅ Hiển thị thông tin thưởng
- ✅ Hướng dẫn cách hoàn thành
- ✅ Test nhắc nhở ngay lập tức
- ✅ Cài đặt linh hoạt theo nhu cầu

## Lưu Ý

- Nhắc nhở chỉ được gửi cho những thói quen đang được bật (enabled = 1)
- Chỉ nhắc nhở những thói quen chưa hoàn thành trong ngày
- Nhắc nhở được gửi vào General channel được cấu hình trong .env 