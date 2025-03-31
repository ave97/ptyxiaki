document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("loginModal");
    const openBtn = document.getElementById("openLogin");
    const closeBtn = document.querySelector(".close");
    const flipContainer = document.querySelector(".flip-container");

    const showRegister = document.getElementById("showRegister");
    const showLogin = document.getElementById("showLogin");

    const loginError = document.getElementById("loginError");
    const errorMessage = modal.getAttribute("data-error");

    // Ελέγχουμε αν υπάρχει error και ανοίγουμε αυτόματα το modal
    if (errorMessage && errorMessage.trim() !== "") {
        modal.classList.add("show");
        loginError.textContent = errorMessage;
        loginError.style.display = "block";
    }

    if (modal.getAttribute("data-register") === "true" || modal.getAttribute("data-register") === "True") {
        modal.classList.add("show");
        flipContainer.classList.add("active");
    }

    // Άνοιγμα popup
    openBtn.onclick = function() {
        modal.classList.add("show");
    };

    // Κλείσιμο popup
    closeBtn.onclick = function() {
        modal.classList.remove("show");
        flipContainer.classList.remove("active"); // Επιστρέφουμε το modal στο αρχικό του state
    };

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.classList.remove("show");
            flipContainer.classList.remove("active");
        }
    };

    // Εναλλαγή σε Εγγραφή (με περιστροφή)
    showRegister.onclick = function(event) {
        event.preventDefault();
        flipContainer.classList.add("active"); // Ενεργοποίηση περιστροφής
    };

    // Εναλλαγή σε Σύνδεση (με περιστροφή πίσω)
    showLogin.onclick = function(event) {
        event.preventDefault();
        flipContainer.classList.remove("active"); // Γυρνάει πίσω στο login
    };

    registerForm.addEventListener("submit", function(event) {
        event.preventDefault();
        console.log("🔹 Register Submitted");
        this.submit(); // Στέλνει τη φόρμα μετά τον έλεγχο
    });
    
});
