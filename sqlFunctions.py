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
        description TEXT, 
        time_limit INTEGER NOT NULL, 
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
        option_1 TEXT NOT NULL, 
        option_2 TEXT NOT NULL, 
        option_3 TEXT, 
        option_4 TEXT, 
        correct_answer INTEGER NOT NULL,  
        FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
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
    cursor.execute("DROP TABLE users")
    connection.commit()
    connection.close()


# drop()
# createUsersDB()
# createStudentsDB()
# createTeachersDB()
# createFriendsDB()
# createQuizDB()
# createQuestionsDB()


def delete(i):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", ((i,)))
    connection.commit()
    connection.close()


delete(2)
delete(3)
delete(4)
delete(5)
