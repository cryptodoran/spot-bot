import os
from bot.models import train

# --- Delete old model and scaler if they exist ---
if os.path.exists("model.pkl"):
    os.remove("model.pkl")
    print("🗑️ Removed old model.pkl")

if os.path.exists("scaler.pkl"):
    os.remove("scaler.pkl")
    print("🗑️ Removed old scaler.pkl")

# --- Retrain model using latest data ---
train.train()

print("✅ Model retrained successfully.")
