import mysql.connector


#Grab Connector
database = mysql.connector.connect(
    host = 'cpsc4910.crxd6v3fbudk.us-east-1.rds.amazonaws.com',
    user = 'admin',
    password = 'cpsc4910',
    database = 'website'
)


#See if we connected
print("Connected to mySQL")

cursor = database.cursor();

print("Enter your UserName")
Name = input()

#Grab info
cursor.execute("SELECT EXISTS(SELECT * FROM users WHERE UserName='"+Name+"')")


myinfo = cursor.fetchall()
print(myinfo[0][0])
if(myinfo[0][0]):
    print("You are in the System!")
else:
    print("You need to sign up.")


#close cursor
cursor.close()
#close connection
database.close()

