import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import RandomizedSearchCV
from pmdarima import auto_arima
import os
import pickle

def load_data():
    """Load preprocessed trip data"""

    trips_preprocessed = pd.read_csv('trips_preprocessed')
    return trips_preprocessed

def select_train_test_indexes(trips_preprocessed):
    """Select indexes for the train and test partitions segmenting by date"""

    idx_train = trips_preprocessed[trips_preprocessed.date_formatted<'2022-11-01'].index
    idx_test = trips_preprocessed[trips_preprocessed.date_formatted>='2022-11-01'].index

    return idx_train, idx_test

def generate_train_test_xgboost(trips_preprocessed, idx_train, idx_test):
    """Generate the train and test dataframes for the XGBoost model"""

    train = trips_preprocessed.loc[idx_train]
    test = trips_preprocessed.loc[idx_test]

    X_train = train
    X_test = test
    y_train= train['trips']
    y_test= test['trips']

    return X_train, y_train, X_test, y_test



def fit_xgboost_model(X_train, y_train):
    """Train an XGBoost model with selected features."""

    weather_vars = ['weather_code (wmo code)', 'temperature_2m_mean (°C)', 'temperature_2m_max (°C)', 'precipitation_sum (mm)', 'precipitation_hours (h)', 'wind_speed_10m_max (km/h)','ratio_temp_max_to_avg_last_7_days']
    history_vars = ['avg_trips_last_week', 'avg_trips_last_month', 'trips_same_day_last_week']
    flags = ['is_weekend','is_holiday']
    categorical_vars = ['quadrant']

    preprocessor = ColumnTransformer(
        transformers=[
            ('weather', SimpleImputer(strategy='mean'), weather_vars),
            ('history', SimpleImputer(strategy='mean'), history_vars),
            ('flags', SimpleImputer(strategy='most_frequent'), flags),
            ('cat', OneHotEncoder(), categorical_vars)
        ],
        remainder='drop'
        )

    # Create XGBoost Regressor
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        random_state=42,
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
    )

    # Create the pipeline with the one-hot encoding step
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('xgb', model)
    ])

    # Fit the model using the pipeline
    pipeline.fit(X_train, y_train)
    print(pipeline['xgb'].get_params())
    return pipeline


def generate_arima_sets(trips_preprocessed, idx_train, idx_test):
    """Generate train and test series for the time series arima model"""

    ts_train = trips_preprocessed.loc[idx_train].set_index('date_formatted').sort_index()
    ts_test = trips_preprocessed.loc[idx_test].set_index('date_formatted').sort_index()

    return ts_train, ts_test


def train_autoarima(ts_train):
    """Train an auto-arima model with selected exogenous features"""

    features = ['is_weekend','is_holiday','precipitation_hours (h)', 'temperature_2m_mean (°C)']
    target = ['trips']

    # iterate through the quadrant to train a time series for each
    quadrants = ts_train['quadrant'].unique()
    
    arima_models = {}

    for q in quadrants:
        series = ts_train[ts_train.quadrant==q]
        model_arima = auto_arima(series[target], exogenous=series[features], suppress_warnings=True)
        arima_models[q] = model_arima

    return arima_models



def evaluate(y_pred, y, set_name, **kwargs):
    """Evaluate predictions from a regression model with RMSE (Root Mean Squared Error) and MAPE (Mean Average Percentage Error)"""

    # Evaluate the model
    rmse = mean_squared_error(y, y_pred, squared=False)
    mape = mean_absolute_percentage_error(y, y_pred)

    print(f'{set_name} - Root Mean Squared Error:       {rmse}')
    print(f'{set_name} - Mean Absolute Percetage Error: {mape}')

    return y_pred


def evaluate_xgboost(model, X_train, y_train, X_test, y_test):
    """Evaluate the XGBoost model for train and test."""

    y_pred = model.predict(X_train)
    y_pred_tr = evaluate(y_pred, y_train, set_name='Train')
    
    y_pred = model.predict(X_test)
    y_pred_ts = evaluate(y_pred, y_test, set_name='Test')


def evaluate_arima(arima_models, ts_test, test_days=61):
    """Evaluate the auto arima models for each quadrant, and for all the predictions combined."""

    # Initialize an array to store the predictions
    y_pred_values = []
    y_test_values = []

    # Iterate through each quadrant model
    for key, model in arima_models.items():
        forecast = model.predict(n_periods=test_days)

        y_pred_q = forecast.tolist()
        y_test_q = ts_test.loc[ts_test.quadrant == key, 'trips'].tolist()
        
        # Evaluate each quadrant
        evaluate(y_pred_q, y_test_q, set_name=f'Test {key}')

        # Concatenate the predictions to the array
        y_pred_values.extend(y_pred_q)
        y_test_values.extend(y_test_q)

    # Evaluate the predictions from all the quadrants
    evaluate(y_pred_values, y_test_values, set_name='Test')
    return

def save_model(model, name):
    """Save the trained models in .pkl files"""

    # Create the 'models/' directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')

    # Save the model to a pickle file in the 'models/' directory
    model_path = f'models/{name}.pkl'
    with open(model_path, 'wb') as file:
        pickle.dump(model, file)
    print(f"Model saved to {model_path}")



def fine_tuning_xgboost(X_train, y_train, xgboost_pipeline):
    """Run a random search for XGBoost hiperparameters and return the best estimatos"""

    # Define a parameter distribution for random search
    param_dist = {
        'xgb__n_estimators': [50, 100, 150],
        'xgb__learning_rate': [0.01, 0.1, 0.2],
        'xgb__max_depth': [3, 5, 7],
        'xgb__min_child_weight': [1, 3, 5, 8, 10, 13, 15],
        'xgb__subsample': [0.8, 1.0],
        'xgb__colsample_bytree': [0.8, 1.0],
        'xgb__gamma': [0, 1, 2],
        'xgb__reg_alpha': [0, 0.1, 0.5],
        'xgb__reg_lambda': [0.1, 1, 2],
    }

    # Perform random search with RMSE as the scoring metric
    random_search = RandomizedSearchCV(estimator=xgboost_pipeline, param_distributions=param_dist, 
                                    n_iter=50, scoring='neg_root_mean_squared_error', cv=3, random_state=42)
    random_search.fit(X_train, y_train)

    # Get the best parameters
    best_params = random_search.best_params_
    print(best_params)

    # return best estimator

    return random_search.best_estimator_



def main():
    trips_preprocessed = load_data()
    idx_train, idx_test = select_train_test_indexes(trips_preprocessed)

    # Train the XGBoost model
    print('training xgboost model')
    X_train, y_train, X_test, y_test = generate_train_test_xgboost(trips_preprocessed, idx_train, idx_test)
    xgb_model = fit_xgboost_model(X_train, y_train)
    
    evaluate_xgboost(xgb_model, X_train, y_train, X_test, y_test)
    save_model(xgb_model, 'xgboost_model')

    # Fine-tune parameters with Random Search
    print('fine tuning xgboost')
    tuned_xgb_model = fine_tuning_xgboost(X_train, y_train, xgb_model)
    evaluate_xgboost(tuned_xgb_model, X_train, y_train, X_test, y_test)
    save_model(tuned_xgb_model, 'tuned_xgboost_model')


    # Train the AutoArima Model
    print('training autoarima model')
    ts_train, ts_test = generate_arima_sets(trips_preprocessed, idx_train, idx_test)
    arima_models = train_autoarima(ts_train)
    evaluate_arima(arima_models, ts_test, test_days=61)
    save_model(arima_models, 'arima_model')

if __name__ == "__main__":
    main()