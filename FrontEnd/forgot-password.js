document.querySelector(".ContinueClass").addEventListener("click", function () {
  const email = document.querySelector(".input-field").value.trim();
  if (email === "") {
    alert("Please enter your email address.");
    return;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert("Please enter a valid email address.");
    return;
  }
  alert("A password reset link has been sent to your email .");
  window.location.href = "project.html";
});
