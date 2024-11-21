import yfinance as yf
import numpy as np
import pickle
import statsmodels.api as sm

class StockModel:
    def __init__(self, model_path):
        # Load the saved model
        with open(model_path, "rb") as file:
            self.model = pickle.load(file)

    def preprocess_stock_data(self, ticker):
        """
        Fetch and preprocess stock data to match the model's input format.
        """
        stock_data = yf.Ticker(ticker).history(period="1y")
        stock_data["Percent Change"] = stock_data["Close"].pct_change()
        # Example features: mean, std, percent change
        features = np.array([
            stock_data["Close"].mean(),
            stock_data["Close"].std(),
            stock_data["Percent Change"].mean()
        ])
        return features.reshape(1, -1)

    def predict(self, ticker):
        """
        Predict stock value based on the model and preprocessed data.
        """
        try:
            # Preprocess the stock data
            input_features = self.preprocess_stock_data(ticker)
            input_features = sm.add_constant(input_features)  # Add constant for OLS model
            prediction = self.model.predict(input_features)[0]
            return prediction
        except Exception as e:
            raise ValueError("Error processing the stock ticker.") from e
