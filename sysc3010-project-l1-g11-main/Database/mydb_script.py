from tinydb import TinyDB, Query

db = TinyDB('db.json')  # Connect to the database

# Insert some data
db.insert({'name': 'Alice', 'age': 25})
db.insert({'name': 'Bob', 'age': 30})

# Print all records to verify
print(db.all())
