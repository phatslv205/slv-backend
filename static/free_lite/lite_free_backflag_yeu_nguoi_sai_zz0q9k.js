document.addEventListener("DOMContentLoaded", function () {
  const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (isDark) {
    // Chế độ tối
    document.body.classList.add('dark');
    document.querySelectorAll("#chat-box *").forEach(el => {
      el.style.color = "#f5f5f5";
      el.style.backgroundColor = "transparent";
    });
    document.querySelectorAll(".message.ai").forEach(el => {
      el.style.backgroundColor = "#222";
    });
    document.querySelectorAll(".message.user").forEach(el => {
      el.style.backgroundColor = "#0052cc";
      el.style.color = "#fff";
    });
  } else {
    // Chế độ sáng
    document.body.classList.remove('dark');
    document.querySelectorAll("#chat-box *").forEach(el => {
      el.style.color = "#222";
      el.style.backgroundColor = "transparent";
    });
    document.querySelectorAll(".message.ai").forEach(el => {
      el.style.backgroundColor = "#f0f0f0";
    });
    document.querySelectorAll(".message.user").forEach(el => {
      el.style.backgroundColor = "#d0e4ff";
      el.style.color = "#000";
    });
  }
});
