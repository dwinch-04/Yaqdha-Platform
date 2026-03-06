// script.js
window.onload = function() {

    const pageLang = document.documentElement.lang;
    const hour = new Date().getHours();
    let message = "";


    if (pageLang === "ar") {
        if (hour < 12) {
            message = "صباح الخير.. كن يقظاً دائماً واحذر من الروابط المشبوهة! 🛡️";
        } else {
            message = "مساء الخير.. تذكر أن وعيك هو خط دفاعك الأول ضد الاحتيال! 🛡️";
        }
    } else {

        if (hour < 12) {
            message = "Good morning.. Stay vigilant and beware of suspicious links! 🛡️";
        } else {
            message = "Good evening.. Remember, your awareness is your first line of defense! 🛡️";
        }
    }

    alert(message);
};
