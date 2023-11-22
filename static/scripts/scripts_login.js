const loginForm = document.getElementById("input");
const loginButton = document.getElementById("button");
const loginErrorMsg = document.getElementById("error-msg");

loginButton.addEventListener("click", (mouse) => {
    mouse.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;

    if (username === "JohnD" && password === "123") {
        alert("Login Successful");
        location.reload();
    } 
    else {
        loginErrorMsg.style.opacity = 1;
    }
})
