from flask import render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta
import shutil
import os
import sqlite3
import subprocess
import glob
import mysql.connector

from app import app, mydb  

mycursor = mydb.cursor()

@app.route('/')
def main():
    return render_template('LoginTest4.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    query = "SELECT * FROM user WHERE username=%s AND password=%s"
    mycursor.execute(query, (username, password))
    result = mycursor.fetchone()

    if result is not None:
        user_id = result[0]
        role = result[7]
        status = result[8]  
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
        return render_template('LoginTest4.html', error='Incorrect username or password')
    
@app.route('/about')       
def about():
    return render_template('AboutPage.html')
    
@app.route('/logout')       
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/register', methods=['POST', 'GET'])        
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        role = request.form['role']
        date = request.form['birth_date']
        school_name = request.form['school']
        additional_school = request.form.get('additional_school')

        query = "INSERT INTO user (Username, Password, U_First_Name, U_Last_Name, Email, Role, Date_of_Birth) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (username, password, first_name, last_name, email, role, date)
        mycursor.execute(query, values)
        mydb.commit()

        query = "SELECT User_ID FROM user WHERE Username = %s"
        mycursor.execute(query, (username,))
        user_id = mycursor.fetchone()[0]

        query = "SELECT School_ID FROM school WHERE Name = %s"
        mycursor.execute(query, (school_name,))
        school_id = mycursor.fetchone()[0]

        query = "INSERT INTO school_user (School_ID, User_ID) VALUES (%s, %s)"
        values = (school_id, user_id)
        mycursor.execute(query, values)
        mydb.commit()

        if role != "Student" and additional_school:
            query = "SELECT School_ID FROM school WHERE Name = %s"
            mycursor.execute(query, (additional_school,))
            additional_school_id = mycursor.fetchone()[0]

            query = "INSERT INTO school_user (School_ID, User_ID) VALUES (%s, %s)"
            values = (additional_school_id, user_id)
            mycursor.execute(query, values)
            mydb.commit()

        return redirect(url_for('main'))
    else:
        query = "SELECT Name FROM school"
        mycursor.execute(query)
        schools = mycursor.fetchall()

        return render_template('RegisterTest6.html', schools=schools)

@app.route('/dashboard')        
def dashboard():
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
    
@app.route('/profile')
def profile():
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
        mycursor.nextset()  
        return render_template('TeacherProfileTest1.html', user=user)
    if role == "Operator":
        query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchall()
        mycursor.nextset()  
        return render_template('OperatorProfileTest1.html', user=user)
    if role == "Admin":
        query = "SELECT * FROM user WHERE User_ID = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchone()
        return render_template('AdminProfileTest1.html', user=user)

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        user_id = session['user_id']
        role = session['role']

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
            
            if additional_school:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                new_school_id = mycursor.fetchone()[0]  
                query = "SELECT School_ID FROM school_user WHERE User_ID = %s AND School_ID <> %s"
                mycursor.execute(query, (user_id, new_school_id))
                old_school_id = mycursor.fetchone()[0]  

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s and School_ID <> %s"
                mycursor.execute(query, (new_school_id, user_id, old_school_id))
            else:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                school_id = mycursor.fetchone()[0]  

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s"
                mycursor.execute(query, (school_id, user_id,))

        elif role == "Admin" or role == "Student":
            query = "UPDATE user SET Password = %s WHERE User_ID = %s"
            mycursor.execute(query, (password, user_id))

        mydb.commit()

        return redirect('/profile')
    else:
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
            mycursor.nextset()
            return render_template('TeacherEditProfilePageTest1.html', user=user)
        if role == "Operator":
            query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s"
            mycursor.execute(query, (user_id,))
            user = mycursor.fetchall()
            mycursor.nextset()
            return render_template('OperatorEditProfilePageTest1.html', user=user)
        if role == "Admin":
            query = "SELECT * FROM user WHERE User_ID = %s"
            mycursor.execute(query, (user_id,))
            user = mycursor.fetchone() 
            return render_template('AdminEditProfilePageTest1.html', user=user)
   

@app.route('/school')           
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
        mycursor.nextset() 
        return render_template('TeacherSchoolPageTest1.html', school=school)
    if role == "Operator":
        query = "SELECT school.* FROM school INNER JOIN school_user ON school.School_ID = school_user.School_ID WHERE school_user.User_ID = %s"
        mycursor.execute(query, (user_id,))
        school = mycursor.fetchall()
        mycursor.nextset() 
        return render_template('OperatorSchoolPageTest1.html', school=school)
    if role == "Admin":     
        query = "SELECT * FROM school"
        mycursor.execute(query)
        school = mycursor.fetchall()
        mycursor.nextset() 
        return render_template('AdminSchoolPageTest1.html', school=school)
    
@app.route('/update_school', methods=['GET', 'POST'])
def update_school():
    role = session['role']
    user_id = session['user_id']
    if request.method == 'POST':
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

        query = "UPDATE school SET Name = %s, Address = %s, City = %s, Phone_Number = %s, Email = %s, P_First_Name = %s, P_Last_Name = %s, O_First_Name = %s, O_Last_Name = %s WHERE School_ID = %s"
        values = (school_name, school_address, school_city, school_phone, school_email, principal_first_name, principal_last_name, operator_first_name, operator_last_name, school_id)
        mycursor.execute(query, values)
        mydb.commit()

        return redirect('/dashboard')

    else:
        if role == "Operator":
            query = "SELECT school.* FROM school INNER JOIN school_user ON school.School_ID = school_user.School_ID WHERE school_user.User_ID = %s"
            mycursor.execute(query, (user_id,))
            school_data = mycursor.fetchall()
            mycursor.nextset()  
        if role == "Admin":     
            query = "SELECT * FROM school"
            mycursor.execute(query)
            school_data = mycursor.fetchall()
            mycursor.nextset()  
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
        selected_author = request.form.get('selected_author')  
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

    query = " SELECT ba.Author FROM book_author AS ba WHERE ba.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    authors = mycursor.fetchall()

    query = " SELECT bc.Category FROM book_category AS bc WHERE bc.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    categories = mycursor.fetchall()

    query = " SELECT bk.Keyword FROM book_keyword AS bk WHERE bk.Book_ID = %s "
    mycursor.execute(query, (book_id,))
    keywords = mycursor.fetchall()

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

    query = "SELECT book.*, AVG(user_book_review.Stars) AS AvgRating FROM book LEFT JOIN user_book_review ON book.Book_ID = user_book_review.Book_ID WHERE book.Book_ID = %s AND user_book_review.Status = 'Approved'"
    mycursor.execute(query, (book_id,))
    book_info = mycursor.fetchone()

    if request.method == 'POST':
        user_id = session['user_id']
        query = "SELECT * FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
        mycursor.execute(query, (user_id, book_id))
        existing_review = mycursor.fetchone()

        if existing_review:
            stars = int(request.form['stars'])
            comment = request.form['comment']
            if role == "Operator" or role == "Teacher" or role == "Admin":
                update_query = "UPDATE user_book_review SET Stars = %s, Comment = %s, Status = 'Approved' WHERE User_ID = %s AND Book_ID = %s"
                values = (stars, comment, user_id, book_id)
                mycursor.execute(update_query, values)
                mydb.commit()
            if role == "Student":
                update_query = "UPDATE user_book_review SET Stars = %s, Comment = %s, Status = 'Pending' WHERE User_ID = %s AND Book_ID = %s"
                values = (stars, comment, user_id, book_id)
                mycursor.execute(update_query, values)
                mydb.commit()
            
        else:
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
    user_id = session['user_id']
    role = session['role']
    delete_user_id = None  

    if role == "Operator" or role == "Admin":
        delete_user_id = request.form.get('user_id')
        print(delete_user_id)
    else:
        delete_user_id = user_id

    
    query = "SELECT * FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
    mycursor.execute(query, (delete_user_id, book_id))
    review = mycursor.fetchone()

    if review:
        delete_query = "DELETE FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
        mycursor.execute(delete_query, (delete_user_id, book_id))
        mydb.commit()

    return redirect(url_for('reviews', book_id=book_id))


@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    role = session['role']
    if request.method == 'POST':
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

        query = "DELETE FROM book_author WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        for author_name in author_names:
            query = "INSERT INTO book_author (Book_ID, Author) VALUES (%s, %s)"
            mycursor.execute(query, (book_id, author_name))

        query = "DELETE FROM book_category WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        for category_name in category_names:
            query = "INSERT INTO book_category (Book_ID, Category) VALUES (%s, %s)"
            mycursor.execute(query, (book_id, category_name))

        query = "DELETE FROM book_keyword WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        for keyword_name in keyword_names:
            query = "INSERT INTO book_keyword (Book_ID, Keyword) VALUES (%s, %s)"
            mycursor.execute(query, (book_id, keyword_name))

        query = "UPDATE book SET ISBN = %s, Publisher = %s, Total_Page_Number = %s, Summary = %s, Available_Copies = %s, Copies = %s, Language = %s WHERE Book_ID = %s"
        mycursor.execute(query, (isbn, publisher, page_number, summary, available_copies, total_copies, language, book_id))
        mydb.commit()

        return redirect(f"/books/{book_id}")

    else:
        query = "SELECT b.*, s.Name AS SchoolName, AVG(ubr.Stars) AS AvgRating FROM book AS b LEFT JOIN user_book_review AS ubr ON b.Book_ID = ubr.Book_ID LEFT JOIN school AS s ON b.School_ID = s.School_ID WHERE b.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        book_info = mycursor.fetchone()

        query = "SELECT ba.Author FROM book_author AS ba WHERE ba.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        authors = mycursor.fetchall()

        query = "SELECT bc.Category FROM book_category AS bc WHERE bc.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        categories = mycursor.fetchall()

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
    if request.method == 'GET':
        if role == "Operator":
            
            return render_template('OperatorAddBook.html')
        elif role == "Admin":
            query = "SELECT Name FROM school"
            mycursor.execute(query)
            schools = mycursor.fetchall()
            return render_template('AdminAddBookPageTest2.html', schools=schools)
        
    elif request.method == 'POST':
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
            query = "SELECT School_ID FROM school WHERE Name = %s"
            mycursor = mydb.cursor()
            mycursor.execute(query, (library,))
            result = mycursor.fetchone()
            if result is None:
                return "Invalid library name"
            school_id = result[0]
        elif role == "Operator":
            school_id = op_school_id

        mycursor = mydb.cursor()
        query = "INSERT INTO book (Title, ISBN, Publisher, Total_Page_Number, Summary, Available_Copies, Copies, Language, Images, School_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (title, isbn, publisher, page_number, summary, available_copies, total_copies, language, cover, school_id)
        mycursor.execute(query, values)
        book_id = mycursor.lastrowid

        for author in authors:
            query = "INSERT INTO book_author (Author, Book_ID) VALUES (%s, %s)"
            values = (author, book_id)
            mycursor.execute(query, values)

        for category in categories:
            query = "INSERT INTO book_category (Category, Book_ID) VALUES (%s, %s)"
            values = (category, book_id)
            mycursor.execute(query, values)

        for keyword in keywords:
            query = "INSERT INTO book_keyword (Keyword, Book_ID) VALUES (%s, %s)"
            values = (keyword, book_id)
            mycursor.execute(query, values)

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
    
    
@app.route('/users/<int:user_id>/update_profile', methods=['GET', 'POST'])
def user_update_profile(user_id):
    if request.method == 'POST':
        user_role = session['role']
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
            
            if additional_school:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                new_school_id = mycursor.fetchone()[0] 

                query = "SELECT School_ID FROM school_user WHERE User_ID = %s AND School_ID <> %s"
                mycursor.execute(query, (user_id, new_school_id))
                old_school_id = mycursor.fetchone()[0] 

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s and School_ID <> %s"
                mycursor.execute(query, (new_school_id, user_id, old_school_id))
            else:
                query = "SELECT School_ID FROM school WHERE Name = %s"
                mycursor.execute(query, (school_name,))
                school_id = mycursor.fetchone()[0] 

                query = "UPDATE school_user SET School_ID = %s WHERE User_ID = %s"
                mycursor.execute(query, (school_id, user_id,))

        elif role == "Admin" or role == "Student":
            query = "UPDATE user SET Password = %s WHERE User_ID = %s"
            mycursor.execute(query, (password, user_id))

        mydb.commit()

        return redirect('/users')
    else:
        role = session['role']
        query = "SELECT u.*, s1.Name AS FirstSchoolName, s2.Name AS SecondSchoolName FROM user u LEFT JOIN school_user su1 ON u.User_ID = su1.User_ID LEFT JOIN school s1 ON su1.School_ID = s1.School_ID LEFT JOIN school_user su2 ON u.User_ID = su2.User_ID AND su2.School_ID <> su1.School_ID LEFT JOIN school s2 ON su2.School_ID = s2.School_ID WHERE u.User_ID = %s LIMIT 1"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchone()
        if role == "Operator":
            return render_template('OperatorEditOtherProfile1Test1.html', user=user)
        if role == "Admin":
            return render_template('AdminEditOtherProfile1Test1.html', user=user)

@app.route('/users/<int:user_id>/delete_profile', methods=['POST'])    
def delete_profile(user_id):
    delete_school_user_query = "DELETE FROM school_user WHERE User_ID = %s"
    mycursor.execute(delete_school_user_query, (user_id,))

    delete_reviews_query = "DELETE FROM user_book_review WHERE User_ID = %s"
    mycursor.execute(delete_reviews_query, (user_id,))

    delete_applications_query = "DELETE FROM user_book_status WHERE User_ID = %s"
    mycursor.execute(delete_applications_query, (user_id,))

    delete_user_query = "DELETE FROM user WHERE User_ID = %s"
    mycursor.execute(delete_user_query, (user_id,))

    mydb.commit()

    return redirect(url_for('dashboard'))

@app.route('/users/<int:user_id>/deactivate_profile', methods=['POST'])    
def deactivate_profile(user_id):
    query = "UPDATE user SET Status = %s WHERE User_ID = %s"
    mycursor.execute(query, ("Deactivated", user_id))
    mydb.commit()

    return redirect(url_for('dashboard'))

@app.route('/users/<int:user_id>/reactivate_profile', methods=['POST']) 
def reactivate_profile(user_id):
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
    
@app.route('/add_school', methods=['POST', 'GET'])      
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

@app.route('/approve_users', methods=['GET', 'POST'])      
def operator_approve_users():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')

        if action == 'Accept':
            query = "UPDATE user SET Status = 'Approved' WHERE User_ID = %s"
            mycursor.execute(query, (user_id,))
            mydb.commit()
        elif action == 'Deny':
            query = "UPDATE user SET Status = 'Deny' WHERE User_ID = %s"
            mycursor.execute(query, (user_id,))
            mydb.commit()
        
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
            school_name = school_name_result[0][0] if school_name_result else None  
            school_name = school_name.strip("(',)") 


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
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')

        if 'deny' in request.form:
            query = "DELETE FROM user_book_review WHERE User_ID = %s AND Book_ID = %s"
            mycursor.execute(query, (user_id, book_id))
            mydb.commit()
        elif 'approve' in request.form:
            query = "UPDATE user_book_review SET Status = 'Approved' WHERE User_ID = %s AND Book_ID = %s"
            mycursor.execute(query, (user_id, book_id))
            mydb.commit()

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
        SELECT c.School_ID, c.Name AS School_Name, COUNT(*) AS Rental_Count
        FROM user u
        JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        JOIN school c ON c.School_ID = b.School_ID
        WHERE (ubs.Type = 'Rent' OR ubs.Type = 'Returned' OR ubs.Type = 'Late')
        '''

        conditions = []
        values = []

        if selected_school:
            conditions.append("c.School_ID = %s")
            values.append(selected_school)

        if selected_year:
            conditions.append("YEAR(ubs.Start_Date) = %s")
            values.append(selected_year)

        if selected_month:
            conditions.append("MONTH(ubs.Start_Date) = %s")
            values.append(selected_month)

        if conditions:
            query = base_query + " AND " + " AND ".join(conditions)
        else:
            query = base_query

        query += " GROUP BY c.School_ID, c.Name"  # Grouping by School_ID and School_Name

        mycursor.execute(query, tuple(values))
        result = mycursor.fetchall()
        print(query)
    else:
        query = '''
        SELECT c.School_ID, c.Name AS School_Name, COUNT(*) AS Rental_Count
        FROM user u
        JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        JOIN school c ON c.School_ID = b.School_ID
        WHERE (ubs.Type = 'Rent' OR ubs.Type = 'Returned')
        GROUP BY c.School_ID, c.Name
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
    WHERE u.Role = 'Teacher' AND TIMESTAMPDIFF(YEAR, u.Date_of_Birth, CURDATE()) < 40 AND (ubs.Type = 'Rent' OR ubs.Type = 'Returned')
    GROUP BY u.User_ID, u.U_First_Name, u.U_Last_Name, u.Role, Age
    ORDER BY NumRentedBooks DESC, u.U_Last_Name
    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery313Test2.html', result=result)  

@app.route('/query314')
def query314():
    query = '''
        SELECT DISTINCT ba.Author
    FROM book_author ba
    WHERE ba.Author NOT IN (
        SELECT ba.Author
        FROM book_author ba
        JOIN book b ON ba.Book_ID = b.Book_ID
        JOIN user_book_status ubs ON b.Book_ID = ubs.Book_ID
        WHERE ubs.Type IN ('Rent', 'Returned', 'Late')
    )

    '''
    mycursor.execute(query)
    result = mycursor.fetchall()
    return render_template('AdminQuery314.html', result=result) 

@app.route('/query315')
def query315():
    query = '''
    SELECT U_First_Name, U_Last_Name, Name, NumRents
    FROM (
        SELECT o.U_First_Name, o.U_Last_Name, s.Name, COUNT(*) AS NumRents
        FROM user u
        INNER JOIN user_book_status ubs ON ubs.User_ID = u.User_ID
        INNER JOIN book b ON b.Book_ID = ubs.Book_ID
        INNER JOIN school_user su ON su.School_ID = b.School_ID
        INNER JOIN school s ON su.School_ID = s.School_ID
        INNER JOIN user o ON o.User_ID = su.User_ID AND o.Role = 'Operator'
        WHERE ubs.Type IN ('Rent', 'Returned', 'Late')
            AND ubs.Start_Date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
        GROUP BY o.User_ID, o.U_First_Name, o.U_Last_Name, s.Name
        HAVING COUNT(*) > 20
    ) AS operators
    WHERE NumRents = (
        SELECT NumRents
        FROM (
            SELECT o.U_First_Name, o.U_Last_Name, s.Name, COUNT(*) AS NumRents
            FROM user u
            INNER JOIN user_book_status ubs ON ubs.User_ID = u.User_ID
            INNER JOIN book b ON b.Book_ID = ubs.Book_ID
            INNER JOIN school_user su ON su.School_ID = b.School_ID
            INNER JOIN school s ON su.School_ID = s.School_ID
            INNER JOIN user o ON o.User_ID = su.User_ID AND o.Role = 'Operator'
            WHERE ubs.Type IN ('Rent', 'Returned', 'Late')
                AND ubs.Start_Date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY o.User_ID, o.U_First_Name, o.U_Last_Name, s.Name
            HAVING COUNT(*) > 20
        ) AS rents
        GROUP BY NumRents
        HAVING COUNT(*) > 1
    )
    ORDER BY U_First_Name;

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

@app.route('/query321', methods=['GET', 'POST'])
def query321():
    user_id = session['user_id']
    
    query = '''
        SELECT DISTINCT bc.Category 
        FROM book AS b 
        INNER JOIN book_category AS bc ON b.Book_ID = bc.Book_ID 
        WHERE b.School_ID IN (SELECT School_ID FROM school_user WHERE User_ID = %s)
    '''
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

    values = []  # Define an empty list for values

    if request.method == 'POST':
        search_title = request.form.get('search_title')
        selected_category = request.form.get('selected_category')
        selected_author = request.form.get('selected_author')  
        selected_language = request.form.get('selected_language')
        copies = request.form.get('copies')

        base_query = '''
        SELECT DISTINCT b.Title, GROUP_CONCAT(DISTINCT ba.Author) AS Authors, GROUP_CONCAT(DISTINCT bc.Category) AS Categories, b.Copies
        FROM book b
        LEFT JOIN book_author ba ON b.Book_ID = ba.Book_ID
        LEFT JOIN book_category bc ON b.Book_ID = bc.Book_ID
        WHERE b.School_ID IN (SELECT School_ID FROM school_user WHERE User_ID = %s)
        '''

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

        if copies:
            conditions.append("b.Copies = %s")
            values.append(copies)

        if conditions:
            query = base_query + " AND " + " AND ".join(conditions) + " GROUP BY b.Book_ID, b.Copies"
        else:
            query = base_query + " GROUP BY b.Book_ID, b.Copies"

        mycursor.execute(query, tuple([user_id] + values))
        result = mycursor.fetchall()
    else:
        query = '''
        SELECT DISTINCT b.Title, GROUP_CONCAT(DISTINCT ba.Author) AS Authors, GROUP_CONCAT(DISTINCT bc.Category) AS Categories, b.Copies
        FROM book b
        LEFT JOIN book_author ba ON b.Book_ID = ba.Book_ID
        LEFT JOIN book_category bc ON b.Book_ID = bc.Book_ID
        WHERE b.School_ID IN (SELECT School_ID FROM school_user WHERE User_ID = %s)
        GROUP BY b.Book_ID, b.Copies
        '''
        mycursor.execute(query, (user_id,))
        result = mycursor.fetchall()

    return render_template('OperatorQuery321.html', result=result, categories=categories, authors=authors)


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

@app.route('/query323select', methods=['GET'])
def query312select():
    query = "SELECT DISTINCT Category FROM book_category"
    mycursor.execute(query)
    categories = mycursor.fetchall()
    return render_template('OperatorQuery323select.html', categories=categories) 

@app.route('/query323')
def query323():
    user_id = session['user_id']
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    category = request.args.get('category')
    category = category.strip("(',)")
    print(category)

    query1 = '''
    SELECT u.User_ID, u.U_First_Name, u.U_Last_Name, AVG(ubr.Stars) AS AvgUserRating
    FROM user u
    INNER JOIN user_book_status ubs ON u.User_ID = ubs.User_ID
    INNER JOIN user_book_review ubr ON ubs.User_ID = ubr.User_ID AND ubs.Book_ID = ubr.Book_ID
    INNER JOIN school_user su ON u.User_ID = su.User_ID
    INNER JOIN book b ON ubs.Book_ID = b.Book_ID
    INNER JOIN book_category bc ON b.Book_ID = bc.Book_ID
    WHERE su.school_id = (SELECT school_id FROM school_user WHERE User_ID = %s)
    '''

    query1_params = [user_id]

    if first_name and last_name:
        query1 += ' AND u.U_First_Name = %s AND u.U_Last_Name = %s'
        query1_params.extend([first_name, last_name])

    if category:
        query1 += ' AND bc.Category = %s'
        query1_params.append(category)

    query1 += '''
        AND ubs.Type IN ('Rent', 'Returned', 'Late')
    GROUP BY u.User_ID, u.U_First_Name, u.U_Last_Name;
    '''

    mycursor.execute(query1, query1_params)
    result1 = mycursor.fetchall()

    query2 = '''
    SELECT bc.Category, AVG(ubr.Stars) AS AvgCategoryRating
    FROM book_category bc
    INNER JOIN book b ON bc.Book_ID = b.Book_ID
    INNER JOIN user_book_review ubr ON b.Book_ID = ubr.Book_ID
    INNER JOIN user u ON u.User_ID = ubr.User_ID
    INNER JOIN school_user su ON u.User_ID = su.User_ID
    WHERE su.school_id = (SELECT school_id FROM school_user WHERE User_ID = %s)
    '''

    query2_params = [user_id]

    if category:
        query2 += ' AND bc.Category = %s'
        query2_params.append(category)

    query2 += ' GROUP BY bc.Category'

    mycursor.execute(query2, query2_params)
    result2 = mycursor.fetchall()

    return render_template('OperatorQuery323.html', result1=result1, result2=result2)

@app.route('/books/<int:book_id>/make_application', methods=['GET', 'POST'])
def make_application(book_id):
    role = session['role']
    user_id = session['user_id']
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_date = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        available_copies = request.form['available_copies']
        try:
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

            return redirect("/dashboard")
        except mysql.connector.Error as error:
            flash(str(error))
            return redirect("/books/" + str(book_id) + "/make_application")

    else:
        query = "SELECT * FROM book WHERE Book_ID = %s"
        mycursor.execute(query, (book_id,))
        book_info = mycursor.fetchone()

        query = "SELECT ba.Author FROM book_author AS ba WHERE ba.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        authors = mycursor.fetchall()

        query = "SELECT bc.Category FROM book_category AS bc WHERE bc.Book_ID = %s"
        mycursor.execute(query, (book_id,))
        categories = mycursor.fetchall()

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
        book_id = request.form['book_id']
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check the status of the pressed cancel application
        query_status = "SELECT Type FROM user_book_status WHERE Status_ID = %s"
        mycursor.execute(query_status, (status_id,))
        status = mycursor.fetchone()[0]
        
        if status == 'Application':
            # If the status is 'Application', check for waiting applications
            query_waiting = """SELECT Status_ID
                            FROM user_book_status
                            WHERE Book_ID = %s
                            AND Type = 'Waiting'
                            ORDER BY Start_Date ASC
                            LIMIT 1"""
            mycursor.execute(query_waiting, (book_id,))
            waiting = mycursor.fetchone()
            
            if waiting:
                wait_status_id = waiting[0]
                query_update_waiting = "UPDATE user_book_status SET Type = 'Application' WHERE Status_ID = %s"
                mycursor.execute(query_update_waiting, (wait_status_id,))
                mydb.commit()
            else:
                query_update_cancel = "UPDATE user_book_status SET Type = 'Cancelled', End_Date = %s WHERE Status_ID = %s "
                mycursor.execute(query_update_cancel, (end_date, status_id,))
                mydb.commit()
                query_update_book = "UPDATE book SET Available_Copies = Available_Copies + 1 WHERE Book_ID = %s"
                mycursor.execute(query_update_book, (book_id,))
                mydb.commit()
        else:
            # If the status is not 'Application', update it to 'Cancelled'
            query_update_cancel = "UPDATE user_book_status SET Type = 'Cancelled', End_Date = %s WHERE Status_ID = %s "
            mycursor.execute(query_update_cancel, (end_date, status_id,))
            mydb.commit()

        return redirect("/applications")
    else:       
        query = """SELECT u.U_First_Name, u.U_Last_Name, b.Title AS Book_Title, ubs.*
        FROM user_book_status ubs
        JOIN user u ON ubs.User_ID = u.User_ID
        JOIN book b ON ubs.Book_ID = b.Book_ID
        WHERE ubs.Type = %s AND ubs.User_ID = %s
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
        user_id = request.form.get('user')
        book_id = request.form.get('book_title')

        try:
            query = "INSERT INTO user_book_status (User_ID, Book_ID, Start_Date, End_Date, Type) VALUES (%s, %s, %s, %s, %s)"
            values = (user_id, book_id, current_date, end_date, "Rent")
            mycursor.execute(query, values)
            mydb.commit()

            query = "UPDATE book SET Available_Copies = Available_Copies - 1 WHERE Book_ID = %s"
            mycursor.execute(query, (book_id,))
            mydb.commit()

            return redirect("/dashboard")
        except mysql.connector.Error as error:
            error_message = str(error)
            flash(error_message)
            return redirect(request.url)  
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
        

        mycursor = mydb.cursor()
        update_query = "UPDATE user_book_status SET Type = %s, Start_Date = %s, End_Date = %s WHERE Status_ID = %s"
        mycursor.execute(update_query, (application_type, current_date, end_date, status_id))
        mydb.commit()
        if action == "deny":
            query = "UPDATE book SET Available_Copies = Available_Copies + 1 WHERE Book_ID = %s"
            mycursor.execute(query, (book_id,))
            mydb.commit()

        return redirect("/operator_approve_applications")

    else:
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
    host = 'localhost'
    user = 'root'
    password = ''
    database = 'LibraryDatabase5'

    backup_dir = r'C:\Users\voudo\Documents\codes\DatabaseLibrary\DatabaseBackups'

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    backup_file = f'backup_{timestamp}.sql'

    backup_file_path = os.path.join(backup_dir, backup_file)

    mysqldump_cmd = f'mysqldump -u {user} --password="" -h {host} {database} > {backup_file_path}'


    try:
        os.system(mysqldump_cmd)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'message': f'Failed to create backup: {str(e)}'}), 500


@app.route('/restore', methods=['GET'])
def restore_backup():
    backup_dir = r'C:\Users\voudo\Documents\codes\DatabaseLibrary\DatabaseBackups'

    backup_files = glob.glob(os.path.join(backup_dir, 'backup_*.sql'))

    return render_template('AdminRestoreSelect.html', backup_files=backup_files)


@app.route('/restore', methods=['POST'])
def restore_backup_post():
    selected_file = request.form.get('backup_file')

    host = 'localhost'
    user = 'root'
    password = ''
    database = 'LibraryDatabase5'

    backup_dir = r'C:\Users\voudo\Documents\codes\DatabaseLibrary\DatabaseBackups'

    backup_file_path = os.path.join(backup_dir, selected_file)

    mysql_cmd = f'mysql -u {user} -p{password} -h {host} {database} < {backup_file_path}'

    try:
        os.system(mysql_cmd)
        return jsonify({'message': 'Database restored successfully'})
    except Exception as e:
        return jsonify({'message': f'Failed to restore database: {str(e)}'}), 500