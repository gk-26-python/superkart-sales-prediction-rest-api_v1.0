# Import necessary libraries
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

# Initialize Flask app
super_kart_app_api = Flask("Super Kart Price Predictor")

# Define paths for the saved preprocessor and model (ensure these are accessible in the deployment environment)
preprocessor_path = 'backend_files/preprocessor.joblib'
model_path = "backend_files/final_superkart_sales_model_v1.0.joblib"

# Load the preprocessor and model globally to avoid reloading on each request
try:
    loaded_preprocessor = joblib.load(preprocessor_path)
    loaded_final_model = joblib.load(model_path)
    print("Preprocessor and model loaded successfully!")
    # Define the original column order as used during training
    # This is crucial for the ColumnTransformer to work correctly with new data
    GLOBAL_ORIGINAL_X_COLUMNS = ['Product_Id', 'Product_Weight', 'Product_Sugar_Content',
                                 'Product_Allocated_Area', 'Product_Type', 'Product_MRP',
                                 'Store_Id', 'Store_Establishment_Year', 'Store_Size',
                                 'Store_Location_City_Type', 'Store_Type', 'Store_Age']

except Exception as e:
    print(f"Error loading model or preprocessor: {e}")
    loaded_preprocessor = None
    loaded_final_model = None
    GLOBAL_ORIGINAL_X_COLUMNS = [] # Ensure it's defined even on error


@super_kart_app_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the Super Kart Price Prediction API!"

# Define a prediction endpoint
@super_kart_app_api.route('/predict', methods=['POST'])
def predict():
    if loaded_preprocessor is None or loaded_final_model is None:
        return jsonify({'error': 'Model or preprocessor not loaded. Check server logs.'}), 500

    try:
        # Get JSON data from request
        data = request.get_json(force=True)

        # Convert input data to DataFrame
        input_df = pd.DataFrame([data])

        # Ensure 'Store_Age' is calculated if not provided in input
        if 'Store_Establishment_Year' in input_df.columns and 'Store_Age' not in input_df.columns:
            current_year = 2024 # Use the same current_year as during training
            input_df['Store_Age'] = current_year - input_df['Store_Establishment_Year']
        # If 'Store_Establishment_Year' is missing but 'Store_Age' is also missing,
        # this might cause an issue. For now, assume 'Store_Establishment_Year' is always present if 'Store_Age' is not.

        # Ensure the input_df columns are in the same order as the training data's X.columns.
        # This is crucial for the ColumnTransformer to apply transformers to the correct columns.
        input_df = input_df.reindex(columns=GLOBAL_ORIGINAL_X_COLUMNS, fill_value=None)

        # Preprocess the input data
        processed_input = loaded_preprocessor.transform(input_df)

        # Make prediction
        prediction = loaded_final_model.predict(processed_input)

        # Return prediction as JSON
        return jsonify({'predicted_sales': prediction[0]})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Example of how to run the app (for local testing, not for Colab directly)
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    super_kart_app_api.run(debug=True)
