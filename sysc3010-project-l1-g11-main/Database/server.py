from flask import Flask, request, jsonify, render_template
from tinydb import TinyDB, Query

app = Flask(__name__)
db = TinyDB('db.json')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    db.insert(data)
    return jsonify({"message": "Data added", "data": data}), 201

@app.route('/get', methods=['GET'])
def get_data():
    return jsonify(db.all())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

