import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import os

# Constants
CARD_WIDTH, CARD_HEIGHT = 1050, 600  # 9x5 cm at 300dpi
MARGIN = 150
ICON_SIZE = 96
GAP_BETWEEN_LINES = 120
ICON_GAP = 40
QR_SIZE = 600

# Fonts
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_AR_REG = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_REG = "assets/fonts/PlusJakartaSans-Medium.ttf"

# Assets
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"
QR_CODE = "assets/icons/qr_code.png"

def load_font(path, size):
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    img = Image.open(path).convert("RGBA")
    return img.resize(size, Image.LANCZOS) if size else img

def draw_contact_line(draw, canvas, icon, text, x, y, font):
    canvas.paste(icon, (x, y), mask=icon)
    text_height = font.getsize(text)[1]
    text_y = y + (ICON_SIZE - text_height) // 2
    draw.text((x + ICON_SIZE + ICON_GAP, text_y), text, font=font, fill="#0F254F")

def generate_front(width, height, fonts, ar_name, ar_title, en_name, en_title, email, phone):
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)

    # Positions
    ar_name_pos = (width - MARGIN, MARGIN)
    ar_title_pos = (width - MARGIN, MARGIN + 100)
    en_name_pos = (MARGIN, MARGIN)
    en_title_pos = (MARGIN, MARGIN + 100)

    # English text
    draw.text(en_name_pos, en_name, font=fonts["en_bold"], fill="#0F254F")
    draw.text(en_title_pos, en_title, font=fonts["en_reg"], fill="#0F254F")

    # Arabic text (right-aligned)
    ar_name_w, _ = draw.textsize(ar_name, font=fonts["ar_bold"])
    ar_title_w, _ = draw.textsize(ar_title, font=fonts["ar_reg"])
    draw.text((ar_name_pos[0] - ar_name_w, ar_name_pos[1]), ar_name, font=fonts["ar_bold"], fill="#0F254F")
    draw.text((ar_title_pos[0] - ar_title_w, ar_title_pos[1]), ar_title, font=fonts["ar_reg"], fill="#0F254F")

    # Icons & contact
    icon_email = load_img(ICON_EMAIL, (ICON_SIZE, ICON_SIZE))
    icon_phone = load_img(ICON_PHONE, (ICON_SIZE, ICON_SIZE))

    contact_start_y = height - MARGIN - (2 * ICON_SIZE) - GAP_BETWEEN_LINES
    draw_contact_line(draw, canvas, icon_email, email, MARGIN, contact_start_y, fonts["info"])
    draw_contact_line(draw, canvas, icon_phone, phone, MARGIN, contact_start_y + ICON_SIZE + GAP_BETWEEN_LINES, fonts["info"])

    # QR
    qr = load_img(QR_CODE, (QR_SIZE, QR_SIZE))
    canvas.paste(qr, (width - MARGIN - QR_SIZE, height - MARGIN - QR_SIZE), mask=qr)

    return canvas

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🔍 Preview (Front)")

# Form inputs
with st.sidebar:
    st.header("📇 معلومات البطاقة")
    ar_name = st.text_input("الاسم بالعربية", "")
    ar_title = st.text_input("المسمى بالعربية", "")
    en_name = st.text_input("Full Name", "")
    en_title = st.text_input("Job Title", "")
    email = st.text_input("Email", "")
    phone = st.text_input("Phone", "")

# Load fonts
fonts = {
    "ar_bold": load_font(FONT_AR_BOLD, 96),
    "ar_reg": load_font(FONT_AR_REG, 60),
    "en_bold": load_font(FONT_EN_BOLD, 96),
    "en_reg": load_font(FONT_EN_REG, 60),
    "info": load_font(FONT_EN_REG, 56),
}

# Generate image
front_img = generate_front(CARD_WIDTH, CARD_HEIGHT, fonts, ar_name, ar_title, en_name, en_title, email, phone)
st.image(front_img)

# PDF download
def save_as_pdf(image, filename):
    buf = BytesIO()
    image.save(buf, format="PDF", resolution=300.0)
    st.download_button(f"📥 {filename}", buf.getvalue(), file_name=filename, mime="application/pdf")

save_as_pdf(front_img, "tray_card_4K.pdf")
save_as_pdf(front_img, "tray_card_print.pdf")
