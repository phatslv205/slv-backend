  document.addEventListener("DOMContentLoaded", function () {
    document.body.classList.add('dark'); //giao diện tối
    document.querySelectorAll("#chat-box *").forEach(el => {
      el.style.color = "#eee"; //chữ màu sáng
    });
  });