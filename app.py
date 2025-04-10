import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display
import io

# Constants
W_4K, H_4K = 3508, 2480
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

# Prepare Arabic text
def reshape_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

# Draw contact info
def draw_contact(draw, fonts, email, phone, x, y):
    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)

    contact_font = fonts["en_regular"]

    # Email
    draw.text((x + ICON_SIZE[0] + ICON_GAP, y), email, font=contact_font, fill="#001F4B")
    draw.bitmap((x, y), icon_email, fill=None)

    y += ICON_SIZE[1] + LINE_SPACING

    # Phone
    draw.text((x + ICON_SIZE[0] + ICON_GAP, y), phone, font=contact_font, fill="#001F4B")
    draw.bitmap((x, y), icon_phone, fill=None)

# Generator
def generate_front(w, h, fonts, ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (w, h), color="white")
    draw = ImageDraw.Draw(img)

    # Prepare text
    ar_name_display = reshape_arabic(ar_name)
    ar_title_display = reshape_arabic(ar_title)

    # Sizes
    ar_name_size = draw.textbbox((0,0), ar_name_display, font=fonts["ar_bold"])
    ar_title_size = draw.textbbox((0,0), ar_title_display, font=fonts["ar_regular"])
    en_name_size = draw.textbbox((0,0), en_name, font=fonts["en_bold"])

    # Positions
    left_x = MARGIN
    top_y = MARGIN
    right_x = w - MARGIN

    # English (Top-Left)
    draw.text((left_x, top_y), en_name, font=fonts["en_bold"], fill="#001F4B")
    draw.text((left_x, top_y + en_name_size[3] + 10), en_title, font=fonts["en_regular"], fill="#001F4B")

    # Arabic (Top-Right)
    ar_name_w = ar_name_size[2] - ar_name_size[0]
    ar_title_w = ar_title_size[2] - ar_title_size[0]
    draw.text((right_x - ar_name_w, top_y), ar_name_display, font=fonts["ar_bold"], fill="#001F4B")
    draw.text((right_x - ar_title_w, top_y + ar_name_size[3] + 10), ar_title_display, font=fonts["ar_regular"], fill="#001F4B")

    # Contact Info (Bottom-Left)
    bottom_y = h - MARGIN - ICON_SIZE[1] * 2 - LINE_SPACING
    draw_contact(draw, fonts, email, phone, left_x, bottom_y)

    # QR Code (Bottom-Right)
    qr = load_img(QR_CODE, (QR_SIZE, QR_SIZE))
    img.paste(qr, (right_x - QR_SIZE, h - MARGIN - QR_SIZE), mask=qr)

    return img

# Streamlit app
st.title("\U0001F50D Preview (Front)")

# Inputs
ar_name = st.text_input("Arabic Name", "")
ar_title = st.text_input("Arabic Job Title", "")
en_name = st.text_input("English Name", "")
en_title = st.text_input("English Job Title", "")
email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

# Fonts
fonts = {
    "ar_regular": load_font(FONT_AR_REGULAR, 72),
    "ar_bold": load_font(FONT_AR_BOLD, 96),
    "en_regular": load_font(FONT_EN_REGULAR, 72),
    "en_bold": load_font(FONT_EN_BOLD, 96)
}

# Generate card
card_front = generate_front(W_4K, H_4K, fonts, ar_name, ar_title, en_name, en_title, email, phone)
buf = io.BytesIO()
card_front.save(buf, format="PDF")
st.download_button("\U0001F4C5 Download Front PDF (4K)", data=buf.getvalue(), file_name="tray_card_4K.pdf")
