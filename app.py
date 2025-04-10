import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# ========== CONFIG ==========
CARD_WIDTH = 1050
CARD_HEIGHT = 600
MARGIN = 150
ICON_SIZE = 96
ICON_GAP = 60
GAP_BETWEEN_LINES = 120
QR_SIZE = 300
TEXT_COLOR = (20, 45, 78)

# ========== ASSETS ==========
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-Bold.ttf"
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"
ICON_EMAIL_PATH = "assets/icons/email.png"
ICON_PHONE_PATH = "assets/icons/phone.png"
QR_CODE_PATH = "assets/qr_code.png"

# ========== HELPERS ==========
def load_font(path, size):
    if not os.path.exists(path):
        st.error(f"❌ Font file missing: {path}")
        raise FileNotFoundError(f"Font file not found: {path}")
    return ImageFont.truetype(path, size)

def load_img(path, size=None):
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.ANTIALIAS)
    return img

def draw_contact_line(draw, canvas, icon, text, x, y, font):
    canvas.paste(icon, (x, y), mask=icon)
    text_height = font.getbbox(text)[3] - font.getbbox(text)[1]
    text_y = y + ICON_SIZE - text_height
    draw.text((x + ICON_SIZE + ICON_GAP, text_y), text, font=font, fill=TEXT_COLOR)

# ========== CARD GENERATOR ==========
def generate_card(ar_name, ar_title, en_name, en_title, email, phone):
    canvas = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(canvas)

    fonts = {
        "ar_bold": load_font(FONT_AR_BOLD, 96),
        "ar_reg": load_font(FONT_AR_REGULAR, 60),
        "en_bold": load_font(FONT_EN_BOLD, 96),
        "en_reg": load_font(FONT_EN_REGULAR, 60),
        "info": load_font(FONT_EN_REGULAR, 56),
    }

    name_top = MARGIN
    draw.text((MARGIN, name_top), en_name, font=fonts["en_bold"], fill=TEXT_COLOR)
    draw.text((MARGIN, name_top + 105), en_title, font=fonts["en_reg"], fill=TEXT_COLOR)
    draw.text((CARD_WIDTH - MARGIN, name_top), ar_name, font=fonts["ar_bold"], fill=TEXT_COLOR, anchor="ra")
    draw.text((CARD_WIDTH - MARGIN, name_top + 105), ar_title, font=fonts["ar_reg"], fill=TEXT_COLOR, anchor="ra")

    # Contact Info
    email_icon = load_img(ICON_EMAIL_PATH, ICON_SIZE)
    phone_icon = load_img(ICON_PHONE_PATH, ICON_SIZE)
    contact_y = CARD_HEIGHT - MARGIN - (2 * ICON_SIZE) - GAP_BETWEEN_LINES
    draw_contact_line(draw, canvas, email_icon, email, MARGIN, contact_y, fonts["info"])
    draw_contact_line(draw, canvas, phone_icon, phone, MARGIN, contact_y + ICON_SIZE + GAP_BETWEEN_LINES, fonts["info"])

    # QR
    qr_code = load_img(QR_CODE_PATH, (QR_SIZE, QR_SIZE))
    canvas.paste(qr_code, (CARD_WIDTH - MARGIN - QR_SIZE, CARD_HEIGHT - MARGIN - QR_SIZE), qr_code)

    return canvas

# ========== STREAMLIT UI ==========
st.set_page_config(layout="centered", page_title="TRAY Business Card Generator")

st.title("📇 TRAY Business Card Generator")

# Input Form
with st.sidebar:
    st.header("📝 Enter Card Info")
    ar_name = st.text_input("Arabic Name", "")
    ar_title = st.text_input("Arabic Title", "")
    en_name = st.text_input("English Name", "")
    en_title = st.text_input("English Title", "")
    email = st.text_input("Email", "")
    phone = st.text_input("Phone", "")

card_image = generate_card(ar_name, ar_title, en_name, en_title, email, phone)

st.subheader("🔍 Card Preview")
st.image(card_image)

# PDF Download
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
