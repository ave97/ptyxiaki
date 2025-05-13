import sqlite3
from werkzeug.security import generate_password_hash


def getConnection():
    connection = sqlite3.connect("eduplay.db")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


# Users
def createUsersDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE NOT NULL, 
        email TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL, 
        role TEXT CHECK(role IN ('student', 'teacher')) NOT NULL, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.commit()
    connection.close()


# Students
# Χρηση του user_id για τη συνδεση των πινακων users και students
def createStudentsDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sid TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


# Teachers
def createTeachersDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tid TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


# Quiz
def createQuizDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT NOT NULL, 
        lesson TEXT,  
        created_by TEXT NOT NULL, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.commit()
    connection.close()


# Questions
def createQuestionsDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        quiz_id INTEGER NOT NULL, 
        question_num INTEGER, 
        question_text TEXT NOT NULL,
        question_type TEXT NOT NULL,
        option_1 TEXT, 
        option_2 TEXT, 
        option_3 TEXT, 
        option_4 TEXT, 
        correct_answer INTEGER,  
        FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


# Matching Type of Question
def createMatchingDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS matching (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        item_1 TEXT NOT NULL,
        item_2 TEXT NOT NULL,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


def createAnsweredQuizDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            answer TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


# Notifications
def createNotficationsDB():
    connection = getConnection()
    cursor = connection.cursor()
    # Δημιουργία πίνακα ειδοποιήσεων
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        type TEXT NOT NULL,
        quiz_id TEXT,
        created_at TEXT,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notification_seen (
        user_type TEXT,
        user_id TEXT,
        notification_id INTEGER,
        seen INTEGER DEFAULT 0,
        PRIMARY KEY (user_type, user_id, notification_id),
        FOREIGN KEY (notification_id) REFERENCES notifications(id)
        );
        """
    )

    connection.commit()
    connection.close()


# Daily Spin
def createDailySpinDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_spin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sid INTEGER NOT NULL,
        spin_date DATE NOT NULL,
        bonus TEXT NOT NULL,
        FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


# Active Bonus
def createActiveBonusDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS active_bonus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sid INTEGER NOT NULL,
        bonus TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


# Achievements
def createAchievementsDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS achievements ()")
    connection.commit()
    connection.close()


# Leaderboard
def createLeaderboardDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS leaderboard ()")
    connection.commit()
    connection.close()


# Friends
def createFriendsDB():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, friend_user_id INTEGER NOT NULL, status TEXT NOT NULL, timestamp TIMESTAMP)"
    )
    connection.commit()
    connection.close()


def hash_existing_passwords():
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("SELECT username, password FROM users")
    users = cursor.fetchall()

    for username, password in users:
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed_password, username),
        )

    connection.commit()
    connection.close()


def deleteUser():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE username=(?)", ("teacher1",))
    print("Done!")
    connection.commit()
    connection.close()


def drop():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("DROP TABLE daily_spin")
    cursor.execute("DROP TABLE active_bonus")
    connection.commit()
    connection.close()


# drop()
# createUsersDB()
# createStudentsDB()
# createTeachersDB()
# createFriendsDB()
# createQuizDB()
# createQuestionsDB()
# createMatchingDB()
# createAnsweredQuizDB()
# createNotficationsDB()
# createDailySpinDB()
# createActiveBonusDB()


def delete(i):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM quiz WHERE id = ?", ((i,)))
    connection.commit()
    connection.close()


def check_column_nullability():
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(questions);")

    columns = cursor.fetchall()
    print(f"Hey {len(columns)}")
    for column in columns:
        column_name = column[1]
        is_nullable = "NULL" if column[3] == 0 else "NOT NULL"
        print(f"Column: {column_name}, Nullability: {is_nullable}")

    conn.close()


# delete()


# Κλήση της συνάρτησης
# check_column_nullability()

# def addPhotoProfileToUsersDB():
#     connection = getConnection()
#     cursor = connection.cursor()
#     cursor.execute(
#         """
#         ALTER TABLE users
#         ADD COLUMN photo_profile TEXT DEFAULT 'default_avatar.jpg';
#         """
#     )
#     connection.commit()
#     connection.close()
