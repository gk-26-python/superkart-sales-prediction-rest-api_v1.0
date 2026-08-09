# Import necessary libraries
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

# Initialize Flask app
super_kart_app_api = Flask("Super Kart Price Predictor")

# Define paths for the saved preprocessor and model (ensure these are accessible in the deployment environment)
preprocessor_path = '/content/drive/MyDrive/SuperKart/preprocessor.joblib'
model_path = '/content/drive/MyDrive/SuperKart/final_superkart_sales_model.joblib'

# Load the preprocessor and model globally to avoid reloading on each request
try:
    loaded_preprocessor = joblib.load(preprocessor_path)
    loaded_final_model = joblib.load(model_path)
    print("Preprocessor and model loaded successfully!")
except Exception as e:
    print(f"Error loading model or preprocessor: {e}")
    loaded_preprocessor = None
    loaded_final_model = None


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
        # The input data should match the structure of X before preprocessing
        input_df = pd.DataFrame([data])

        # Ensure 'Store_Age' is calculated if not provided in input
        if 'Store_Establishment_Year' in input_df.columns and 'Store_Age' not in input_df.columns:
            current_year = 2024 # Use the same current_year as during training
            input_df['Store_Age'] = current_year - input_df['Store_Establishment_Year']

        # Preprocess the input data
        # Ensure the order of columns and feature names are consistent with training
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
