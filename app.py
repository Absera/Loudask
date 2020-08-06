from flask import render_template, Flask, redirect, url_for, request, flash, session
import mysql.connector
from datetime import timedelta, time
import datetime


# Flask app generated
app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.permanent_session_lifetime = timedelta(days=15)

# MYSQL database connection
database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="mydb"
)
database_cursor = database.cursor()


# Routes
# Registration route
@app.route("/register")
def registerPage():
    if "email_or_phone_login" in session:
        session.pop("email_or_phone_login", None) # clears the session , if there is any      
    return render_template('register.html')


@app.route("/register", methods=['POST', 'GET'])
def registerAction():

    if request.method == "POST":
        username = request.form.get("username-text")
        email_or_phone = request.form.get("email-or-phone-text")
        password = request.form.get("password-text")
        password_confirm = request.form.get("password-confirm-text")

        if username != "" and email_or_phone != "" and password != "" and password_confirm != "":
            if password == password_confirm:
                try:
                    database_command = "INSERT INTO users (name, email_or_phone, password) VALUES (%s, %s, %s)"
                    data_values = (username, email_or_phone, password)
                    database_cursor.execute(database_command, data_values)
                    database.commit()

                    return redirect(url_for('loginPage'))
                except:
                    return render_template('register.html')
            else:
                flash("Password confirmation error!", "Error")
                return render_template('register.html') # If there is password confirmation error
        else:
            flash("No blank spaces!", "Error")
            return render_template("register.html") # If there is blank left space


# Login route
@app.route("/")
def loginPage():
    if "email_or_phone_login" in session:
        return redirect(url_for("home"))
    else:
        return render_template("login.html")


@app.route("/", methods=['POST', 'GET'])
def loginAction():
    if request.method == "POST":

        session.permanent = True
        email_or_phone_login = request.form.get("email-or-phone-login")
        session["email_or_phone_login"] = email_or_phone_login

        password_login = request.form.get("password-login")

        database_command = "SELECT password FROM users WHERE email_or_phone = %s "
        data_value = (email_or_phone_login,)
        database_cursor.execute(database_command, data_value) 
        passwordLoaded = database_cursor.fetchall()

        database_command_for_username = "SELECT name FROM users WHERE email_or_phone = %s "
        data_value_for_username = (email_or_phone_login,)
        database_cursor.execute(database_command_for_username, data_value_for_username)
        nameLoaded = database_cursor.fetchall()
        try:
            nameLoaded = nameLoaded[0][0] # name of the user changed from list to single string
        except:
            pass # i can also flash() somthing like 'Error occured'

        try:
            passwordLoaded = passwordLoaded[0][0] # password of the user changed to single string
        except:
            pass # i can also flash() somthing like Error occured

        try:
            if email_or_phone_login != "" and password_login != "":
                if password_login == passwordLoaded:
                    return redirect(url_for('home'))
                else:
                    flash("Incorrect password!", "Error")
                    return render_template("login.html")
            else:
                flash("No blank spaces!", "Error")
                return render_template("login.html")
        except:
            return render_template("login.html") # if any error occurs in the above code
        return render_template("login.html") 

# Logout route
@app.route("/logout")
def logout():
    session.pop("email_or_phone_login", None) # clears the session
    return redirect(url_for("loginPage")) # redirect to the login page


# Questions route # adding questions
@app.route("/questions")
def postQuestionPage():
    if "email_or_phone_login" in session:
        return render_template('add_question.html')
    else:
        return(redirect(url_for("home")))

    return False

@app.route("/questions", methods=['POST', 'GET'])
def postQuestionAction():
    if request.method == "POST":
        email_or_phone_after_login = session["email_or_phone_login"] # the email or phone number of the user once after logged in
        post_title = request.form.get("select")
        post_content = request.form.get("post-content")
        timeNow = datetime.datetime.now()

        if post_title != "None" and post_content != "":
            db_command = "SELECT id FROM users WHERE email_or_phone = %s"
            db_value = (email_or_phone_after_login,)
            database_cursor.execute(db_command, db_value)
            userIdWhoPostQuestion = database_cursor.fetchall()[0][0]


            database_command_posting = "INSERT INTO posts (user_id, post_title, post_content, post_time) VALUES (%s, %s, %s, %s)"
            data_values_posting = (userIdWhoPostQuestion, post_title, post_content, timeNow)
            database_cursor.execute(database_command_posting, data_values_posting)                
            database.commit()            
            return redirect(url_for("home"))
        else:
            flash("Please select a topic and Enter your question", "Error")

    return render_template('add_question.html')
       
@app.route("/myquestions", methods=['GET', 'POST'])
def showMyQuestions():
    if "email_or_phone_login" in session:
        email_or_phone = session["email_or_phone_login"]  

        database_command  = "SELECT id FROM users WHERE email_or_phone = %s"
        database_value = (email_or_phone, )  
        database_cursor.execute(database_command, database_value)
        try:
            user_id_who_post_this_question = database_cursor.fetchall()[0][0] # to get out the id from the list
        except:
            pass

        db_command = "SELECT * FROM posts WHERE user_id  = %s "
        db_value = (user_id_who_post_this_question, )
        database_cursor.execute(db_command, db_value)
        allMyQuestions = database_cursor.fetchall()

        for myQuestion in allMyQuestions:
            myQuestion_id_ = myQuestion[0]
            myQuestion_user_id_ = myQuestion[1]
            myQuestion_title_ = myQuestion[2]
            myQuestion_content_ = myQuestion[3]
            myQuestion_time_ = myQuestion[4]

            aQuestion = (myQuestion_title_, myQuestion_content_, myQuestion_time_)
            flash(aQuestion)   
    else:
        pass # i can flash his somthing like 'login first to see your question' 
    return render_template('my_questions.html')


@app.route("/answer")
def answerPage():
    if "email_or_phone_login" in session:
        return render_template("add_answer.html")
    else:
        return(redirect(url_for("home")))

    return False
    

@app.route("/answer", methods=['GET', 'POST'])
def answerAction():

    IdOfSelectedQuestion = session["post_id_session"]
    answer_content = request.form.get("answer_content")
    timeNow = datetime.datetime.now()

    if IdOfSelectedQuestion != "":
        if answer_content != "":
            database_command = "INSERT INTO answers (post_id, answer_content, time) VALUES (%s, %s, %s)"
            data_values = (IdOfSelectedQuestion, answer_content, timeNow)
            database_cursor.execute(database_command, data_values)
            database.commit()

            #flash("Answer posted succesfully!")
            return redirect(url_for("showAnswers"))
        else:
            pass #flash("What about your answer!")
    else:
        pass #flash("Make sure you have selected a question!")


    return render_template("add_answer.html") 

@app.route("/showAnswers")
def showAnswers():

    # displaying the selected question on the top
    post_id = session["post_id_session"]
    database_command = "SELECT * FROM posts WHERE post_id = %s"
    database_value = (post_id, )
    database_cursor.execute(database_command, database_value)
    post = database_cursor.fetchall()

            

    dbcmd = "SELECT COUNT(answer_id) FROM answers WHERE post_id =%s" #to count number of answer_id by their post_id
    dbvl = (session["post_id_session"], )
    database_cursor.execute(dbcmd, dbvl)
    try:
        allAnswerIds = database_cursor.fetchall()[0][0]
    except:
        pass
    session["numberOfAnswers"] = int(allAnswerIds)

            

    # displayin the answers added by another users
    post_id = session["post_id_session"]
    database_command = "SELECT * FROM answers WHERE post_id = %s ORDER BY answer_id DESC"
    database_value = (post_id, )
    database_cursor.execute(database_command, database_value)
    allAnswers = database_cursor.fetchall()

    for Answer in allAnswers:
        post_id_ = Answer[0]
        answer_id_ = Answer[1]
        answer_content_ = Answer[2]
        answer_time_ = Answer[3]

        anAnswer = (post_id_, answer_id_, answer_content_, answer_time_)
        
        if session["post_id_session"]:
            flash(anAnswer)
        else:
            return "Select question first!"
    return render_template("show_answers.html", post_id=post_id, numberOfAnswers=session["numberOfAnswers"], postIdOfSelectedQuestion=session["post_id_session"])    
    
    
@app.route("/help")
def help():
    return render_template("help.html")


# Index webpage
@app.route("/index", methods=['GET', 'POST'])
def home():         
    db_command = "SELECT * FROM posts ORDER BY post_id DESC"
    database_cursor.execute(db_command)
    allPostsInDatabase = database_cursor.fetchall()
    
    for post in allPostsInDatabase:
        post_id_ = post[0] # First index, post ID
        user_id_ = post[1] # Second index
        post_title_ = post[2] # post title
        post_content_ = post[3] # Main message, question
        post_time_ = post[4] # Post time
        
        aPost = (post_title_, post_content_, post_time_, post_id_)
        if "email_or_phone_login" in session:
            session["post_id"] = aPost[3]
            flash(aPost)

    else:
        pass # i can also flash here somthing like 'there are no posts s far'

    if "email_or_phone_login" in session:
        email_or_phone = session["email_or_phone_login"]

        database_command = "SELECT name FROM users WHERE email_or_phone = %s"
        database_value = (email_or_phone, )
        database_cursor.execute(database_command, database_value)
        username_after_login = database_cursor.fetchall()
        

    else:
        return redirect(url_for("loginPage"))

    # this is an ID of a post which a user clicked the answer button on 
    post_id_session = request.form.get("select-btn")
    session["post_id_session"] = post_id_session

    return render_template('index.html', postIdOfSelectedQuestion=session["post_id_session"])



# # Run
if __name__ == "__main__":
    app.run()
