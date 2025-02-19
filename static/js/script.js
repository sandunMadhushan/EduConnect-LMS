document.querySelectorAll("textarea:not([readonly])").forEach(textarea => {
    textarea.addEventListener("input", adjustHeight);
});

function adjustHeight(event) {
    let textarea = event.target;
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
}
