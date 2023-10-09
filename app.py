from flask import Flask, render_template, request, session, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "DdDpqHe0lckeyZ4u"

connection = sqlite3.connect("users.db", check_same_thread=False)
cursor = connection.cursor()

def delete(n):
  query = f"DELETE FROM users WHERE id={n}"
  cursor.execute(query)
  connection.commit()
  
def createTable():
  query = '''
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(32),
    password VARCHAR(32)
  )
  '''
  cursor.execute(query)
  
def addToTable(values):
  query = f"INSERT INTO users(username, password) VALUES ('{values[0]}', '{values[1]}')"
  cursor.execute(query)
  connection.commit()
  
def getListFromDatabase():
  query = "SELECT * FROM users"
  stuff = cursor.execute(query)
  lines = stuff.fetchall()
  return lines

@app.route('/')
def index():
    session["register_error"] = ""
    return render_template('register.html', message = session["register_error"])

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template('register.html', message = session["register_error"])
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        if len(username) < 4:
            session["register_error"] = "Username must be at least 4 characters long."
            return render_template('register.html', message = session["register_error"])
        if len(username) > 16:
            session["register_error"] = "Username must be no more than 16 characters long."
            return render_template('register.html', message = session["register_error"])
        if len(password) < 8:
            session["register_error"] = "Password must be at least 8 characters long."
            return render_template('register.html', message = session["register_error"])
        if len(password) > 32:
            session["register_error"] = "Password must be no more than 32 characters long."
            return render_template('register.html', message = session["register_error"])
        if password != confirm_password:
            session["register_error"] = "Password and confirmation password do not match."
            return render_template('register.html', message = session["register_error"])
        usernames_taken = []
        for line in getListFromDatabase():
            usernames_taken.append(line[1])
        if username in usernames_taken:
            session["register_error"] = "Username is already taken."
            return render_template('register.html', message = session["register_error"])
        session["register_error"] = None
        addToTable([username, password])
        print(getListFromDatabase())
        session["signed_in"] = True
        session["signed_user"] = username
        return redirect('/content')
    
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
      return render_template('login.html')
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        usernames_exist = []
        username_id = None
        for line in getListFromDatabase():
            usernames_exist.append(line[1])
        if username not in usernames_exist:
            session["logon_error"] = "Username does not exist."
            return render_template('login.html', message = session["logon_error"])
        username_id = usernames_exist.index(username) + 1
        passwords = []
        for line in getListFromDatabase():
            passwords.append(line[2])
        password_of_username = passwords[username_id - 1]
        if password != password_of_username:
            session["logon_error"] = "Incorrect password."
            return render_template('login.html', message = session["logon_error"])
        session["logon_error"] = None
        session["signed_in"] = True
        session["signed_user"] = username
        return redirect('/content')

@app.route('/content')
def content():
    username = session["signed_user"]
    if username == None:
        return redirect('/')
    if session["signed_in"] == False:
        return redirect('/')
    return render_template('index.html', username = username)

@app.route('/logout')
def logout():
    session["signed_in"] = False
    session["signed_user"] = None
    return redirect('/')

def main():
    createTable()

main()