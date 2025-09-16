import tkinter as tk
from tkinter import messagebox
import mysql.connector
from streamlit import title

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="root",  # 🔒 Change this
    database="library_db"
)
cursor = db.cursor()

# ------------------ LIBRARY WINDOW ------------------
def open_library_window(role):
    lib = tk.Tk()
    lib.title("Library System")
    lib.geometry("400x300")

    def display_books():
        cursor.execute("SELECT title, is_lent, lent_to FROM books")
        books = cursor.fetchall()
        output = "Books:\n"
        for title, is_lent, lent_to in books:
            if is_lent:
                output += f"❌ {title} (Lent to {lent_to})\n"
            else:
                output += f"✅ {title}\n"
        messagebox.showinfo("Books", output)

    def add_book():
        if role != 'admin':
            return messagebox.showwarning("Access Denied", "Only admins can add books.")
        title = entry_book.get()
        cursor.execute("INSERT INTO books (title) VALUES (%s)", (title,))
        db.commit()
        messagebox.showinfo("Success", f"'{title}' added.")

    def lend_book():
        if role != 'admin':
            return messagebox.showwarning("Access Denied", "Only admins can lend books.")
        title = entry_book.get()
        user = entry_user.get()
        cursor.execute("UPDATE books SET is_lent=1, lent_to=%s WHERE title=%s AND is_lent=0", (user, title))
        db.commit()
        if cursor.rowcount:
            messagebox.showinfo("Lent", f"'{title}' lent to {user}.")
        else:
            messagebox.showwarning("Unavailable", "Book already lent or not found.")

    def return_book():
        if role != 'admin':
            return messagebox.showwarning("Access Denied", "Only admins can return books.")
        title = entry_book.get()
        cursor.execute("UPDATE books SET is_lent=0, lent_to=NULL WHERE title=%s", (title,))
        db.commit()
        if cursor.rowcount:
            messagebox.showinfo("Returned", f"'{title}' returned.")
        else:
            messagebox.showwarning("Not Found", "Book not found or not lent.")

    # GUI
    tk.Label(lib, text=f"Welcome, {role.upper()}").pack(pady=10)
    tk.Label(lib, text="Book Name:").pack()
    entry_book = tk.Entry(lib)
    entry_book.pack()

    tk.Label(lib, text="User Name (for lend):").pack()
    entry_user = tk.Entry(lib)
    entry_user.pack()

    tk.Button(lib, text="Display Books", command=display_books).pack(pady=5)
    tk.Button(lib, text="Add Book", command=add_book).pack()
    tk.Button(lib, text="Lend Book", command=lend_book).pack()
    tk.Button(lib, text="Return Book", command=return_book).pack()

    lib.mainloop()

# ------------------ LOGIN WINDOW ------------------
def login():
    username = entry_username.get()
    password = entry_password.get()
    cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    if result:
        role = result[0]
        login_window.destroy()
        open_library_window(role)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# ------------------ SIGNUP WINDOW ------------------
def open_signup():
    def signup_user():
        username = entry_new_user.get()
        password = entry_new_pass.get()
        role = var_role.get()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            db.commit()
            messagebox.showinfo("Success", "Account created. You can log in now.")
            signup_win.destroy()
        except mysql.connector.errors.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    signup_win = tk.Toplevel(login_window)
    signup_win.title("Signup")
    signup_win.geometry("300x250")

    tk.Label(signup_win, text="Username:").pack()
    entry_new_user = tk.Entry(signup_win)
    entry_new_user.pack()

    tk.Label(signup_win, text="Password:").pack()
    entry_new_pass = tk.Entry(signup_win, show='*')
    entry_new_pass.pack()

    tk.Label(signup_win, text="Role:").pack()
    var_role = tk.StringVar(value="user")
    tk.OptionMenu(signup_win, var_role, "user", "admin").pack()

    tk.Button(signup_win, text="Sign Up", command=signup_user).pack(pady=10)

# ------------------ MAIN LOGIN WINDOW ------------------
login_window = tk.Tk()
login_window.title("Library Login")
login_window.geometry("300x220")

tk.Label(login_window, text="Username:").pack(pady=5)
entry_username = tk.Entry(login_window)
entry_username.pack()

tk.Label(login_window, text="Password:").pack(pady=5)
entry_password = tk.Entry(login_window, show='*')
entry_password.pack()

tk.Button(login_window, text="Login", command=login).pack(pady=10)
tk.Button(login_window, text="Sign Up", command=open_signup).pack()

login_window.mainloop()
