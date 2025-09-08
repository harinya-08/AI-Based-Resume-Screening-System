
document.querySelector(".ContinueClass").addEventListener("click", function() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  if (!username || !password) {
    alert("Please enter both username and password.");
    return;
  }
  const usernameRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  if (!usernameRegex.test(username)) {
    alert("Enter a valid email address as username.");
    return;
  }
  const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@]).{6,}$/;
  if (!passwordRegex.test(password)) {
    alert("Password must contain at least 1 uppercase, 1 digit, and '@'.");
    return;
  }e
  window.location.href = "applicant-dashboard.html";
});
