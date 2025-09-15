
async function loadHome() { const root = document.getElementById("root"); try { const res = await fetch("/api/home_info"); const data = await res.json(); const guest = data.guest || false; if (!data.success) { return root.innerHTML = `<div class="text-red-500 p-4 text-center"> ${data.message || "Lỗi xác thực."}</div>`; } if (guest) { return root.innerHTML = ` 
<div class="absolute inset-0 -z-10 overflow-hidden"> 
  <svg class="absolute left-1/2 top-0 h-[64rem] w-[128rem] -translate-x-1/2 stroke-black/5 dark:stroke-white/10 [mask-image:radial-gradient(64rem_64rem_at_center,white,transparent)]" aria-hidden="true"> 
    <defs> 
      <pattern id="grid-pattern" width="200" height="200" x="50%" y="50%" patternUnits="userSpaceOnUse"> 
        <path d="M.5 200V.5H200" fill="none" /> 
      </pattern> 
    </defs> 
    <rect width="100%" height="100%" stroke-width="0" fill="url(#grid-pattern)" /> 
  </svg> 
  <div class="absolute left-1/2 top-0 -translate-x-1/2 blur-3xl opacity-50 animate-pulse" style="background: radial-gradient(closest-side at 50% 30%, #0ea5e9, transparent 70%); width: 100vw; height: 64rem;"> 
  </div> 
</div> 

<main class="relative z-10 flex flex-col items-center justify-center min-h-screen text-center px-4 animate__animated animate__fadeInUp"> 
  <h1 class="text-5xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 drop-shadow-xl animate-[shine_4s_linear_infinite]"> 
    SolverViet 
  </h1> 

  <p class="mt-3 text-base text-gray-700 dark:text-gray-300 max-w-md leading-relaxed"> 
    Nền tảng AI hỗ trợ học tập, sáng tạo, và tự động hóa – mang lại trải nghiệm cá nhân hóa tối ưu. 
    Được điều chỉnh để phù hợp với từng người dùng. Hệ thống AI có hơn 
    <b>90 loại tính cách cá nhân hóa</b>, có thể thay đổi tùy thích theo tâm trạng hoặc sở thích. 
  </p> 

  <div class="mt-6 text-sm text-left text-gray-800 dark:text-white bg-white/80 dark:bg-white/10 backdrop-blur-xl p-6 rounded-2xl shadow-xl max-w-md space-y-3 border border-cyan-400/30 hover:shadow-cyan-500/30 transition duration-300"> 
    <p><b>AI Chat</b> – Trò chuyện cùng AI có tính cách, hiểu cảm xúc & phản hồi linh hoạt.</p> 
    <p><b>SmartDoc</b> – Tạo bài viết, văn bản, biểu mẫu hoặc bảng tính trong vài giây.</p> 
    <p><b>ImageCrafter</b> – Chuyển mô tả thành hình ảnh sống động do AI vẽ.</p> 
    <p><b>Code Smasher</b> – Mã hóa JavaScript bảo mật, giúp bảo vệ code dễ dàng.</p> 
    <p><b>NexuWord</b> – Thử thách AI nối từ siêu đỉnh, mỗi ván chơi là một trận đấu trí cực căng! 🔥</p>
    <p><b>Phản hồi cá tính</b> – AI sẽ mang phong cách phản hồi tương ứng với từng tính cách AI với hơn 90 loại.</p>

  </div> 

  <a href="/login" class="mt-8 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-semibold hover:scale-105 hover:shadow-xl transition-all duration-300 shadow-lg animate-bounce"> 
    Đăng nhập để khám phá 
  </a> 

  <p class="mt-5 text-xs text-gray-500 italic dark:text-gray-400"> 
    Dành cho học sinh, sinh viên, giáo viên, lập trình viên, người làm nội dung – và bạn. 
  </p> 
</main> 

<style> 
  @keyframes shine { 
    0% { background-position: -200% 0; } 
    100% { background-position: 200% 0; } 
  } 
  .animate-[shine_4s_linear_infinite] { 
    background-image: linear-gradient(110deg, #0ea5e9 0%, #3b82f6 40%, #0ea5e9 60%); 
    background-size: 200% auto; 
    animation: shine 4s linear infinite; 
    background-clip: text; 
    -webkit-background-clip: text; 
    color: transparent; 
  } 
</style> 
`;

} const { avatar_url, vip_status, user_unread_senders = [], has_seen_intro } = data; if (!has_seen_intro) { showIntroGuide(); } root.innerHTML = ` <header class="text-white px-6 py-4 flex justify-between items-center border-b-2 border-[#00aaff] text-white bg-gradient-to-r ${themeClass}"> <div class="flex items-center gap-4"> <div class="flex flex-col leading-tight"> <h1 class="text-3xl font-bold text-cyan-600 dark:text-cyan-400">SolverViet</h1> <span class="text-xs text-gray-500 dark:text-white-400 mt-1">© 2025. All rights reserved.</span> </div> </div> <div class="flex items-center gap-4"> ${avatar_url && !avatar_url.includes("logos/logo.png") ? ` <a href="/user-info" title="Thông tin tài khoản" class="flex flex-col items-center"> <img src="${avatar_url}" alt="Avatar" class="w-11 h-11 rounded-full object-cover border-2 border-cyan-400 hover:scale-105 transition duration-200"> ${typeof vip_status === "string" && vip_status ? `<span class="mt-1 text-[11px] font-semibold px-2 py-[2px] rounded-full shadow-md border ${ vip_status.startsWith("SLV") ? "bg-yellow-400 text-black border-yellow-300 animate-pulse" : vip_status.startsWith("Lite") ? "bg-white text-black border-gray-300" : "bg-gray-500 text-white" }"> ${ vip_status.startsWith("SLV") ? "SLV (Premium)" : vip_status.startsWith("Lite") ? "Lite (Plus)" : vip_status } </span>` : ""} </a> ` : ""} </div> </header> 
<nav class="grid grid-cols-6 text-sm font-semibold text-center border-b border-cyan-400 text-white bg-gradient-to-r ${themeClass} text-black dark:text-white"> 
<a href="/chat_redirect" class="flex flex-col items-center gap-1 py-3 hover:text-cyan-500">
  <lord-icon
    src="/static/loding/chat.json"
    trigger="hover"
    colors="primary:#00e5ff"
    style="width:36px;height:36px">
  </lord-icon>
  <span>ChatAI</span>
</a>

<div id="smartdoc-menu" class="relative flex flex-col items-center gap-1 py-3 hover:text-cyan-500 cursor-pointer">
  <lord-icon
      src="${window.SOLVER_ICON_SMARTDOC}"
      trigger="hover"
      colors="primary:#00c9ff,secondary:#ffffff"
      style="width:36px;height:36px">
  </lord-icon>
  <span>SmartDoc</span>

  <div id="smartdoc-submenu"
       class="absolute top-[70px] opacity-0 scale-95 translate-y-2 transition-all duration-300 ease-out
              bg-white dark:bg-[#1c1f26] border border-gray-300 dark:border-gray-700 rounded-xl shadow-xl
              flex-col z-50 min-w-[200px] text-sm overflow-hidden pointer-events-none">
 
    <a href="/smartdoc" class="flex items-center gap-2 px-4 py-3 hover:bg-gray-500 text-black dark:text-white transition bg-white dark:bg-[#1c1f26]">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 4H7a2 2 0 01-2-2V6a2 2 0 012-2h5l5 5v11a2 2 0 01-2 2z" />
      </svg>
      Text Editor
    </a>
    <a href="/image_crafter" class="flex items-center gap-2 px-4 py-3 hover:bg-gray-500 text-green-600 dark:text-white transition bg-white dark:bg-[#1c1f26]">
      <i data-lucide="image-plus" class="w-4 h-4 text-green-500"></i>
      Image Crafter
    </a>
    <a href="/js_mifing" class="flex items-center gap-2 px-4 py-3 hover:bg-gray-500 text-purple-500 dark:text-white transition bg-white dark:bg-[#1c1f26]">
      <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path d="M16 18l6-6-6-6M8 6l-6 6 6 6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      Code Smasher (JS)
    </a>
    <a href="/noi_tu" class="flex items-center gap-2 px-4 py-3 hover:bg-gray-500 text-yellow-500 dark:text-white transition bg-white dark:bg-[#1c1f26]">
      <i data-lucide="text" class="w-4 h-4 text-yellow-400"></i>
      NexuWord
    </a>
  </div>
</div>

<a href="/friends" class="relative flex flex-col items-center gap-1 py-3 hover:text-cyan-500">
  <lord-icon
    src="/static/loding/friend.json"
    trigger="hover"
    colors="primary:#00e5ff"
    style="width:36px;height:36px;transform:scale(1.25);">
  </lord-icon>
  <span>Friend</span>
  ${user_unread_senders.length > 0 ? `
    <span id="friend-badge"
      class="absolute -top-1 right-[20%] bg-red-600 text-white text-[10px] rounded-full px-[5px]">
      ${user_unread_senders.length > 10 ? '+9' : user_unread_senders.length}
    </span>` : ""}
</a>

 <button onclick="goTo('/gop-y')" class="flex flex-col items-center gap-1 py-3 hover:text-cyan-500">
  <lord-icon
    src="/static/loding/gop_y.json"
    trigger="hover"
    colors="primary:#00e5ff"
    style="width:36px;height:36px">
  </lord-icon>
  <span>Góp ý / Báo lỗi</span>
</button>
 <a href="/user-info" class="flex flex-col items-center gap-1 py-3 hover:text-cyan-500">
  <lord-icon
    src="/static/loding/info.json"
    trigger="hover"
    colors="primary:#00e5ff"
    style="width:36px;height:36px">
  </lord-icon>
  <span>Thông tin</span>
</a>
 <a href="/upgradeWaguri_9d7s2x4kP1tY0mVn6cQ8hR5eB3aZxLw_fJ7k" class="flex flex-col items-center gap-1 py-3 hover:text-cyan-500">
  <lord-icon
    src="/static/loding/pay.json"
    trigger="hover"
    colors="primary:#00e5ff"
    style="width:36px;height:36px">
  </lord-icon>
  <span>Service</span>
</a>
</nav>
 <main class="flex flex-col items-center justify-center h-[calc(100vh-144px)] text-center px-4 bg-gradient-to-br ${themeClass}">
  <h1 class="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 drop-shadow-md animate-pulse flex items-center gap-2">
    SolverViet
    <span class="text-xs bg-gradient-to-r from-black-500 to-cyan-500 text-white px-2 py-0.5 rounded-full shadow-md animate-pulse">v1.7</span>
  </h1>
  <p class="mt-2 text-sm text-gray-400">nơi kết nối trí tuệ và công nghệ</p>
  <span class="hidden from-green-200 to-pink-200 from-yellow-300 to-orange-300 from-amber-400 to-orange-400 from-blue-900 to-slate-800"></span>
</main>
 `; lucide.createIcons(); } catch (err) { console.error(err); root.innerHTML = `<div class="text-red-500 text-center p-4"> Không thể tải giao diện.</div>`; } }function goTo(url) { window.location.href = url; } 
let themeClass = "from-[#0f1115] via-[#0a1a2f] to-[#09304a]";

 loadHome(); 
 function showIntroGuide() { const overlay = document.createElement("div"); overlay.className = "fixed inset-0 bg-black bg-opacity-80 z-[999] flex justify-center items-center text-white text-sm"; overlay.innerHTML = ` <div class="bg-white text-black max-w-md w-full rounded-lg shadow-lg p-6 text-center animate__animated animate__fadeIn relative"> <h2 class="text-2xl font-bold mb-3"> Chào mừng bạn đến với <span class="text-cyan-600">SolverViet</span>!</h2> <p class="mb-4 text-[15px]">Đây là nơi kết nối giữa trí tuệ và công nghệ – giúp bạn học tập, làm việc và sáng tạo hiệu quả hơn.</p> <ul class="text-left text-[14px] list-disc pl-5 space-y-1"> <li><b>AI</b>: Trò chuyện với trí tuệ nhân tạo cực kỳ thông minh</li> <li><b>Friend</b>: Nhắn tin với bạn bè, chia sẻ mọi điều</li> <li><b>SmartDoc</b>: Tổng hợp nhiều tính năng (game,văn bản,code,...)</li> <li><b>Code Smasher</b>: Mã hóa code JavaScript an toàn</li> <li><b>Service</b>: Nâng cấp gói AI để sử dụng mạnh mẽ hơn</li> </ul> <p class="mt-4 text-[14px] text-gray-600 italic"> Bạn có thể nhận thưởng khi thực hiện nhiệm vụ trong phần <a href="/user-info" class="text-cyan-600 hover:underline font-semibold">Thông tin cá nhân</a>. </p> <button onclick="dismissIntroGuide()" class="mt-6 px-5 py-2 bg-cyan-500 text-white rounded hover:bg-cyan-600 transition">Tôi đã hiểu</button> <p class="mt-4 text-[12px] text-gray-500 italic"> <i>Thank you for reading. We’ll do our best to serve you with care and dedication.</i> </p> </div> `; document.body.appendChild(overlay); } function dismissIntroGuide() { document.querySelector("body > .fixed")?.remove(); localStorage.setItem("seen_intro", "yes"); fetch("/api/set_intro_seen", { method: "POST" }).catch((err) => { console.warn("Không thể lưu trạng thái has_seen_intro:", err); }); }



