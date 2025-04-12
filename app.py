
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import io
import os

# Constants
BASE_W, BASE_H = 3840, 2160
SCALE = 2
W, H = BASE_W * SCALE, BASE_H * SCALE
MARGIN = 150 * SCALE
QR_SIZE = 600 * SCALE
ICON_SIZE = (96 * SCALE, 96 * SCALE)
ICON_GAP = 30 * SCALE
LINE_SPACING = 120 * SCALE

# Paths
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"
QR_CODE = "assets/icons/qr_code.png"
LOGO_BACK = "assets/icons/tray_logo_white.png"

def load_font(path, size):
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.LANCZOS)
    return img

def reshape_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def generate_front(fonts, ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (W, H), color="white")
    draw = ImageDraw.Draw(img)

    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)
    qr_code = load_img(QR_CODE, (QR_SIZE, QR_SIZE))

    ar_name = reshape_arabic(ar_name)
    ar_title = reshape_arabic(ar_title)

    draw.text((MARGIN, MARGIN), en_name, font=fonts["en_bold"], fill="#001F4B")
    draw.text((MARGIN, MARGIN + int(110 * SCALE)), en_title, font=fonts["en_regular"], fill="#001F4B")

    AR_Y_OFFSET = -30 * SCALE
    draw.text((W - MARGIN, MARGIN + AR_Y_OFFSET), ar_name, font=fonts["ar_bold"], fill="#001F4B", anchor="ra")
    draw.text((W - MARGIN, MARGIN + AR_Y_OFFSET + int(110 * SCALE)), ar_title, font=fonts["ar_regular"], fill="#001F4B", anchor="ra")

    contact_y = H - MARGIN - ICON_SIZE[1] * 2 - LINE_SPACING
    img.paste(icon_email, (MARGIN, contact_y), icon_email)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + 10), email, font=fonts["en_regular"], fill="#001F4B")

    contact_y += ICON_SIZE[1] + LINE_SPACING
    img.paste(icon_phone, (MARGIN, contact_y), icon_phone)
    draw.text((MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + 10), phone, font=fonts["en_regular"], fill="#001F4B")

    img.paste(qr_code, (W - MARGIN - QR_SIZE, H - MARGIN - QR_SIZE), qr_code)

    return img.resize((BASE_W, BASE_H), Image.LANCZOS)

def generate_back():
    img = Image.new("RGB", (W, H), "#ea2f2f")
    if not os.path.exists(LOGO_BACK):
        return img.resize((BASE_W, BASE_H), Image.LANCZOS)
    logo = load_img(LOGO_BACK, (1300 * SCALE, 1300 * SCALE))
    img.paste(logo, ((W - logo.width) // 2, (H - logo.height) // 2), logo)
    return img.resize((BASE_W, BASE_H), Image.LANCZOS)

st.set_page_config(layout="centered")
st.title("🖼️ Business Card Generator")

ar_name = st.text_input("Arabic Name", "")
ar_title = st.text_input("Arabic Job Title", "")
en_name = st.text_input("English Name", "")
en_title = st.text_input("English Job Title", "")
email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

fonts = {
    "ar_bold": load_font(FONT_AR_BOLD, 144),
    "ar_regular": load_font(FONT_AR_REGULAR, 96),
    "en_bold": load_font(FONT_EN_BOLD, 144),
    "en_regular": load_font(FONT_EN_REGULAR, 96),
}

if all([ar_name, ar_title, en_name, en_title, email, phone]):
    with st.container():
        front = generate_front(fonts, ar_name, ar_title, en_name, en_title, email, phone)
        back = generate_back()

        st.image(front)

        combined_buf = io.BytesIO()
        front.save(combined_buf, format="PDF", save_all=True, append_images=[back])
        combined_buf.seek(0)

        st.download_button(
            "📥 Download Front + Back PDF (High Quality)",
            data=combined_buf,
            file_name="tray_card_highres.pdf",
            mime="application/pdf"
        )
