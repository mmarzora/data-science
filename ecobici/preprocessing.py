import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import holidays

from utils.preprocessor import AddQuadrantColumn, DatetimeTransformer, DateFeaturesTransformer, TimeFeaturesTransformer, AverageTempLast7DaysTransformer, RatioTempTransformer, RollingAveragesTransformer, MergeHolidaysTransformer, ReplaceOutliersByDayOfWeek

def load_data():
    """Read datasets for trips, weather and holidays"""
    # load trips data for 2022
    trips = pd.read_csv('data/trips_2022.csv').iloc[:,2:]

    # load weather data for 2022
    weather = pd.read_csv('weather/open-meteo-34.62S58.41W19m.csv', delimiter=';')

    # load holidays in argentina for 2022
    ar_holidays = holidays.Argentina(years=2022)
    ar_holidays = pd.DataFrame(ar_holidays.items(), columns=['Date', 'Holiday'])
    ar_holidays['Date'] = ar_holidays['Date'].astype('str')

    return trips, weather, ar_holidays

def preprocess_data(trips, weather, ar_holidays):
    """Generate dataset with total trips by date and quadrant, and add new features"""

    # Create and apply a pipeline for classifying origin stations in a quadrant
    quadrant_classifier_pipeline = Pipeline([
        ('add_quadrant', AddQuadrantColumn())
    ])
    trips_transformed = quadrant_classifier_pipeline.fit_transform(trips)
    print('added quadrant')

    # Create and apply a pipeline for extracting features from datetime stamp
    datetime_pipeline = Pipeline([
        ('datetime_transformer', DatetimeTransformer()),
        ('date_features_transformer', DateFeaturesTransformer()),
        ('time_features_transformer', TimeFeaturesTransformer())
    ])
    trips_dt = datetime_pipeline.transform(trips_transformed)
    print('added datetime features')
    
    # Generate a dataframe with date - quadrant cardinality, to predict trips by quadrant and day
    trips_dt_quadrant = trips_dt[['month','date_formatted', 'weekday','is_weekend','quadrant']].value_counts().reset_index().rename(columns={0:'trips'})
    print('grouped by date and quadrant')


    # Add features to the weather dataframe
    weather_pipeline = Pipeline([
        ('avg_temp_last_7_days', AverageTempLast7DaysTransformer()),
        ('ratio_temp_max', RatioTempTransformer())
    ])

    weather_transformed = weather_pipeline.fit_transform(weather)

    # Add weather features to the trips dataset
    trips_dt_wht = trips_dt_quadrant.merge(weather_transformed, left_on='date_formatted', right_on='time', how='left')
    print('added weather features')

    # Sort by date
    trips_dt_wht['date'] = pd.to_datetime(trips_dt_wht['date_formatted'])
    trips_dt_wht = trips_dt_wht.sort_values(by='date')


    # Add new features - Rolling averages of trips, Flag Holidays and Replace outliers
    # Outliers are identified by weekday and quadrant, and are replaced by the mean of that weekday and quadrant to keep all days in the series complete
    pipeline = Pipeline([
        ('rolling_trip_avg', RollingAveragesTransformer()),
        ('flag_holidays', MergeHolidaysTransformer(holidays_df=ar_holidays)),
        ('flag_outlier', ReplaceOutliersByDayOfWeek())
    ])

    trips_dt_wht_hol_transformed = pipeline.fit_transform(trips_dt_wht)
    print('Added rolling averages, holidays and outliers')

    return trips_dt_wht_hol_transformed


def write_data(trips_dt_wht_hol_transformed):
    """Save preprocessed dataset"""

    path = 'trips_preprocessed'
    trips_dt_wht_hol_transformed.to_csv(path)
    print(f'saved in {path}')


def main():
    trips, weather, ar_holidays = load_data()
    trips_dt_quadrant = preprocess_data(trips, weather, ar_holidays)
    write_data(trips_dt_quadrant)

if __name__ == "__main__":
    main()