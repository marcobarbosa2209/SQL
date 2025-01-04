from flask import Flask, request, render_template, redirect, url_for, flash
import pyodbc
import webview
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing error messages

# Database connection credentials
SERVER = "localhost,1433"
DATABASE = "LicencaAutomovel"
USERNAME = "sa"
PASSWORD = "Mb31013498"

# Database connection function

def connect_db():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USERNAME};"
            f"PWD={PASSWORD};"
            "Encrypt=no;"
        )
        return conn, None  # Return connection and no error
    except pyodbc.Error as e:
        return None, str(e)  # Return no connection and the error message

@app.route('/')
def home():
    conn, error = connect_db()
    if conn is None:  # Connection failed
        return render_template('error.html', error_message=error)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    conn, error = connect_db()
    if conn is None:  # Connection failed
        flash(f"Database connection failed: {error}", "danger")
        return redirect(url_for('home'))

    username = request.form.get('username')
    password = request.form.get('password')

    # Validate credentials against the database
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM Users WHERE username = ? AND password = ?", (username, password)
        )
        user = cursor.fetchone()
        if user:
            return f"Welcome, {username}!"
        else:
            flash("Invalid username or password!", "danger") 
            return redirect(url_for('home'))
    except pyodbc.Error as e:
        flash(f"Database query error: {e}", "danger")
        return redirect(url_for('home'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def handle_register():
    conn, error = connect_db()
    if conn is None:  # Connection failed
        flash(f"Database connection failed: {error}", "danger")
        return redirect(url_for('register'))

    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash("Passwords do not match!", "danger")
        return redirect(url_for('register'))

    # Add the new user to the database
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()
        flash("User registered successfully!", "success")
        return redirect(url_for('home'))
    except pyodbc.IntegrityError:
        flash("Username already exists!", "danger")
        return redirect(url_for('register'))
    except pyodbc.Error as e:
        flash(f"Database error: {e}", "danger")
        return redirect(url_for('register'))

def start_flask():
    """Start the Flask app in a separate thread."""
    app.run(debug=False, use_reloader=False)  # Disable reloader for PyWebView compatibility

if __name__ == '__main__':
    # Run Flask in a thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Launch PyWebView
    webview.create_window('Login App', 'http://127.0.0.1:5000')
    webview.start()