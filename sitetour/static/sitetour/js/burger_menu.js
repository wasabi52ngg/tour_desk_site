    document.addEventListener("DOMContentLoaded", function () {
    const burgerMenu = document.querySelector(".burger-menu");
    const header = document.querySelector(".header");

    // Переключение состояния активности
    burgerMenu.addEventListener("click", function () {
        console.log("Бургер-меню нажато");
        header.classList.toggle("active");
    });

    // Закрытие меню при клике вне его области
    document.addEventListener("click", function (event) {
        if (!header.contains(event.target) && header.classList.contains("active")) {
            console.log("Клик вне меню");
            header.classList.remove("active");
        }
    });
});