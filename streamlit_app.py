import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# Class for managing stock data
class StockManager:
    @staticmethod
    def fetch_stock_data(ticker):
        end = datetime.now()
        start = datetime(end.year - 1, end.month, end.day)
        stock_data = yf.Ticker(ticker).history(start=start, end=end)
        return stock_data

# Class for managing the dashboard
class Dashboard:
    def __init__(self, stock_manager):
        self.stock_manager = stock_manager

    def render_dashboard(self):
        st.title("Stock Price Dashboard")

        # Stock Visualization Section
        st.write("### Stock Visualization")
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, AMZN):", "AAPL")
        if st.button("Show Stock Visualization"):
            try:
                stock_data = self.stock_manager.fetch_stock_data(ticker)
                st.write(f"### {ticker} Stock Data (Last 5 Rows):")
                st.dataframe(stock_data.tail())

                # Visualization
                st.line_chart(stock_data["Close"])
                st.write(f"**Current Price of {ticker}:** ${stock_data['Close'].iloc[-1]:.2f}")
            except Exception as e:
                st.error(f"Error fetching stock data: {e}")

# Main app logic
def main():
    stock_manager = StockManager()
    dashboard = Dashboard(stock_manager)
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
