import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# Class for managing stock data and model analysis
class StockModel:
    def __init__(self):
        self.feature_names = []

    def fetch_stock_data(self, ticker):
        end = datetime.now()
        start = end - timedelta(days=5*365)  # 5 years of data
        data = yf.Ticker(ticker).history(start=start, end=end)
        return data

    def feature_engineering(self, data):
        # Calculate percent change
        data["Percent Change"] = data["Close"].pct_change() * 100

        # Calculate 5-day future close and percent changes
        data["5d_future_close"] = data["Close"].shift(-5)
        data["5d_close_future_pct"] = data["5d_future_close"].pct_change(5) * 100
        data["5d_close_pct"] = data["Close"].pct_change(5) * 100

        # Add moving averages and RSI indicators
        self.feature_names = ["5d_close_pct"]
        for n in [14, 30, 50, 200]:
            data[f"ma{n}"] = data["Close"].rolling(window=n).mean() / data["Close"]
            data[f"rsi{n}"] = self.calculate_rsi(data["Close"], n)
            self.feature_names.extend([f"ma{n}", f"rsi{n}"])

        return data.dropna()

    def calculate_rsi(self, prices, period):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def visualize_data(self, data):
        # Histogram of Percent Change
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data["Percent Change"].dropna(), bins=75, edgecolor="black")
        ax.set_title("Percent Change Histogram")
        ax.set_xlabel("Percent Change")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # Correlation matrix visualization
        corr = data[["5d_close_pct", "5d_close_future_pct"]].corr()
        st.write("Correlation Matrix:")
        st.write(corr)

# Dashboard class
class Dashboard:
    def __init__(self, stock_model):
        self.stock_model = stock_model
        self.portfolio = {}
        self.balance = 0  # Starting balance of 0

    def render_sidebar(self):
        st.sidebar.title("Stock Portfolio")
        
        # Display current balance
        st.sidebar.subheader(f"Current Balance: ${self.balance:.2f}")
        
        # Add money button
        if st.sidebar.button("Add $1000"):
            self.balance += 1000
            st.sidebar.success("$1000 added to your balance!")

        # List of stocks
        st.sidebar.subheader("Your Stocks")
        for stock, quantity in self.portfolio.items():
            st.sidebar.text(f"{stock}: {quantity} shares")

        # Add new stock to portfolio
        new_stock = st.sidebar.text_input("Add a new stock to your portfolio:")
        quantity = st.sidebar.number_input("Quantity:", min_value=1, value=1, step=1)
        if st.sidebar.button("Add to Portfolio"):
            if new_stock:
                self.portfolio[new_stock] = self.portfolio.get(new_stock, 0) + quantity
                st.sidebar.success(f"{quantity} shares of {new_stock} added to your portfolio!")
            else:
                st.sidebar.error("Please enter a valid stock symbol.")

    def render_dashboard(self):
        st.title("Stock Price Dashboard with Analysis")
        
        # Render sidebar
        self.render_sidebar()

        # Main content
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

                # Display stock price chart
                st.write("### Stock Price Chart:")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(data.index, data["Close"])
                ax.set_title(f"{ticker} Stock Price")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Error processing stock data: {e}")

# Main app logic
def main():
    stock_model = StockModel()
    dashboard = Dashboard(stock_model)
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
