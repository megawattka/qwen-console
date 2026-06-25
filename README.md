# 🧠 Qwen Console
A console-based chat client for Qwen3 AI** – lightweight, fast, and browser‑free
---

## 📖 About

Qwen Console is a command‑line tool that lets you chat with Qwen3 AI models directly from your terminal. It handles authentication, session management, and streaming responses – giving you a simple and speedy way to interact with Qwen without opening a browser.

---

## ✨ Features

- 🔐 **Simple authentication** – Generate a token using your Qwen credentials
- 💬 **Interactive chat** – Start a conversation with a temporary chat session
- ⚡ **Streaming responses** – See the AI reply in real‑time, word by word
- 📦 **Minimal dependencies** – Built with `httpx` and `asyncio`
- 🧩 **Extensible** – The `qwen` module can be imported and used in other Python projects

---

## 📋 Prerequisites

- 🐍 Python 3.10 or higher
- 🌐 A valid Qwen AI account (email and password)

---

## 🚀 Startup

1. **Set up environment variables** – copy the example environment file and fill in your credentials:

       cp .env.dist .env

   Then edit `.env` with your Qwen email and password.

---

## 💻 Usage

### Generate an authentication token

    python gen_auth.py

This will use the credentials from your `.env` file to obtain a token and save it locally.

### Start a chat session

    python main.py

Once running, you can type your messages and see the AI’s streaming responses in real‑time. The session is temporary – close the program to end it.

---

## ⚙️ How It Works

1. **Authentication** – `gen_auth.py` reads your Qwen credentials from `.env`, sends them to the Qwen API, and stores the returned token.
2. **Chat session** – `main.py` loads the saved token, establishes a session with the Qwen chat endpoint, and enters an interactive loop.
3. **Streaming** – The client uses `httpx` and `asyncio` to receive the AI’s responses incrementally, printing each word as it arrives.
4. **Extensibility** – The `qwen` module encapsulates the API logic, so you can import it into your own Python projects for custom integrations.

---

## 📜 License

This project is licensed under the terms included in the `LICENSE` file.

---

## 👤 Author

**megawattka** – [GitHub Profile](https://github.com/megawattka)

---

## ⚠️ Disclaimer

This software is provided for educational and personal use only. Use at your own risk. The author is not responsible for any misuse, data loss, or damage caused by this software. Always keep your credentials secure and never share your `.env` file.
