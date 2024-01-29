import matplotlib.pyplot as plt

def plot_forecasted_series(y_train, forecast, y_true) :

    # Plot the actual values
    plt.plot(y_train, label='Actual')

    # Plot the predicted values
    plt.plot(range(len(y_train), len(y_train) + len(forecast)), forecast, label='Forecast', color='red')
    plt.plot(range(len(y_train), len(y_train) + len(y_true)), y_true, label='Test Data', color='green')

    plt.legend()
    plt.show()