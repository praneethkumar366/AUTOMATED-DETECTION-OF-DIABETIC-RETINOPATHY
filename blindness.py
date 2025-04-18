# blindness.py with PDF report generation, prediction timestamp, and progress bar
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector as sk
from model import *
from send_sms import send
from tkinter import Label as TkLabel
from datetime import datetime
from fpdf import FPDF
import os
import threading

print('GUI SYSTEM STARTED...')

# Global login state
y = False

# Connect to MySQL
db_config = {
    'host': "localhost",
    'user': "root",
    'password': "praneeth",
    'database': "blindness_detection"
}

connection = sk.connect(**db_config)
sql = connection.cursor()

def generate_pdf_report(username, value, classes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf.cell(200, 10, txt="Retinal Blindness Detection Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Username: {username}", ln=True)
    pdf.cell(200, 10, txt=f"Predicted Label: {value}", ln=True)
    pdf.cell(200, 10, txt=f"Predicted Class: {classes}", ln=True)
    pdf.cell(200, 10, txt=f"Timestamp: {timestamp}", ln=True)

    filename = f"report_{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    print(f"PDF report saved as {filename}")

def LogIn():
    global y
    username = box1.get().strip()
    password = box2.get().strip()

    if not username or not password:
        messagebox.showinfo("Error", "Please enter both username and password.")
        return

    query = "SELECT * FROM THEGREAT WHERE USERNAME = %s AND PASSWORD = %s"
    sql.execute(query, (username, password))
    data = sql.fetchone()

    if data:
        messagebox.showinfo('Login Success', f'Welcome back, {username}!')
        y = True
    else:
        messagebox.showinfo('Login Failed', 'Invalid Username or Password')

def Signup():
    username = box1.get().strip()
    password = box2.get().strip()

    if not username or not password:
        messagebox.showinfo("Error", "Please enter both username and password.")
        return

    sql.execute("SELECT * FROM THEGREAT WHERE USERNAME = %s", (username,))
    if sql.fetchone():
        messagebox.showinfo("Error", "Username already exists. Try a new one.")
        return

    query = "INSERT INTO THEGREAT (USERNAME, PASSWORD) VALUES (%s, %s)"
    sql.execute(query, (username, password))
    connection.commit()
    messagebox.showinfo("Signed up", f"Hi {username},\nNow you can login with your credentials!")

def show_progress_bar():
    progress = Toplevel(root)
    progress.title("Processing")
    progress.geometry("300x100")
    Label(progress, text="Predicting, please wait...", font=("Segoe UI", 12)).pack(pady=10)
    pb = Progressbar(progress, orient=HORIZONTAL, length=250, mode='indeterminate')
    pb.pack(pady=5)
    pb.start(10)
    return progress, pb

def run_prediction(username, file_path):
    try:
        value, classes = main(file_path)
        send(value, classes)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql.execute("UPDATE THEGREAT SET PREDICT = %s WHERE USERNAME = %s", (value, username))
        connection.commit()

        generate_pdf_report(username, value, classes)

        result_window = Toplevel(root)
        result_window.title("Detection Result")
        result_window.geometry("600x500")
        result_window.configure(bg='#f9f9f9')

        TkLabel(result_window, text="Blindness Detection Report", font=('Segoe UI', 20, 'bold'), bg='#f9f9f9', fg='#00796b').pack(pady=20)
        TkLabel(result_window, text=f"Predicted Label: {value}", font=('Segoe UI', 14), bg='#f9f9f9').pack(pady=10)
        TkLabel(result_window, text=f"Predicted Class: {classes}", font=('Segoe UI', 14), bg='#f9f9f9').pack(pady=10)

        image = Image.open(file_path).convert('RGB')
        image = image.resize((300, 300))
        img_tk = ImageTk.PhotoImage(image)
        image_label = TkLabel(result_window, image=img_tk, bg='#f9f9f9')
        image_label.image = img_tk
        image_label.pack(pady=10)

        Button(result_window, text="Close", command=result_window.destroy, style="Accent.TButton").pack(pady=10)

        print('Thanks for using the system!')

    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", f"Something went wrong: {e}")


def OpenFile():
    username = box1.get().strip()
    if not y:
        messagebox.showinfo("Access Denied", "You need to login first.")
        return

    file_path = askopenfilename()
    if not file_path:
        messagebox.showwarning("No File", "No image selected.")
        return

    progress_win, pb = show_progress_bar()

    def threaded_run():
        run_prediction(username, file_path)
        pb.stop()
        progress_win.destroy()

    threading.Thread(target=threaded_run).start()

# GUI Setup
root = Tk()
root.title("SK's Blindness Detection System")
root.configure(bg='#f0f8ff')
root.minsize(850, 500)
root.resizable(True, True)

style = Style()
style.theme_use("clam")
style.configure("Accent.TButton", font=('Segoe UI', 12, 'bold'), foreground='white', background='#00796b', padding=10)
style.map("Accent.TButton",
        foreground=[('pressed', 'white'), ('active', 'white')],
        background=[('pressed', '#004d40'), ('active', '#004d40')])

font_main = ('Segoe UI', 16)
font_title = ('Segoe UI', 26, 'bold')

frame = Frame(root, padding=20, style='TFrame')
frame.pack(fill=BOTH, expand=True)
frame.configure(style='TFrame')

label1 = Label(frame, text="Retinal Blindness Detection", font=font_title, background='#f0f8ff', foreground='#00796b')
label1.grid(padx=10, pady=10, row=0, column=0, columnspan=3, sticky='w')

label2 = Label(frame, text="Username:", font=font_main, background='#f0f8ff')
label2.grid(padx=10, pady=10, row=1, column=0, sticky='e')
box1 = Entry(frame, font=('Segoe UI', 14), width=30)
box1.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky='w')

label3 = Label(frame, text="Password:", font=font_main, background='#f0f8ff')
label3.grid(padx=10, pady=10, row=2, column=0, sticky='e')
box2 = Entry(frame, show='*', font=('Segoe UI', 14), width=30)
box2.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky='w')

button3 = Button(frame, text="Signup", command=Signup, style="Accent.TButton")
button3.grid(row=3, column=1, pady=20, padx=10, sticky='e')

button1 = Button(frame, text="LogIn", command=LogIn, style="Accent.TButton")
button1.grid(row=3, column=2, pady=20, padx=10, sticky='w')

button2 = Button(frame, text="Upload Image", command=OpenFile, width=25, style="Accent.TButton")
button2.grid(row=4, column=1, columnspan=2, pady=10, padx=10)

root.mainloop()
