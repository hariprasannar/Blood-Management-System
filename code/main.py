import mysql.connector
import os
from datetime import datetime


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="blood_bank"
)

cursor = db.cursor()

def add_donor():
    name = input("Enter Name: ")
    age = int(input("Enter Age: "))
    blood_group = input("Enter Blood Group: ")
    phone = input("Enter Phone: ")

    query = "INSERT INTO donors (name, age, blood_group, phone) VALUES (%s, %s, %s, %s)"
    values = (name, age, blood_group, phone)

    cursor.execute(query, values)
    db.commit()

    print("Donor added successfully")

def view_donors():
    cursor.execute("SELECT * FROM donors")
    result = cursor.fetchall()

    print("\nDonor List:")
    for row in result:
        print(row)

def search_donor():
    bg = input("Enter Blood Group: ")
    query = "SELECT * FROM donors WHERE blood_group = %s"
    cursor.execute(query, (bg,))
    result = cursor.fetchall()

    print("\nMatching Donors:")
    for row in result:
        print(row)


def add_request():
    name = input("Enter Patient Name: ")
    bg = input("Enter Blood Group Needed: ")
    units = int(input("Enter Units: "))

    query = "INSERT INTO requests (patient_name, blood_group, units) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, bg, units))
    db.commit()

    print("Request added successfully")


def backup_database():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{now}.sql"

    command = f"mysqldump -u root -p blood_bank > {backup_file}"
    
    print("\nEnter MySQL password when prompted...")
    os.system(command)

    print(f"Backup created: {backup_file}")


def add_acceptor():
    name = input("Enter Patient Name: ")
    age = int(input("Enter Age: "))
    blood_group = input("Enter Blood Group Needed: ")
    units = int(input("Enter Units Needed: "))
    phone = input("Enter Phone: ")

    query = """INSERT INTO acceptors 
               (name, age, blood_group, units_needed, phone) 
               VALUES (%s, %s, %s, %s, %s)"""

    cursor.execute(query, (name, age, blood_group, units, phone))
    db.commit()

    print("Acceptor added successfully")

def view_acceptors():
    cursor.execute("SELECT * FROM acceptors")
    result = cursor.fetchall()

    print("\nAcceptor List:")
    for row in result:
        print(row)


def match_donor():
    bg = input("Enter Required Blood Group: ")

    query = "SELECT * FROM donors WHERE blood_group = %s"
    cursor.execute(query, (bg,))
    result = cursor.fetchall()

    if result:
        print("\nAvailable Donors:")
        for row in result:
            print(row)
    else:
        print("No matching donors found")


def menu():
    while True:
        print("\nBlood Management System")
        print("1. Add Donor")
        print("2. View Donors")
        print("3. Search Donor")
        print("4. Add Acceptor")
        print("5. View Acceptors")
        print("6. Match Donor")
        print("7. Backup Database")
        print("8. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            add_donor()
        elif choice == '2':
            view_donors()
        elif choice == '3':
            search_donor()
        elif choice == '4':
            add_acceptor()
        elif choice == '5':
            view_acceptors()
        elif choice == '6':
            match_donor()
        elif choice == '7':
            backup_database()
        elif choice == '8':
            print("Exiting...")
            break
        else:
            print("Invalid choice")


menu()