import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import io
import os

# Constants
W_4K, H_4K = 3840, 2160
MARGIN = 150
QR_SIZE = 600
ICON_SIZE = (96, 96)
ICON_GAP = 30
LINE_SPACING = 120

# Paths
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"
QR_CODE = "assets/icons/qr_code.png"

# Loaders
def load_font(path, size):
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.LANCZOS)
    return img

def reshape_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

# Generator
def generate_front(w, h, fonts, ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (w, h), color="white")
    draw = ImageDraw.Draw(img)

    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)
    qr_code = load_img(QR_CODE, (QR_SIZE, QR_SIZE))

    # Reshape Arabic
    ar_name = reshape_arabic(ar_name)
    ar_title = reshape_arabic(ar_title)

    # Top Left (English)
    draw.text((MARGIN, MARGIN), en_name, font=fonts["en_bold"], fill="#001F4B")
    draw.text((MARGIN, MARGIN + 110), en_title, font=fonts["en_regular"], fill="#001F4B")

    # Top Right (Arabic)
    AR_Y_OFFSET = -30
    draw.text((w - MARGIN, MARGIN + AR_Y_OFFSET), ar_name, font=fonts["ar_bold"], fill="#001F4B", anchor="ra")
    draw.text((w - MARGIN, MARGIN + AR_Y_OFFSET + 110), ar_title, font=fonts["ar_regular"], fill="#001F4B", anchor="ra")

    # Bottom Left
    contact_y = h - MARGIN - ICON_SIZE[1]*2 - LINE_SPACING
    img.paste(icon_email, (MARGIN, contact_y), icon_email)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + 10), email, font=fonts["en_regular"], fill="#001F4B")

    contact_y += ICON_SIZE[1] + LINE_SPACING
    img.paste(icon_phone, (MARGIN, contact_y), icon_phone)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + 10), phone, font=fonts["en_regular"], fill="#001F4B")

    # Bottom Right (QR)
    img.paste(qr_code, (w - MARGIN - QR_SIZE, h - MARGIN - QR_SIZE), qr_code)

    return img

# Back face generator
def generate_back(w, h):
    img = Image.new("RGB", (w, h), "#ea2f2f")
    logo_path = "assets/icons/tray_logo_white.png"
    if not os.path.exists(logo_path):
        st.error(f"⚠️ Logo not found at: {logo_path}")
        return img
    logo = load_img(logo_path, (1300, 1300))
    img.paste(logo, ((w - logo.width) // 2, (h - logo.height) // 2), logo)
    return img

# Streamlit app
st.set_page_config(layout="centered")
st.title("\U0001F50D Preview (Front)")

ar_name = st.text_input("Arabic Name", "")
ar_title = st.text_input("Arabic Job Title", "")
en_name = st.text_input("English Name", "")
en_title = st.text_input("English Job Title", "")
email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

fonts = {
    "ar_bold": load_font(FONT_AR_BOLD, 96),
    "ar_regular": load_font(FONT_AR_REGULAR, 72),
    "en_bold": load_font(FONT_EN_BOLD, 96),
    "en_regular": load_font(FONT_EN_REGULAR, 72),
}

if all([ar_name, ar_title, en_name, en_title, email, phone]):
    tab1, tab2 = st.tabs(["Front Face", "Back Face"])

    with tab1:
        card_image = generate_front(W_4K, H_4K, fonts, ar_name, ar_title, en_name, en_title, email, phone)
        st.image(card_image)
        buf_front = io.BytesIO()
        card_image.save(buf_front, format="PDF")
        buf_front.seek(0)
        st.download_button("📅 Download Front PDF (4K)", data=buf_front, file_name="tray_card_4K.pdf", mime="application/pdf")

    with tab2:
        card_back = generate_back(W_4K, H_4K)
        st.image(card_back)
        buf_back = io.BytesIO()
        card_back.save(buf_back, format="PDF")
        buf_back.seek(0)
        st.download_button("📅 Download Back PDF", data=buf_back, file_name="tray_card_back.pdf", mime="application/pdf")
st.download_button("📥 Download Front PDF (4K)", data=buf, file_name="tray_card_4K.pdf", mime="application/pdf")
