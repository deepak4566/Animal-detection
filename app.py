import streamlit as st
from utils import save_user, verify_password, send_email
import tensorflow as tf
import numpy as np
from PIL import Image

import re


# Load the trained model
model = tf.keras.models.load_model('wildlife_rcnn_model.h5')

# Define the class names corresponding to the indices in your dataset
class_names = ['Lion', 'Cheetah', 'Leopard', 'Tiger', 'Jaguar']  # Update this list based on your dataset

# Function to validate email format
def validate_email(email):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None

# Function to preprocess images
def preprocess_image(img):
    img = img.resize((128, 128))  # Adjust based on your model's input size
    img_array = np.array(img) / 255.0  # Normalize
    return np.expand_dims(img_array, axis=0)  # Add batch dimension

# CSS for button styling
st.markdown("""
    <style>
        .stButton {
            background-color: #4CAF50; /* Green */
            border: none;
            color: black;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Menu
st.title("Wildlife Detection App")
st.subheader("Welcome to the Wildlife Detection App")
st.write("Please choose an option below:")

# User state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'show_login' not in st.session_state:
    st.session_state.show_login = False

if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

# Show Home Page
if not st.session_state.logged_in:
    if st.button("🏠 Home", key="home"):
        st.session_state.show_login = False
        st.session_state.show_signup = False

    # Sign Up Page
    if st.button("Sign Up", key="signup"):
        st.session_state.show_signup = True
        st.session_state.show_login = False

    if st.session_state.show_signup:
        st.subheader("Sign Up")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type='password', key="signup_password")
        
        if st.button("Create Account", key="create_account"):
            save_user(username, password)
            st.success("Account created successfully!")
            st.session_state.show_signup = False  # Hide signup form after creation

    # Login Page
    if st.button("Login", key="login"):
        st.session_state.show_login = True
        st.session_state.show_signup = False

    if st.session_state.show_login:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type='password', key="login_password")
        
        if st.button("Login", key="login_button"):
            if verify_password(username, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.balloons()  # Optional: Show balloons on successful login
                st.session_state.show_login = False  # Hide login form after successful login
            else:
                st.error("Invalid credentials!")

# After successful login, show a new page for image upload and detection
if st.session_state.logged_in:
    st.write("You are now logged in!")

    # Create a sidebar or main area for image upload
    st.sidebar.header("Image Detection")
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)

        # Prepare to store detection results
        if 'predicted_class' not in st.session_state:
            st.session_state.predicted_class = None

        # Button to detect animal
        if st.button("Detect Animal"):
            # Preprocess and predict
            processed_image = preprocess_image(image)
            predictions = model.predict(processed_image)
            predicted_class_index = np.argmax(predictions, axis=1)[0]  # Get the index of the highest prediction
            st.session_state.predicted_class = class_names[predicted_class_index]  # Store prediction in session state
            st.success(f"Detected: {st.session_state.predicted_class}")

        # Display predicted class if available
        if st.session_state.predicted_class:
            st.write(f"Predicted Class: {st.session_state.predicted_class}")

        # Email Notification with validation
        email = st.text_input("Enter your email for alerts:", key="email_input")
        if st.button("Send Email Alert", key="send_email"):
            if email and validate_email(email) and 'predicted_class' in st.session_state:
                subject = "Animal Detection Alert"
                message = f"Detected: {st.session_state.predicted_class}"
                send_email(email, subject, message)
                st.success("Email alert sent successfully!")
            else:
                st.error("Please enter a valid email address.")


    # Log Out Option
    if st.sidebar.button("Log Out", key="logout"):
        st.session_state.logged_in = False
        st.session_state.predicted_class = None  # Clear prediction on logout
        st.success("You have logged out.")
