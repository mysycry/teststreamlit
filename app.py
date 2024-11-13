import os
import openai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(page_title="FreightMate™ - Your Freight Comparison Specialist", page_icon="🚚", layout="wide")

# Custom CSS
st.markdown("""
<style>
    body {
        color: #333333;
        background-color: #f0f0f0;
    }
    .stApp {
        background-image: url('https://freight-images.public.blob.vercel-storage.com/freight-background-NzI4MzM0.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #0066cc;
        border: 2px solid #004c99;
    }
    .stTextInput>div>div>input {
        color: #333333;
        background-color: #ffffff;
    }
    .stTextArea>div>div>textarea {
        color: #333333;
        background-color: #ffffff;
    }
    .card {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv("FreightMate_sample_dataset.csv")

df = load_data()

# Title
st.title('FreightMate™ - Your Freight Comparison Specialist')

# Navigation menu
menu = ["Home", "Freight Finder", "Rate Calculator", "About"]
choice = st.selectbox("Navigation", menu)

if choice == "Home":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("Welcome to FreightMate™! We help you find the most cost-effective freight options by comparing rates, schedules, and routes.")
    st.write("## What FreightMate™ Does")
    st.write("Our tool analyzes a comprehensive dataset of freight providers to offer you the best shipping solutions tailored to your needs.")
    st.write("## Key Features")
    st.write("- **Efficient Comparison:** Compare freight rates, transit times, and schedules across multiple carriers.")
    st.write("- **Route Optimization:** Find the most efficient routes for your shipments.")
    st.write("- **Cost Savings:** Identify the most cost-effective options for your freight needs.")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "Freight Finder":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Find the Best Freight Option")
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox("Select Origin", df['Origin'].unique())
    with col2:
        destination = st.selectbox("Select Destination", df['Destination'].unique())
    
    if st.button("Find Cheapest Freight"):
        filtered_df = df[(df['Origin'] == origin) & (df['Destination'] == destination)]
        if not filtered_df.empty:
            cheapest_freight = filtered_df.loc[filtered_df['Freight Rate (USD)'].idxmin()]
            st.success(f"The cheapest freight option from {origin} to {destination} is:")
            st.json(cheapest_freight.to_dict())
        else:
            st.warning("No direct routes found for the selected origin and destination.")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "Rate Calculator":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Freight Rate Calculator")
    weight = st.number_input("Enter shipment weight (kg)", min_value=0.1, step=0.1)
    distance = st.number_input("Enter shipping distance (km)", min_value=1, step=1)
    
    if st.button("Calculate Estimated Rate"):
        # This is a simplified calculation. In a real-world scenario, you'd use more complex pricing models.
        estimated_rate = weight * distance * 0.01  # Example calculation
        st.success(f"Estimated freight rate: ${estimated_rate:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "About":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("About FreightMate™")
    st.write("FreightMate™ is your trusted partner in freight logistics. Our advanced algorithms and comprehensive database ensure that you always get the best rates and routes for your shipments.")
    st.write("### Our Mission")
    st.write("To simplify freight logistics and empower businesses with cost-effective shipping solutions.")
    st.markdown('</div>', unsafe_allow_html=True)

# RAG Implementation
def get_rag_response(query):
    context = df.to_string()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are FreightMate, a freight comparison specialist. Only answer questions related to freight rates and scheduling."},
            {"role": "user", "content": f"Based on this data: {context}\n\nUser query: {query}"}
        ]
    )
    return response.choices[0].message['content']

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Ask FreightMate™")
user_query = st.text_input("Ask about freight rates and scheduling:")
if user_query:
    with st.spinner("FreightMate™ is thinking..."):
        rag_response = get_rag_response(user_query)
    st.write("FreightMate's Response:")
    st.write(rag_response)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("© 2024 FreightMate™ | All Rights Reserved")