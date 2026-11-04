"use strict";

const status = document.getElementById("status");

function update() {
    const now = new Date();
    const minutes = now.getHours() * 60 + now.getMinutes();

    const silent =
        now.getFullYear() === 2026 &&
        now.getMonth() === 10 &&
        now.getDate() === 11 &&
        minutes >= 660 &&
        minutes < 662;

    status.textContent = silent
        ? "Two Minutes of Silence"
        : "In Remembrance";
}

update();
setInterval(update, 1000);
