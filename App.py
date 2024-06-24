import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import PyPDF2
from docx import Document
import base64
from io import BytesIO
from PIL import Image

# Functions for file reading
def read_txt(file):
    return file.getvalue().decode("utf-8")

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf.pages])

# Function to filter out stopwords
def filter_stopwords(text, additional_stopwords=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_stopwords))
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# Function to create download link for plot
def get_image_download_link(buffered, format_):
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}">Download Plot as {format_}</a>'

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Set up page config (placed at the very beginning)
st.set_page_config(page_title="Word Cloud Generator", page_icon=":cloud:")

# Streamlit code with golden theme and styled creator name
st.markdown(f"""
    <div style="background-color: #ffd700; padding: 1px; border-radius: 5px; border: px solid navy;">
        <h3 style='color: navy; font-size: 36px;'>Word Cloud Generator ✨</h3>
    </div>
""", unsafe_allow_html=True)

# Add wordcloud image for sample
image_url = 'https://cdn.pixabay.com/photo/2016/04/27/01/39/search-1355847_1280.png'
st.sidebar.image(image_url, use_column_width=True)

# Detailed description of the app
st.markdown("""
#### WordCloud:
This application allows you to create a stylish and customizable word cloud from text data. You can upload a text, PDF, or DOCX file, and the app will generate a word cloud based on the content of the file.
""")

# Golden theme CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color:;
        color: black;
    }
    .st-bk {
        color: black;
    }
    .st-ax {
        font-family: "Arial", sans-serif;
        font-size: 16px;
    }
    .css-1cpxqw2 a {
        color: black !important;
    }
    .css-1aumxhk {
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Animation CSS
st.markdown("""
    <style>
    .st-bk {
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to read uploaded file and process
def process_file(uploaded_file):
    if uploaded_file:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)

        # Check the file type and read the file
        if uploaded_file.type == "text/plain":
            text = read_txt(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        else:
            st.error("File type not supported. Please upload a txt, pdf or docx file.")
            st.stop()

        # Generate word count table
        words = text.split()
        word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)

        # Sidebar: Checkbox and Multiselect box for stopwords
        use_standard_stopwords = st.checkbox("Use standard stopwords?", True)
        top_words = word_count['Word'].head(50).tolist()
        additional_stopwords = st.multiselect("Additional stopwords:", sorted(top_words))

        if use_standard_stopwords:
            all_stopwords = STOPWORDS.union(set(additional_stopwords))
        else:
            all_stopwords = set(additional_stopwords)

        text = filter_stopwords(text, all_stopwords)

        if text:
            # Word Cloud dimensions
            width = st.slider("Select Word Cloud Width", 400, 2000, 1200, 50)
            height = st.slider("Select Word Cloud Height", 200, 2000, 800, 50)

            # Additional customization options
            color_map = st.selectbox("Select Color Map", ["viridis", "plasma", "inferno", "magma", "cividis", "Blues", "Greens", "Oranges", "Purples", "Reds"])
            
            # Generate wordcloud
            st.subheader("Generated Word Cloud")
            fig, ax = plt.subplots(figsize=(width/100, height/100))
            wordcloud_img = WordCloud(width=width, height=height, background_color='white', max_words=200, contour_width=3, colormap=color_map).generate(text)
            ax.imshow(wordcloud_img, interpolation='bilinear')
            ax.axis('off')

            # Save plot functionality
            format_ = st.selectbox("Select file format to save the plot", ["png", "jpeg", "svg", "pdf"])
            resolution = st.slider("Select Resolution", 100, 500, 300, 50)
            
            st.pyplot(fig)
            if st.button(f"Save as {format_}"):
                buffered = BytesIO()
                plt.savefig(buffered, format=format_, dpi=resolution)
                buffered.seek(0)  # Rewind the buffer
                st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)

        st.subheader("Word Count Table")
        st.write(word_count)
        # Provide download link for table
        if st.button('Download Word Count Table as CSV'):
            st.markdown(get_table_download_link(word_count, "word_count.csv", "Click Here to Download"), unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("📁 Choose a file", type=["txt", "pdf", "docx"])

# Optional: Check if file is uploaded and process it
if uploaded_file is not None:
    process_file(uploaded_file)

# Apply CSS styling to the file uploader button
st.markdown(
    """
    <style>
    /* Add some padding and border to the file uploader button */
    .st-cq {
        padding: 8px 12px; /* Adjust padding as needed */
        border: 2px solid #3366FF; /* Border color */
        border-radius: 5px; /* Optional: Add border radius */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("""
    <div style="background-color: ; padding: 10px; border-radius: 5px; border: 1px solid #e5b200; text-align: center;">
        <h3 style="color: black;">About the Creator</h3>
        <h2 style="color: navy; font-size: 26px;">Danish Mubashar</h2>
        <div style="display: flex; flex-direction: column; align-items: center;">
            <img src="https://media.licdn.com/dms/image/D4D03AQELllA0lPk4aA/profile-displayphoto-shrink_400_400/0/1715315331343?e=2147483647&v=beta&t=b1lBAk60t37uv2901yndcly7-R0t7E7AGcalM0Ho7rE" alt="Profile Picture" style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid navy; margin-bottom: 15px;">
            <p style="color: black;">I am a Data Scientist and I love to create beautiful and interactive data visualizations.</p>
            <div style="margin-top: 20px;">
                <p style="color: navy; font-size: 16px; font-weight: bold;">Connect with me:</p>
                <a href="https://www.linkedin.com/in/muhammad-danish-mubashar-002b912a0/?originalSubdomain=pk" target="_blank" style="display: inline-block; background-color: #0077B5; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">LinkedIn</a>
                <a href="https://github.com/DanishMUbashar" target="_blank" style="display: inline-block; background-color: #333; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">GitHub</a>
                <a href="https://www.kaggle.com/danishmubashar" target="_blank" style="display: inline-block; background-color: #20BEFF; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">Kaggle</a>
            </div>
            <div style="margin-top: 10px;">
                <a href="mailto:danishmubashar81@gmail.com" style="display: inline-block; background-color: #DB4437; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">Email</a>
                <a href="tel:+923042193281" style="display: inline-block; background-color: #4CAF50; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">Phone</a>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)
