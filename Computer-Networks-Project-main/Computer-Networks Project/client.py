import socket
from threading import Thread
import time,sys,select
import tkinter
from tkinter import messagebox,ttk
import pandas

HOST="10.86.3.121"
PORT=8080
BUFFERSIZE=4096

remaining_time = 60
question_number = 0

df=pandas.read_excel("Questions.xlsx")

# HOST=input("Enter Host address : ")
# PORT=int(input("Enter port number : "))

CLIENT = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
CLIENT.connect((HOST,PORT))

def next_question(question_number_label,question_label,button_a,button_b,button_c,button_d,answer_entry):
    global question_number,remaining_time
    
    remaining_time=60
    

    question_number += 1
    question_number_label.config(text=f"Question {question_number}")
    
    answer=answer_entry.get()
    print(f"Your answered : {answer}")
    CLIENT.send(bytes(answer,"utf8"))
    
    question=CLIENT.recv(256).decode("utf8")
    # print(f"Combined: {question}")
    question,option_1,option_2,option_3,option_4,answer = question.split("|")
    print(f"Question : {question}")
    # print(f"{question} , {option_1} , {option_2} , {option_3} , {option_4} , {answer}")
    
    question_label.config(text=question)
    
    if option_2=="nan":
        pass
    else:
        button_a.config(text=option_1)
        button_b.config(text=option_2)
        button_c.config(text=option_3)
        button_d.config(text=option_4)
        
    answer_entry.delete(0,tkinter.END)
        
    next_question_button = tkinter.Button(frame, bg="#80ffdb", text="Next Question", font=('Helvetica', 16), borderwidth=1, relief="solid",padx=10,pady=10,command=lambda: next_question(question_number_label,question_label,button_a,button_b,button_c,button_d,answer_entry))
    next_question_button.grid(row=6, column=0, pady=10)
    window.update_idletasks()

def update_timer(timer_label):
    global remaining_time

    if remaining_time > 0:
        remaining_time -= 1
        timer_label.configure(text=f"Time Remaining: {remaining_time} seconds")
        window.after(1000, update_timer,timer_label)
    else:
        timer_label.configure(text="Time's up!")

def questions_screen():
    global df
    
    clear_screen()
    window.title('Quiz Application')
    
    frame.configure(bg="#a2d2ff",height=600,width=800)

    question_number_label = tkinter.Label(frame, bg="#80ffdb",text="Question 1", font=('Helvetica', 16), borderwidth=2, relief="sunken",padx=15,pady=15)
    question_number_label.grid(sticky="w",row=0,column=0,padx=20,pady=20)

    timer_label = tkinter.Label(frame, bg="#80ffdb",text="Time Remaining: 60 seconds", font=('Helvetica', 16), borderwidth=2, relief="sunken",padx=15,pady=15)
    timer_label.grid(sticky="e",row=0,column=4,padx=20,pady=20)
    update_timer(timer_label)
    
    frame.grid_columnconfigure(0, weight=2)
    frame.grid_columnconfigure(4, minsize=300, weight=0)

    frame.pack_propagate(False)
    frame.pack(fill="both",expand=True)
    
    question_label = tkinter.Label(frame, bg="#a2d2ff", text="", font=('Helvetica', 20), padx=20,pady=20, wraplength=700)
    question_label.grid(row=1, column=0, columnspan=6, sticky="news",pady=10,padx=10)
    
    print("Questions from server")
    # for i in range(0,6,1):
    question=CLIENT.recv(256).decode("utf8")
    
    # print(f"Combined: {question}")
    question,option_1,option_2,option_3,option_4,answer = question.split("|")
    print(f"Question : {question}")
    
    question_label.config(text=question)
    
    if option_1=="nan":
        answer_label = tkinter.Label(frame, text="Type Answer", bg='#a2d2ff', fg="#000000", font=("Georgia", 16))
        answer_entry = tkinter.Entry(frame, font=("Arial", 16))
        answer_label.grid(row=2, column=0)
        answer_entry.grid(row=2, column=1, pady=20)
    else:
        button_a = tkinter.Button(frame, bg="#a2d2ff",text=option_1, font=("Georgia", 12))
        button_a.grid(row=2, column=1,sticky="news", padx=10,pady=10)
        
        button_b = tkinter.Button(frame, bg="#a2d2ff",text=option_2, font=("Georgia", 12))
        button_b.grid(row=2, column=4,sticky="news", padx=10,pady=10)
        
        button_c = tkinter.Button(frame, bg="#a2d2ff",text=option_3, font=("Georgia", 12))
        button_c.grid(row=3, column=1,sticky="news", padx=10,pady=10)
        
        button_d = tkinter.Button(frame, bg="#a2d2ff",text=option_4, font=("Georgia", 12))
        button_d.grid(row=3, column=4,sticky="news", padx=10,pady=10)
        
        answer_label = tkinter.Label(frame, text="Enter answer", bg='#a2d2ff', fg="#000000", font=("Georgia", 16))
        answer_entry = tkinter.Entry(frame, font=("Arial", 16))
        answer_label.grid(row=4, column=0)
        answer_entry.grid(row=4, column=1, pady=20)
        
    next_question_button = tkinter.Button(frame, bg="#80ffdb", text="Next Question", font=('Helvetica', 16), borderwidth=1, relief="solid",padx=10,pady=10,command=lambda: next_question(question_number_label,question_label,button_a,button_b,button_c,button_d,answer_entry))
    next_question_button.grid(row=6, column=0, pady=10)
    
    window.update_idletasks()
        

def on_select(combo):
    global df
    
    selected_item = combo.get() 
    print(f'Selected Quiz: {selected_item}')
    CLIENT.send(bytes(selected_item,"utf8"))
    questions_screen()

def clear_screen():
    for widget in frame.winfo_children():
        widget.pack_forget()
        widget.destroy()

def select_genre():
    clear_screen()
    window.title('Genre Select')

    header_label = tkinter.Label(frame, text='Select your topic of choice', bg="#9d9d9d", font=("Georgia", 16))
    header_label.pack(pady=40)

    combo = ttk.Combobox(frame, values=['Physics', 'Chemistry', 'Maths', 'English', 'Logical Reasoning', 'General Knowledge'])
    combo.pack(pady=10)
    combo.set('Chemistry')

    select_button = tkinter.Button(frame, text='Select', command=lambda: on_select(combo))
    select_button.pack(pady=10)

    combo['state'] = 'readonly'

def on_enter(event):
    login_button.config(cursor="hand2")

def on_leave(event):
    login_button.config(cursor="")

def login():
    # username=username_entry.get()
    # password=password_entry.get()
    
    username="user1"
    password="pass1"
    
    credentials=f"{username}-{password}"
    
    CLIENT.send(bytes(credentials,"utf8"))
    
    data=CLIENT.recv(1024).decode("utf8")
    
    if data=="1":
        messagebox.showinfo(title="Login Success", message="You successfully logged in.")
        select_genre()
    elif data=="0":
        messagebox.showerror(title="Error", message="Invalid login.")
        


def start_game():
    data=CLIENT.recv(1024).decode("utf8")
    print(data)

client_thread=Thread(target=start_game)
client_thread.start()

window = tkinter.Tk()
window.title("Login Form")
window.geometry("800x600")
window.configure(bg='#9D9D9D')

frame = tkinter.Frame(bg='#9d9d9d')

login_label = tkinter.Label(
    frame, text="Login", bg='#9D9D9D', fg="#170F11", font=("Times New Roman", 30))

username_label = tkinter.Label(
    frame, text="Username", bg='#9D9D9D', fg="#FFFFFF", font=("Georgia", 16))

username_entry = tkinter.Entry(frame, font=("Arial", 16))
password_entry = tkinter.Entry(frame, show="*", font=("Arial", 16))
password_label = tkinter.Label(
    frame, text="Password", bg='#9D9D9D', fg="#FFFFFF", font=("Georgia", 16))

login_button = tkinter.Button(
    frame, text="Login", bg="#170F11", fg="#FFFFFF", font=("Georgia", 16), command=login)

login_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=60)
username_label.grid(row=1, column=0)
username_entry.grid(row=1, column=1, pady=20)
password_label.grid(row=2, column=0)
password_entry.grid(row=2, column=1, pady=20)
login_button.grid(row=3, column=0, columnspan=2, pady=30)

login_button.bind("<Enter>", on_enter)
login_button.bind("<Leave>", on_leave)

frame.pack()
window.mainloop()

CLIENT.close()