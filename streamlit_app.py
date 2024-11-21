import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt

# Class for managing stock data and model analysis
class StockModel:
    def __init__(self):
        self.feature_names = []

    def fetch_stock_data(self, ticker):
        end = datetime.now()
        start = datetime(end.year - 5, end.month, end.day)
        data = yf.Ticker(ticker).history(start=start, end=end)
        return data

    def feature_engineering(self, data):
        # Calculate percent change
        data["Percent Change"] = data["Adj Close"].pct_change()

        # Calculate 5-day future close and percent changes
        data["5d_future_close"] = data["Adj Close"].shift(-5)
        data["5d_close_future_pct"] = data["5d_future_close"].pct_change(5)
        data["5d_close_pct"] = data["Adj Close"].pct_change(5)

        # Add moving averages and RSI indicators
        self.feature_names = ["5d_close_pct"]
        for n in [14, 30, 50, 200]:
            data[f"ma{n}"] = talib.SMA(data["Adj Close"].values, timeperiod=n) / data["Adj Close"]
            data[f"rsi{n}"] = talib.RSI(data["Adj Close"].values, timeperiod=n)
            self.feature_names.extend([f"ma{n}", f"rsi{n}"])

        return data.dropna()

    def visualize_data(self, data):
        # Histogram of Percent Change
        plt.figure(figsize=(10, 6))
        plt.hist(data["Percent Change"], bins=75, edgecolor="black")
        plt.title("Percent Change Histogram")
        plt.xlabel("Percent Change")
        plt.ylabel("Frequency")
        st.pyplot(plt)

        # Correlation matrix visualization
        corr = data[["5d_close_pct", "5d_close_future_pct"]].corr()
        st.write("Correlation Matrix:")
        st.write(corr)

# Dashboard class
class Dashboard:
    def __init__(self, stock_model):
        self.stock_model = stock_model

    def render_dashboard(self):
        st.title("Stock Price Dashboard with Analysis")
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA):", "AAPL")

        if st.button("Analyze Stock"):
            try:
                data = self.stock_model.fetch_stock_data(ticker)
                st.write(f"### {ticker} Stock Data (Last 5 Rows):")
                st.dataframe(data.tail())

                # Perform feature engineering
                data = self.stock_model.feature_engineering(data)

                # Display features and target
                st.write("### Engineered Features (First 5 Rows):")
                st.dataframe(data[self.stock_model.feature_names].head())

                # Visualize data
                st.write("### Visualizations:")
                self.stock_model.visualize_data(data)
            except Exception as e:
                st.error(f"Error processing stock data: {e}")

# Main app logic
def main():
    stock_model = StockModel()
    dashboard = Dashboard(stock_model)
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
