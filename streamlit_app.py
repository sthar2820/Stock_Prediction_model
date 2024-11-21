import streamlit as st
import hashlib
import json
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# Helper functions for password hashing and user data
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Class for managing user authentication
class AuthManager:
    def __init__(self, user_data_file="user_data.json"):
        self.user_data_file = user_data_file
        self.user_data = self.load_user_data()

    def load_user_data(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, "r") as file:
                return json.load(file)
        return {}

    def save_user_data(self):
        with open(self.user_data_file, "w") as file:
            json.dump(self.user_data, file)

    def signup(self, username, password, confirm_password):
        if username in self.user_data:
            return "Username already exists. Please choose another one."
        elif password != confirm_password:
            return "Passwords do not match."
        else:
            self.user_data[username] = hash_password(password)
            self.save_user_data()
            return "Account created successfully! You can log in now."

    def login(self, username, password):
        if username in self.user_data and self.user_data[username] == hash_password(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            return f"Welcome, {username}!"
        return "Invalid username or password."

# Class for managing stock data and analysis
class StockManager:
    def __init__(self):
        self.tech_stocks = ['AAPL', 'GOOG', 'MSFT', 'AMZN']
        self.company_names = ["APPLE", "GOOGLE", "MICROSOFT", "AMAZON"]

    def fetch_tech_stocks(self):
        end = datetime.now()
        start = datetime(end.year - 1, end.month, end.day)
        company_list = []

        for stock, com_name in zip(self.tech_stocks, self.company_names):
            data = yf.Ticker(stock).history(start=start, end=end)
            data["company_name"] = com_name
            company_list.append(data)

        return pd.concat(company_list, axis=0)

    def fetch_stock_trends(self, ticker):
        stock_data = yf.Ticker(ticker)
        hist_data = stock_data.history(period="7d", interval="1h")
        current_price = stock_data.info.get('regularMarketPrice', 'N/A')
        return hist_data, current_price

# Class for managing the dashboard
class Dashboard:
    def __init__(self, auth_manager, stock_manager):
        self.auth_manager = auth_manager
        self.stock_manager = stock_manager

    def render_dashboard(self):
        if st.session_state.get("logged_in"):
            st.subheader(f"Welcome to the Dashboard, {st.session_state['username']}!")

            # Tech Stocks Section
            st.write("### Tech Stock Data")
            tech_df = self.stock_manager.fetch_tech_stocks()
            with st.expander("View Tech Stock Data (Collapsible)", expanded=True):
                st.dataframe(tech_df.tail(10))

            # Stock Trends Section
            st.write("### Current Stock Price Trends")
            ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, AMZN):", "AAPL")
            if st.button("Show Stock Trends"):
                try:
                    hist_data, current_price = self.stock_manager.fetch_stock_trends(ticker)
                    st.write(f"### {ticker} - Last 7 Days Performance (Hourly)")
                    st.line_chart(hist_data["Close"])
                    st.write(f"**Current Price of {ticker}:** ${current_price}")
                except Exception as e:
                    st.error("Error fetching stock data. Please check the ticker symbol.")

            # Trending Stocks
            st.write("### Top 5 Trending Stocks")
            for stock in self.stock_manager.tech_stocks:
                try:
                    _, current_price = self.stock_manager.fetch_stock_trends(stock)
                    st.write(f"**{stock}**: ${current_price}")
                except:
                    st.write(f"**{stock}**: Unable to fetch data.")
        else:
            st.error("Please log in to access the Dashboard.")

# Main app logic
def main():
    st.title("Stock Price Dashboard")
    st.sidebar.title("Navigation")
    auth_mode = st.sidebar.selectbox("Choose Mode", ["Login", "Signup", "Dashboard"])

    auth_manager = AuthManager()
    stock_manager = StockManager()
    dashboard = Dashboard(auth_manager, stock_manager)

    if auth_mode == "Signup":
        st.subheader("Signup")
        username = st.text_input("Enter Username")
        password = st.text_input("Enter Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Create Account"):
            message = auth_manager.signup(username, password, confirm_password)
            st.success(message) if "successfully" in message else st.error(message)

    elif auth_mode == "Login":
        st.subheader("Login")
        username = st.text_input("Enter Username")
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            message = auth_manager.login(username, password)
            st.success(message) if "Welcome" in message else st.error(message)

    elif auth_mode == "Dashboard":
        dashboard.render_dashboard()

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    main()
