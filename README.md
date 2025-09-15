# SLV Backend

Backend source code for **SolverViet** – a Vietnamese AI assistant & smart platform built with:

* OpenAI GPT-4o / GPT-3.5 API
* Flask + PostgreSQL + SQLAlchemy
* Admin review system
* AI chat (Lite / VIP), image generation, memory, and more

---

## 🔑 Key Features

* AI Chat Lite (free tier) + GPT VIP plan (daily quota)
* Image generation using OpenAI Vision (text-to-image or image edit)
* Emoji reaction to AI replies
* Memory system: save custom notes per user
* Feedback & rating system after each session
* Admin panel: approve VIP plans, view transactions, block users
* SmartDoc: generate documents via GPT
* Game (Vietnamese Word Chain): reward, bonus tips, leaderboard
* Auto email payment checker + Telegram bot for alerts
* Support multi-session + history + saved conversations

---

## 🧱 Tech Stack

| Layer    | Tech                           |
| -------- | ------------------------------ |
| Backend  | Flask + SQLAlchemy             |
| Database | PostgreSQL                     |
| AI Core  | OpenAI GPT API (4o, 3.5-turbo) |
| Frontend | HTML + JS (custom template)    |
| Auth     | Session-based                  |
| Others   | Caddy server, AZDIGI VPS       |

---

## 🚀 Setup & Run Locally

1. **Clone the repo**

   ```bash
   git clone https://github.com/phatslv205/slv-backend.git
   cd slv-backend
   ```

2. **Create virtual environment & install packages**

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**

   * Create database `slv_users`
   * Update your `.env` or `config.py` with your DB credentials (user/pass)

4. **Run server**

   ```bash
   python run.py
   ```

---

## 📬 Contact

Developed by [phatslv205](https://github.com/phatslv205).
For questions or custom deployment: **[phatslv205@gmail.com](mailto:phatth.viettel@gmail.com)**

---

## 📄 License

Private project – please contact the author for usage rights.
