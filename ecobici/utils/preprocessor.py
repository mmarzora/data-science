from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd

class AddQuadrantColumn(BaseEstimator, TransformerMixin):
    """Assign each origin station to a quadrant based on latitude and longitude"""
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X['quadrant'] = X.apply(self.determine_quadrant, axis=1)
        return X

    def determine_quadrant(self, row):
        if row['lat_estacion_origen'] > -34.6:
            if row['long_estacion_origen'] > -58.43:
                return 'NE'
            else:
                return 'NO'
        else:
            if row['long_estacion_origen'] > -58.43:
                return 'SE'
            else:
                return 'SO'

class DatetimeTransformer(TransformerMixin):
    """Transform origin date to datetime"""
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X['fecha_origen_recorrido'] = pd.to_datetime(X['fecha_origen_recorrido'])
        return X

class DateFeaturesTransformer(TransformerMixin):
    """Extract date features:
    - date_formatted: date formatted as '%Y-%m-%d'
    - month: month as '%Y-%m'
    - weekday: day of the week ordered as 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    - is_weekend: flag for Saturday and Sunday
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X['date_formatted'] = X['fecha_origen_recorrido'].dt.strftime('%Y-%m-%d')
        X['month'] = X['fecha_origen_recorrido'].dt.strftime('%Y-%m')
        X['weekday'] = X['fecha_origen_recorrido'].dt.day_name()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        X['weekday'] = pd.Categorical(X['weekday'], categories=weekday_order, ordered=True)
        X['is_weekend'] = (X['weekday'].isin(['Saturday', 'Sunday'])).astype(int)
        return X

class TimeFeaturesTransformer(TransformerMixin):
    """Extract time features:
    - hour: Hour of the trip
    - time_segment: segmetn hours into 'Morning', 'Noon', 'Afternoon', 'Night'
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X['hour'] = X['fecha_origen_recorrido'].dt.hour
        conditions = [
            (X['hour'] >= 5) & (X['hour'] < 12),
            (X['hour'] >= 12) & (X['hour'] < 17),
            (X['hour'] >= 17) & (X['hour'] < 21),
            (X['hour'] >= 21) | (X['hour'] < 5)
        ]
        time_segments = ['Night', 'Morning', 'Noon', 'Afternoon', 'Night']
        X['time_segment'] = pd.cut(X['hour'], bins=[0, 5, 12, 17, 21, 24], labels=time_segments, right=False, ordered=False)
        return X


# Custom transformer for calculating the average temperature of the last 7 days
class AverageTempLast7DaysTransformer(BaseEstimator, TransformerMixin):
    """Calculate 7 day rolling average for max temperature"""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X['time_formatted'] = pd.to_datetime(X['time'])
        X = X.sort_values(by='time_formatted')
        X['avg_temp_last_7_days'] = X['temperature_2m_max (°C)'].shift(1).rolling(window=7, min_periods=1).mean()
        return X

# Custom transformer for creating the new column with the ratio
class RatioTempTransformer(BaseEstimator, TransformerMixin):
    """Calculate ratio for max temperature / rolling average 7 days"""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X['ratio_temp_max_to_avg_last_7_days'] = X['temperature_2m_max (°C)'] / X['avg_temp_last_7_days']
        return X
    

class RollingAveragesTransformer(BaseEstimator, TransformerMixin):
    """Calculate rolling average features for trips - separated by weekdays and weekends:
        - trips_last_day
        - avg_trips_last_week
        - avg_trips_last_month
        - trips_same_day_last_week

    Rollings are calculated over the weekday series or the weekend series, but not combined.
    
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):

        # Partition by quadrant
        for quadrant in X['quadrant'].unique():
            quadrant_mask = X['quadrant'] == quadrant
            weekday_mask = X['is_weekend'] == 0

            mask = quadrant_mask & weekday_mask

            # 1. Trips Last Day
            X.loc[mask, 'trips_last_day'] = X.loc[mask, 'trips'].shift(1)

            # 2. Average Trips Last Week - Las 5 weekday days
            X.loc[mask, 'avg_trips_last_week'] = X.loc[mask, 'trips'].shift().rolling(window=5, min_periods=1).mean()

            # 3. Average Trips Last Month - Last 20 weekday days (no weekends)
            X.loc[mask, 'avg_trips_last_month'] = X.loc[mask, 'trips'].shift().rolling(window=20, min_periods=1).mean()

            # 4. Trips Same Day Last Week - 5 days ago
            X.loc[mask, 'trips_same_day_last_week'] = X.loc[mask].groupby(X['date'].dt.weekday)['trips'].shift(5)

        # Calculate rolling averages for weekends - only usings weekend days

        # Partition by quadrant
        for quadrant in X['quadrant'].unique():
            quadrant_mask = X['quadrant'] == quadrant
            weekday_mask = X['is_weekend'] == 1

            mask = quadrant_mask & weekday_mask

            # 1. Trips Last Day
            X.loc[mask, 'trips_last_day'] = X.loc[mask, 'trips'].shift(1)

            # 2. Average Trips Last Week - Last 2 weekend days
            X.loc[mask, 'avg_trips_last_week'] = X.loc[mask, 'trips'].shift().rolling(window=2, min_periods=1).mean()

            # 3. Average Trips Last Month - Last 8 weekend days
            X.loc[mask, 'avg_trips_last_month'] = X.loc[mask, 'trips'].shift().rolling(window=8, min_periods=1).mean()

            # 4. Trips Same Day Last Week
            X.loc[mask, 'trips_same_day_last_week'] = X.loc[mask].groupby(X['date'].dt.weekday)['trips'].shift(2)


            return X
    
# Custom transformer for merging holidays and adding 'is_holiday' column
class MergeHolidaysTransformer(BaseEstimator, TransformerMixin):
    """Add flag for holidays"""

    def __init__(self, holidays_df):
        self.holidays_df = holidays_df

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        merged_df = X.merge(self.holidays_df, left_on='date_formatted', right_on='Date', how='left')
        merged_df['is_holiday'] = merged_df['Holiday'].notnull().astype('int')
        return merged_df
    

class ReplaceOutliersByDayOfWeek(BaseEstimator, TransformerMixin):
    """Identify outliers using the inter-quertile range method grouping by quadrant and weekday. Replace outliers with the mean for the group."""
    def __init__(self, iqr_multiplier=1.5, outlier_flag_column='is_outlier'):
        self.iqr_multiplier = iqr_multiplier
        self.outlier_flag_column = outlier_flag_column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Group by day of the week and calculate IQR for each group
        grouped = X.groupby(['weekday','quadrant'])['trips']
        q1 = grouped.quantile(0.25)
        q3 = grouped.quantile(0.75)
        iqr = q3 - q1

        # Define the lower and upper bounds to flag outliers
        lower_bound = (q1 - self.iqr_multiplier * iqr).reset_index().rename(columns={'trips':'lower'})
        upper_bound = (q3 + self.iqr_multiplier * iqr).reset_index().rename(columns={'trips':'upper'})

        # Flag outliers
        X = X.merge(lower_bound, on=['weekday','quadrant'], how='left').merge(upper_bound, on=['weekday','quadrant'], how='left')
        X[self.outlier_flag_column] = (X['trips'] > X['upper']) | (X['trips'] < X['lower'])
        X = X.drop(columns=['lower','upper'])

        # Impute outliers with the mean for quadrant and day of week
        X.loc[X['is_outlier'], 'trips'] = X[X['is_outlier']].groupby(['quadrant', 'weekday'])['trips'].transform('mean')


        return X
