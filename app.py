import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# === Constants ===
CARD_WIDTH = 1600
CARD_HEIGHT = 900
MARGIN = 150
QR_SIZE = 600
ICON_SIZE = (96, 96)
LINE_SPACING = 60

# === Paths ===
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
ICON_EMAIL = "assets/icons/email.png"
ICON_PHONE = "assets/icons/phone.png"
QR_CODE = "assets/icons/qr_code.png"

# === Helpers ===
def load_font(path, size):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Font file not found: {path}")
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.ANTIALIAS)
    return img

def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])

def generate_card(ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    # Load Fonts
    fonts = {
        "ar_bold": load_font(FONT_AR_BOLD, 96),
        "ar_regular": load_font(FONT_AR_REGULAR, 60),
        "en_bold": load_font(FONT_EN_BOLD, 96),
        "en_regular": load_font(FONT_EN_REGULAR, 60),
    }

    # Top-Left (EN)
    x_en = MARGIN
    y_en = MARGIN
    draw.text((x_en, y_en), en_name, font=fonts["en_bold"], fill="#0F2B5B")
    draw.text((x_en, y_en + 100), en_title, font=fonts["en_regular"], fill="#0F2B5B")

    # Top-Right (AR)
    ar_name_size = text_size(draw, ar_name, fonts["ar_bold"])
    ar_title_size = text_size(draw, ar_title, fonts["ar_regular"])
    x_ar = CARD_WIDTH - MARGIN - ar_name_size[0]
    y_ar = MARGIN
    draw.text((x_ar, y_ar), ar_name, font=fonts["ar_bold"], fill="#0F2B5B")
    draw.text((CARD_WIDTH - MARGIN - ar_title_size[0], y_ar + 100), ar_title, font=fonts["ar_regular"], fill="#0F2B5B")

    # Bottom-Left (Contact)
    x_icon = MARGIN
    y_contact = CARD_HEIGHT - MARGIN - 2 * (ICON_SIZE[1] + LINE_SPACING)
    icon_email = load_img(ICON_EMAIL, ICON_SIZE)
    icon_phone = load_img(ICON_PHONE, ICON_SIZE)

    img.paste(icon_email, (x_icon, y_contact), mask=icon_email)
    draw.text((x_icon + ICON_SIZE[0] + 20, y_contact + 16), email, font=fonts["en_regular"], fill="#0F2B5B")

    y_phone = y_contact + ICON_SIZE[1] + LINE_SPACING
    img.paste(icon_phone, (x_icon, y_phone), mask=icon_phone)
    draw.text((x_icon + ICON_SIZE[0] + 20, y_phone + 16), phone, font=fonts["en_regular"], fill="#0F2B5B")

    # Bottom-Right (QR)
    qr = load_img(QR_CODE, (QR_SIZE, QR_SIZE))
    img.paste(qr, (CARD_WIDTH - MARGIN - QR_SIZE, CARD_HEIGHT - MARGIN - QR_SIZE), mask=qr)

    return img

# === Streamlit App ===
st.set_page_config(layout="centered")
st.title("🔍 Preview (Front)")

ar_name = st.text_input("Arabic Name", "")
ar_title = st.text_input("Arabic Job Title", "")
en_name = st.text_input("English Name", "")
en_title = st.text_input("English Job Title", "")
email = st.text_input("Email", "")
phone = st.text_input("Phone", "")

if any([ar_name, ar_title, en_name, en_title, email, phone]):
    card_image = generate_card(ar_name, ar_title, en_name, en_title, email, phone)
    st.image(card_image)

    # Export
    card_image.save("tray_card_4K.pdf", format="PDF", resolution=300.0)
    st.download_button("📥 tray_card_4K.pdf", data=open("tray_card_4K.pdf", "rb"), file_name="tray_card_4K.pdf")
