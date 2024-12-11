import os
from io import BytesIO
from flask import Flask, render_template, jsonify, request, send_from_directory
import numpy as np
import pandas as pd
import tensorflow.keras.backend as K
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import get_custom_objects

app = Flask(__name__)
app.config['TESTING'] = True  # This enables the testing configuration

# Placeholder for your data (replace with your actual data loading logic)
supervised_data = pd.read_excel('data/supervised_data.xlsx', index_col=0, parse_dates=True)


@app.route('/')
def home():
    """Home route for rendering the index page."""
    print("Home route accessed")
    return render_template('index.html')


@app.route('/historical_data', methods=['GET'])
def historical_data():
    """Fetch and return historical data in JSON format."""
    int(historical_df) = pd.read_excel('data/pivot_df.xlsx', index_col=0, parse_dates=True)
    historical_df.index = historical_df.index.strftime('%Y-%m-%d')  # Convert dates to strings
    historical_data_json = historical_df.to_dict(orient='index')
    return jsonify({'dates': list(historical_df.index), 'data': historical_data_json})


# Register standard MSE function
def mse(y_true, y_pred):
    """Mean Squared Error loss function."""
    return K.mean(K.square(y_true - y_pred), axis=-1)


get_custom_objects().update({'mse': mse})

# Load your model with the correct custom objects
model = load_model('model/transformer_model.h5', custom_objects={'mse': mse})  # Ensure correct path


def prepare_forecast_input(data, n_in=20):
    """Prepare the forecast input based on the previous data."""
    if len(data) < n_in:
        raise ValueError("Insufficient data to prepare forecast input")
    last_values = data[-n_in:]
    forecast_input = np.reshape(last_values, (1, n_in, data.shape[1]))
    return forecast_input


def forecast_lstm_multiple_steps(model, data_pivot, feature_columns, target_columns, window_size, forecast_steps):
    """Forecast multiple steps using the LSTM model."""
    forecast_input_data = data_pivot[feature_columns].values
    forecast_input = prepare_forecast_input(forecast_input_data, n_in=window_size)

    all_predictions = []
    forecast_dates = []

    last_date = data_pivot.index[-1]

    for step in range(forecast_steps):
        forecast = model.predict(forecast_input)
        all_predictions.append(forecast[0])
        forecast_dates.append(last_date + pd.DateOffset(days=step + 1))

        forecast_input_data = np.roll(forecast_input_data, shift=-1, axis=0)
        forecast_input_data[-1, :len(target_columns)] = forecast[0]
        forecast_input = prepare_forecast_input(forecast_input_data, n_in=window_size)

    forecast_df = pd.DataFrame(np.array(all_predictions), columns=target_columns, index=forecast_dates)
    return forecast_df


@app.route('/forecast', methods=['POST'])
def forecast():
    """Generate a forecast for a given city and period."""
    city = request.form.get('city')
    period = int(request.form.get('period'))  # Ensure period is an integer
    if city and period:
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

        forecast_df = forecast_lstm_multiple_steps(model, supervised_data, feature_columns, target_columns, window_size, forecast_steps)

        if f'cong_ratio_{city.upper()}(t)' in forecast_df.columns:
            city_data = forecast_df[[f'cong_ratio_{city.upper()}(t)']]
            city_data.index = city_data.index.strftime('%Y-%m-%d')  # Convert dates to strings
            forecast_data = city_data.to_dict(orient='index')

            return jsonify({'dates': list(city_data.index), 'data': forecast_data})
        else:
            return jsonify({'error': 'City not found in forecast data.'}), 404
    else:
        return jsonify({'error': 'City and period are required.'}), 400


@app.route('/favicon.ico')
def favicon():
    """Serve the favicon for the application."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
