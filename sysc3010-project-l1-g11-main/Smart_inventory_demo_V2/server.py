from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "inventory.db"

def init_db():
    """Creates the inventory table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiration_date TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route('/add_item', methods=['POST'])
def add_item():
    """Endpoint to add an item to the inventory database."""
    data = request.json
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (id, name, quantity, expiration_date) VALUES (?, ?, ?, ?)",
                       (data['id'], data['name'], data['quantity'], data['expiration_date']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Item added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_inventory', methods=['GET'])
def get_inventory():
    """Endpoint to retrieve all inventory items."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()

    inventory_list = [{"id": item[0], "name": item[1], "quantity": item[2], "expiration_date": item[3]} for item in items]
    return jsonify(inventory_list)

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

