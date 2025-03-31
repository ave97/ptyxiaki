document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const formData = {
            name: document.getElementById("name").value,
            age: document.getElementById("age").value,
            sid: document.getElementById("sid").value
        };

        try {
            const response = await fetch("http://127.0.0.1:5000/submit", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            console.log(result.message);
        } catch (error) {
            console.error("Error: ", error);
        }
    });

});