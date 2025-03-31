document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("editQuizModal");
    const closeBtn = modal.querySelector(".close");
    const editButtons = document.querySelectorAll(".quick-edit-btn");

    let latestQuizCard = null;

    // Άνοιγμα του modal όταν πατηθεί "Edit"
    editButtons.forEach(button => {
        button.addEventListener("click", function () {
            const quizId = this.getAttribute("data-quiz-id");
            fetch(`/quiz/${quizId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById("quizTitle").value = data.title;
                    document.getElementById("quizDescription").value = data.description;
                    document.getElementById("quizTime").value = data.time_limit;
                    modal.classList.add("show");
                });
            latestQuizCard = quizId;
        });
    });

    // Κλείσιμο του modal
    closeBtn.addEventListener("click", function () {
        modal.classList.remove("show");
    });

    // Κλείσιμο αν ο χρήστης πατήσει εκτός του modal
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.classList.remove("show");
        }
    });

    const saveBtn = document.getElementById("modalSaveBtn");
    saveBtn.addEventListener("click", function (event) {
        event.preventDefault();
        const quizId = latestQuizCard;

        console.log("Saving quiz with id : " + quizId);

        const title = document.getElementById("quizTitle").value;
        const description = document.getElementById("quizDescription").value;
        const time_limit = document.getElementById("quizTime").value;

        console.log("Title: " + title + ", Description: " + description + ", Time Limit: " + time_limit);

        fetch("/update_quiz", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                quiz_id: quizId,
                title: title,
                description: description,
                time_limit: time_limit
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const saveModal = document.getElementById("saveModal");
                    saveModal.classList.add("show");
                    setTimeout(function () {
                        saveModal.classList.remove("show");
                    }, 2000);
                } else {
                    console.error("Failed to save changes:", data.error);
                }
            }).catch(error => console.error("Error: " + error));

        latestQuizCard = null;
    });

    const delBtns = document.querySelectorAll(".delete-btn");
    delBtns.forEach(button => {
        button.addEventListener("click", function () {
            var confirm = window.confirm("Are you sure you want to delete this quiz?");
            if (confirm) {
                var quiz = this.closest(".quiz-card").getAttribute("data-quiz-id");
                fetch("/delete_quizzes", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ quiz_ids: quiz })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("Quiz is deleted successfully!");
                            button.closest(".quiz-card").remove();
                        } else {
                            alert("Error: " + data.error);
                        }
                    }).catch(error => console.error("Error: " + data.error));

            }
        });
    })

    const selectAll = document.getElementById("selectAll");
    const allCheckboxes = document.querySelectorAll(".quiz-card-checkbox");

    selectAll.addEventListener("change", function () {
        console.log(selectAll.checked);
        allCheckboxes.forEach(checkbox => {
            checkbox.checked = selectAll.checked;
        });
    });

    allCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            if (!this.checked) {
                selectAll.checked = false;
            }

            if ([...allCheckboxes].every(checkbox => checkbox.checked)) {
                selectAll.checked = true;
            }
        });
    });

    const deleteSelectedBtn = document.getElementById("deleteSelected");
    const duplicateBtn = document.getElementById("duplicateSelected");
    const exportBtn = document.getElementById("exportCSV");

    deleteSelectedBtn.addEventListener("click", function () {
        var confirm = window.confirm("Are you sure you want to delete selected quizzes?");
        if (confirm) {
            var selectedQuizzes = document.querySelectorAll(".quiz-card-checkbox:checked");
            if (selectedQuizzes.length === 0) {
                alert("No quizzes selected.");
                return;
            }

            var quizIds = Array.from(selectedQuizzes).map(quiz => quiz.closest(".quiz-card").getAttribute("data-quiz-id"));

            fetch("/delete_quizzes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ quiz_ids: quizIds })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Quizzes deleted successfully!");
                        selectedQuizzes.forEach(quiz => {
                            quiz.closest(".quiz-card").remove()
                        });
                    } else {
                        alert("Error: " + data.error);
                    }
                }).catch(error => console.error("Error: " + data.error));
        } else {
            return;
        }
    });

});
