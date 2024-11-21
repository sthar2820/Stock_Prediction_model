pip install yfinance talib numpy pandas scikit-learn statsmodels
import pickle
from sklearn.tree import DecisionTreeRegressor
import statsmodels.api as sm
import pandas as pd
import yfinance as yf
import numpy as np

# Fetch historical stock data
symbol = "AAPL"
start_date = "2000-01-01"
data = yf.download(symbol, start=start_date)

# Prepare the data
data["Percent Change"] = data["Adj Close"].pct_change()
data["5d_future_close"] = data["Adj Close"].shift(-5)
data["5d_close_future_pct"] = data["5d_future_close"].pct_change(5)
data["5d_close_pct"] = data["Adj Close"].pct_change(5)

# Add TA-Lib features (moving averages and RSI)
feature_names = ["5d_close_pct"]
for n in [14, 30, 50, 200]:
    data[f"ma{n}"] = data["Adj Close"].rolling(window=n).mean() / data["Adj Close"]
    data[f"rsi{n}"] = 100 - (100 / (1 + data["Adj Close"].diff().rolling(n).mean() / abs(data["Adj Close"].diff().rolling(n).mean())))
    feature_names.extend([f"ma{n}", f"rsi{n}"])

# Drop NA values for consistent training
data = data.dropna()

# Prepare features and targets
features = sm.add_constant(data[feature_names])
targets = data["5d_close_future_pct"]

# Train-test split
train_size = int(0.85 * len(features))
train_features, test_features = features[:train_size], features[train_size:]
train_targets, test_targets = targets[:train_size], targets[train_size:]

# Train the best-performing model (Decision Tree Regressor with max_depth=3)
best_model = DecisionTreeRegressor(max_depth=3)
best_model.fit(train_features, train_targets)

# Save the trained model
with open("stock_prediction_model.pkl", "wb") as model_file:
    pickle.dump(best_model, model_file)

print("Model saved as 'stock_prediction_model.pkl'")
