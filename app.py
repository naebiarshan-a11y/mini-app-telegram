import os
import sqlite3
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# ذخیره دیتابیس دقیقاً در پوشه ای که app.py قرار دارد
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "configs.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            code TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اشتراک‌گذاری کانفیگ</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            background-color: var(--tg-theme-bg-color, #17212b);
            color: var(--tg-theme-text-color, #f5f5f5);
            font-family: Tahoma, sans-serif;
            margin: 0; padding: 15px; box-sizing: border-box;
        }
        .card {
            background-color: var(--tg-theme-secondary-bg-color, #232e3c);
            padding: 15px; border-radius: 10px; margin-bottom: 15px;
        }
        input, select, textarea {
            width: 100%; padding: 10px; margin-top: 8px; margin-bottom: 12px;
            border-radius: 6px; border: 1px solid #3d4d5e;
            background-color: var(--tg-theme-bg-color, #17212b);
            color: var(--tg-theme-text-color, #fff); box-sizing: border-box;
        }
        button {
            background-color: var(--tg-theme-button-color, #2b5278);
            color: var(--tg-theme-button-text-color, #ffffff);
            border: none; padding: 10px 15px; border-radius: 6px;
            width: 100%; cursor: pointer; font-weight: bold;
        }
        .config-item {
            background: var(--tg-theme-bg-color, #17212b);
            border: 1px solid #2b5278; padding: 12px;
            border-radius: 8px; margin-bottom: 10px;
        }
        .badge {
            background: #2b5278; padding: 3px 8px; border-radius: 4px;
            font-size: 12px; display: inline-block; margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h3>➕ ثبت کانفیگ جدید</h3>
        <input type="text" id="title" placeholder="عنوان (مثلاً: آلمان همه‌کاره)">
        <select id="type">
            <option value="VLESS">VLESS</option>
            <option value="VMess">VMess</option>
            <option value="Trojan">Trojan</option>
            <option value="Shadowsocks">Shadowsocks</option>
        </select>
        <textarea id="code" rows="3" placeholder="لینک کانفیگ را اینجا کپی کنید..."></textarea>
        <button onclick="addConfig()">ذخیره کانفیگ</button>
    </div>

    <h3>📋 لیست کانفیگ‌ها</h3>
    <div id="config-list">در حال دریافت...</div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.ready(); tg.expand();

        async function loadConfigs() {
            const res = await fetch('/api/configs');
            const configs = await res.json();
            const list = document.getElementById('config-list');
            list.innerHTML = '';
            
            if (configs.length === 0) {
                list.innerHTML = '<p style="text-align:center; opacity:0.6;">هنوز کانفیگی ثبت نشده است.</p>';
                return;
            }

            configs.forEach(c => {
                list.innerHTML += `
                    <div class="config-item">
                        <span class="badge">${c.type}</span>
                        <strong style="display:block; margin-bottom:5px;">${c.title}</strong>
                        <button onclick="copyCode('${c.code}')">📋 کپی کانفیگ</button>
                    </div>
                `;
            });
        }

        async function addConfig() {
            const title = document.getElementById('title').value;
            const type = document.getElementById('type').value;
            const code = document.getElementById('code').value;

            if (!title || !code) {
                tg.showAlert('لطفاً تمام فیلدها را پر کنید.');
                return;
            }

            await fetch('/api/configs', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, type, code})
            });

            document.getElementById('title').value = '';
            document.getElementById('code').value = '';
            if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
            loadConfigs();
        }

        function copyCode(text) {
            navigator.clipboard.writeText(text);
            if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
            tg.showAlert('کانفیگ با موفقیت کپی شد!');
        }

        loadConfigs();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/configs", methods=["GET"])
def get_configs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, type, code FROM configs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(
        [
            {"id": r[0], "title": r[1], "type": r[2], "code": r[3]}
            for r in rows
        ]
    )


@app.route("/api/configs", methods=["POST"])
def add_config():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO configs (title, type, code) VALUES (?, ?, ?)",
        (data["title"], data["type"], data["code"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)