from django.shortcuts import render,redirect

# Create your views here.
import mysql.connector
from django.contrib import messages

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='S1tty1$great',
        database='estate'
        
    )

#Very first page which you will see after hitting URL
def home(request):
    return render(request,'home.html')

#login view
def login_user(request):
    if request.method=='POST':
        uname=request.POST['user_name']
        pwd=request.POST['password']

        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM USER WHERE user_name=%s AND PASSWORD=%s", (uname, pwd))
        user = cursor.fetchone()
        conn.close()

        if user:
            redirect('main_menu')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request,'login.html')

#register view
def register(request):
    if request.method=='POST':
        uname = request.POST['user_name']
        email = request.POST['email']
        phone = request.POST['phoneno']
        password = request.POST['password']

        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO USER(USER_NAME, EMAIL, PHONENO, PASSWORD) VALUES (%s, %s, %s, %s)",
                       (uname, email, phone, password))
        
        conn.commit()
        conn.close()

        return redirect('main_menu')
    
#Home page of our platform
def main_menu(request):
    return render(request, 'main_menu.html')
        





