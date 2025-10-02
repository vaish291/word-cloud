# app.py
import streamlit as st
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="Word Cloud Generator", layout="centered")

st.title("🔤 Word Cloud Generator (Streamlit)")

# Sidebar controls
st.sidebar.header("Options")
max_words = st.sidebar.slider("Max words", min_value=50, max_value=1000, value=200, step=10)
background_color = st.sidebar.color_picker("Background color", "#ffffff")
colormap = st.sidebar.selectbox("Colormap (matplotlib)", 
                                ["viridis","plasma","inferno","magma","cividis","tab10","tab20","coolwarm","rainbow","Pastel1"])
use_mask = st.sidebar.checkbox("Use mask (upload PNG/JPG with transparent background or silhouette)", value=False)
scale = st.sidebar.slider("Image scale (dpi-like)", 1, 3, 2)

st.sidebar.markdown("---")
st.sidebar.write("Extra stopwords (comma separated)")
extra_stopwords_text = st.sidebar.text_input("", "")

# Input area
st.subheader("Input text")
input_mode = st.radio("Get text from:", ("Paste / Type text", "Upload text file (txt)", "Use sample text"), index=0)

text = ""
uploaded_txt = None
if input_mode == "Paste / Type text":
    text = st.text_area("Enter your text here", height=200)
elif input_mode == "Upload text file (txt)":
    uploaded_txt = st.file_uploader("Upload .txt file", type=["txt"])
    if uploaded_txt:
        try:
            text = uploaded_txt.read().decode("utf-8", errors="ignore")
        except Exception:
            # fallback
            uploaded_txt.seek(0)
            text = uploaded_txt.read().decode("latin-1", errors="ignore")
else:
    # sample text — replace with anything you prefer
    text = ("Streamlit makes it easy to build beautiful apps for machine learning and data science. "
            "Word clouds are a popular way to visualize text data by showing the most frequent words. "
            "This example app supports masks, stopwords, color maps, and downloading the generated image.")

if not text.strip():
    st.info("Enter or upload text to generate a word cloud.")
    st.stop()

# Mask upload
mask = None
if use_mask:
    mask_file = st.file_uploader("Upload mask image (PNG/JPG). White/transparent areas will be ignored.", type=["png","jpg","jpeg"])
    if mask_file:
        mask_img = Image.open(mask_file).convert("RGBA")
        # Convert RGBA to mask: non-white/transparent becomes 1, white becomes 0
        # Simpler: convert to grayscale and consider >250 as background
        mask_gray = mask_img.convert("L")
        mask_arr = np.array(mask_gray)
        # invert so that silhouette is 255 and background 0
        mask = np.where(mask_arr > 250, 0, 255).astype(np.uint8)

# Build stopwords set
stopwords = set(STOPWORDS)
if extra_stopwords_text.strip():
    extras = [w.strip() for w in extra_stopwords_text.split(",") if w.strip()]
    stopwords.update(extras)

# Generate button
if st.button("Generate Word Cloud"):
    # create wordcloud
    wc = WordCloud(width=800*scale,
                   height=400*scale,
                   background_color=background_color,
                   max_words=max_words,
                   stopwords=stopwords,
                   colormap=colormap,
                   mask=mask,
                   contour_width=0 if mask is None else 1,
                   contour_color='black' if mask is not None else None,
                   random_state=42)

    wc.generate(text)

    # Render to image buffer
    fig, ax = plt.subplots(figsize=(10*scale, 5*scale))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)

    st.image(buf, use_column_width=True)

    # Download button
    st.download_button(
        label="Download image (PNG)",
        data=buf,
        file_name="wordcloud.png",
        mime="image/png"
    )

st.markdown("---")
st.markdown("**Tips:** Use clear text (longer text gives better results). Add words to stopwords to remove them from the cloud. For masks, use a silhouette image (white background improves results).")
