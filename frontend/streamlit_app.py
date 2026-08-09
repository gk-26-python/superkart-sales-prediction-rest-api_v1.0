
import streamlit as st
import requests
import pandas as pd
import io

# --- Streamlit App UI ---
st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")
st.title("SuperKart Sales Prediction App")
st.markdown("Enter product and store details to predict sales.")

# --- Single Prediction Section ---
st.header("Single Product Sales Prediction")

# Input fields for product details
with st.expander("Product Details"): # Using expander to organize inputs
    product_id = st.text_input("Product ID", "FD6114")
    product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66, format="%.2f")
    product_sugar_content = st.selectbox("Product Sugar Content", ['Low Sugar', 'Regular', 'No Sugar'], key="single_sugar")
    product_allocated_area = st.number_input("Product Allocated Area (Ratio)", min_value=0.0, max_value=1.0, value=0.027, format="%.3f")
    product_type = st.selectbox("Product Type", [
        'Fruits and Vegetables', 'Snack Foods', 'Frozen Foods', 'Dairy', 'Household',
        'Baking Goods', 'Canned', 'Health and Hygiene', 'Meat', 'Soft Drinks',
        'Breads', 'Hard Drinks', 'Others', 'Starchy Foods', 'Breakfast', 'Seafood'
    ], key="single_product_type")
    product_mrp = st.number_input("Product MRP (Maximum Retail Price)", min_value=0.0, value=100.0, format="%.2f")

# Input fields for store details
with st.expander("Store Details"): # Using expander to organize inputs
    store_id = st.text_input("Store ID", "OUT010")
    store_establishment_year = st.number_input("Store Establishment Year", min_value=1900, max_value=2024, value=1999, format="%d")
    store_size = st.selectbox("Store Size", ['Medium', 'High', 'Small'], key="single_store_size")
    store_location_city_type = st.selectbox("Store Location City Type", ['Tier 1', 'Tier 2', 'Tier 3'], key="single_city_type")
    store_type = st.selectbox("Store Type", ['Supermarket Type1', 'Supermarket Type2', 'Departmental Store', 'Food Mart'], key="single_store_type")

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

# Prediction button for single prediction
if st.button("Predict Single Sales", key="single_predict_button"): # Added key
    try:
        # Make a POST request to the Flask API. Replace with your actual backend URL
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

# --- Batch Prediction Section ---
st.header("Batch Sales Prediction (Upload CSV)")

uploaded_file = st.file_uploader("Upload CSV file for batch predictions", type=["csv"], key="batch_file_uploader") # Added key

if uploaded_file is not None:
    try:
        # Read the uploaded CSV file into a Pandas DataFrame
        batch_df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:")
        st.dataframe(batch_df.head())

        # Expected columns for prediction (excluding 'Store_Age' as it's derived by the backend)
        expected_columns = [
            'Product_Id', 'Product_Weight', 'Product_Sugar_Content', 'Product_Allocated_Area',
            'Product_Type', 'Product_MRP', 'Store_Id', 'Store_Establishment_Year',
            'Store_Size', 'Store_Location_City_Type', 'Store_Type'
        ]

        if not all(col in batch_df.columns for col in expected_columns):
            missing_cols = [col for col in expected_columns if col not in batch_df.columns]
            st.error(f"Error: The uploaded CSV is missing expected columns for prediction: {', '.join(missing_cols)}.\nPlease ensure your CSV has all the required input features.")
        elif batch_df.empty:
            st.warning("The uploaded CSV file appears to be empty or contains no valid data rows.")
        else:
            if st.button("Run Batch Predictions", key="run_batch_predictions_button"): # Added key
                st.write("Initiating batch predictions...")
                predictions = []
                progress_bar = st.progress(0)
                for i, row in batch_df.iterrows():
                    data_to_send = row.to_dict()
                    response = requests.post("http://backend:7860/predict", json=data_to_send)

                    if response.status_code == 200:
                        prediction = response.json().get('predicted_sales')
                        predictions.append(prediction)
                    else:
                        st.error(f"Error predicting for row {i+1}: {response.status_code} - {response.text}")
                        predictions.append(None) # Append None for failed predictions
                    progress_bar.progress((i + 1) / len(batch_df))

                # Add predictions to the DataFrame
                batch_df['Predicted_Sales'] = predictions
                st.success("Batch predictions complete!")
                st.dataframe(batch_df)

                # Option to download results
                csv_output = batch_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Predictions as CSV",
                    data=csv_output,
                    file_name="batch_predictions.csv",
                    mime="text/csv",
                )

    except Exception as e:
        st.error(f"An error occurred during file processing or prediction: {e}")

st.markdown("--- ")
st.write("Note: The backend API must be running for predictions to work.")
