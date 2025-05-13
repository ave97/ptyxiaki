document.addEventListener("DOMContentLoaded", function () {

    const links = document.querySelectorAll(".sidebar ul li a");
    const currentPath = window.location.pathname;

    links.forEach(link => {
        if (currentPath.includes(link.pathname) && link.pathname != "/") {
            link.classList.add("active");
        }
    });

    const viewButtons = document.querySelectorAll("#view-btn");

    viewButtons.forEach(button => {
        button.addEventListener("click", function () {
            const quizId = button.dataset.quizId;
            fetch("/quiz/" + button.dataset.quizId)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = "/view_quiz/" + button.dataset.quizId;
                    } else {
                        console.log("Error: " + data.error);
                    }
            }).catch(error => console.error("Error: " + error));
        });
    });
});