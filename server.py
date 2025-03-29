import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__master__":
    port = int(os.environ.get("PORT", 10000))  # Render автоматически назначает порт
    app.run(host="0.0.0.0", port=port)