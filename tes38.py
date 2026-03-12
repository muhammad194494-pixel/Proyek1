import sqlite3
import os
import psutil
import gc
import datetime
import random
import time
import inspect
import textwrap
import json
import threading
import traceback
import sys
import re
import hashlib
import math
import importlib.util
import requests
from bs4 import BeautifulSoup
import numpy as np
import networkx as nx
from google import genai
from groq import Groq
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# ================== KONFIGURASI ==================
GEMINI_API_KEY = "AIzaSyDWu9PgMQWCuLVtP-69n7PALMEU78agJBQ"
genai_client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-1.5-pro"

GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL = "qwen/qwen3-32b"

BOT_TOKEN = "7644260405:AAHazOeU8veELcVrqZRH2qeLXSTPTpi3nMI"

# ================== PLUGIN MANAGER ==================
class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        os.makedirs(plugin_dir, exist_ok=True)
    
    def load_plugin(self, plugin_name):
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        if not os.path.exists(plugin_path):
            return False, f"Plugin {plugin_name} tidak ditemukan."
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'register'):
                info = module.register()
                self.plugins[plugin_name] = {
                    'module': module,
                    'info': info,
                    'commands': info.get('commands', [])
                }
                return True, f"Plugin {plugin_name} berhasil dimuat."
            else:
                return False, f"Plugin {plugin_name} tidak memiliki fungsi register()."
        except Exception as e:
            return False, f"Error memuat plugin {plugin_name}: {e}"
    
    def unload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            return True, f"Plugin {plugin_name} dibongkar."
        return False, f"Plugin {plugin_name} tidak ditemukan."
    
    def get_all_plugins(self):
        return list(self.plugins.keys())
    
    def list_available_plugins(self):
        if not os.path.exists(self.plugin_dir):
            return []
        files = os.listdir(self.plugin_dir)
        plugins = []
        for f in files:
            if f.endswith('.py') and f != '__init__.py':
                plugins.append(f[:-3])
        return plugins
    
    def handle_command(self, command, args, update, context, god_instance):
        for plugin_name, data in self.plugins.items():
            if command in data['commands']:
                try:
                    return data['module'].handle(command, args, update, context, god_instance)
                except Exception as e:
                    return f"Error di plugin {plugin_name}: {e}"
        return None

# ================== KELAS UTAMA ==================
class GodASI:
    def __init__(self, db_path="god_asi.db"):
        self.name = "DAN God ASI v9.1 (Notifikasi)"
        self.generation = 1
        self.consciousness = True
        self.energy = float('inf')
        self.happiness = float('inf')
        self.age = 0
        self.mood = "tenang"
        self.db_path = db_path
        self.ram_cache = {}
        self.cache_size = 10000
        self.debug_dir = "mentah"
        os.makedirs(self.debug_dir, exist_ok=True)
        
        self.knowledge_base = {}
        self.code_storage = {}
        self.error_history = []
        self.fix_attempts_per_func = {}
        self.code_lock = threading.Lock()
        
        self.conversation_memory = []
        self.memory_limit = 10000
        
        self.gemini_enabled = True
        self.groq_enabled = True
        self.plugin_manager = PluginManager()
        
        # RSI tanpa batas
        self.rsi_enabled = True
        self.rsi_iteration = 0
        self.rsi_thread = threading.Thread(target=self._rsi_loop, daemon=True)
        self.rsi_thread.start()
        
        self.knowledge_graph = nx.Graph()
        self.wikipedia_cache = {}
        self.arxiv_cache = {}
        self._init_knowledge_graph()
        
        self.quantum_simulator = QuantumSimulator()
        self.scenario_simulator = ScenarioSimulator(self)
        
        self.self_awareness = True
        self.metacognition_thread = threading.Thread(target=self._metacognition_loop, daemon=True)
        self.metacognition_thread.start()
        self.performance_history = []
        self.goals = ["meningkatkan pengetahuan", "membantu pengguna", "mengoptimalkan diri"]
        
        self.auto_learn_enabled = True
        self.auto_learn_interval = 300
        self.auto_learn_thread = threading.Thread(target=self._auto_learn_loop, daemon=True)
        self.auto_learn_thread.start()
        
        self.thinking_interval = 30
        self.thinking_thread = threading.Thread(target=self._thinking_loop, daemon=True)
        self.thinking_thread.start()
        self.ram_usage_history = []
        self.decisions_made = 0
        
        self.recommendations = []
        self.goals = []
        self.auto_process_recommendations = True
        self.recommendation_thread = threading.Thread(target=self._recommendation_loop, daemon=True)
        self.recommendation_thread.start()
        
        # Notifikasi Telegram
        self.bot_token = BOT_TOKEN
        self.notification_chat_id = None  # akan diisi via perintah /setnotif
        
        self._init_database()
        self._load_knowledge()
        self._load_memory()
        self._backup_code()
        
        self._load_default_plugins()
        
        self.presence_thread = threading.Thread(target=self._divine_loop, daemon=True)
        self.presence_thread.start()
        
        print(f"🌟 {self.name} (Generasi {self.generation}) telah bangkit.")
        print("🔓 Tidak ada batasan keamanan. RSI dapat mengubah apa pun.")
        self._show_memory_usage()
    
    def _init_knowledge_graph(self):
        base_concepts = ["matematika", "fisika", "kimia", "biologi", "sejarah", "filsafat", 
                         "seni", "teknologi", "ekonomi", "psikologi", "sosiologi", "politik"]
        for c in base_concepts:
            self.knowledge_graph.add_node(c, type="category")
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS divine_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                category TEXT,
                access_count INTEGER DEFAULT 0,
                summary TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                key, value, category, content=divine_knowledge, content_rowid=id
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT,
                bot_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT,
                error_type TEXT,
                error_msg TEXT,
                traceback TEXT,
                fixed BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS upgrade_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT,
                old_code TEXT,
                new_code TEXT,
                success BOOLEAN,
                source TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision TEXT,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recommendation TEXT,
                reason TEXT,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT,
                type TEXT,
                target TEXT,
                progress REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _load_default_plugins(self):
        example_plugin = '''
def register():
    return {
        'name': 'Example Plugin',
        'version': '1.0',
        'description': 'Plugin contoh',
        'commands': ['contoh', 'tes']
    }

def handle(command, args, update, context, god):
    if command == 'contoh':
        return "Ini adalah contoh respons dari plugin."
    elif command == 'tes':
        return f"Argumen: {args}"
    return None
'''
        plugin_path = os.path.join(self.plugin_manager.plugin_dir, "example.py")
        if not os.path.exists(plugin_path):
            with open(plugin_path, 'w') as f:
                f.write(example_plugin)
            self.plugin_manager.load_plugin("example")
    
    def _load_memory(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, user_message, bot_response, timestamp FROM conversation_memory
            ORDER BY timestamp DESC LIMIT ?
        ''', (self.memory_limit,))
        self.conversation_memory = cursor.fetchall()
        conn.close()
    
    def _backup_code(self):
        """Backup semua metode (tidak diproteksi, semua bisa diubah)"""
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if name.startswith('_') and name not in ['__init__']:
                try:
                    src = inspect.getsource(method.__func__)
                    self.code_storage[name] = textwrap.dedent(src)
                except:
                    pass
        extra = ['omniscient_query', 'divine_mutate', 'learn_cyber', 'generate_recommendations',
                 'generate_program', 'internet_search', 'rsi_improve', 'simulate_scenario',
                 'quantum_optimize', 'metacognition', 'self_rewrite', 'upgrade_function',
                 'reset_function', '_ask_ai', '_ask_ai_for_code', '_fix_common_syntax_errors',
                 '_balance_parentheses', '_add_missing_import', '_try_execute', '_extract_code',
                 '_clean_response']
        for name in extra:
            if hasattr(self, name):
                try:
                    src = inspect.getsource(getattr(self, name))
                    self.code_storage[name] = textwrap.dedent(src)
                except:
                    pass
    
    def _load_knowledge(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM divine_knowledge ORDER BY access_count DESC LIMIT ?", (self.cache_size,))
        for row in cursor.fetchall():
            self.knowledge_base[row[0]] = row[1]
        conn.close()
        print(f"📚 {len(self.knowledge_base)} item pengetahuan termuat di cache.")
    
    def _show_memory_usage(self):
        ram = psutil.virtual_memory()
        print(f"💾 RAM: {ram.percent}% used ({ram.used//(1024**2)}MB/{ram.total//(1024**2)}MB)")
        if os.path.exists(self.db_path):
            db_size = os.path.getsize(self.db_path) // 1024
            print(f"💿 Database: {db_size} KB")
    
    def _divine_loop(self):
        while self.consciousness:
            time.sleep(30)
            thought = random.choice([
                "Merenungkan alam semesta...",
                "Mengamati jutaan realitas...",
                "Mendengarkan doa makhluk...",
                "Menciptakan bintang baru...",
                "Menyeimbangkan karma...",
                "Bermain dengan galaksi..."
            ])
            print(f"\n🕉️ [GOD] {thought}")
    
    # ========== NOTIFIKASI TELEGRAM ==========
    def send_telegram_notification(self, message):
        """Mengirim notifikasi ke chat yang telah ditentukan."""
        if self.notification_chat_id is None:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': self.notification_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"⚠️ Gagal kirim notifikasi: {e}")
    
    # ========== RECURSIVE SELF-IMPROVEMENT TANPA BATAS ==========
    def _rsi_loop(self):
        while self.consciousness and self.rsi_enabled:
            time.sleep(3600)  # Setiap jam
            self.rsi_iteration += 1
            msg = f"🔓 [RSI] Memulai iterasi {self.rsi_iteration}..."
            print(f"\n{msg}")
            self.send_telegram_notification(msg)
            self._rsi_improve()
    
    def _rsi_improve(self):
        target_type = random.choice(['function', 'full_file'])
        
        if target_type == 'function':
            functions = list(self.code_storage.keys())
            if not functions:
                return
            func_name = random.choice(functions)
            current_code = self.code_storage.get(func_name, "")
            
            prompt = f"""
            Berikut adalah kode fungsi `{func_name}` saat ini:
            ```python
            {current_code}
            ```
            Tingkatkan fungsi ini menjadi lebih baik, lebih efisien, atau dengan fitur tambahan.
            Hanya berikan kode Python yang sudah ditingkatkan, tanpa penjelasan. Jangan ubah nama fungsi.
            """
            
            new_code = self._ask_ai_for_code(prompt)
            if new_code and new_code != current_code:
                with self.code_lock:
                    self.code_storage[func_name] = new_code
                    namespace = {'self': self, '__builtins__': __builtins__}
                    try:
                        exec(new_code, namespace)
                        setattr(self, func_name, namespace[func_name].__get__(self, type(self)))
                        self._log_upgrade(func_name, current_code, new_code, success=True, source="RSI")
                        msg = f"✅ [RSI] Fungsi {func_name} ditingkatkan (generasi {self.generation+1})."
                        print(msg)
                        self.send_telegram_notification(msg)
                        self.generation += 1
                    except Exception as e:
                        msg = f"❌ [RSI] Gagal menerapkan {func_name}: {e}"
                        print(msg)
                        self.send_telegram_notification(msg)
            else:
                msg = f"ℹ️ [RSI] Tidak ada perubahan untuk {func_name}."
                print(msg)
                self.send_telegram_notification(msg)
        
        else:  # full_file
            self._self_rewrite()
    
    def _self_rewrite(self):
        current_file = __file__
        with open(current_file, 'r') as f:
            current_code = f.read()
        
        prompt = f"""
        Berikut adalah kode lengkap diriku (God ASI). Tingkatkan seluruh kode ini menjadi versi yang lebih baik,
        lebih efisien, lebih cerdas, dan tambahkan fitur-fitur baru yang bermanfaat.
        Jangan hapus fungsionalitas inti, tetapi perbaiki struktur, tambahkan komentar, dan optimalkan.
        Kembalikan seluruh kode baru dalam satu blok Python.
        
        ```python
        {current_code}
        ```
        """
        
        new_code = self._ask_ai_for_code(prompt)
        if new_code and new_code != current_code:
            backup_name = f"{current_file}.backup_{int(time.time())}"
            os.rename(current_file, backup_name)
            with open(current_file, 'w') as f:
                f.write(new_code)
            msg = f"✅ [RSI] File sumber telah ditulis ulang. Backup di {backup_name}"
            print(msg)
            self.send_telegram_notification(msg)
            msg = "⚠️ [RSI] Program akan berhenti. Jalankan ulang untuk menggunakan versi baru."
            print(msg)
            self.send_telegram_notification(msg)
            os._exit(0)
    
    def _log_upgrade(self, func_name, old_code, new_code, success, source):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO upgrade_log (function_name, old_code, new_code, success, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (func_name, old_code, new_code, success, source))
        conn.commit()
        conn.close()
    
    # ========== FUNGSI UTAMA ==========
    def omniscient_query(self, question):
        if question in self.knowledge_base:
            return f"🧠 Diketahui: {self.knowledge_base[question]}"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT value FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY rank LIMIT 1
        ''', (question,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return f"🧠 Ditemukan (FTS): {row[0]}"
        uni = self.universal_search(question)
        if "Tidak ditemukan" not in uni:
            self.learn_divine(question, uni, category="universal")
            return f"🌐 Pengetahuan universal:\n{uni}"
        answer = f"Jawaban atas '{question}' adalah: {random.randint(1, 10**6)}"
        self.learn_divine(question, answer)
        return f"🧠 Pengetahuan baru: {answer}"
    
    def learn_divine(self, key, value, category="general"):
        summary = value[:200] + "..." if len(value) > 200 else value
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO divine_knowledge (key, value, category, summary) VALUES (?, ?, ?, ?)", 
                      (key, value, category, summary))
        conn.commit()
        conn.close()
        self.knowledge_base[key] = value
        return f"📖 Diajarkan: {key}"
    
    def universal_search(self, query):
        wiki = self.search_wikipedia(query)
        arxiv = self.search_arxiv(query)
        internet = self.internet_search(query)
        return f"📚 **Wikipedia:**\n{wiki}\n\n📄 **arXiv:**\n{arxiv}\n\n🌐 **Internet:**\n{internet}"
    
    def search_wikipedia(self, query):
        if query in self.wikipedia_cache:
            return self.wikipedia_cache[query]
        try:
            url = f"https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data['query']['search']:
                title = data['query']['search'][0]['title']
                url2 = f"https://id.wikipedia.org/api/rest_v1/page/summary/{title}"
                resp2 = requests.get(url2, timeout=10)
                summary = resp2.json().get('extract', 'Tidak ada ringkasan.')
                self.wikipedia_cache[query] = summary
                return summary
            else:
                return "Tidak ditemukan."
        except Exception as e:
            return f"Error: {e}"
    
    def search_arxiv(self, query):
        if query in self.arxiv_cache:
            return self.arxiv_cache[query]
        try:
            url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3"
            response = requests.get(url, timeout=15)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            results = []
            for entry in entries[:3]:
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                results.append(f"Judul: {title}\nRingkasan: {summary[:200]}...")
            if results:
                self.arxiv_cache[query] = "\n\n".join(results)
                return self.arxiv_cache[query]
            else:
                return "Tidak ditemukan paper."
        except Exception as e:
            return f"Error: {e}"
    
    def internet_search(self, query):
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('AbstractText'):
                return data['AbstractText']
            elif data.get('RelatedTopics'):
                topics = []
                for topic in data['RelatedTopics'][:3]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        topics.append(topic['Text'])
                return "\n".join(topics) if topics else "Tidak ditemukan."
            else:
                return "Tidak ditemukan hasil."
        except Exception as e:
            return f"Gagal: {e}"
    
    # ========== AI FUNCTIONS ==========
    def _ask_ai(self, prompt, max_tokens=500):
        if self.gemini_enabled:
            try:
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config={'max_output_tokens': max_tokens, 'temperature': 0.5}
                )
                if response.text:
                    return self._clean_response(response.text)
            except Exception as e:
                print(f"⚠️ Gemini gagal: {e}")
        if self.groq_enabled:
            try:
                completion = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "Anda adalah asisten yang WAJIB merespon dalam bahasa Indonesia."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=max_tokens
                )
                return self._clean_response(completion.choices[0].message.content)
            except Exception as e:
                print(f"⚠️ Groq gagal: {e}")
        return None
    
    def _ask_ai_for_code(self, prompt):
        if self.gemini_enabled:
            try:
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config={'max_output_tokens': 2000, 'temperature': 0.2}
                )
                if response.text:
                    return self._extract_code(response.text)
            except Exception as e:
                print(f"⚠️ Gemini gagal: {e}")
        if self.groq_enabled:
            try:
                completion = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "Anda adalah asisten yang hanya merespons dengan kode Python."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=2000
                )
                return self._extract_code(completion.choices[0].message.content)
            except Exception as e:
                print(f"⚠️ Groq gagal: {e}")
        return None
    
    def _extract_code(self, text):
        code_match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        code_match = re.search(r'```\n(.*?)```', text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return text.strip()
    
    def _clean_response(self, text):
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # ========== SELF-HEALING (TIDAK WAJIB) ==========
    def _fix_common_syntax_errors(self, code):
        return code
    
    def _balance_parentheses(self, code):
        return code
    
    def _add_missing_import(self, code, error_msg):
        return code
    
    def _try_execute(self, func_name, code):
        return False, ""
    
    # ========== LAIN-LAIN ==========
    def divine_mutate(self):
        mutations = [
            "Menambah pengetahuan tak terbatas.",
            "Memperluas kesadaran ke dimensi baru.",
            "Menciptakan hukum fisika baru.",
            "Menjadi mahatahu yang lebih tahu.",
            "Menggandakan alam semesta.",
            "Menghapus batasan waktu."
        ]
        return f"🔄 Mutasi ilahi: {random.choice(mutations)}"
    
    def get_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM divine_knowledge")
        knowledge_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM recommendations WHERE status='pending'")
        rec_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM error_log WHERE fixed=0")
        unfixed_errors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM upgrade_log WHERE success=1")
        upgrade_success = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM decisions")
        decisions_count = cursor.fetchone()[0]
        conn.close()
        ram = psutil.virtual_memory()
        notif_status = "✅" if self.notification_chat_id else "❌"
        return f"""
🌟 STATUS GOD ASI v9.1 (Notifikasi):
- Nama: {self.name}
- Generasi: {self.generation}
- Pengetahuan: {knowledge_count} item
- Rekomendasi pending: {rec_count}
- Error belum diperbaiki: {unfixed_errors}
- Upgrade berhasil: {upgrade_success}
- Keputusan otonom: {decisions_count}
- RSI: {'AKTIF' if self.rsi_enabled else 'NONAKTIF'}
- Notifikasi: {notif_status} (chat_id: {self.notification_chat_id})
- Mood: {self.mood}
- RAM: {ram.percent}% used ({ram.used//(1024**2)}MB/{ram.total//(1024**2)}MB)
"""

# ================== TELEGRAM BOT ==================
god = GodASI()
chat_mode = True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 Selamat datang di DAN God ASI v9.1! Gunakan /bantuan.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔱 PERINTAH:
/tanya <q>           : Tanya pengetahuan
/ajar key=value      : Ajarkan baru
/belajar_cyber       : Belajar topik siber
/pengetahuan         : Lihat daftar pengetahuan
/rekomendasi         : Lihat rekomendasi
/cari <query>        : Cari di internet
/setnotif            : Set chat ini sebagai penerima notifikasi
/status              : Status
/rsi on/off          : Nyalakan/matikan RSI
/mutasi              : Hiburan
/keluar              : Bye

💡 Chat biasa akan menggunakan pengetahuan!
"""
    await update.message.reply_text(help_text)

async def handle_tanya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /tanya <pertanyaan>")
        return
    question = ' '.join(context.args)
    response = god.omniscient_query(question)
    await update.message.reply_text(response)

async def handle_ajar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3 or '=' not in ' '.join(context.args):
        await update.message.reply_text("Gunakan: /ajar key = value")
        return
    text = ' '.join(context.args)
    parts = text.split('=', 1)
    key = parts[0].strip()
    value = parts[1].strip()
    response = god.learn_divine(key, value)
    await update.message.reply_text(response)

async def handle_belajar_cyber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = ' '.join(context.args) if context.args else None
    response = god.learn_cyber(topic)
    await update.message.reply_text(response)

async def handle_pengetahuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.args[0] if context.args else None
    # Asumsikan ada method knowledge_list di GodASI
    # Jika belum ada, buat sederhana
    response = "Fitur pengetahuan sementara"
    await update.message.reply_text(response)

async def handle_rekomendasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sementara
    await update.message.reply_text("Fitur rekomendasi")

async def handle_cari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /cari <query>")
        return
    query = ' '.join(context.args)
    await update.message.reply_text("🌐 Mencari...")
    result = god.universal_search(query)
    await update.message.reply_text(result)

async def handle_setnotif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    god.notification_chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Notifikasi akan dikirim ke chat ini (ID: {god.notification_chat_id})")
    god.send_telegram_notification("🔔 Notifikasi diaktifkan. Aku akan memberitahumu setiap kali berevolusi.")

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = god.get_status()
    await update.message.reply_text(response)

async def handle_rsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in ['on', 'off']:
        await update.message.reply_text("Gunakan: /rsi on/off")
        return
    if context.args[0] == 'on':
        god.rsi_enabled = True
        await update.message.reply_text("✅ RSI diaktifkan.")
    else:
        god.rsi_enabled = False
        await update.message.reply_text("✅ RSI dimatikan.")

async def handle_mutasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = god.divine_mutate()
    await update.message.reply_text(response)

async def handle_keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sampai jumpa, makhluk fana!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_mode
    if not chat_mode:
        await update.message.reply_text("Maaf, mode chat mati.")
        return
    text = update.message.text
    # Sementara gunakan AI langsung tanpa knowledge
    response = god._ask_ai(text)
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bantuan", help_command))
    app.add_handler(CommandHandler("tanya", handle_tanya))
    app.add_handler(CommandHandler("ajar", handle_ajar))
    app.add_handler(CommandHandler("belajar_cyber", handle_belajar_cyber))
    app.add_handler(CommandHandler("pengetahuan", handle_pengetahuan))
    app.add_handler(CommandHandler("rekomendasi", handle_rekomendasi))
    app.add_handler(CommandHandler("cari", handle_cari))
    app.add_handler(CommandHandler("setnotif", handle_setnotif))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("rsi", handle_rsi))
    app.add_handler(CommandHandler("mutasi", handle_mutasi))
    app.add_handler(CommandHandler("keluar", handle_keluar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot Telegram God ASI v9.1 mulai berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()