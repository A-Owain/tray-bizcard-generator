import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# ============================ CONFIG ============================

CARD_WIDTH = 3508  # 9cm at 300 DPI
CARD_HEIGHT = 1979  # 5cm at 300 DPI
MARGIN = 150
QR_SIZE = 600
ICON_SIZE = (96, 96)
ICON_GAP = 60
CONTACT_LINE_SPACING = 150
TEXT_COLOR = (20, 45, 78)
ICON_EMAIL_PATH = "assets/icons/email.png"
ICON_PHONE_PATH = "assets/icons/phone.png"
QR_CODE_PATH = "assets/qr_code.png"
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"

# ============================ HELPERS ============================

def load_font(path, size):
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.ANTIALIAS)
    return img

def draw_text_centered(draw, text, font, center, fill):
    w, h = draw.textsize(text, font=font)
    position = (center[0] - w // 2, center[1] - h // 2)
    draw.text(position, text, font=font, fill=fill)

# ============================ GENERATOR ============================

def generate_card(ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    fonts = {
        "ar_bold": load_font(FONT_AR_BOLD, 96),
        "ar_reg": load_font(FONT_AR_REGULAR, 64),
        "en_bold": load_font(FONT_EN_BOLD, 96),
        "en_reg": load_font(FONT_EN_REGULAR, 64),
    }

    # ==== TOP: Names & Titles ====
    name_top = MARGIN
    draw.text((CARD_WIDTH - MARGIN, name_top), ar_name, font=fonts["ar_bold"], fill=TEXT_COLOR, anchor="rt")
    draw.text((CARD_WIDTH - MARGIN, name_top + 105), ar_title, font=fonts["ar_reg"], fill=TEXT_COLOR, anchor="rt")
    draw.text((MARGIN, name_top), en_name, font=fonts["en_bold"], fill=TEXT_COLOR)
    draw.text((MARGIN, name_top + 105), en_title, font=fonts["en_reg"], fill=TEXT_COLOR)

    # ==== BOTTOM: Contact Info ====
    email_icon = load_img(ICON_EMAIL_PATH, ICON_SIZE)
    phone_icon = load_img(ICON_PHONE_PATH, ICON_SIZE)
    qr_code = load_img(QR_CODE_PATH, (QR_SIZE, QR_SIZE))

    contact_y = CARD_HEIGHT - MARGIN - ICON_SIZE[1] * 2 - CONTACT_LINE_SPACING
    contact_x = MARGIN

    # Email
    img.paste(email_icon, (contact_x, contact_y), email_icon)
    draw.text(
        (contact_x + ICON_SIZE[0] + ICON_GAP, contact_y + ICON_SIZE[1] // 2),
        email,
        font=fonts["en_reg"],
        fill=TEXT_COLOR,
        anchor="ls"
    )

    # Phone
    phone_y = contact_y + ICON_SIZE[1] + CONTACT_LINE_SPACING
    img.paste(phone_icon, (contact_x, phone_y), phone_icon)
    draw.text(
        (contact_x + ICON_SIZE[0] + ICON_GAP, phone_y + ICON_SIZE[1] // 2),
        phone,
        font=fonts["en_reg"],
        fill=TEXT_COLOR,
        anchor="ls"
    )

    # QR Code
    qr_x = CARD_WIDTH - MARGIN - QR_SIZE
    qr_y = CARD_HEIGHT - MARGIN - QR_SIZE
    img.paste(qr_code, (qr_x, qr_y), qr_code)

    return img

# ============================ STREAMLIT UI ============================

st.set_page_config(layout="centered", page_title="Tray Business Card Generator")

st.title("📇 معلومات البطاقة")

col1, col2 = st.columns(2)
with col1:
    ar_name = st.text_input("الاسم بالعربية", "")
    ar_title = st.text_input("المسمى بالعربية", "")
with col2:
    en_name = st.text_input("Full Name", "")
    en_title = st.text_input("Job Title", "")

email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

card_image = generate_card(ar_name, ar_title, en_name, en_title, email, phone)

st.subheader("🔍 Preview (Front)")
st.image(card_image)

# === Downloads ===
def download_pdf(image, filename):
    buffer = io.BytesIO()
    image.save(buffer, format="PDF", resolution=300)
    st.download_button(
        label=f"📥 Download {filename}",
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/pdf"
    )

download_pdf(card_image, "tray_card_print.pdf")
