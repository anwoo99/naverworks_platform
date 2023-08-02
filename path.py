import os

# Root Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Log Directory
LOG_DIR = os.path.join(BASE_DIR, "log")

# INFO Directory
INFO_DIR = os.path.join(BASE_DIR, "info")

# Authorization Directory
AUTH_DIR = os.path.join(INFO_DIR, "auth")

# Device Information Direcotry
DEVICE_DIR = os.path.join(INFO_DIR, "device")

# Holiday Directory
HOLIDAY_DIR = os.path.join(INFO_DIR, "holiday")

# Notifications Directory
OCC_DIR = os.path.join(INFO_DIR, "occ")

# Weekly Report Directory
WEEKLY_REPORT_DIR = os.path.join(INFO_DIR, "weekly_report")

# Kakao Directory
KAKAO_DIR = os.path.join(INFO_DIR, "kakao")

# MAIN PIPE
MAIN_PIPE = os.path.join(BASE_DIR, "tmp", "MAIN_PIPE")
MAIN_PIPE2 = os.path.join(BASE_DIR, "tmp", "MAIN_PIPE2")

