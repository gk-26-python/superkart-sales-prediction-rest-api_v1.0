
import streamlit as st
import requests
import pandas as pd

# --- Streamlit App UI ---
st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")
st.title("SuperKart Sales Prediction App")
st.markdown("Enter product and store details to predict sales.")

# Input fields for product details
st.header("Product Details")
product_id = st.text_input("Product ID", "FD6114")
product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66, format="%.2f")
product_sugar_content = st.selectbox("Product Sugar Content", ['Low Sugar', 'Regular', 'No Sugar'])
product_allocated_area = st.number_input("Product Allocated Area (Ratio)", min_value=0.0, max_value=1.0, value=0.027, format="%.3f")
product_type = st.selectbox("Product Type", [
    'Fruits and Vegetables', 'Snack Foods', 'Frozen Foods', 'Dairy', 'Household',
    'Baking Goods', 'Canned', 'Health and Hygiene', 'Meat', 'Soft Drinks',
    'Breads', 'Hard Drinks', 'Others', 'Starchy Foods', 'Breakfast', 'Seafood'
])
product_mrp = st.number_input("Product MRP (Maximum Retail Price)", min_value=0.0, value=100.0, format="%.2f")

# Input fields for store details
st.header("Store Details")
store_id = st.text_input("Store ID", "OUT010")
store_establishment_year = st.number_input("Store Establishment Year", min_value=1900, max_value=2024, value=1999, format="%d")
store_size = st.selectbox("Store Size", ['Medium', 'High', 'Small'])
store_location_city_type = st.selectbox("Store Location City Type", ['Tier 1', 'Tier 2', 'Tier 3'])
store_type = st.selectbox("Store Type", ['Supermarket Type1', 'Supermarket Type2', 'Departmental Store', 'Food Mart'])

# Create a dictionary for the input data
input_data = {
    'Product_Id': product_id,
    'Product_Weight': product_weight,
    'Product_Sugar_Content': product_sugar_content,
    'Product_Allocated_Area': product_allocated_area,
    'Product_Type': product_type,
    'Product_MRP': product_mrp,
    'Store_Id': store_id,
    'Store_Establishment_Year': store_establishment_year,
    'Store_Size': store_size,
    'Store_Location_City_Type': store_location_city_type,
    'Store_Type': store_type
}

# Prediction button
if st.button("Predict Sales"):
    try:
        # Make a POST request to the Flask API. Replace with your actual backend URL
        # In a Docker Compose setup, 'backend' would resolve to the Flask service
        # For local testing, you might use 'http://localhost:5000/predict' or 'http://127.0.0.1:5000/predict'
        response = requests.post("http://backend:7860/predict", json=input_data)

        if response.status_code == 200:
            prediction = response.json()
            predicted_sales = prediction.get('predicted_sales')
            st.success(f"Predicted Product Store Sales Total: ${predicted_sales:,.2f}")
        else:
            st.error(f"Error from API: {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Could not connect to the backend API. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


st.markdown("--- ")
st.write("Note: The backend API must be running for predictions to work.")
