from flask import render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta
import shutil
import os
import sqlite3
import subprocess
import glob
import mysql.connector

from app import app, mydb  # Import the `app` and `mydb` objects from app

# create a cursor object
mycursor = mydb.cursor()

@app.route('/')     # OKAY
def main():
    return render_template('LoginTest4.html')

@app.route('/login', methods=['POST'])      #OKAY
def login():
    # get the username and password from the form
    username = request.form['username']
    password = request.form['password']

    # query the database to find a matching user
    query = "SELECT * FROM user WHERE username=%s AND password=%s"
    mycursor.execute(query, (username, password))
    result = mycursor.fetchone()

    if result is not None:
        user_id = result[0]
        role = result[7]
        status = result[8]  # Check if the user is approved
        session['user_id'] = user_id
        session['role'] = role

        if status == "Approved":
            return redirect(url_for('dashboard'))
        if status == "Deactivated":
            return render_template('LoginTest4.html', error='Your account is deactivated')
        elif status == "pending":
            return render_template('LoginTest4.html', error='Please wait for the account to get approved')
        elif status == "Deny":
            return render_template('LoginTest4.html', error='Your account was denied access. Please contact the moderator')
        else:
            return render_template('LoginTest4.html', error='There is something wrong with your account. Please contact the moderator')
    else:
        # incorrect credentials
        return render_template('LoginTest4.html', error='Incorrect username or password')
    
@app.route('/about')       # OKAY
def about():
    return render_template('AboutPage.html')
    
@app.route('/logout')       # OKAY
def logout():
    # Clear the session data and redirect to the login page
    session.clear()
    return redirect(url_for('main'))

@app.route('/register', methods=['POST', 'GET'])        ##  OKAY
def register():
    if request.method == 'POST':
        # get user input from the form
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        role = request.form['role']
        date = request.form['birth_date']
        school_name = request.form['school']
        additional_school = request.form.get('additional_school')

        # insert user data into the user table
        query = "INSERT INTO user (Username, Password, U_First_Name, U_Last_Name, Email, Role, Date_of_Birth) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (username, password, first_name, last_name, email, role, date)
        mycursor.execute(query, values)
        mydb.commit()

        # Retrieve the user ID from the user table based on the username
        query = "SELECT User_ID FROM user WHERE Username = %s"
        mycursor.execute(query, (username,))
        user_id = mycursor.fetchone()[0]

        # retrieve the school ID from the school table based on the school name
        query = "SELECT School_ID FROM school WHERE Name = %s"
        mycursor.execute(query, (school_name,))
        school_id = mycursor.fetchone()[0]

        # insert the primary school ID and user ID into the school_user table
        query = "INSERT INTO school_user (School_ID, User_ID) VALUES (%s, %s)"
        values = (school_id, user_id)
        mycursor.execute(query, values)
        mydb.commit()

        if role != "Student" and additional_school:
            # retrieve the additional school ID from the school table based on the school name
            query = "SELECT School_ID FROM school WHERE Name = %s"
            mycursor.execute(query, (additional_school,))
            additional_school_id = mycursor.fetchone()[0]

            # insert the additional school ID and user ID into the school_user table
            query = "INSERT INTO school_user (School_ID, User_ID) VALUES (%s, %s)"
            values = (additional_school_id, user_id)
            mycursor.execute(query, values)
            mydb.commit()

        # redirect to the main page
        return redirect(url_for('main'))
    else:
        query = "SELECT Name FROM school"
        mycursor.execute(query)
        schools = mycursor.fetchall()

        return render_template('RegisterTest6.html', schools=schools)

@app.route('/dashboard')        ##  OKAY
def dashboard():
    # get the Role from the session
    role = session['role']
    if role == "Student":
        return render_template('StudentMainPageTest1.html')
    if role == "Teacher":
        return render_template('TeacherMainPageTest1.html')
    if role == "Operator":
        return render_template('OperatorMainPageTest1.html')
    if role == "Admin":
        return render_template('AdminMainPageTest1.html')
    else:
        return "there is something wrong with your account"
    
@app.route('/profile')          ##  
def profile():
    # get the user ID from the session
    user_id = session['user_id']
    role = session['role']

    if role == "Student":
        query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchone()
        return render_template('StudentProfileTest1.html', user=user)
    if role == "Teacher":
        query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchall()
        mycursor.nextset()  # Consume remaining results
        return render_template('TeacherProfileTest1.html', user=user)
    if role == "Operator":
        query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchall()
        mycursor.nextset()  # Consume remaining results
        return render_template('OperatorProfileTest1.html', user=user)
    if role == "Admin":
        query = "SELECT * FROM user WHERE User_ID = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchone()
        return render_template('AdminProfileTest1.html', user=user)

@app.route('/update_profile', methods=['GET', 'POST'])    # OKAY 
def update_profile():
    # Check if the request is a POST method (form submission)
    if request.method == 'POST':
        user_id = session['user_id']
        role = session['role']
        # Retrieve the updated profile data from the form
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        role = request.form.get('role')
        dob = request.form.get('dob')
        school_name = request.form.get('school_name')
        additional_school = request.form.get('additional_school')
        
        if role == "Teacher" or role == "Operator":
            query = "UPDATE user SET Username = %s, Password = %s, U_First_Name = %s, U_Last_Name = %s, Email = %s, Role = %s, Date_of_Birth = %s WHERE User_ID = %s"
            mycursor.execute(query, (username, password, first_name, last_name, email, role, dob, user_id))

            # print(query)
            # print((username, first_name, last_name, email, role, dob, user_id))
            # Update the school information if provided
            
            if additional_school:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                new_school_id = mycursor.fetchone()[0]  # Fetch the value from the result tuple

                query = "SELECT School_ID FROM school_user WHERE User_ID = %s AND School_ID <> %s"
                mycursor.execute(query, (user_id, new_school_id))
                old_school_id = mycursor.fetchone()[0]  # Fetch the value from the result tuple

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s and School_ID <> %s"
                mycursor.execute(query, (new_school_id, user_id, old_school_id))
            else:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                school_id = mycursor.fetchone()[0]  # Fetch the value from the result tuple

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s"
                mycursor.execute(query, (school_id, user_id,))

        elif role == "Admin" or role == "Student":
            query = "UPDATE user SET Password = %s WHERE User_ID = %s"
            mycursor.execute(query, (password, user_id))

        # Commit the changes to the database
        mydb.commit()

        # Redirect the user back to the profile page with updated data
        return redirect('/profile')
    else:
        # Retrieve the current user's data and pass it to the template
        user_id = session['user_id']
        role = session['role']

        if role == "Student":
            query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
            mycursor.execute(query, (user_id,))
            user = mycursor.fetchone()
            return render_template('StudentEditProfilePageTest1.html', user=user)
        if role == "Teacher":
            query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
            mycursor.execute(query, (user_id,))
            user = mycursor.fetchall()
            mycursor.nextset()  # Consume remaining results
            return render_template('TeacherEditProfilePageTest1.html', user=user)
        if role == "Operator":
            query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
            mycursor.execute(query, (user_id,))
            user = mycursor.fetchall()
            mycursor.nextset()  # Consume remaining results
            return render_template('OperatorEditProfilePageTest1.html', user=user)
        if role == "Admin":
            query = "SELECT * FROM user WHERE User_ID = %s"
            mycursor.execute(query, (user_id,))
            user = mycursor.fetchone() 
            return render_template('AdminEditProfilePageTest1.html', user=user)
   

@app.route('/school')           ## OKAY
def school():
    user_id = session['user_id']
    role = session['role']

    if role == "Student":
        query = "SELECT school.* FROM school INNER JOIN school_user ON school.School_ID = school_user.School_ID WHERE school_user.User_ID = %s"
        mycursor.execute(query, (user_id,))
        school = mycursor.fetchone()
        return render_template('StudentSchoolPageTest1.html', school=school)
    if role == "Teacher":
        query = "SELECT school.* FROM school INNER JOIN school_user ON school.School_ID = school_user.School_ID WHERE school_user.User_ID = %s"
        mycursor.execute(query, (user_id,))
        school = mycursor.fetchall()
        mycursor.nextset()  # Consume remaining results
        return render_template('TeacherSchoolPageTest1.html', school=school)
    if role == "Operator":
        query = "SELECT school.* FROM school INNER JOIN school_user ON school.School_ID = school_user.School_ID WHERE school_user.User_ID = %s"
        mycursor.execute(query, (user_id,))
        school = mycursor.fetchall()
        mycursor.nextset()  # Consume remaining results
        return render_template('OperatorSchoolPageTest1.html', school=school)
    if role == "Admin":     
        query = "SELECT * FROM school"
        mycursor.execute(query)
        school = mycursor.fetchall()
        mycursor.nextset()  # Consume remaining results
        return render_template('AdminSchoolPageTest1.html', school=school)
    
@app.route('/update_school', methods=['GET', 'POST'])
def update_school():
    role = session['role']
    user_id = session['user_id']
    if request.method == 'POST':
        # Retrieve form data
        school_id = request.form['school_id']
        school_name = request.form['school_name']
        school_address = request.form['school_address']
        school_city = request.form['school_city']
        school_phone = request.form['school_phone']
        school_email = request.form['school_email']
        principal_first_name = request.form['principal_first_name']
        principal_last_name = request.form['principal_last_name']
        operator_first_name = request.form['operator_first_name']
        operator_last_name = request.form['operator_last_name']

        # Update school information in the database
        query = "UPDATE school SET Name = %s, Address = %s, City = %s, Phone_Number = %s, Email = %s, P_First_Name = %s, P_Last_Name = %s, O_First_Name = %s, O_Last_Name = %s WHERE School_ID = %s"
        values = (school_name, school_address, school_city, school_phone, school_email, principal_first_name, principal_last_name, operator_first_name, operator_last_name, school_id)
        mycursor.execute(query, values)
        mydb.commit()

        # Redirect to the school details page
        return redirect('/dashboard')

    else:
        if role == "Operator":
            query = "SELECT school.* FROM school INNER JOIN school_user ON school.School_ID = school_user.School_ID WHERE school_user.User_ID = %s"
            mycursor.execute(query, (user_id,))
            school_data = mycursor.fetchall()
            mycursor.nextset()  # Consume remaining results
        if role == "Admin":     
            query = "SELECT * FROM school"
            mycursor.execute(query)
            school_data = mycursor.fetchall()
            mycursor.nextset()  # Consume remaining results
        # Pass school data to the template for rendering
        return render_template('OperatorSchoolEditPageTest1.html', school=school_data)


@app.route('/books', methods=['GET', 'POST'])
def books():
    user_id = session['user_id']
    role = session['role']
    query = "SELECT DISTINCT bc.Category FROM book AS b INNER JOIN book_category AS bc ON b.Book_ID = bc.Book_ID WHERE b.School_ID IN (SELECT School_ID FROM school_user WHERE User_ID = %s)"
    mycursor.execute(query, (user_id,))
    categories = mycursor.fetchall()

    query = """SELECT DISTINCT ba.Author
        FROM book AS b
        INNER JOIN book_author AS ba
        ON b.Book_ID = ba.Book_ID
        WHERE b.School_ID IN (
            SELECT School_ID
            FROM school_user
            WHERE User_ID = %s
        )"""
    mycursor.execute(query, (user_id,))
    authors = mycursor.fetchall()

    if request.method == 'POST':
        search_title = request.form.get('search_title')
        selected_category = request.form.get('selected_category')
        selected_author = request.form.get('selected_author')  # Added author selection
        selected_language = request.form.get('selected_language')
        availability = request.form.get('availability')

        base_query = """SELECT DISTINCT b.*
                FROM book AS b
                INNER JOIN book_category AS bc ON b.Book_ID = bc.Book_ID
                INNER JOIN book_author AS ba ON b.Book_ID = ba.Book_ID
                WHERE 1=1"""

        conditions = []
        values = []

        if search_title:
            conditions.append("b.Title LIKE %s")
            values.append(f"%{search_title}%")

        if selected_category:
            selected_category = selected_category.strip("(',)")
            conditions.append("bc.Category = %s")
            values.append(selected_category)

        if selected_author:
            selected_author = selected_author.strip("(',)")
            conditions.append("ba.Author = %s")
            values.append(selected_author)

        if selected_language:
            conditions.append("b.Language = %s")
            values.append(selected_language)

        if availability:
            conditions.append("b.Available_Copies >= 1")

        if conditions:
            query = base_query + " AND " + " AND ".join(conditions)
        else:
            query = base_query

        if role != "Admin":
            query += " AND b.School_ID IN (SELECT School_ID FROM school_user WHERE User_ID = %s)"
            values.append(user_id)

        mycursor.execute(query, tuple(values))
        books = mycursor.fetchall()
    else:
        if role == "Admin":
            query = "SELECT * FROM book"
            mycursor.execute(query)
            books = mycursor.fetchall()
        else:
            query = "SELECT * FROM book WHERE School_ID IN (SELECT School_ID FROM school_user WHERE User_ID = %s)"
            mycursor.execute(query, (user_id,))
            books = mycursor.fetchall()

    if role == "Admin":
        query = "SELECT DISTINCT Category FROM book_category"
        mycursor.execute(query)
        all_categories = mycursor.fetchall()

        query = "SELECT DISTINCT Author FROM book_author"
        mycursor.execute(query)
        all_authors = mycursor.fetchall()

        return render_template('AdminBooksPageTest1.html', books=books, categories=all_categories, authors=all_authors)
    if role == "Teacher":
        return render_template('TeacherBooksPageTest1.html', books=books, categories=categories, authors=authors)
    if role == "Operator":
        return render_template('OperatorBooksPageTest1.html', books=books, categories=categories, authors=authors)
    if role == "Student":
        return render_template('StudentBooksPageTest4.html', books=books, categories=categories, authors=authors)


@app.route('/books/<int:book_id>')
def book(book_id):
    role = session['role']

    # Retrieve book information
    query = """
    SELECT
        b.*,
        s.Name AS SchoolName,
        AVG(ubr.Stars) AS AvgRating
    FROM
        book AS b
        LEFT JOIN user_book_review AS ubr ON b.Book_ID = ubr.Book_ID
        LEFT JOIN school AS s ON b.School_ID = s.School_ID
    WHERE
        b.Book_ID = %s
        AND ubr.Status = 'Approved'
"""
    mycursor.execute(query, (book_id,))
    book_info = mycursor.fetchone()

    # Retrieve authors for the book
    query = " SELECT ba.Author FROM book_author AS ba WHERE ba.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    authors = mycursor.fetchall()

    # Retrieve categories for the book
    query = " SELECT bc.Category FROM book_category AS bc WHERE bc.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    categories = mycursor.fetchall()

    # Retrieve keywords for the book
    query = " SELECT bk.Keyword FROM book_keyword AS bk WHERE bk.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    keywords = mycursor.fetchall()

    # Retrieve reviews for the book
    query = " SELECT u.Username, ubr.Stars, ubr.Comment FROM user_book_review AS ubr INNER JOIN user AS u ON ubr.User_ID = u.User_ID WHERE ubr.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    reviews = mycursor.fetchall()
    if role == "Operator":
        return render_template('OperatorBookDisplayTest1.html', book_info=book_info, authors=authors, categories=categories, keywords=keywords, reviews=reviews)
    if role == "Admin":
        return render_template('AdminBookDisplayTest1.html', book_info=book_info, authors=authors, categories=categories, keywords=keywords, reviews=reviews)
    if role == "Teacher":
        return render_template('TeacherBookDisplayTest1.html', book_info=book_info, authors=authors, categories=categories, keywords=keywords, reviews=reviews)
    else:
        return render_template('StudentBookDisplayTest1.html', book_info=book_info, authors=authors, categories=categories, keywords=keywords, reviews=reviews)

@app.route('/books/<int:book_id>/reviews', methods=['GET', 'POST'])
def reviews(book_id):
    role = session['role']

    # Retrieve book information and average rating from approved reviews
    query = "SELECT book.*, AVG(user_book_review.Stars) AS AvgRating FROM book LEFT JOIN user_book_review ON book.Book_ID = user_book_review.Book_ID WHERE book.Book_ID = %s AND user_book_review.Status = 'Approved'"
    mycursor.execute(query, (book_id,))
    book_info = mycursor.fetchone()

    if request.method == 'POST':
        # Check if the user already has a review for the book
        user_id = session['user_id']
        query = "SELECT * FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
        mycursor.execute(query, (user_id, book_id))
        existing_review = mycursor.fetchone()

        if existing_review:
            # Update the existing review
            stars = int(request.form['stars'])
            comment = request.form['comment']
            update_query = "UPDATE user_book_review SET Stars = %s, Comment = %s WHERE User_ID = %s AND Book_ID = %s"
            values = (stars, comment, user_id, book_id)
            mycursor.execute(update_query, values)
            mydb.commit()
        else:
            # Insert the new review
            stars = int(request.form['stars'])
            comment = request.form['comment']
            if role == "Operator" or role == "Teacher" or role == "Admin":
                insert_query = "INSERT INTO user_book_review (User_ID, Book_ID, Stars, Comment, Status) VALUES (%s, %s, %s, %s, 'Approved')"
                values = (user_id, book_id, stars, comment)
                mycursor.execute(insert_query, values)
            else:
                insert_query = "INSERT INTO user_book_review (User_ID, Book_ID, Stars, Comment) VALUES (%s, %s, %s, %s)"
                values = (user_id, book_id, stars, comment)
                mycursor.execute(insert_query, values)
            mydb.commit()

    # Retrieve approved reviews for the book (including the newly added/updated one)
    query = "SELECT user.Username, user_book_review.Stars, user_book_review.Comment, user_book_review.User_ID FROM user_book_review INNER JOIN user ON user_book_review.User_ID = user.User_ID WHERE user_book_review.Book_ID = %s AND user_book_review.Status = 'Approved'"
    mycursor.execute(query, (book_id,))
    reviews = mycursor.fetchall()

    if role == "Operator":
         return render_template('OperatorReviewsPageTest1.html', book_info=book_info, reviews=reviews)
    if role == "Admin":
         return render_template('AdminReviewsPageTest1.html', book_info=book_info, reviews=reviews)
    if role == "Teacher":
         current_user = session['user_id']
         return render_template('TeacherReviewsPageTest1.html', book_info=book_info, reviews=reviews, current_user=current_user)
    else:
         current_user = session['user_id']
         return render_template('StudentReviewsPageTest1.html', book_info=book_info, reviews=reviews, current_user=current_user)



@app.route('/books/<int:book_id>/reviews/delete', methods=['POST'])
def delete_review(book_id):
    # Check if the review belongs to the current user
    user_id = session['user_id']
    role = session['role']
    delete_user_id = None  # Initialize delete_user_id variable

    if role == "Operator" or role == "Admin":
        # Retrieve the user ID from the request
        delete_user_id = request.form.get('user_id')
        print(delete_user_id)
    else:
        delete_user_id = user_id

    
    query = "SELECT * FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
    mycursor.execute(query, (delete_user_id, book_id))
    review = mycursor.fetchone()

    if review:
        # Delete the review
        delete_query = "DELETE FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
        mycursor.execute(delete_query, (delete_user_id, book_id))
        mydb.commit()

    # Redirect back to the reviews page for the book
    return redirect(url_for('reviews', book_id=book_id))


@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    role = session['role']
    if request.method == 'POST':
        # Retrieve form data
        author_names = request.form.getlist('author[]')
        isbn = request.form['isbn']
        publisher = request.form['publisher']
        page_number = request.form['page_number']
        summary = request.form['summary']
        available_copies = request.form['available_copies']
        total_copies = request.form['total_copies']
        category_names = request.form.getlist('category[]')
        language = request.form['language']
        keyword_names = request.form.getlist('keyword[]')

        # Update authors for the book
        query = "DELETE FROM book_author WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        for author_name in author_names:
            query = "INSERT INTO book_author (Book_ID, Author) VALUES (%s, %s)"
            mycursor.execute(query, (book_id, author_name))

        # Update categories for the book
        query = "DELETE FROM book_category WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        for category_name in category_names:
            query = "INSERT INTO book_category (Book_ID, Category) VALUES (%s, %s)"
            mycursor.execute(query, (book_id, category_name))

        # Update keywords for the book
        query = "DELETE FROM book_keyword WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        for keyword_name in keyword_names:
            query = "INSERT INTO book_keyword (Book_ID, Keyword) VALUES (%s, %s)"
            mycursor.execute(query, (book_id, keyword_name))

        # Update book information
        query = "UPDATE book SET ISBN = %s, Publisher = %s, Total_Page_Number = %s, Summary = %s, Available_Copies = %s, Copies = %s, Language = %s WHERE Book_ID = %s"
        mycursor.execute(query, (isbn, publisher, page_number, summary, available_copies, total_copies, language, book_id))
        mydb.commit()

        # Redirect to the book display page
        return redirect(f"/books/{book_id}")

    else:
        # Retrieve book information
        query = "SELECT b.*, s.Name AS SchoolName, AVG(ubr.Stars) AS AvgRating FROM book AS b LEFT JOIN user_book_review AS ubr ON b.Book_ID = ubr.Book_ID LEFT JOIN school AS s ON b.School_ID = s.School_ID WHERE b.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        book_info = mycursor.fetchone()

        # Retrieve authors for the book
        query = "SELECT ba.Author FROM book_author AS ba WHERE ba.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        authors = mycursor.fetchall()

        # Retrieve categories for the book
        query = "SELECT bc.Category FROM book_category AS bc WHERE bc.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        categories = mycursor.fetchall()

        # Retrieve keywords for the book
        query = "SELECT bk.Keyword FROM book_keyword AS bk WHERE bk.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        keywords = mycursor.fetchall()
        if role == "Operator":
            return render_template('OperatorBookEditPageTest1.html', book_info=book_info, authors=authors, categories=categories, keywords=keywords)
        elif role == "Admin":
            return render_template('AdminBookEditPage.html', book_info=book_info, authors=authors, categories=categories, keywords=keywords)
    
@app.route('/books/add_book', methods=['GET', 'POST'])
def add_book():
    user_id = session['user_id']
    role = session['role']
    query = "SELECT School_ID FROM school_user WHERE User_ID = %s"
    mycursor = mydb.cursor()
    mycursor.execute(query, (user_id,))
    op_school_id_result = mycursor.fetchall()
    op_school_id = op_school_id_result[0][0] if op_school_id_result else None
    #op_school_id = op_school_id.strip("(',)")
    if request.method == 'GET':
        # Retrieve the list of available schools from the database
        if role == "Operator":
            
            return render_template('OperatorAddBook.html')
        elif role == "Admin":
            query = "SELECT Name FROM school"
            mycursor.execute(query)
            schools = mycursor.fetchall()
            return render_template('AdminAddBookPageTest2.html', schools=schools)
        
    elif request.method == 'POST':
        # Extract book data from the form submission
        title = request.form['title']
        authors = request.form.getlist('author[]')
        isbn = request.form['isbn']
        publisher = request.form['publisher']
        page_number = request.form['page_number']
        summary = request.form['summary']
        available_copies = request.form['available_copies']
        total_copies = request.form['total_copies']
        categories = request.form.getlist('category[]')
        language = request.form['language']
        keywords = request.form.getlist('keyword[]')
        cover = request.form['cover']
        if role == "Admin":
            library = request.form['library']
            # Get the School_ID based on the library name
            query = "SELECT School_ID FROM school WHERE Name = %s"
            mycursor = mydb.cursor()
            mycursor.execute(query, (library,))
            result = mycursor.fetchone()
            if result is None:
                return "Invalid library name"
            school_id = result[0]
        elif role == "Operator":
            school_id = op_school_id

        # Perform the database insertion
        mycursor = mydb.cursor()
        query = "INSERT INTO book (Title, ISBN, Publisher, Total_Page_Number, Summary, Available_Copies, Copies, Language, Images, School_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (title, isbn, publisher, page_number, summary, available_copies, total_copies, language, cover, school_id)
        mycursor.execute(query, values)
        book_id = mycursor.lastrowid

        # Insert authors into the database
        for author in authors:
            query = "INSERT INTO book_author (Author, Book_ID) VALUES (%s, %s)"
            values = (author, book_id)
            mycursor.execute(query, values)

        # Insert categories into the database
        for category in categories:
            query = "INSERT INTO book_category (Category, Book_ID) VALUES (%s, %s)"
            values = (category, book_id)
            mycursor.execute(query, values)

        # Insert keywords into the database
        for keyword in keywords:
            query = "INSERT INTO book_keyword (Keyword, Book_ID) VALUES (%s, %s)"
            values = (keyword, book_id)
            mycursor.execute(query, values)

        # Commit the changes to the database
        mydb.commit()

        return redirect(url_for('dashboard'))


@app.route('/queries')
def query():
    role = session['role']
    if role == 'Admin':
        return render_template('AdminQueries.html')
    elif role == 'Operator':
        return render_template('OperatorQueries.html')

@app.route('/queries2')
def query2():
    return render_template('QueriesTest2.html')

@app.route('/users')
def users():
    user_id = session['user_id']
    role = session['role']
    if role == "Operator":
        query = """SELECT user.*
                FROM user
                JOIN school_user
                ON user.User_ID = school_user.User_ID
                WHERE school_user.School_ID = (
                    SELECT School_ID
                    FROM school_user
                    WHERE User_ID = %s
                )"""
        mycursor.execute(query, (user_id,))
        users = mycursor.fetchall()
        return render_template('OperatorAllUsersPageTest1.html', users=users)
    else:
        query = "SELECT * FROM user"
        mycursor.execute(query)
        users = mycursor.fetchall()
        return render_template('AdminAllUsersPageTest1.html', users=users)

@app.route('/users/<int:user_id>')
def users_profile(user_id):
    role = session['role']

    query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s LIMIT 1"
    mycursor.execute(query, (user_id,))
    user = mycursor.fetchone()
    if role == "Operator":
        return render_template('OperatorOtherProfile1Test1.html', user=user)
    if role == "Admin":
        return render_template('AdminOtherProfile1Test1.html', user=user)
    
    
@app.route('/users/<int:user_id>/update_profile', methods=['GET', 'POST'])    # OKAY 
def user_update_profile(user_id):
    # Check if the request is a POST method (form submission)
    if request.method == 'POST':
        user_role = session['role']
        # Retrieve the updated profile data from the form
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        role = request.form.get('role')
        dob = request.form.get('dob')
        school_name = request.form.get('school_name')
        additional_school = request.form.get('additional_school')
        
        if role == "Teacher" or role == "Operator":
            query = "UPDATE user SET Username = %s, Password = %s, U_First_Name = %s, U_Last_Name = %s, Email = %s, Role = %s, Date_of_Birth = %s WHERE User_ID = %s"
            mycursor.execute(query, (username, password, first_name, last_name, email, role, dob, user_id))

            # print(query)
            # print((username, first_name, last_name, email, role, dob, user_id))
            # Update the school information if provided
            
            if additional_school:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                new_school_id = mycursor.fetchone()[0]  # Fetch the value from the result tuple

                query = "SELECT School_ID FROM school_user WHERE User_ID = %s AND School_ID <> %s"
                mycursor.execute(query, (user_id, new_school_id))
                old_school_id = mycursor.fetchone()[0]  # Fetch the value from the result tuple

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s and School_ID <> %s"
                mycursor.execute(query, (new_school_id, user_id, old_school_id))
            else:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                school_id = mycursor.fetchone()[0]  # Fetch the value from the result tuple

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s"
                mycursor.execute(query, (school_id, user_id,))

        elif role == "Admin" or role == "Student":
            query = "UPDATE user SET Password = %s WHERE User_ID = %s"
            mycursor.execute(query, (password, user_id))

        # Commit the changes to the database
        mydb.commit()

        # Redirect the user back to the profile page with updated data
        return redirect('/users')
    else:
        # Retrieve the current user's data and pass it to the template
        role = session['role']
        query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s LIMIT 1"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchone()
        if role == "Operator":
            return render_template('OperatorEditOtherProfile1Test1.html', user=user)
        if role == "Admin":
            return render_template('AdminEditOtherProfile1Test1.html', user=user)

@app.route('/users/<int:user_id>/delete_profile', methods=['POST'])     # OKAY
def delete_profile(user_id):
    # Delete user from school_user table
    delete_school_user_query = "DELETE FROM school_user WHERE User_ID = %s"
    mycursor.execute(delete_school_user_query, (user_id,))

    # Delete user's reviews from user_book_review table
    delete_reviews_query = "DELETE FROM user_book_review WHERE User_ID = %s"
    mycursor.execute(delete_reviews_query, (user_id,))

    # Delete user's applications from user_book_status table
    delete_applications_query = "DELETE FROM user_book_status WHERE User_ID = %s"
    mycursor.execute(delete_applications_query, (user_id,))

    # Delete user from user table
    delete_user_query = "DELETE FROM user WHERE User_ID = %s"
    mycursor.execute(delete_user_query, (user_id,))

    # Commit the changes
    mydb.commit()

    # Return a response indicating success (HTTP status code 200)
    return redirect(url_for('dashboard'))

@app.route('/users/<int:user_id>/deactivate_profile', methods=['POST'])     # OKAY
def deactivate_profile(user_id):
    # Update user status to "Deactivated"
    query = "UPDATE user SET Status = %s WHERE User_ID = %s"
    mycursor.execute(query, ("Deactivated", user_id))
    mydb.commit()

    return redirect(url_for('dashboard'))

@app.route('/users/<int:user_id>/reactivate_profile', methods=['POST'])     # OKAY
def reactivate_profile(user_id):
    # Update user status to "Approved"
    query = "UPDATE user SET Status = %s WHERE User_ID = %s"
    mycursor.execute(query, ("Approved", user_id))
    mydb.commit()

    return redirect(url_for('dashboard'))

@app.route('/users/<int:user_id>/card')
def card(user_id):
    query = '''
    SELECT u.*, s1.Name 
    FROM user u 
    LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID 
    LEFT JOIN school s1 ON su1.School_ID = s1.School_ID 
    LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID 
    WHERE u.User_ID = %s;
    '''
    mycursor.execute(query, (user_id,))
    user = mycursor.fetchone()
    return render_template('OperatorBorrowingCardUser.html', user=user)

@app.route('/answer')
def answer():
    role = session['role']
    if role == "Admin":
        query = "SELECT * FROM user"
        mycursor.execute(query)
        users = mycursor.fetchall()
        return render_template('AdminAllUsersPageTest1.html', users=users)
    
@app.route('/add_school', methods=['POST', 'GET'])      #OKAY
def add_school():
    if request.method == 'POST':
        school_name = request.form['school_name']
        address = request.form['address']
        city = request.form['city']
        phone_number = request.form['phone_number']
        email = request.form['email']
        p_first_name = request.form['p_first_name']
        p_last_name = request.form['p_last_name']
        o_first_name = request.form['o_first_name']
        o_last_name = request.form['o_last_name']

        query = "INSERT INTO school (Name, Address, City, Phone_Number, Email, P_First_Name, P_Last_Name, O_First_Name, O_Last_Name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (school_name, address, city, phone_number, email, p_first_name, p_last_name, o_first_name, o_last_name)

        mycursor = mydb.cursor()
        mycursor.execute(query, values)
        mydb.commit()

        return redirect(url_for('dashboard'))
    if request.method == 'GET':
        return render_template('AdminAddSchoolPageTest1.html')

@app.route('/approve_users', methods=['GET', 'POST'])       # OK ALLA PREPEI NA BALO KAI TO SCHOOL ID MESA
def operator_approve_users():
    # Check if the request is a POST method (form submission)
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')

        if action == 'Accept':
            # Update the user's status to "Approved" in the database
            query = "UPDATE user SET Status = 'Approved' WHERE User_ID = %s"
            mycursor.execute(query, (user_id,))
            mydb.commit()
        elif action == 'Deny':
            # Update the user's status to "Deny" in the database
            query = "UPDATE user SET Status = 'Deny' WHERE User_ID = %s"
            mycursor.execute(query, (user_id,))
            mydb.commit()
        

        # Redirect the user back to the user approval page
        return redirect('/approve_users')

    else:
        role = session['role']
        user_id = session['user_id']
        if role == "Admin":
            query = "SELECT * FROM user WHERE Status = 'pending' AND Role = 'Operator'"
            mycursor.execute(query)
            users = mycursor.fetchall()
            return render_template('AdminApproveUsersPageTest1.html', users=users)
        if role == "Operator":
            query = "SELECT school.Name FROM school_user JOIN user ON user.User_ID = school_user.User_ID JOIN school ON school.School_ID = school_user.School_ID WHERE user.User_ID = %s"
            mycursor.execute(query, (user_id,))
            school_name_result = mycursor.fetchall()
            school_name = school_name_result[0][0] if school_name_result else None  # Extract the string value from the tuple
            school_name = school_name.strip("(',)")  # Remove symbols from school_name


            if school_name:
                query = """
                    SELECT user.*
                    FROM school_user
                    JOIN user ON user.User_ID = school_user.User_ID
                    JOIN school ON school.School_ID = school_user.School_ID
                    WHERE user.Status = 'pending'
                        AND (user.Role = 'Teacher' OR user.Role = 'Student')
                        AND school.Name = %s
                """
                mycursor.execute(query, (school_name,))
                users = mycursor.fetchall()
            else:
                users = []
            return render_template('OperatorApproveUsersPageTest2.html', users=users, school_name=school_name)

@app.route('/operator_approve_comments', methods=['GET', 'POST'])      
def operator_approve_comments():
    user_id = session['user_id']
    
    # Check if the request is a POST method (form submission)
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')

        if 'deny' in request.form:
            # Delete the user's data from the database
            query = "DELETE FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
            mycursor.execute(query, (user_id, book_id))
            mydb.commit()
        elif 'approve' in request.form:
            # Update the user's status to "Approved" in the database
            query = "UPDATE user_book_review SET Status = 'Approved' WHERE User_ID = %s AND Book_ID = %s"
            mycursor.execute(query, (user_id, book_id))
            mydb.commit()

        # Redirect the user back to the user approval page
        return redirect('/operator_approve_comments')

    else:
        role = session['role']
        if role == "Operator":
            query = "SELECT r.* FROM user_book_review AS r \
            INNER JOIN book AS b ON r.Book_ID = b.Book_ID \
            INNER JOIN school_user AS su ON b.School_ID = su.School_ID \
            INNER JOIN school AS s ON su.School_ID = s.School_ID \
            WHERE r.Status = 'pending' AND su.User_ID = %s"
            mycursor.execute(query, (user_id,))
            reviews = mycursor.fetchall()
            return render_template('OperatorApproveReviewsTest1.html', reviews=reviews)
        
@app.route('/query311', methods=['GET', 'POST'])
def query311():
    if request.method == 'POST':
        selected_school = request.form.get('selected_school')
        selected_year = request.form.get('selected_year')
        selected_month = request.form.get('selected_month')

        base_query = '''
        SELECT b.School_ID, c.Name, u.U_First_Name, u.U_Last_Name, b.Title,
        (
        SELECT GROUP_CONCAT(DISTINCT Category SEPARATOR ', ')
        FROM book_category
        WHERE Book_ID = b.Book_ID
        ) AS Categories,
        (
        SELECT GROUP_CONCAT(DISTINCT Author SEPARATOR ', ')
         FROM book_author
        WHERE Book_ID = b.Book_ID
        ) AS Authors
        FROM user u
        JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        JOIN school c ON c.School_ID = b.School_ID
        WHERE ubs.Type = 'Rent' OR ubs.Type = 'Returned'
        '''

        conditions = []
        values = []

        if selected_school:
            conditions.append("b.School_ID = %s")
            values.append(selected_school)

        if selected_year:
            conditions.append("YEAR(ubs.Start_Date) = %s")
            values.append(selected_year)

        if selected_month:
            conditions.append("MONTH(ubs.Start_Date) = %s")
            values.append(selected_month)

        if conditions:
            query = base_query + " AND " + " AND ".join(conditions) + " ORDER BY b.School_ID"
        else:
            query = base_query + " ORDER BY b.School_ID"

        mycursor.execute(query, tuple(values))
        result = mycursor.fetchall()
    else:
        query = '''
        SELECT b.School_ID, c.Name, u.U_First_Name, u.U_Last_Name, b.Title,
        (
        SELECT GROUP_CONCAT(DISTINCT Category SEPARATOR ', ')
        FROM book_category
        WHERE Book_ID = b.Book_ID
        ) AS Categories,
        (
        SELECT GROUP_CONCAT(DISTINCT Author SEPARATOR ', ')
        FROM book_author
        WHERE Book_ID = b.Book_ID
        ) AS Authors
        FROM user u
        JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        JOIN school c ON c.School_ID = b.School_ID
        WHERE ubs.Type = 'Rent' OR ubs.Type = 'Returned'
        ORDER BY b.School_ID;
        '''
        mycursor.execute(query)
        result = mycursor.fetchall()

    schools_query = "SELECT School_ID, Name FROM school;"
    mycursor.execute(schools_query)
    schools = mycursor.fetchall()

    years_query = "SELECT DISTINCT YEAR(Start_Date) FROM user_book_status;"
    mycursor.execute(years_query)
    years = [str(row[0]) for row in mycursor.fetchall()]

    months_query = "SELECT DISTINCT MONTH(Start_Date) FROM user_book_status;"
    mycursor.execute(months_query)
    months = [str(row[0]) for row in mycursor.fetchall()]

    return render_template('AdminQuery311Test2.html', result=result, schools=schools, years=years, months=months)





@app.route('/query312', methods=['GET'])
def query312():
    query = "SELECT DISTINCT Category FROM book_category"
    mycursor.execute(query)
    categories = mycursor.fetchall()
    return render_template('AdminQuery312Select.html', categories=categories) 
    
@app.route('/query312a', methods=['GET'])
def query312a():
    category = request.args.get('category')
    category = category.strip("(',)")
    query = '''
    SELECT ba.Author, b.Title, bc.Category AS Category
    FROM book_category bc
    JOIN book_author ba ON bc.Book_ID = ba.Book_ID
    JOIN book b ON bc.Book_ID = b.Book_ID
    WHERE bc.Category = %s
    GROUP BY ba.Author, b.Title, bc.Category
    ORDER BY ba.Author
    '''
    mycursor.execute(query, (category,))
    result = mycursor.fetchall()
    return render_template('AdminQuery312aTest1.html', result=result)

@app.route('/query312b', methods=['GET'])
def query312b():
    category = request.args.get('category')
    category = category.strip("(',)")
    query = '''
    SELECT u.U_First_Name, u.U_Last_Name, u.Role, b.Title, ubs.Start_Date, bc.Category, ubs.Type
    FROM book_category bc
    INNER JOIN book b ON b.Book_ID = bc.Book_ID
    INNER JOIN user_book_status ubs ON b.Book_ID = ubs.Book_ID
    INNER JOIN user u ON u.User_ID = ubs.User_ID
    WHERE u.Role = 'Teacher' AND (ubs.Type = 'Rent' OR ubs.Type = 'Returned' OR ubs.Type = 'Late') AND YEAR(ubs.Start_Date) = YEAR(CURDATE()) AND bc.Category = %s
    GROUP BY u.User_ID, u.U_First_Name, u.U_Last_Name, u.Role, b.Title, ubs.Start_Date, bc.Category, ubs.Type
    ORDER BY u.User_ID
    '''
    mycursor.execute(query, (category,))
    result = mycursor.fetchall()
    return render_template('AdminQuery312b.html', result=result)


@app.route('/query313')
def query313():
    query = '''
    SELECT u.User_ID, u.U_Last_Name, u.U_First_Name, u.Role, TIMESTAMPDIFF(YEAR, u.Date_of_Birth, CURDATE()) AS Age, COUNT(ubs.Book_ID) AS NumRentedBooks
    FROM user u
    INNER JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
    INNER JOIN book b ON b.Book_ID = ubs.Book_ID
    WHERE u.Role = 'Teacher' AND TIMESTAMPDIFF(YEAR, u.Date_of_Birth, CURDATE()) <= 40 AND (ubs.Type = 'Rent' OR ubs.Type = 'Returned')
    GROUP BY u.User_ID, u.U_First_Name, u.U_Last_Name, u.Role, Age
    ORDER BY NumRentedBooks DESC, u.U_Last_Name
    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery313Test2.html', result=result)  

@app.route('/query314')
def query314():
    query = '''
    SELECT ba.Author, b.Title
    FROM book b
    JOIN book_author ba ON b.Book_ID = ba.Book_ID
    LEFT JOIN user_book_status ubs ON b.Book_ID = ubs.Book_ID
    WHERE ubs.Type = 'Rent' OR ubs.Type = 'Returned' OR ubs.Type = 'Late'
    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery314.html', result=result) 

@app.route('/query315')
def query315():
    query = '''
    SELECT o.U_First_Name, o.U_Last_Name, s.Name, COUNT(*) AS NumRents
    FROM user u
    INNER JOIN user_book_status ubs ON ubs.User_ID = u.User_ID
    INNER JOIN book b ON b.Book_ID = ubs.Book_ID
    INNER JOIN school_user su ON su.School_ID = b.School_ID
    INNER JOIN school s ON su.School_ID = s.School_ID
    INNER JOIN user o ON o.User_ID = su.User_ID AND o.Role = 'Operator'
    WHERE ubs.Type IN ('Rent', 'Returned', 'Late') AND YEAR(ubs.Start_Date) = YEAR(CURDATE())
    GROUP BY o.User_ID, o.U_First_Name, o.U_Last_Name
    ORDER BY o.U_First_Name;
    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery315.html', result=result) 

@app.route('/query316')
def query316():
    query = '''
    SELECT bc1.Category AS Category1, bc2.Category AS Category2, COUNT(*) AS Count
    FROM book_category bc1
    JOIN book_category bc2 ON bc1.Book_ID = bc2.Book_ID
    JOIN user_book_status ubs ON bc1.Book_ID = ubs.Book_ID
    WHERE ubs.Type IN ('Rent', 'Returned', 'Late') AND bc1.Category < bc2.Category
    GROUP BY bc1.Category, bc2.Category
    ORDER BY Count DESC
    LIMIT 3;
    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery316.html', result=result) 

@app.route('/query317')
def query317():
    query = '''
    SELECT a.Author, COUNT(DISTINCT b.Title) AS NumBooks
    FROM book_author AS a
    JOIN book AS b ON a.Book_ID = b.Book_ID
    GROUP BY a.Author
    HAVING COUNT(DISTINCT b.Title) >= (
        SELECT COUNT(DISTINCT b2.Title) - 5
        FROM book_author AS a2
        JOIN book AS b2 ON a2.Book_ID = b2.Book_ID
        GROUP BY a2.Author
        ORDER BY COUNT(DISTINCT b2.Title) DESC
        LIMIT 1
    )
    ORDER BY NumBooks DESC
    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery317.html', result=result)

@app.route('/query322', methods=['GET', 'POST'])
def query322():
    user_id = session['user_id']
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    days_of_delay = request.form.get('days_of_delay')

    query = '''
    SELECT u.U_First_Name, u.U_Last_Name, b.Title, DATEDIFF(CURDATE(), ubs.End_Date) AS `Days of Delay`
    FROM user u 
    INNER JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
    INNER JOIN book b ON b.Book_ID = ubs.Book_ID
    INNER JOIN school_user su ON u.User_ID = su.User_ID
    WHERE ubs.Type = 'Late' AND su.school_id = (SELECT school_id FROM school_user WHERE User_ID = %s)
    '''

    filters = []
    parameters = [user_id]

    if first_name:
        filters.append("u.U_First_Name LIKE %s")
        parameters.append(f"%{first_name}%")

    if last_name:
        filters.append("u.U_Last_Name LIKE %s")
        parameters.append(f"%{last_name}%")

    if days_of_delay:
        filters.append("DATEDIFF(CURDATE(), ubs.End_Date) >= %s")
        parameters.append(int(days_of_delay))

    if filters:
        query += " AND " + " AND ".join(filters)

    query += " ORDER BY `Days of Delay` DESC"

    mycursor.execute(query, parameters)
    result = mycursor.fetchall()
    return render_template('OperatorQuery322.html', result=result)

@app.route('/query323')
def query323():
    user_id = session['user_id']
    query1 = '''
    SELECT u.User_ID, u.U_First_Name, u.U_Last_Name, AVG(ubr.Stars) AS AvgUserRating
    FROM user u
    INNER JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
    INNER JOIN user_book_review ubr ON ubs.User_ID = ubr.User_ID AND ubs.Book_ID = ubr.Book_ID
    INNER JOIN school_user su ON u.User_ID = su.User_ID
    WHERE su.school_id = (SELECT school_id FROM school_user WHERE User_ID = %s)
    GROUP BY u.User_ID, u.U_First_Name;
    '''
    mycursor.execute(query1, (user_id,))
    result1 = mycursor.fetchall()

    query2 = '''
    SELECT bc.Category, AVG(ubr.Stars) AS AvgCategoryRating
    FROM book_category bc
    INNER JOIN book b ON bc.Book_ID = b.Book_ID
    INNER JOIN user_book_review ubr ON b.Book_ID = ubr.Book_ID
    INNER JOIN user u ON u.User_ID = ubr.User_ID
    INNER JOIN school_user su ON u.User_ID = su.User_ID
    WHERE su.school_id = (SELECT school_id FROM school_user WHERE User_ID = %s)
    GROUP BY bc.Category
    '''
    mycursor.execute(query2, (user_id,))
    result2 = mycursor.fetchall()

    return render_template('OperatorQuery323.html', result1=result1, result2=result2)

@app.route('/books/<int:book_id>/make_application', methods=['GET', 'POST'])
def make_application(book_id):
    role = session['role']
    user_id = session['user_id']
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_date = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        # Check for error messages using a try-except block
        available_copies = request.form['available_copies']
        try:
            # Insert application into the database
            user_id = session['user_id']
            if int(available_copies) >= 1:
                status = "Application"
            else:
                status = "Waiting"
            
            query = "INSERT INTO user_book_status (User_ID, Book_ID, Start_Date, End_Date, Type) VALUES (%s, %s, %s, %s, %s)"
            values = (user_id, book_id, current_date, end_date, status)
            mycursor.execute(query, values)
            mydb.commit()
            print(available_copies)
            if int(available_copies) >= 1:
                query = "UPDATE book SET Available_Copies = Available_Copies - 1 WHERE Book_ID = %s"
                mycursor.execute(query, (book_id,))
                mydb.commit()

            # Redirect to the applications page
            return redirect("/dashboard")
        except mysql.connector.Error as error:
            # Display error message in a pop-up box
            flash(str(error))
            return redirect("/books/" + str(book_id) + "/make_application")

    else:
        # Retrieve book information and average rating from approved reviews
        query = "SELECT * FROM book WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        book_info = mycursor.fetchone()

        # Retrieve authors for the book
        query = "SELECT ba.Author FROM book_author AS ba WHERE ba.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        authors = mycursor.fetchall()

        # Retrieve categories for the book
        query = "SELECT bc.Category FROM book_category AS bc WHERE bc.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        categories = mycursor.fetchall()

        # Retrieve keywords for the book
        query = "SELECT bk.Keyword FROM book_keyword AS bk WHERE bk.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        keywords = mycursor.fetchall()

        return render_template('BookApplicationPageTest1.html', book_info=book_info, role=role,
                               start_date=current_date, end_date=end_date, authors=authors,
                               categories=categories, keywords=keywords)


@app.route('/applications', methods=['GET', 'POST'])
def applications():
    user_id = session['user_id']
    role = session['role']
    if request.method == 'POST':
        status_id = request.form['status_id']
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_query = "UPDATE user_book_status SET Type = 'Cancelled', End_Date = %s WHERE Status_ID = %s "
        mycursor.execute(update_query, (end_date, status_id,))
        mydb.commit()
        
        return redirect("/applications")
    else:       #get method
        query = """SELECT
            u.U_First_Name,
            u.U_Last_Name,
            b.Title AS Book_Title,
            ubs.*
        FROM
            user_book_status ubs
        JOIN
            user u ON ubs.User_ID = u.User_ID
        JOIN
            book b ON ubs.Book_ID = b.Book_ID
        WHERE
            ubs.Type = %s
            AND ubs.User_ID = %s
        """

        types = ["Rent", "Returned", "Late", "Application", "Cancelled", "Waiting"]
        rent_list = []
        returned_list = []
        late_list = []
        application_list = []
        cancelled_list = []
        waiting_list = []

        for t in types:
            mycursor.execute(query, (t, user_id))
            if t == 'Rent':
                rent_list = mycursor.fetchall()
            elif t == 'Returned':
                returned_list = mycursor.fetchall()
            elif t == 'Late':
                late_list = mycursor.fetchall()
            elif t == 'Application':
                application_list = mycursor.fetchall()
            elif t == 'Cancelled':
                cancelled_list = mycursor.fetchall()
            elif t == 'Waiting':
                waiting_list = mycursor.fetchall()
        if role == "Student":
            return render_template('StudentMyApplicationsPageTest1.html', rent_list=rent_list,returned_list=returned_list,late_list=late_list,application_list=application_list, cancelled_list=cancelled_list, waiting_list=waiting_list)                  
        if role == "Teacher":
            return render_template('TeacherMyApplicationsPageTest1.html', rent_list=rent_list,returned_list=returned_list,late_list=late_list,application_list=application_list, cancelled_list=cancelled_list, waiting_list=waiting_list)
        

@app.route('/approve_applications', methods=['GET', 'POST'])
def operator_applications():
    role = session['role']

    if request.method == 'POST':
        mycursor = mydb.cursor()
        status_id = request.form['status_id']
        book_id = request.form['book_id']
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_query = "UPDATE user_book_status SET Type = 'Returned', End_Date = %s WHERE Status_ID = %s"
        mycursor.execute(update_query, (end_date, status_id,))
        mydb.commit()

        query = """SELECT *
                FROM user_book_status
                WHERE Book_ID = %s
                AND Type = 'Waiting'
                ORDER BY Start_Date ASC
                LIMIT 1
                """
        mycursor.execute(query, (book_id,))
        waiting = mycursor.fetchone()
        mydb.commit()
        if(waiting):
            wait_status_id = waiting[0]
            print(wait_status_id)
        else:
            wait_status_id = None
        if(wait_status_id): 
            query = "UPDATE user_book_status SET Type = 'Application' WHERE Status_ID = %s"
            mycursor.execute(query, (wait_status_id,))
            mydb.commit()   
        else:
            query = "UPDATE book SET Available_Copies = Available_Copies + 1 WHERE Book_ID = %s"
            mycursor.execute(query, (book_id,))
            mydb.commit()

        return redirect("/approve_applications")

    else:
        user_id = session['user_id']
        query = "SELECT School_ID FROM school_user WHERE User_ID = %s"
        mycursor = mydb.cursor()
        mycursor.execute(query, (user_id,))
        op_school_id_result = mycursor.fetchall()
        op_school_id = op_school_id_result[0][0] if op_school_id_result else None
        query = """
        SELECT u.U_First_Name, u.U_Last_Name, b.Title AS Book_Title, ubs.*
        FROM user_book_status ubs
        JOIN user u ON ubs.User_ID = u.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        JOIN school_user us ON ubs.User_ID = us.User_ID
        WHERE us.School_ID = %s AND ubs.Type = %s
        """
        types = ["Rent", "Returned", "Late", "Application", "Cancelled", "Waiting"]
        rent_list = []
        returned_list = []
        late_list = []
        application_list = []
        cancelled_list = []
        waiting_list = []

        for t in types:
            mycursor.execute(query, (op_school_id, t))
            if t == 'Rent':
                rent_list = mycursor.fetchall()
            elif t == 'Returned':
                returned_list = mycursor.fetchall()
            elif t == 'Late':
                late_list = mycursor.fetchall()
            elif t == 'Application':
                application_list = mycursor.fetchall()
            elif t == 'Cancelled':
                cancelled_list = mycursor.fetchall()
            elif t == 'Waiting':
                waiting_list = mycursor.fetchall()

        return render_template('OperatorApplicationsPage.html', rent_list=rent_list, returned_list=returned_list, 
                                                    late_list=late_list, application_list=application_list, cancelled_list=cancelled_list, waiting_list=waiting_list)


@app.route('/operator_make_application', methods=['GET', 'POST'])
def operator_make_application():
    user_id = session['user_id']
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_date = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S")

    query = "SELECT School_ID FROM school_user WHERE User_ID = %s"
    mycursor = mydb.cursor()
    mycursor.execute(query, (user_id,))
    op_school_id_result = mycursor.fetchall()
    op_school_id = op_school_id_result[0][0] if op_school_id_result else None

    if request.method == 'POST':
        # Read User_ID and Book_ID from the form
        user_id = request.form.get('user')
        book_id = request.form.get('book_title')

        # Insert application into the database
        try:
            query = "INSERT INTO user_book_status (User_ID, Book_ID, Start_Date, End_Date, Type) VALUES (%s, %s, %s, %s, %s)"
            values = (user_id, book_id, current_date, end_date, "Rent")
            mycursor.execute(query, values)
            mydb.commit()

            # Reduce available copies of the book
            query = "UPDATE book SET Available_Copies = Available_Copies - 1 WHERE Book_ID = %s"
            mycursor.execute(query, (book_id,))
            mydb.commit()

            # Redirect to the applications page
            return redirect("/dashboard")
        except mysql.connector.Error as error:
            error_message = str(error)
            flash(error_message)
            return redirect(request.url)  # Redirect back to the same page to display the error message
    else:
        query = "SELECT Book_ID, Title FROM book WHERE School_ID = %s AND Available_Copies >= 1"
        mycursor.execute(query, (op_school_id,))
        books = mycursor.fetchall()
        query = """SELECT user.User_ID, user.U_First_Name, user.U_Last_Name
                FROM user
                JOIN school_user
                ON user.User_ID = school_user.User_ID
                WHERE school_user.School_ID = (
                    SELECT School_ID
                    FROM school_user
                    WHERE User_ID = %s
                )"""
        mycursor.execute(query, (user_id,))
        users = mycursor.fetchall()

        return render_template('OperatorAddApplication.html', users=users, books=books)
    
@app.route('/operator_approve_applications', methods=['GET', 'POST'])
def operator_approve_applications():
    if request.method == 'POST':
        status_id = request.form['status_id']
        action = request.form['action']
        book_id = request.form['book_id']

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if action == 'accept':
            application_type = 'Rent'
            end_date = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S")
        elif action == 'deny':
            application_type = 'Cancelled'
            end_date = current_date
        

        # Perform the database update for the application
        mycursor = mydb.cursor()
        update_query = "UPDATE user_book_status SET Type = %s, Start_Date = %s, End_Date = %s WHERE Status_ID = %s"
        mycursor.execute(update_query, (application_type, current_date, end_date, status_id))
        mydb.commit()
        if action == "deny":
            # Increase available copies of the book
            query = "UPDATE book SET Available_Copies = Available_Copies + 1 WHERE Book_ID = %s"
            mycursor.execute(query, (book_id,))
            mydb.commit()

        return redirect("/operator_approve_applications")

    else:
        # Load data for applications to be displayed on the HTML page
        # Fetch applications with their corresponding Status_ID
        user_id = session['user_id']
        query = "SELECT School_ID FROM school_user WHERE User_ID = %s"
        mycursor = mydb.cursor()
        mycursor.execute(query, (user_id,))
        op_school_id_result = mycursor.fetchall()
        op_school_id = op_school_id_result[0][0] if op_school_id_result else None

        current_date = datetime.now()
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)

        query = """
        SELECT u.U_First_Name, u.U_Last_Name, b.Title AS Book_Title, ubs.*
        FROM user_book_status ubs
        JOIN user u ON ubs.User_ID = u.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        JOIN school_user us ON ubs.User_ID = us.User_ID
        WHERE
            us.School_ID = %s
            AND ubs.Type = 'Application'
            AND ubs.Status_ID = (
                SELECT MIN(ubs2.Status_ID)
                FROM user_book_status ubs2
                WHERE ubs2.User_ID = ubs.User_ID
                    AND ubs2.Book_ID = ubs.Book_ID
                    AND ubs2.Type = ubs.Type
            )
            AND (
                (
                    u.Role = 'Student'
                    AND (
                        SELECT COUNT(*)
                        FROM user_book_status ubs3
                        WHERE ubs3.User_ID = u.User_ID
                            AND ubs3.Type IN ('Rent', 'Late')
                            AND ubs3.Start_Date >= %s
                            AND ubs3.Start_Date <= %s
                            AND (ubs3.Status_ID != ubs.Status_ID OR ubs3.Status_ID IS NULL)
                    ) < 2
                )
                OR
                (
                    u.Role = 'Teacher'
                    AND (
                        SELECT COUNT(*)
                        FROM user_book_status ubs4
                        WHERE ubs4.User_ID = u.User_ID
                            AND ubs4.Type IN ('Rent', 'Late')
                            AND ubs4.Start_Date >= %s
                            AND ubs4.Start_Date <= %s
                            AND (ubs4.Status_ID != ubs.Status_ID OR ubs4.Status_ID IS NULL)
                    ) < 1
                )
            )
        ORDER BY b.Title
        """
        mycursor = mydb.cursor()
        mycursor.execute(query, (op_school_id, week_start, week_end, week_start, week_end))
        applications = mycursor.fetchall()

        return render_template('OperatorApproveApplications.html', applications=applications)



@app.route('/control_panel')
def control_panel():
    role = session['role']
    if role == "Admin":
        return render_template('AdminControlPanel.html') 
    if role == "Operator":
        return render_template('OperatorControlPanel.html') 

@app.route('/backup', methods=['POST'])
def create_backup():
    # Get the current date and time to create a unique backup file name
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Specify the name of the backup file
    backup_file = f'backup_{timestamp}.sql'

    # Specify the MySQL database connection details
    host = 'localhost'
    user = 'root'
    password = ''
    database = 'LibraryDatabase5'

    # Specify the path to the backup directory
    backup_dir = r'C:\Users\voudo\Documents\codes\DatabaseLibrary\DatabaseBackups'

    # Construct the mysqldump command
    mysqldump_cmd = f'mysqldump --host={host} --user={user} --password={password} {database} > {os.path.join(backup_dir, backup_file)}'

    try:
        # Execute the mysqldump command using subprocess
        subprocess.check_output(mysqldump_cmd, shell=True)
        return redirect(url_for('dashboard'))
    except subprocess.CalledProcessError as e:
        return jsonify({'message': f'Failed to create backup: {str(e.output)}'}), 500


# Database restore route
@app.route('/restore', methods=['GET'])
def restore_backup():
    # Specify the path to the backup directory
    backup_dir = r'C:\Users\voudo\Documents\codes\DatabaseLibrary\DatabaseBackups'

    # Get a list of backup files in the directory
    backup_files = glob.glob(os.path.join(backup_dir, 'backup_*.sql'))

    return render_template('AdminRestoreSelect.html', backup_files=backup_files)

@app.route('/restore', methods=['POST'])
def restore_backup_post():
    # Get the selected backup file from the form data
    selected_file = request.form.get('backup_file')

    # Specify the MySQL database connection details
    host = 'localhost'
    user = 'root'
    password = ''
    database = 'LibraryDatabase5'

    # Specify the path to the backup directory
    backup_dir = r'C:\Users\voudo\Documents\codes\DatabaseLibrary\DatabaseBackups'

    # Construct the full path to the selected backup file
    backup_file_path = os.path.join(backup_dir, selected_file)

    print(backup_file_path)

    # Construct the mysql command to restore the database from the backup file
    mysql_cmd = f'mysql --host={host} --user={user} --password={password} {database} < {backup_file_path}'

    try:
        # Execute the mysql command using subprocess
        subprocess.check_output(mysql_cmd, shell=True)
        return jsonify({'message': 'Database restored successfully'})
    except subprocess.CalledProcessError as e:
        return jsonify({'message': f'Failed to restore database: {str(e.output)}'}), 500
    
    