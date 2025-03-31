import sqlite3
from werkzeug.security import generate_password_hash
from users import Student, Teacher
from quiz import Question, Quiz
from datetime import datetime
from sqlFunctions import getConnection


def selectUser(username):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    if user and user[3] == "teacher":
        return Teacher(user[0], user[1], user[2], user[3])
    return user


def getTeacherInfo(username):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT teachers.tid, users.username, users.email, users.password FROM users JOIN teachers on users.id = teachers.user_id WHERE users.username = ?",
        (username,),
    )
    teacher_data = cursor.fetchone()
    connection.close()

    if teacher_data:
        return Teacher(*teacher_data)
    return None


def insertUser(username, email, password, role):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        hashed_password = password
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?,?,?,?)",
            (username, email, hashed_password, role),
        )

        user_id = cursor.lastrowid
        if role == "student":
            sid = generate_id("student")
            cursor.execute(
                "INSERT INTO students (sid, user_id) VALUES (?,?)", (sid, user_id)
            )
        else:
            tid = generate_id("teacher")
            cursor.execute(
                "INSERT INTO teachers (tid, user_id) VALUES (?,?)", (tid, user_id)
            )
        connection.commit()
        print(f"✅ User {username} ({role}) created successfully!")
    except sqlite3.Error as error:
        print(f"An error occured in function insertUser: {error}")
        connection.rollback()
    finally:
        connection.close()
    
    return


def updateUser():
    try:
        connection = getConnection()
        cursor = connection.cursor()

        connection.commit()
    except sqlite3.Error as error:
        print(f"An error occured in function updateUser: {error}")
        connection.rollback()
    finally:
        connection.close()
    return


def deleteUser(username):
    return


# Στοχος να δημιουργηθει το sid ή tid αναλογα με τον ρολο του χρηστη, π.χ. st2501, αν ο χρηστης ειναι student, γραφτηκε το 2025 και ειναι ο πρωτος στη λιστα που γραφτηκε
def generate_id(role):
    conn = getConnection()
    cursor = conn.cursor()

    year_suffix = datetime.now().year % 100
    prefix = "st" if role == "student" else "te"

    cursor.execute(f"SELECT COUNT(*) FROM {role}s")
    count = cursor.fetchone()[0] + 1

    conn.close()
    return f"{prefix}{year_suffix}{count:02d}"


def insertQuiz(quiz: Quiz, teacher: Teacher):
    title = quiz.getTitle()
    time = quiz.getTime()
    desc = quiz.getDescription()

    tid = teacher.getTid()

    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO quiz (title, description, time_limit, created_by) VALUES (?, ?, ?, ?)",
            (title, desc, time, teacher.getTid()),
        )

        quiz_id = cursor.lastrowid  # για να παρουμε το τελευταιο id
        connection.commit()
    except sqlite3.Error as error:
        print(f"An error occured in function insertQuiz: {error}")
        connection.rollback()
    finally:
        connection.close()

    return quiz_id


def insertQuestion(quiz_id, question: Question):
    qNum = question.getQuestionNum()
    qText = question.getQuestionText()
    print(f"Here is again the qTxt inside insertQuestion: {qText}")
    option1 = question.getOption1()
    option2 = question.getOption2()
    option3 = question.getOption3()
    option4 = question.getOption4()
    correctAnswer = question.getCorrectAnswer()

    try:
        conn = getConnection()
        cursor = conn.cursor()

        print(
            f"DEBUG: quiz_id={quiz_id}, qNum={qNum}, qText={qText}, option1={option1}, option2={option2}, option3={option3}, option4={option4}, correctAnswer={correctAnswer}"
        )

        cursor.execute(
            "INSERT INTO questions (quiz_id, question_num, question_text, option_1, option_2, option_3, option_4, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (quiz_id, qNum, qText, option1, option2, option3, option4, correctAnswer),
        )
        conn.commit()
    except sqlite3.Error as error:
        print(f"An error occured in function insertQuestion: {error}")
        conn.rollback()
    finally:
        conn.close()


def getQuizById(quiz_id):
    connection = sqlite3.connect("eduplay.db")
    connection.row_factory = (
        sqlite3.Row
    )  # Μετατρέπει τα αποτελέσματα σε dictionary-like αντικείμενα
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM quiz WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    connection.close()

    return dict(quiz) if quiz else None  # Μετατρέπει σε dictionary αν υπάρχει


# get quizzes created by teacher id
def getQuizzesByTeacher(tid):
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT quiz.id, quiz.title, quiz.created_at, COUNT(questions.id) as numOfQuestions 
        FROM quiz 
        LEFT JOIN questions ON quiz.id = questions.quiz_id 
        WHERE quiz.created_by = ? 
        GROUP BY quiz.id
        """,
        (tid,),
    )

    quizzes = cursor.fetchall()
    connection.close()

    return [dict(quiz) for quiz in quizzes]  # Μετατροπή κάθε Row σε dictionary


# get quizzes by quiz_id
def getQuestionsBy(quiz_id):
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", ((quiz_id,)))
    questions = cursor.fetchall()
    connection.close()
    return [dict(q) for q in questions]


# delete quiz and its questions
def deleteQuizzes(quiz_ids):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM quiz WHERE id = ?", ((quiz_ids,)))
        connection.commit()
    except sqlite3.Error as error:
        print(f"An error occured in function deleteQuizzes: {error}")
        connection.rollback()
    finally:
        connection.close()
    return


def quickEditQuiz(quiz_id, title, description, time_limit):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE quiz SET title = ?, description = ?, time_limit = ? WHERE id = ?",
            (title, description, time_limit, quiz_id),
        )
        connection.commit()
        print("Quiz updated successfully!")
    except sqlite3.Error as error:
        print(f"An error occured {error}")
    finally:
        connection.close()
    return
