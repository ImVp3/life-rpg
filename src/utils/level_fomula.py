def exp_needed_for_level(level: int) -> int:
    """Tính EXP cần để lên cấp"""
    return int(100 * (1.5 ** (level - 1)))

def get_realm_name(level):
    """Lấy tên cảnh giới tu tiên theo level"""
    realms = {
        1: "Phàm Nhân",
        2: "Luyện Thể", 
        3: "Trúc Cơ",
        4: "Kim Đan", 
        5: "Nguyên Anh",
        6: "Hóa Thần",
        7: "Luyện Hư", 
        8: "Hợp Thể",
        9: "Đại Thừa",
        10: "Phi Thăng"
    }
    return realms.get(level, f"Cảnh Giới {level}")

def get_realm_description(level):
    """Lấy mô tả cảnh giới tu tiên"""
    descriptions = {
        1: "Cửa ngõ tu luyện - bắt đầu hành trình nghịch thiên",
        2: "Rèn luyện thể chất, chuẩn bị cho việc hấp thụ linh khí",
        3: "Đã có thể hấp thụ linh khí, bắt đầu tu luyện chân chính",
        4: "Kết tinh linh khí thành kim đan, sức mạnh tăng vọt",
        5: "Nguyên thần xuất hiện, khả năng cảm ứng linh khí mạnh mẽ",
        6: "Hóa thần thành công, có thể phân thân và điều khiển linh khí",
        7: "Luyện hư thành thực, khả năng tạo không gian riêng",
        8: "Hợp thể với thiên địa, trở thành một phần của vũ trụ",
        9: "Đại thừa cảnh giới - gần như bất tử, có thể tạo thế giới",
        10: "Phi thăng thành công - vượt qua giới hạn của thế giới này"
    }
    return descriptions.get(level, "Cảnh giới vượt xa sự hiểu biết của phàm nhân")
