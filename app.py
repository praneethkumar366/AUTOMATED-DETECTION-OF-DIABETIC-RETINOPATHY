import streamlit as st
import torch
import torchvision.transforms as transforms
from PIL import Image
import cv2
import numpy as np

# Load the trained model
@st.cache_resource
def load_model():
    model = torch.load("model.pth", map_location=torch.device("cpu"))  # Change path if needed
    model.eval()
    return model

model = load_model()

# Define image preprocessing function
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Adjust based on model input size
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension
    return image

# Function to predict
def predict(image):
    processed_image = preprocess_image(image)
    with torch.no_grad():
        output = model(processed_image)
        _, predicted = torch.max(output, 1)
    return "Blindness Detected" if predicted.item() == 1 else "No Blindness Detected"

# Streamlit UI
st.title("🩺 Retinal Blindness Detection")
st.write("Upload an image to check for blindness.")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Load and display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Predict button
    if st.button("Predict"):
        result = predict(image)
        st.write(f"### 🔍 Result: {result}")
