import sqlite3, traceback
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


def getStudentInfo(username):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT students.sid FROM users JOIN students on users.id = students.user_id WHERE users.username = ?",
            (username,),
        )
        student_info = cursor.fetchone()
        return student_info
    except sqlite3.Error as error:
        print(f"An error occured in function getStudentInfo: {error}")
    finally:
        connection.close()
    return 0


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


def updateUser(old_username, username, email, password):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        update_query = (
            "UPDATE users SET username = ?, email = ?, password = ? WHERE username = ?;"
        )
        # Εκτέλεση της εντολής με τα δεδομένα που στείλαμε
        cursor.execute(update_query, (username, email, password, old_username))
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
    lesson = quiz.getLesson()

    tid = teacher.getTid()

    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO quiz (title, lesson, created_by) VALUES (?, ?, ?)",
            (title, lesson, tid),
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
    qType = question.getQuestionType()

    print(f"QType is {qType}")
    # Getting the options (for multiple choice questions)
    if qType == "multiple_choice":
        options = question.getOptions()
        option1 = options.get("option1")
        option2 = options.get("option2")
        option3 = options.get("option3")
        option4 = options.get("option4")
    else:
        option1 = None
        option2 = None
        option3 = None
        option4 = None

    # Get the correct answer for all question types
    correctAnswer = question.getCorrectAnswer()

    # For matching questions, get the matching items if available
    matchingItems = question.getMatchingItems() if qType == "matching" else None

    try:
        conn = getConnection()
        cursor = conn.cursor()

        # Debugging output for all the parameters
        print(
            f"DEBUG: quiz_id={quiz_id}, qNum={qNum}, qText={qText}, qType={qType}, "
            f"option1={option1}, option2={option2}, option3={option3}, option4={option4}, "
            f"correctAnswer={correctAnswer}, matchingItems={matchingItems}"
        )

        # If it's a matching question, don't insert a correct answer (set it to NULL)
        if qType == "matching":
            correctAnswer = None

        # Insert the question into the database
        cursor.execute(
            """
            INSERT INTO questions (quiz_id, question_num, question_text, question_type, option_1, option_2, option_3, option_4, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quiz_id,
                qNum,
                qText,
                qType,
                option1,
                option2,
                option3,
                option4,
                correctAnswer,
            ),
        )

        question_id = cursor.lastrowid
        conn.commit()

        if qType == "matching" and matchingItems:
            print(f"DEBUG: Inserting matching items for question_id {question_id}")
            for i in range(0, len(matchingItems), 2):
                print(
                    f"DEBUG: Matching items: {matchingItems[i]}, {matchingItems[i + 1]}"
                )
                item_1 = matchingItems[i]
                item_2 = matchingItems[i + 1]
                cursor.execute(
                    "INSERT INTO matching (question_id, item_1, item_2) VALUES (?, ?, ?)",
                    (question_id, item_1, item_2),
                )
            conn.commit()

    except sqlite3.Error as error:
        print(f"An error occurred in function insertQuestion: {error}")
        print(f"Traceback: {traceback.format_exc()}")
        conn.rollback()
    finally:
        conn.close()


def createNotification(message, username, target_role, quiz_id, quiz_creator=None):
    try:
        connection = getConnection()
        cursor = connection.cursor()

        # Ανάκτηση του user_id για τον χρήστη που δημιουργεί την ειδοποίηση (π.χ. ο καθηγητής ή ο μαθητής)
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        uid = cursor.fetchone()

        if uid is None:
            print(f"User with username {username} not found.")
            return

        user_id = uid[0]
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Δημιουργία ειδοποίησης στον πίνακα 'notifications'
        cursor.execute(
            "INSERT INTO notifications (message, type, quiz_id, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
            (message, "quiz_notification", quiz_id, created_at, user_id),
        )
        notification_id = cursor.lastrowid

        # Αν target_role είναι "student", στέλνουμε την ειδοποίηση σε όλους τους μαθητές
        if target_role == "student":
            cursor.execute(
                """
                SELECT students.sid
                FROM users
                JOIN students ON users.id = students.user_id
                WHERE users.role = 'student'
                """,
            )

            student_ids = cursor.fetchall()
            for student_id in student_ids:
                cursor.execute(
                    "INSERT INTO notification_seen (user_type, user_id, notification_id, seen) VALUES (?, ?, ?, ?)",
                    ("student", student_id[0], notification_id, 0),
                )

        # Αν target_role είναι "teacher" στέλνουμε ειδοποίηση στον καθηγητή.
        elif target_role == "teacher" and quiz_creator is not None:
            cursor.execute("SELECT id FROM users WHERE username = ?", (quiz_creator,))
            creator_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO notification_seen (user_type, user_id, notification_id, seen) VALUES (?, ?, ?, ?)",
                ("teacher", creator_id, notification_id, 0),
            )

        connection.commit()

    except sqlite3.Error as error:
        print(f"An error occurred in function createNotification: {error}")
        connection.rollback()
    finally:
        connection.close()


def getNotification(user_id):
    try:
        connection = getConnection()
        cursor = connection.cursor()

        # Φιλτράρουμε για ειδοποιήσεις που δεν έχουν δει οι χρήστες
        cursor.execute(
            """
            SELECT notifications.*, notification_seen.seen 
            FROM notifications
            JOIN notification_seen 
            ON notifications.id = notification_seen.notification_id
            WHERE notification_seen.user_id = ? AND notification_seen.seen = 0
            """,
            (user_id,),
        )

        notification_data = cursor.fetchall()

        return notification_data
    except sqlite3.Error as error:
        print(f"An error occurred in function getNotification: {error}")
    finally:
        connection.close()


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


def getQuizByTitle(quiz_title):
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM quiz WHERE title = ?", ((quiz_title,)))
    quiz = cursor.fetchall()
    connection.close()
    return quiz


# get quizzes created by teacher id
def getQuizzesByTeacher(tid):
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT quiz.id, quiz.title, quiz.lesson, quiz.created_at, COUNT(questions.id) as numOfQuestions 
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


def getLatestQuizzesByTeacher(tid):
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT quiz.id, quiz.title, quiz.lesson, quiz.created_at, COUNT(questions.id) as numOfQuestions
        FROM quiz
        LEFT JOIN questions ON quiz.id = questions.quiz_id
        WHERE quiz.created_by = ?
        GROUP BY quiz.id
        ORDER BY quiz.created_at DESC
        LIMIT 3
        """,
        (tid,),
    )

    quizzes = cursor.fetchall()
    connection.close()

    return [dict(quiz) for quiz in quizzes]


# get quizzes by quiz_id
def getQuestionsBy(quiz_id):
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", ((quiz_id,)))
    questions = cursor.fetchall()
    connection.close()
    return [dict(q) for q in questions]


def deleteQuizzes(quiz_ids):
    try:
        connection = getConnection()
        cursor = connection.cursor()

        placeholders = ",".join("?" for _ in quiz_ids)
        cursor.execute(f"DELETE FROM quiz WHERE id IN ({placeholders})", quiz_ids)
        connection.commit()

    except sqlite3.Error as error:
        print(f"An error occurred in function deleteQuizzes: {error}")
        connection.rollback()
    finally:
        connection.close()
    return


def deleteQuestionById(question_id):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
    except Exception as e:
        print("Error deleting question:", e)
        conn.rollback()
    finally:
        conn.close()


def quickEditQuiz(quiz_id, title, lesson):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE quiz SET title = ?, lesson = ? WHERE id = ?",
            (title, lesson, quiz_id),
        )
        connection.commit()
        print("Quiz updated successfully!")
    except sqlite3.Error as error:
        print(f"An error occured: {error}")
    finally:
        connection.close()
    return


def getAllQuizzesByID(tid):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT teachers.tid, COUNT(*) FROM quiz JOIN teachers ON teachers.tid=quiz.created_by WHERE created_by=?",
            (tid,),
        )
        result = cursor.fetchone()
        return result[1] if result else 0
    except sqlite3.Error as error:
        print(f"An error occured: {error}")
    finally:
        connection.close()
    return 0


def getMatchingItems(question_id):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT item_1, item_2 FROM matching WHERE question_id = ?", (question_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [item for pair in rows for item in pair]  # flat list


# Update Quiz function
def updateQuiz(quiz_id, title, lesson):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE quiz
            SET title = ?, lesson = ?
            WHERE id = ?
        """,
            (title, lesson, quiz_id),
        )
        conn.commit()
    except Exception as e:
        print("Error updating quiz:", e)
        conn.rollback()
        raise
    finally:
        conn.close()


# Update Question function
def updateQuestion(
    question_id,
    text,
    qtype,
    option1=None,
    option2=None,
    option3=None,
    option4=None,
    correctAnswer=None,
):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE questions
            SET question_text = ?, question_type = ?, option_1 = ?, option_2 = ?, option_3 = ?, option_4 = ?, correct_answer = ?
            WHERE id = ?
        """,
            (
                text,
                qtype,
                option1,
                option2,
                option3,
                option4,
                correctAnswer,
                question_id,
            ),
        )
        conn.commit()
    except Exception as e:
        print("Error updating question:", e)
        conn.rollback()
        raise
    finally:
        conn.close()


# Update Matching function
def replaceMatchingPairs(question_id, matching_items):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        # Διαγραφή παλιών
        cursor.execute("DELETE FROM matching WHERE question_id = ?", (question_id,))

        # Προσθήκη νέων (ανα 2)
        for i in range(0, len(matching_items), 2):
            item_1 = matching_items[i]
            item_2 = matching_items[i + 1]
            cursor.execute(
                """
                INSERT INTO matching (question_id, item_1, item_2)
                VALUES (?, ?, ?)
            """,
                (question_id, item_1, item_2),
            )

        conn.commit()
    except Exception as e:
        print("Error replacing matching pairs:", e)
        conn.rollback()
        raise
    finally:
        conn.close()


# Daily Spins
def getDailySpins(sid, date):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM daily_spin WHERE sid = ? AND spin_date = ?
        """,
        (sid, date),
    )
    result = cursor.fetchone()
    connection.close()
    return result


# Insert Daily Spins
def insertDailySpins(sid, date, bonus):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO daily_spin (sid, spin_date, bonus) VALUES (?, ?, ?)
        """,
        (sid, date, bonus),
    )
    connection.commit()
    connection.close()


# Active Bonus
def insertActiveBonus(sid, bonus, starts_at, expires_at):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO active_bonus (sid, bonus, start_date, end_date) VALUES (?, ?, ?, ?)
        """,
        (sid, bonus, starts_at, expires_at),
    )
    connection.commit()
    connection.close()


# Get Active Bonus
def getActiveBonuses(sid):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT bonus, end_date FROM active_bonus
        WHERE sid = ? AND end_date > CURRENT_TIMESTAMP
        ORDER BY end_date ASC
        """,
        (sid,),
    )
    results = cursor.fetchall()
    connection.close()

    bonuses = []
    for bonus_type, expires in results:
        expires_dt = datetime.fromisoformat(expires)
        formatted = expires_dt.strftime('%d/%m/%Y %H:%M')
        bonuses.append({"bonus": bonus_type, "expires": formatted})
    return bonuses
