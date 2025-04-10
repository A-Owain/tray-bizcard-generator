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
LOGO_BACK = "assets/icons/tray_logo_white.png"

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

# Front face generator
def generate_front(w, h, fonts, ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (w, h), color="white")
    draw = ImageDraw.Draw(img)

    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)
    qr_code = load_img(QR_CODE, (QR_SIZE, QR_SIZE))

    ar_name = reshape_arabic(ar_name)
    ar_title = reshape_arabic(ar_title)

    draw.text((MARGIN, MARGIN), en_name, font=fonts["en_bold"], fill="#001F4B")
    draw.text((MARGIN, MARGIN + 220), en_title, font=fonts["en_regular"], fill="#001F4B")

    AR_Y_OFFSET = -60
    draw.text((w - MARGIN, MARGIN + AR_Y_OFFSET), ar_name, font=fonts["ar_bold"], fill="#001F4B", anchor="ra")
    draw.text((w - MARGIN, MARGIN + AR_Y_OFFSET + 220), ar_title, font=fonts["ar_regular"], fill="#001F4B", anchor="ra")

    contact_y = h - MARGIN - ICON_SIZE[1]*2 - LINE_SPACING
    img.paste(icon_email, (MARGIN, contact_y), icon_email)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + 0), email, font=fonts["en_regular"], fill="#001F4B")

    contact_y += ICON_SIZE[1] + LINE_SPACING
    img.paste(icon_phone, (MARGIN, contact_y), icon_phone)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + 0), phone, font=fonts["en_regular"], fill="#001F4B")

    img.paste(qr_code, (w - MARGIN - QR_SIZE, h - MARGIN - QR_SIZE), qr_code)

    return img

# Back face generator
def generate_back(w, h):
    img = Image.new("RGB", (w, h), "#ea2f2f")
    if not os.path.exists(LOGO_BACK):
        st.error(f"⚠️ Logo not found at: {LOGO_BACK}")
        return img
    logo = load_img(LOGO_BACK, (1300, 1300))
    img.paste(logo, ((w - logo.width) // 2, (h - logo.height) // 2), logo)
    return img

# Streamlit app
st.set_page_config(layout="centered")
st.title("🖼️ Business Card Generator")

# Inputs
ar_name = st.text_input("Arabic Name", "")
ar_title = st.text_input("Arabic Job Title", "")
en_name = st.text_input("English Name", "")
en_title = st.text_input("English Job Title", "")
email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

fonts = {
    "ar_bold": load_font("assets/fonts/NotoSansArabic-SemiBold.ttf", 144),
    "ar_regular": load_font("assets/fonts/NotoSansArabic-Regular.ttf", 96),
    "en_bold": load_font("assets/fonts/PlusJakartaSans-Bold.ttf", 144),
    "en_regular": load_font("assets/fonts/PlusJakartaSans-Regular.ttf", 96),
}

if all([ar_name, ar_title, en_name, en_title, email, phone]):
    with st.container():
        card_image = generate_front(W_4K, H_4K, fonts, ar_name, ar_title, en_name, en_title, email, phone)
        card_back = generate_back(W_4K, H_4K)

        st.image(card_image)

        combined_buf = io.BytesIO()
        card_image.save(combined_buf, format="PDF", save_all=True, append_images=[card_back])
        combined_buf.seek(0)

        st.download_button(
            "📥 Download Front + Back PDF",
            data=combined_buf,
            file_name="tray_card_combined.pdf",
            mime="application/pdf"
        )
