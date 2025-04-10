import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# Constants
W_4K, H_4K = 3840, 2160
W_PRINT, H_PRINT = 1063, 591  # 9x5 cm at 300 DPI
MARGIN = 150
ICON_SIZE = (96, 96)
ICON_GAP = 30
LINE_SPACING = 120
QR_SIZE = 600

# Asset paths
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"
QR_CODE = "assets/icons/qr_code.png"
LOGO_BACK = "assets/icons/tray_logo_white.png"
