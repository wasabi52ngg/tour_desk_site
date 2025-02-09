document.addEventListener("DOMContentLoaded", function () {
    const toggles = document.querySelectorAll(".dropdown-toggle");

    toggles.forEach((toggle) => {
        toggle.addEventListener("click", function (e) {
            e.preventDefault();
            this.classList.toggle("active");

            const dropdown = this.nextElementSibling;
            if (dropdown.style.display === "block") {
                dropdown.style.display = "none";
            } else {
                dropdown.style.display = "block";
            }
        });
    });
});
