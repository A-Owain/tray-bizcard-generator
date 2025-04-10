
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

# Constants
CARD_WIDTH = 1440
CARD_HEIGHT = 800
MARGIN = 150
QR_SIZE = 600
ICON_SIZE = (96, 96)
GAP_BETWEEN_LINES = 90
ICON_GAP = 40

# Font paths
FONT_AR_BOLD = "assets/fonts/NotoSansArabic-SemiBold.ttf"
FONT_AR_REGULAR = "assets/fonts/NotoSansArabic-Regular.ttf"
FONT_EN_BOLD = "assets/fonts/PlusJakartaSans-Bold.ttf"
FONT_EN_REGULAR = "assets/fonts/PlusJakartaSans-Regular.ttf"

# Load font
def load_font(path, size):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Font file not found: {path}")
    return ImageFont.truetype(path, size)

# Load image
def load_img(path, size=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size, Image.LANCZOS)
    return img

# Generate card
def generate_card(ar_name, ar_title, en_name, en_title, email, phone):
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    fonts = {
        "ar_bold": load_font(FONT_AR_BOLD, 96),
        "ar_regular": load_font(FONT_AR_REGULAR, 60),
        "en_bold": load_font(FONT_EN_BOLD, 96),
        "en_regular": load_font(FONT_EN_REGULAR, 60),
    }

    # Top right: Arabic
    ar_name_size = draw.textsize(ar_name, font=fonts["ar_bold"])
    ar_title_size = draw.textsize(ar_title, font=fonts["ar_regular"])
    ar_name_pos = (CARD_WIDTH - MARGIN - ar_name_size[0], MARGIN)
    ar_title_pos = (CARD_WIDTH - MARGIN - ar_title_size[0], ar_name_pos[1] + ar_name_size[1] + 5)

    draw.text(ar_name_pos, ar_name, font=fonts["ar_bold"], fill="#0f254c")
    draw.text(ar_title_pos, ar_title, font=fonts["ar_regular"], fill="#0f254c")

    # Top left: English
    en_name_pos = (MARGIN, MARGIN)
    en_title_pos = (MARGIN, en_name_pos[1] + ar_name_size[1] + 5)

    draw.text(en_name_pos, en_name, font=fonts["en_bold"], fill="#0f254c")
    draw.text(en_title_pos, en_title, font=fonts["en_regular"], fill="#0f254c")

    # Bottom right: QR
    qr = load_img("assets/icons/qr_code.png")
    qr = ImageOps.contain(qr, (QR_SIZE, QR_SIZE))
    qr_pos = (CARD_WIDTH - MARGIN - qr.width, CARD_HEIGHT - MARGIN - qr.height)
    img.paste(qr, qr_pos, qr)

    # Bottom left: contact info
    icon_email = load_img("assets/icons/email.png", ICON_SIZE)
    icon_phone = load_img("assets/icons/phone.png", ICON_SIZE)

    contact_font = fonts["en_regular"]
    contact_y = CARD_HEIGHT - MARGIN - ICON_SIZE[1] * 2 - GAP_BETWEEN_LINES

    # Email
    img.paste(icon_email, (MARGIN, contact_y), icon_email)
    draw.text(
        (MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + (ICON_SIZE[1] - contact_font.getsize(email)[1]) // 2),
        email,
        font=contact_font,
        fill="#0f254c",
    )

    # Phone
    contact_y += ICON_SIZE[1] + GAP_BETWEEN_LINES
    img.paste(icon_phone, (MARGIN, contact_y), icon_phone)
    draw.text(
        (MARGIN + ICON_SIZE[0] + ICON_GAP, contact_y + (ICON_SIZE[1] - contact_font.getsize(phone)[1]) // 2),
        phone,
        font=contact_font,
        fill="#0f254c",
    )

    return img

# Streamlit UI
st.title("🔍 Preview (Front)")

with st.form("card_info"):
    ar_name = st.text_input("الاسم بالعربية", "")
    ar_title = st.text_input("المسمى الوظيفي بالعربية", "")
    en_name = st.text_input("Full Name", "")
    en_title = st.text_input("Job Title", "")
    email = st.text_input("Email", "")
    phone = st.text_input("Phone", "")

    submitted = st.form_submit_button("Generate Card")

if submitted:
    card_image = generate_card(ar_name, ar_title, en_name, en_title, email, phone)

    st.image(card_image, caption="Business Card Preview", use_column_width=True)

    # Save as 4K
    card_image.save("tray_card_4K.pdf", "PDF", resolution=300)
    st.download_button("⬇️ tray_card_4K.pdf", data=open("tray_card_4K.pdf", "rb"), file_name="tray_card_4K.pdf")
