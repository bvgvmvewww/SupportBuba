from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!", 200

if __name__ == '__master__':
    app.run(host='0.0.0.0', port=8080)
