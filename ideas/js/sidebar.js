document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".sidebar ul li a");
    const contentDiv = document.getElementById("dynamic-content");

    links.forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault(); // ❌ Αποτρέπει την ανανέωση της σελίδας
            const page = this.getAttribute("data-page"); // Παίρνει το όνομα του HTML αρχείου
            
            if (page) {
                fetch(page) // 📌 Φορτώνει τη σελίδα μέσω AJAX
                    .then(response => response.text())
                    .then(html => {
                        contentDiv.innerHTML = html; // Ενημερώνει το περιεχόμενο της σελίδας
                    })
                    .catch(error => console.error("❌ Σφάλμα στη φόρτωση:", error));
            }
        });
    });
});
