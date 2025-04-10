
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
LOGO_BACK = "assets/icons/Tray_logo_white.png"

# Load font
def load_font(path, size):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Font file not found: {path}")
    return ImageFont.truetype(path, size)

# Load and resize image
def load_img(path, size):
    img = Image.open(path).convert("RGBA")
    img = img.resize(size, Image.Resampling.LANCZOS)
    return img

# Generate front face
def generate_front(w, h, fonts):
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)

    # User Inputs
    ar_name = st.text_input("Arabic Name")
    ar_title = st.text_input("Arabic Job Title")
    en_name = st.text_input("English Name")
    en_title = st.text_input("English Job Title")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    # Coordinates
    left_x = MARGIN
    right_x = w - MARGIN
    top_y = MARGIN

    # Name positions
    draw.text((left_x, top_y), en_name, font=fonts["en_bold"], fill="#001F4B")
    draw.text((left_x, top_y + fonts["en_bold"].getsize(en_name)[1] + 10), en_title, font=fonts["en_regular"], fill="#001F4B")

    ar_name_size = fonts["ar_bold"].getsize(ar_name)
    ar_title_size = fonts["ar_regular"].getsize(ar_title)
    draw.text((right_x - ar_name_size[0], top_y), ar_name, font=fonts["ar_bold"], fill="#001F4B")
    draw.text((right_x - ar_title_size[0], top_y + ar_name_size[1] + 10), ar_title, font=fonts["ar_regular"], fill="#001F4B")

    # Icons
    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)

    contact_y = h - MARGIN - (ICON_SIZE[1] * 2 + LINE_SPACING)
    img.paste(icon_email, (left_x, contact_y), icon_email)
    draw.text((left_x + ICON_SIZE[0] + ICON_GAP, contact_y + 20), email, font=fonts["en_regular"], fill="#001F4B")

    contact_y += ICON_SIZE[1] + LINE_SPACING
    img.paste(icon_phone, (left_x, contact_y), icon_phone)
    draw.text((left_x + ICON_SIZE[0] + ICON_GAP, contact_y + 20), phone, font=fonts["en_regular"], fill="#001F4B")

    # QR code
    qr = load_img(QR_CODE, (QR_SIZE, QR_SIZE))
    img.paste(qr, (w - MARGIN - QR_SIZE, h - MARGIN - QR_SIZE), qr)

    return img

# Generate back face
def generate_back(w, h):
    img = Image.new("RGB", (w, h), "#ea2f2f")
    logo = load_img(LOGO_BACK, (1300, 1300))
    img.paste(logo, ((w - logo.width) // 2, (h - logo.height) // 2), logo)
    return img

# Load fonts
fonts = {
    "ar_bold": load_font(FONT_AR_BOLD, 96),
    "ar_regular": load_font(FONT_AR_REGULAR, 64),
    "en_bold": load_font(FONT_EN_BOLD, 96),
    "en_regular": load_font(FONT_EN_REGULAR, 64),
}

# Streamlit UI
st.title("🔍 Preview (Front)")
tab1, tab2 = st.tabs(["Front Face", "Back Face"])

with tab1:
    card_front = generate_front(W_4K, H_4K, fonts)

    buf = io.BytesIO()
    card_front.save(buf, format="PDF")
    st.download_button("📥 Download Front PDF (4K)", data=buf.getvalue(), file_name="tray_card_4K.pdf")

    st.image(card_front)

with tab2:
    card_back = generate_back(W_4K, H_4K)

    buf = io.BytesIO()
    card_back.save(buf, format="PDF")
    st.download_button("📥 Download Back PDF", data=buf.getvalue(), file_name="tray_card_back.pdf")

    st.image(card_back)
