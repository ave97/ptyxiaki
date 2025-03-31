document.addEventListener("DOMContentLoaded", function () {
    const questionsContainer = document.getElementById("questionsContainer");
    const addQuestionButton = document.getElementById("addQuestion");
    let questionCount = 1;

    addQuestionButton.addEventListener("click", function () {
        questionCount++;
        const newQuestion = document.createElement("div");
        newQuestion.classList.add("question");

        newQuestion.innerHTML = `
            <h3>Question ${questionCount}</h3>
            <label>Question: </label>
            <input type="textarea" name="question_${questionCount}" required>

            <div class="options-container">
                <label>Options: </label>
                <input type="text" name="option_${questionCount}_1" placeholder="Answer 1" required>
                <input type="text" name="option_${questionCount}_2" placeholder="Answer 2" required>
                <input type="text" name="option_${questionCount}_3" placeholder="Answer 3" required>
                <input type="text" name="option_${questionCount}_4" placeholder="Answer 4" required>
            </div>
            
            <label>Correct Answer:</label>
            <select name="correct_${questionCount}" required>
                <option value="1">Answer 1</option>
                <option value="2">Answer 2</option>
                <option value="3">Answer 3</option>
                <option value="4">Answer 4</option>
            </select>
            <button type="button" class="removeQuestion">Remove Question</button>
        `;

        questionsContainer.appendChild(newQuestion);
    });

    const removeQuestion = document.getElementById("removeQuestion");

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("removeQuestion")) {
            event.target.closest(".question").remove();
            questionCount--;
            updateQuestionNumbers();
        }
    });

    function updateQuestionNumbers() {
        const allQuestions = document.querySelectorAll(".question");
        console.log("Helllooooo");
        allQuestions.forEach((question, index) => {
            const questionTitle = question.querySelector("h3");
            questionTitle.textContent = 'Question ' + (index + 1);
            const inputs = question.querySelectorAll("input, select");
            inputs.forEach(input => {
                input.name = input.name.replace(/\d+/, index + 1);
                console.log(index);
            });
        });
    }
});
