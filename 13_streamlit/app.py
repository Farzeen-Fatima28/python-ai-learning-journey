import streamlit as st

st.title("My First Streamlit App")
st.write("Hello! This is a simple interactive app built with Python.")

# Text input
name = st.text_input("Enter your name")

# Slider
age = st.slider("Select your age", 0, 100, 25)

# Button
if st.button("Submit"):
    st.write(f"Hi {name}, you are {age} years old!")

# Dropdown/selectbox
subject = st.selectbox("Favorite subject", ["Math", "Science", "Computer Science"])
st.write(f"You selected: {subject}")