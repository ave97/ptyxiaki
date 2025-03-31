document.addEventListener("DOMContentLoaded", function () {

    const links = document.querySelectorAll(".sidebar ul li a");
    const currentPath = window.location.pathname;

    links.forEach(link => {
        if (currentPath.includes(link.pathname) && link.pathname != "/") {
            link.classList.add("active");
        }
    });
});
