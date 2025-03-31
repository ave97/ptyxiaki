from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import database
from werkzeug.security import check_password_hash, generate_password_hash
from quiz import Question, Quiz
import os, re
from users import Teacher, Student


app = Flask(__name__)
app.secret_key = os.urandom(24)  # 24 τυχαιοι χαρακτηρες


@app.route("/")
def home():
    if "user" in session:
        return dashboard()
    return render_template("home.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    if password is None:
        print("Δεν βρέθηκε το password στο request!")
    else:
        print(password)

    if not username or not email or not password or not role:
        return render_template(
            "home.html", error="Συμπληρώστε όλα τα πεδία!", register=True
        )

    if len(password) < 6:
        return render_template(
            "home.html",
            error="Ο κωδικός πρέπει να περιέχει τουλάχιστον 6 χαρακτήρες!",
            register=True,
        )

    email_regex = r"[a-zA-z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return render_template(
            "home.html", error="Το email δεν έχει έγκυρη μορφή!", register=True
        )

    # Έλεγχος αν υπάρχει ήδη ο χρήστης
    existing_user = database.selectUser(username)
    if existing_user:
        return render_template(
            "home.html", error="Το όνομα χρήστη υπάρχει ήδη!", register=True
        )

    hashed_pass = generate_password_hash(password)
    # Προσθήκη νέου χρήστη στη βάση
    database.insertUser(username, email, hashed_pass, role)

    print(f"Εγγραφή νέου χρήστη: {username} ως {role}")
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"Username: {username}, Password: {password}")

        user = database.selectUser(username)
        print(user[3])
        if user:
            session["user"] = username
            session["role"] = user[4]
            print(check_password_hash(user[3], password))
            if check_password_hash(user[3], password):
                print(
                    f"Επιτυχής σύνδεση: {username} Ρόλος: {session['role']}"
                )  # Εμφανίζει το όνομα χρήστη
                return dashboard()
        print("Αποτυχία σύνδεσης!")  # Αν τα στοιχεία είναι λάθος
        return render_template("home.html", error="Λάθος username ή password")
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():
    if "user" in session:
        userRole = session["role"]
        if userRole == "teacher":
            return redirect(url_for("teacher_dashboard"))
        elif userRole == "student":
            return redirect(url_for("student_dashboard"))
    return redirect(url_for("home"))


@app.route("/teacher/dashboard")
def teacher_dashboard():
    if "user" not in session or session["role"] != "teacher":
        return redirect(url_for("no_access"))

    return render_template(
        "teacher_dashboard.html", user=session["user"], role=session["role"]
    )


@app.route("/student/dashboard")
def student_dashboard():
    if "user" not in session or session["role"] != "student":
        return redirect(url_for("no_access"))
    return render_template(
        "student_dashboard.html", user=session["user"], role=session["role"]
    )


@app.route("/account")
def myAccount():
    if "user" in session:
        username = session["user"]
        user = database.selectUser(username)
        print(
            f"My Account details: {username} and user: {user} and his role is: {user[4]}"
        )
        return render_template(
            "account.html", user=session["user"], role=session["role"]
        )


@app.route("/create")
def create_quiz():
    if "user" not in session or session["role"] != "teacher":
        return redirect(url_for("no_access"))
    return render_template("create_quiz.html", user=session["user"])


@app.route("/create_quiz", methods=["GET", "POST"])
def save_quiz():
    if request.method == "POST":
        if "user" not in session or session["role"] != "teacher":
            return redirect(url_for("no_access"))

        teacher = database.getTeacherInfo(session["user"])

        quizTitle = request.form.get("quizTitle")
        quizTime = request.form.get("quizTime")
        quizDescription = request.form.get("quizDescription")

        quiz = Quiz(quizTitle, quizTime, quizDescription)

        quiz_id = database.insertQuiz(quiz, teacher)

        questionNum = 1
        while f"question_{questionNum}" in request.form:
            questionText = request.form.get(f"question_{questionNum}")
            if not questionText:
                break
            print(f"Here is the qTxt: {questionText}")
            option1 = request.form.get(f"option_{questionNum}_1")
            option2 = request.form.get(f"option_{questionNum}_2")
            option3 = request.form.get(f"option_{questionNum}_3")
            option4 = request.form.get(f"option_{questionNum}_4")
            correctAnswer = request.form.get(f"correct_{questionNum}")
            question = Question(
                questionNum,
                questionText,
                option1,
                option2,
                option3,
                option4,
                correctAnswer,
            )
            database.insertQuestion(quiz_id, question)
            questionNum += 1

        return redirect(url_for("history"))

    return render_template("teacher_dashboard.html", user=session["user"])


@app.route("/history")
def history():
    if "user" not in session or session["role"] != "teacher":
        return redirect(url_for("no_access"))

    teacher = database.getTeacherInfo(session["user"])
    quizzes = database.getQuizzesByTeacher(teacher.getTid())

    return render_template("history.html", user=session["user"], quizzes=quizzes)


@app.route("/quiz/<int:quiz_id>")
def get_quiz(quiz_id):
    if "user" not in session or session["role"] != "teacher":
        return jsonify({"error": "Unauthorized"}), 403

    quiz = database.getQuizById(quiz_id)
    questions = database.getQuestionsBy(quiz_id)

    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    quiz_data = {
        "id": quiz["id"],
        "title": quiz["title"],
        "description": quiz["description"],
        "time_limit": quiz["time_limit"],
        "questions": [
            {
                "id": q["id"],
                "question_text": q["question_text"],
                "options": [q["option_1"], q["option_2"], q["option_3"], q["option_4"]],
                "correct_answer": q["correct_answer"],
            }
            for q in questions
        ],
    }

    return jsonify(quiz_data)


@app.route("/delete_quizzes", methods=["POST"])
def delete_quizzes():
    if "user" not in session or session["role"] != "teacher":
        return redirect(url_for("no_access"))

    data = request.get_json()
    quiz_ids = data.get("quiz_ids", [])
    if not quiz_ids:
        return jsonify({"error": "No quizzes selected"}), 400

    for quiz_id in quiz_ids:
        database.deleteQuizzes(quiz_id)
    return jsonify({"success": True, "message": "Quizzes deleted successfully!"})


@app.route("/update_quiz", methods=["POST"])
def update_quiz():
    if "user" not in session or session["role"] != "teacher":
        return redirect(url_for("no_access"))

    data = request.get_json()
    quiz_id = data.get("quiz_id")
    title = data.get("title")
    description = data.get("description")
    time_limit = data.get("time_limit")

    if not quiz_id or not title or not description or not time_limit:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    return


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/no_access")
def no_access():
    return render_template("no_access.html")


# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)