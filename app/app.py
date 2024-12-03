from flask import Flask, render_template, jsonify, request
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import get_custom_objects
import tensorflow.keras.backend as K
from io import BytesIO
import matplotlib.pyplot as plt




app = Flask(__name__)

# Placeholder for your data (replace with your actual data loading logic)
supervised_data = pd.read_excel('data/supervised_data.xlsx', index_col=0, parse_dates=True)  # Update as needed



@app.route('/')
def home():
    print("Home route accessed")
    return render_template('index.html')

@app.route('/historical_data', methods=['GET'])
def historical_data():
    # Placeholder for fetching historical data
    # Replace with your logic to retrieve historical data
    historical_data = pd.read_excel('data/pivot_df.xlsx', index_col=0, parse_dates=True)
    
    # Convert historical data to JSON format
    historical_df = historical_data  # Adjust as needed to get historical data
    historical_df.index = historical_df.index.strftime('%Y-%m-%d')  # Convert dates to strings
    historical_data_json = historical_df.to_dict(orient='index')

    return jsonify({'dates': list(historical_df.index), 'data': historical_data_json})

# Register standard MSE function
def mse(y_true, y_pred):
    return K.mean(K.square(y_true - y_pred), axis=-1)

get_custom_objects().update({'mse': mse})

# Load your model with the correct custom objects
model = load_model('model/transformer_model.h5', custom_objects={'mse': mse})  # Ensure correct path

#model = tf.keras.models.load_model('model/transformer_model.h5')
#model = load_model('model/transformer_model.keras')

# Placeholder for your data (replace with your actual data loading logic)
supervised_data = pd.read_excel('data/supervised_data.xlsx', index_col=0, parse_dates=True)  # Update as needed

def prepare_forecast_input(data, n_in=20):
    if len(data) < n_in:
        raise ValueError("Insufficient data to prepare forecast input")
    last_values = data[-n_in:]
    forecast_input = np.reshape(last_values, (1, n_in, data.shape[1]))
    return forecast_input

def forecast_lstm_multiple_steps(model, data_pivot, feature_columns, target_columns, window_size, forecast_steps):
    # Prepare initial forecast input
    forecast_input_data = data_pivot[feature_columns].values
    forecast_input = prepare_forecast_input(forecast_input_data, n_in=window_size)
    
    # Initialize list to store all predictions and dates
    all_predictions = []
    forecast_dates = []

    # Extract the last date from the index
    last_date = data_pivot.index[-1]

    for step in range(forecast_steps):
        # Predict the next values
        forecast = model.predict(forecast_input)
        
        # Store the predictions
        all_predictions.append(forecast[0])
        
        # Generate the forecast date
        forecast_dates.append(last_date + pd.DateOffset(days=step + 1))
        
        # Update the forecast input with the new predictions
        forecast_input_data = np.roll(forecast_input_data, shift=-1, axis=0)
        
        # Only include the feature columns in the input data for the next prediction
        forecast_input_data[-1, :len(target_columns)] = forecast[0]
        
        # Prepare the new input for the next prediction
        forecast_input = prepare_forecast_input(forecast_input_data, n_in=window_size)


    
    # Convert predictions to a DataFrame and include dates
    forecast_df = pd.DataFrame(np.array(all_predictions), columns=target_columns, index=forecast_dates)
    
    return forecast_df




@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    if request.method == 'POST':
        city = request.form.get('city')
        period = int(request.form.get('period'))  # Ensure period is an integer
        if city and period:
            # Parameters
            forecast_steps = period
            window_size = 20
            feature_columns = [col for col in supervised_data.columns if col not in [
                'cong_ratio_CASABLANCA(t)', 'cong_ratio_FES(t)', 
                'cong_ratio_MARRAKECH(t)', 'cong_ratio_MEKNES(t)', 
                'cong_ratio_OUJDA ANGAD(t)', 'cong_ratio_RABAT(t)', 'cong_ratio_TANGER ASSILAH(t)'
            ]]
            target_columns = [
                'cong_ratio_CASABLANCA(t)', 'cong_ratio_FES(t)', 
                'cong_ratio_MARRAKECH(t)', 'cong_ratio_MEKNES(t)', 
                'cong_ratio_OUJDA ANGAD(t)', 'cong_ratio_RABAT(t)', 'cong_ratio_TANGER ASSILAH(t)'
            ]
            
            # Forecast future values
            forecast_df = forecast_lstm_multiple_steps(model, supervised_data, feature_columns, target_columns, window_size, forecast_steps)
                        # Convert the DataFrame to JSON format
            # Filter data for the specified city
            if f'cong_ratio_{city.upper()}(t)' in forecast_df.columns:
                city_data = forecast_df[[f'cong_ratio_{city.upper()}(t)']]
                city_data.index = city_data.index.strftime('%Y-%m-%d')  # Convert dates to strings
                forecast_data = city_data.to_dict(orient='index')

                return jsonify({'dates': list(city_data.index), 'data': forecast_data})
            else:
                return jsonify({'error': 'City not found in forecast data.'}), 404
        else:
            return jsonify({'error': 'City and period are required.'}), 400
    return jsonify({'error': 'Invalid request method.'}), 405

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001,use_reloader=False)
