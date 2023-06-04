## This project is part of our Semester Project for the class "Databases" in the 6th semester of the School of Electrical and Computer Engineering of the National Technical University of Athens

## Installation Guide

Before we begin make sure you have installed the latest version of Python, you have [GIT](https://git-scm.com/download/win) and you have a program like [XAMPP](https://www.apachefriends.org/download.html) installed to test the code in a local server.

### Step-by-Step instructions

1. Open the terminal and go to the directory you would like to store the app files.
2. Make sure you are running the local host server (XAMPP is running with Apache and MySQL active).
3. In the terminal, clone the GitHub repository with this command: 
	```
	git clone https://github.com/StavrosXr/Database-Library
	```
4. In the terminal, execute this command to change the directory to the one we just made:
	```
	cd Database-Library
	```
5. In the terminal, run the following script to download all required libraries:
	```
	pip install -r requirements.txt
	```
	if you get an error when running this try running this instead: 
	
	***python -m pip install -r requirements.txt***
6. To download the database, we first need to go to the directory that you have the bin of the installed XAMPP (for example: C:\xampp\mysql\bin)
	```
	cd C:\xampp\mysql\bin
	```
7. Execute this command to make the empty library:
	```
	mysql -u root -p -e "CREATE DATABASE MyLibrary
	```
	When prompted to enter a password, hit ENTER.
8. Then in the terminal, execute this command to load the database:
	```
	mysql -u root -p -h localhost MyLibrary < {backup_file_path}
	```
	where {backup_file_path} is the path to the library.sql file.  
	For example "..\Database-Library\library.sql. 
	If you get an error when running this try saving the library.sql file in an all english path
9.  Go back to the directory of the project ( "..\Database-Library\ ) with the cd command. 
10. Depending on your python version use the command ***python3 app.py*** or ***python app.py*** or ***py app.py*** and visit http://localhost:5000/ from a browser to run the web app or click the link that appears when you run the app.
	
## ER DIAGRAM
![Alt text](Diagrams/ER-DIAGRAM.png "ER-DIAGRAM")

## RELATIONAL DIAGRAM
![Alt text](Diagrams/RELATIONAL-DIAGRAM.png "ER-DIAGRAM")

## SCREENSHOTS
![Alt text](Diagrams/Screenshot1.png "SCREENSHOT1")
![Alt text](Diagrams/Screenshot2.png "SCREENSHOT1")
![Alt text](Diagrams/Screenshot3.png "SCREENSHOT1")
