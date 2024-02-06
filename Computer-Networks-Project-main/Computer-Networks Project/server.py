import socket
import threading
import time
import pandas
import sys

HOST="10.86.3.121"
PORT=8080
BUFFERSIZE=1024
CURR_CLIENT_NO = 0
TOT_CLIENT_NO=0
SERVER=None

connections=[]
addresses={}

df=pandas.read_excel("Questions.xlsx")
score=0

def select_questions(sheet_name,client):
    global df,questions,score
    
    df=pandas.read_excel("Questions.xlsx",sheet_name=sheet_name)
    
    subset=df.sample(n=6)
    
    questions=subset["Question"].values
    option_1=subset["Option_1"].values
    option_2=subset["Option_2"].values
    option_3=subset["Option_3"].values
    option_4=subset["Option_4"].values
    answer=subset["Answer"].values
    
    for i in range(0,len(questions),1):
        print(f"Question : {questions[i]}")
        
        print(f"Option 1 : {option_1[i]}")
        
        print(f"Option 2 : {option_2[i]}")
        
        print(f"Option 3 : {option_3[i]}")
        
        print(f"Option 4 : {option_4[i]}")
        
        print(f"Answer : {answer[i]}")
        
        combined=f"{questions[i]}|{option_1[i]}|{option_2[i]}|{option_3[i]}|{option_4[i]}|{answer[i]}"
        print(f"Combined :{combined}")
        
        client.send(bytes(combined,"utf8"))
        
        user_answer = client.recv(128).decode("utf8")
        
        if user_answer == answer[i]:
            score+=1
            print(f"Score : {score}")
    

def credential_check(credentials):
    with open('Credentials.txt', 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.strip()

            if line==credentials:
                return True
    return False

def handle_client(client):
    client.send(bytes("Welcome to the quiz!","utf8"))
    
    credentials=client.recv(1024).decode("utf8")
    print(credentials)
    
    if credential_check(credentials):
        client.send("1".encode("utf8"))
    else:
        client.send(bytes("0","utf8"))
        
    sheet_name=client.recv(1024).decode("utf8")
    print(sheet_name)
    
    select_questions(sheet_name,client)
    

def Main():
    global SERVER
    global TOT_CLIENT_NO,CURR_CLIENT_NO
    TOT_CLIENT_NO=int(input("Enter max number of players : "))
    
    SERVER = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    SERVER.bind((HOST,PORT))
    SERVER.listen(TOT_CLIENT_NO)
    
    while CURR_CLIENT_NO<TOT_CLIENT_NO:
        CURR_CLIENT_NO+=1
        client,client_address=SERVER.accept()
        
        print("Connection "+str(CURR_CLIENT_NO)+" : "+client_address[0])

        # addresses[client]=client_address
        client_handler_thr=threading.Thread(target=handle_client,args=(client,))
        client_handler_thr.start()
        # client.close()    
    SERVER.close()
    
if __name__ == '__main__':
    Main()