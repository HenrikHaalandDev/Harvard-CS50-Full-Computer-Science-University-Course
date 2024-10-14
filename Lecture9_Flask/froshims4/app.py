from flask import Flask, redirect, render_template, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
DATABASE_CONFIG = {
    'user': 'root',         # Your MariaDB username
    'password': 'Blindbat11!',          # Your MariaDB password
    'host': 'localhost',     # Your database host (e.g., localhost)
    'database': 'user'       # The database name to be created
}

# Helper function to connect to the database
def create_db_connection(database=None):
    try:
        connection = mysql.connector.connect(
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            host=DATABASE_CONFIG['host'],
            database=database  # Specify the database here
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to create the database and the registrants table
def create_database_and_table():
    # Create a connection without specifying a database
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']}")
        cursor.close()
        connection.close()

    # Now create a connection with the newly created database
    connection = create_db_connection(DATABASE_CONFIG['database'])
    if connection:
        cursor = connection.cursor()
        # Create the registrants table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            sport VARCHAR(50)
        )
        """)
        cursor.close()
        connection.close()

# Call the function to create the database and table on startup
create_database_and_table()

SPORTS = [
    "Basketball",
    "Soccer",
    "Ultimate Frisbee",
]

@app.route("/")
def index():
    return render_template("index.html", sports=SPORTS)

@app.route("/deregister", methods=["POST"])
def deregister():
    # Forget registrant
    id = request.form.get("id")
    if id:
        try:
            connection = create_db_connection(DATABASE_CONFIG['database'])  # Connect with the database
            if connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM registrants WHERE id = %s", (id,))
                connection.commit()
                cursor.close()
                connection.close()
        except Error as e:
            print(f"Error: {e}")
        return redirect("/registrants")

@app.route("/register", methods=["POST"])
def register():
    # Validate submission
    name = request.form.get("name")
    sport = request.form.get("sport")
    if not name or sport not in SPORTS:
        return render_template("failure.html")
    
    # Remember registrant
    try:
        connection = create_db_connection(DATABASE_CONFIG['database'])  # Connect with the database
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO registrants (name, sport) VALUES (%s, %s)", (name, sport))
            connection.commit()
            cursor.close()
            connection.close()
    except Error as e:
        print(f"Error: {e}")

    # Confirm registration
    return redirect("/registrants")

@app.route("/registrants")
def registrants():
    try:
        connection = create_db_connection(DATABASE_CONFIG['database'])  # Connect with the database
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM registrants")
            registrants = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template("registrants.html", registrants=registrants)
        else:
            return "Database connection failed", 500
    except Error as e:
        print(f"Error: {e}")
        return "An error occurred while fetching registrants", 500

if __name__ == "__main__":
    app.run(debug=True)
