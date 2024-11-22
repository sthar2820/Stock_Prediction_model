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

# Chatbot class
class Chatbot:
    def __init__(self):
        self.responses = {
            "hello": "Hello! How can I assist you with stock analysis today?",
            "help": "I can help you analyze stocks, view your portfolio, and add money to your balance. What would you like to do?",
            "analyze": "To analyze a stock, enter the ticker symbol in the main dashboard and click 'Analyze Stock'.",
            "portfolio": "You can view your portfolio in the sidebar. It shows your current balance and the stocks you own.",
            "add money": "To add money to your balance, enter the amount in the sidebar and click 'Add Money'.",
            "bye": "Goodbye! Feel free to return if you need more assistance with stock analysis.",
        }

    def get_response(self, user_input):
        user_input = user_input.lower()
        for key in self.responses:
            if key in user_input:
                return self.responses[key]
        return "I'm sorry, I don't understand. Could you please rephrase your question or ask for 'help'?"

# Dashboard class
class Dashboard:
    def __init__(self, stock_model, chatbot):
        self.stock_model = stock_model
        self.chatbot = chatbot
        self.portfolio = {}
        if 'balance' not in st.session_state:
            st.session_state.balance = 0
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def render_sidebar(self):
        st.sidebar.title("Stock Portfolio")
        
        # Display current balance
        st.sidebar.subheader(f"Current Balance: ${st.session_state.balance:.2f}")
        
        # Add custom amount of money
        amount_to_add = st.sidebar.number_input("Enter amount to add:", min_value=0.01, value=100.00, step=0.01, format="%.2f")
        if st.sidebar.button("Add Money"):
            st.session_state.balance += amount_to_add
            st.sidebar.success(f"${amount_to_add:.2f} added to your balance!")
            st.sidebar.experimental_rerun()

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

    def render_chatbot(self):
        st.subheader("Chatbot Assistant")
        user_input = st.text_input("Ask me anything about stock analysis:")
        if st.button("Send"):
            bot_response = self.chatbot.get_response(user_input)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", bot_response))

        for role, message in st.session_state.chat_history:
            if role == "You":
                st.write(f"You: {message}")
            else:
                st.write(f"Bot: {message}")

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

        # Render chatbot
        self.render_chatbot()
        def __init__(self, stock_model, chatbot):
            self.stock_model = stock_model
            self.chatbot = chatbot
            self.stock_prediction = StockPrediction()  # New instance
            self.portfolio = {}
        if 'balance' not in st.session_state:
            st.session_state.balance = 0
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            
        if st.button("Train & Predict"):
            try:
        # Prepare data
                data = self.stock_model.fetch_stock_data(ticker)
                data = self.stock_model.feature_engineering(data)
        
        # Train the model
                model, mse = self.stock_prediction.train_model(data, self.stock_model.feature_names, "5d_future_close")
                st.success(f"Model trained! Mean Squared Error: {mse:.2f}")
        
        # Predict future prices
                future_predictions = self.stock_prediction.predict_future(model, data, self.stock_model.feature_names)
                data["Predicted Future Price"] = future_predictions

        # Display predictions
                st.write("### Future Price Predictions (Last 10 Rows):")
                st.dataframe(data[["Close", "5d_future_close", "Predicted Future Price"]].tail(10))

        # Visualization
                st.write("### Predicted vs. Actual Future Prices:")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(data.index, data["5d_future_close"], label="Actual Future Price", color="blue")
                ax.plot(data.index, data["Predicted Future Price"], label="Predicted Future Price", color="red")
                ax.set_title(f"{ticker} Future Price Predictions")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.legend()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error during prediction: {e}")
                st.write("### Predict Stock Prices:")
                st.button("Train & Predict")



# Main app logic
def main():
    stock_model = StockModel()
    chatbot = Chatbot()
    dashboard = Dashboard(stock_model, chatbot)
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
