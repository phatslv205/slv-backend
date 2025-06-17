window.addEventListener('DOMContentLoaded', (event) => {
    const solvesLeftInput = document.getElementById("solves_left");
    const solveBtn = document.getElementById("solve-btn");
    const watchAdBtn = document.getElementById("watch-ad-btn"); // Nút xem quảng cáo nếu có
  
    let solvesLeft = solvesLeftInput ? parseInt(solvesLeftInput.value) : 0;
  
    if (solveBtn) {
      if (solvesLeft <= 0) {
        solveBtn.disabled = true;
        if (watchAdBtn) {
          watchAdBtn.style.display = "inline-block"; // Hiện nút xem quảng cáo nếu hết lượt
        }
      } else {
        solveBtn.disabled = false;
        if (watchAdBtn) {
          watchAdBtn.style.display = "none"; // Ẩn nút xem quảng cáo nếu còn lượt
        }
      }
    }
  });
  
  // Hàm khi người dùng bấm nút "Xem quảng cáo"
  function watchAd() {
    fetch("/watch_ad", { method: "POST" })
      .then(response => response.json())
      .then(data => {
        alert(data.message);
        location.reload(); // Load lại trang để cập nhật lượt mới
      })
      .catch(err => {
        alert("Lỗi khi xem quảng cáo!");
      });
  }
  