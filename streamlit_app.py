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
    def __init__(self, auth_manager, stock_manager):
        self.auth_manager = auth_manager
        self.stock_manager = stock_manager

    def render_dashboard(self):
        if st.session_state.get("logged_in"):
            st.subheader(f"Welcome to the Dashboard, {st.session_state['username']}!")

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
