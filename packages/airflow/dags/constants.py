SHIFT_CONFIG = {
    "normal": {
        "check_in_reference": "08:15",
        "check_out_reference": "17:30"
    },
    "leave_morning": {
        "check_in_reference": "13:15",  # Bắt đầu làm buổi chiều
        "check_out_reference": "17:30"
    },
    "leave_afternoon": {
        "check_in_reference": "08:15",
        "check_out_reference": "12:00"  # Kết thúc làm buổi sáng
    },
    "leave_full_day": {
        "check_in_reference": None,
        "check_out_reference": None
    }
}


RULES = [
    {
        "min": 1,
        "max": 15,
        "deduct": lambda free: 0 if free > 0 else 1 # Được miễn trừ nếu còn free allowance
    },
    {
        "min": 16,
        "max": 60,
        "deduct": lambda free: 1
    },
    {
        "min": 61,
        "max": 120,
        "deduct": lambda free: 2
    },
    {
        "min": 121,
        "max": 240,
        "deduct": lambda free: 4
    },
    {
        "min": 241,
        "max": 360,
        "deduct": lambda free: 6
    },
    {
        "min": 361,
        "max": 480,
        "deduct": lambda free: 8
    }
    {
        "min": 481,
        "max": 555,
        "deduct": lambda free: 8
    }
]

FREE_PER_MONTH = 5
