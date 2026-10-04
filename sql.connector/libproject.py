from mysql.connector import pooling
from dotenv import load_dotenv
import os
from  mysql.connector.errors import Error

load_dotenv()
password = os.getenv("DB_PASSWORD")
# CONNECTING TO THE DATABASE
pool = pooling.MySQLConnectionPool (
    pool_name= "libpool",
    pool_size= 5,
    host = "localhost",
    port = 3307,
    user = "root",
    password = password,

)
conn = pool.get_connection()
# created a cursor
cursor = conn.cursor()
# cretaed a database 
cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
# using library_db 
cursor.execute("USE library_db")

# creating book tabel
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books(
        id INT AUTO_INCREMENT PRIMARY KEY,
        title  VARCHAR(50),
        author VARCHAR(30),
        total_copies INT,
        available_copies INT
    )
""")
# creating a borrow records table 
cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrow_records(
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_id INT,
        member_name VARCHAR(50),
        borrow_date VARCHAR(20)
    )
""")

cursor.close()     
conn.close() 
    
# FUNCTION TO ADD A NEW BOOK 
def add_newbook():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("USE library_db")
        multiple = int(input("enter no of books to add: "))
        data = []
        for i in range(1,multiple+1):
            new_book  = input("enter the name of the new book title: ").capitalize().strip()
            author = input("enter name of the author: ").capitalize().strip()
            no_of_copies = int(input("enter no of copies of the book: "))
            available_copies = no_of_copies
            tulip = (new_book,author,no_of_copies,available_copies)
            data.append(tulip)
        
        cursor.executemany("INSERT INTO books(title,author,total_copies,available_copies) VALUES (%s,%s,%s,%s)", data)
        conn.commit()
        print("The new book has add to the list!")

    except ValueError as e:
        print("invalid input! please enter a valid input")
    except Error as e:
        print("database error:", e)
    cursor.close()
    conn.close()

# FUNCTION FOR VIEWING THE BOOKS 
def view_books():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("USE library_db")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Book_id : {row['id']}.\nName of the book : {row['title']}.\nAuthor of the book: {row['author']}.\nTotal copies : {row['total_copies']} copies.\nAvailable_copies : {row['available_copies']}")
            print()
    except Error as e:
        print("database error: ",e)

    cursor.close()
    conn.close()

#  FUNCTION FOR UPDATING THE BOOK DEATILS 
def update():
    view_books()
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("USE library_db")
        id = int(input("enter an id you want to edit: "))
        no_of_copies = int(input("enter how many copies are available: "))
        cursor.execute("UPDATE books set total_copies = %s WHERE id = %s",(no_of_copies,id))
        conn.commit()
        print(cursor.rowcount,"row(s) updated")
    
    except TypeError as e:
        print("invalid input! please enter a valid input")
    except Error as e:
        print("database error:", e)
    cursor.close()
    conn.close()

# FUNCTION TO DELETE A ROW
def delete_book():
    view_books()
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("USE library_db")
        id = int(input("enter an id you want to edit: "))
        cursor.execute("DELETE from books WHERE id = %s",(id,))
        conn.commit()
        print(cursor.rowcount,"row(s) updated")

    except ValueError as e:
        print("invalid input! please enter a valid input")
    except Error as e:
        print("database error:", e)
    cursor.close()
    conn.close()

# FUNCTION TO TRACK BOOKS 
def borrow_book():
    try:
        view_books()
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("USE library_db")
        id = int(input("enter an id to borrow a book: "))
        name = input("enter your name: ")
        cursor.execute("SELECT available_copies FROM books WHERE id = %s",(id,))
        tulip = cursor.fetchone()
        available = tulip[0]
        if available == 0:
            print("NO books are available right now!")
        else:
            cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = %s",(id,))
            cursor.execute("INSERT INTO borrow_records(book_id,member_name,borrow_date) VALUES (%s,%s,CURDATE())",(id,name,))
            conn.commit()
            print(cursor.rowcount,"row(s) updated")

    except Error as e:
        conn.rollback()
        print("transaction failed: ",e)
    cursor.close()
    conn.close()


# FUNCTION TO TRACK BOOKS 
def returned_books():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("USE library_db")
        id = int(input("enter an id to return the book: "))
        cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = %s AND available_copies < total_copies",(id,))
        conn.commit()
        print(cursor.rowcount, "row(s) updated")


    except ValueError as e:
        print("invalid input! please enter a valid input")
    except Error as e:
        print("database error:", e)

    cursor.close()
    conn.close()

# FUNCTION TO CONTROL THE PROGRAM 
def main():
    while True:
        # displaying the menu
        print("========= MENU =========")
        print("1. Add_New_Books\n2. View_Books\n3. Update\n4. Deleting\n5. Borrowed_Books_List\n6. Returned_Books_List\n7.Exit")
        print("========================")

        # TAKING USER INPUT
        user_input = int(input("Choose a number from the list: "))
        if user_input == 1:
            add_newbook()
        elif user_input == 2:
            view_books()
        elif user_input == 3:
            update()
        elif user_input == 4:
            delete_book()
        elif user_input == 5:
            borrow_book()
        elif user_input == 6:
            returned_books()
        elif user_input == 7:
            print("Thank you!")
            break

main()

