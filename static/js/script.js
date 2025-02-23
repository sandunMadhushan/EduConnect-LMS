document.querySelectorAll("textarea:not([readonly])").forEach(textarea => {
    textarea.addEventListener("input", adjustHeight);
});

function adjustHeight(event) {
    let textarea = event.target;
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
}


const alerts = document.querySelectorAll('.alert');


alerts.forEach(alert => {
  setTimeout(() => {
    alert.style.opacity = '0';  
    setTimeout(() => alert.remove(), 500); 
  }, 5000);  
});