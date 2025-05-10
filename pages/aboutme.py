import streamlit as st

st.set_page_config(page_title="About the Author", layout="wide")

st.title("👤 About the Author")

st.markdown("""
### Hi, I'm Yoong Sin 👋

I'm the creator of this Garmin Health & Performance Dashboard.

As a passionate software engineer and data science practitioner, I built this dashboard to help runners, cyclists, and health enthusiasts analyze and visualize their performance data with ease.

**Background:**
- Master's in Data Science, Universiti Teknologi Malaysia
- Bachelor's in Chemical Engineering, Universiti Sains Malaysia
- Data Science Engineer @ Coherent

**Technologies Used in this App:**
- Python
- Streamlit
- Plotly
- pandas
- fitparse

**Why I Made This:**
I wanted a tool that could ingest Garmin and Strava data, let users tweak pace zones, compare training sessions, and provide insightful feedback — all without needing to code.

**Let’s Connect:**
- [LinkedIn](https://www.linkedin.com/in/tehyoongsin/)
- [GitHub](https://github.com/Ether-silicon)

Thanks for using this app! Feel free to reach out or suggest improvements 🙌
""")

with st.sidebar:
    st.header("👨‍💻 Profile")
    st.markdown("**Name:** Teh Yoong Sin")
    st.markdown("**Role:** Data Science Engineer @ Coherent")
    st.markdown("**Field:** Data Science, Data Analytics")
    st.markdown("**Country:** Malaysia")

    st.sidebar.markdown("### 🎯 Interests")
    st.sidebar.markdown("""
    - Marathon Training  
    - Personal Fitness Data    
    """)