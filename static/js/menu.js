// Menu sanduíche
document.addEventListener("DOMContentLoaded", () => {
    const buttonnav = document.getElementById("button_point-point-point");
    const nav = document.getElementById("menu_nav");

    if (buttonnav) {
        buttonnav.addEventListener("click", () => {
            if (nav.style.display === "none" || nav.style.display === "") {
                nav.style.display = "flex";
            } else {
                nav.style.display = "none";
            }
        });
    }
});
