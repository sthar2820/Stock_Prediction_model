import streamlit as st
import hashlib
import json
import os
import pandas as pd
import yfinance as yf  # Install with `pip install yfinance`

# Helper functions for password hashing and user data
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    with open("user_data.json", "w") as file:
        json.dump(user_data, file)

# App title
st.title("Stock Price Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
auth_mode = st.sidebar.selectbox("Choose Mode", ["Login", "Signup", "Dashboard"])

# Load user data
user_data = load_user_data()

# Authentication
if auth_mode == "Signup":
    st.subheader("Signup")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if username in user_data:
            st.error("Username already exists. Please choose another one.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            user_data[username] = hash_password(password)
            save_user_data(user_data)
            st.success("Account created successfully! You can log in now.")

elif auth_mode == "Login":
    st.subheader("Login")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if username in user_data and user_data[username] == hash_password(password):
            st.success(f"Welcome, {username}!")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("Invalid username or password.")

# Dashboard (only accessible after login)
if auth_mode == "Dashboard":
    if st.session_state.get("logged_in"):
        st.subheader(f"Welcome to the Dashboard, {st.session_state['username']}!")

        # Stock Trends Section
        st.write("### Current Stock Price Trends")
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, AMZN):", "AAPL")
        if st.button("Show Stock Trends"):
            try:
                # Fetch real-time stock data
                stock_data = yf.Ticker(ticker)
                hist_data = stock_data.history(period="7d", interval="1h")  # Last 7 days with hourly updates

                # Display stock data
                st.write(f"### {ticker} - Last 7 Days Performance (Hourly)")
                st.line_chart(hist_data["Close"])

                # Display current price
                current_price = stock_data.info['regularMarketPrice']
                st.write(f"**Current Price of {ticker}:** ${current_price:.2f}")

            except Exception as e:
                st.error("Error fetching stock data. Please check the ticker symbol.")

        # Top 5 Trending Stocks (Static Example)
        st.write("### Top 5 Trending Stocks")
        trending_stocks = ["AAPL", "TSLA", "AMZN", "GOOGL", "MSFT"]
        for stock in trending_stocks:
            try:
                stock_info = yf.Ticker(stock)
                st.write(f"**{stock}**: ${stock_info.info['regularMarketPrice']:.2f}")
            except:
                st.write(f"**{stock}**: Unable to fetch data.")
    else:
        st.error("Please log in to access the Dashboard.")
