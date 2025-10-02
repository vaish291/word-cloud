# app.py
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.title("☁️ Word Cloud Demo")

# Take input
text = st.text_area("Enter text here:", "Hello world! Streamlit makes word clouds easy.")

# Generate word cloud
if text:
    wc = WordCloud(width=500, height=300, background_color="white").generate(text)

    # Show with matplotlib
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    st.pyplot(fig)
