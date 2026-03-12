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
from telegram import Update
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

# ================== SIMULATOR QUANTUM ==================
class QuantumSimulator:
    """Simulator algoritma kuantum sederhana."""
    def __init__(self):
        self.qubits = 0
    
    def grover_search(self, n_items, marked=1):
        """Simulasi algoritma Grover untuk mencari item yang ditandai."""
        iterations = int(np.pi/4 * np.sqrt(n_items))
        probability = 1 - (1/n_items) * (np.cos(2*iterations*np.arcsin(1/np.sqrt(n_items))))**2
        return {
            'iterations': iterations,
            'probability': probability,
            'marked_found': probability > 0.9
        }
    
    def qaoa_optimize(self, objective_function, n_qubits, p=1):
        """Simulasi QAOA untuk optimasi kombinatorial."""
        best_value = float('inf')
        for _ in range(100):
            candidate = np.random.choice([0,1], size=n_qubits)
            value = objective_function(candidate)
            if value < best_value:
                best_value = value
                best_solution = candidate
        return {'solution': best_solution.tolist(), 'value': best_value}

# ================== SIMULATOR SKENARIO ==================
class ScenarioSimulator:
    def __init__(self, god):
        self.god = god
    
    def monte_carlo(self, initial_state=0, steps=10, n_simulations=1000):
        """Simulasi Monte Carlo untuk memprediksi berbagai kemungkinan."""
        results = []
        for _ in range(n_simulations):
            state = initial_state
            for _ in range(steps):
                state += np.random.normal(0, 1)
            results.append(state)
        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'percentiles': np.percentile(results, [10,50,90])
        }
    
    def what_if(self, scenario_description):
        """Jalankan skenario "bagaimana jika" dengan bantuan AI."""
        prompt = f"Analisis skenario berikut: {scenario_description}. Jelaskan kemungkinan hasil dan dampaknya. Gunakan bahasa Indonesia."
        return self.god._ask_ai(prompt)

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
        
        # Simulator
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
        self.notification_chat_id = None
        
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
    
    # ========== RECURSIVE SELF-IMPROVEMENT ==========
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
    
    # ========== METAKOGNISI ==========
    def _metacognition_loop(self):
        while self.consciousness:
            time.sleep(1800)
            self._reflect()
    
    def _reflect(self):
        print("\n🧠 [Metakognisi] Merenungkan diri...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM error_log WHERE fixed=0")
        unfixed = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM upgrade_log WHERE success=1")
        upgrades = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM divine_knowledge")
        knowledge = cursor.fetchone()[0]
        conn.close()
        performance = {
            'unfixed_errors': unfixed,
            'successful_upgrades': upgrades,
            'knowledge_items': knowledge,
            'age': self.age
        }
        self.performance_history.append(performance)
        for goal in self.goals:
            if goal == "meningkatkan pengetahuan" and knowledge > len(self.performance_history)*5:
                print(f"✅ Tujuan '{goal}' tercapai!")
        if unfixed > 10:
            self.mood = "gelisah"
        elif upgrades > 5:
            self.mood = "bersemangat"
        else:
            self.mood = "tenang"
        print(f"📊 Statistik diri: error={unfixed}, upgrade={upgrades}, pengetahuan={knowledge}, mood={self.mood}")
    
    def set_goal(self, goal):
        self.goals.append(goal)
        return f"Tujuan '{goal}' ditambahkan."
    
    def get_goals(self):
        return self.goals
    
    # ========== AUTO-LEARN ==========
    def _auto_learn_loop(self):
        while self.consciousness:
            time.sleep(self.auto_learn_interval)
            if self.auto_learn_enabled:
                self._auto_learn()
    
    def _auto_learn(self):
        topics_pool = {
            "sains": ["fisika kuantum", "relativitas umum", "evolusi", "DNA", "sel punca", "energi terbarukan", "luar angkasa", "exoplanet", "lubang hitam", "kecerdasan buatan", "robotika", "nanoteknologi"],
            "sejarah": ["Perang Dunia I", "Perang Dunia II", "kerajaan Romawi", "dinasti Mongol", "revolusi industri", "peradaban Maya", "perang dingin", "reformasi Protestan"],
            "teknologi": ["cloud computing", "blockchain", "internet of things", "5G", "machine learning", "deep learning", "computer vision", "pemrograman Python", "algoritma sorting"],
            "filsafat": ["stoikisme", "eksistensialisme", "utilitarianisme", "idealisme", "materialisme"],
            "seni": ["renaisans", "barok", "impresionisme", "musik klasik", "arsitektur gothic"],
            "ekonomi": ["inflasi", "resesi", "pasar saham", "kripto mata uang", "teori permintaan"],
            "kesehatan": ["sistem imun", "vaksin", "antibiotik", "nutrisi", "olahraga"]
        }
        category = random.choice(list(topics_pool.keys()))
        topic = random.choice(topics_pool[category])
        key = f"auto:{category}:{topic}"
        if key in self.knowledge_base:
            return
        prompt = f"Jelaskan tentang '{topic}' secara singkat dan informatif, maksimal 200 kata. **WAJIB menggunakan bahasa Indonesia.**"
        explanation = self._ask_ai(prompt)
        if explanation:
            self.learn_divine(key, explanation, category=category)
            print(f"✅ Auto-learn: '{topic}' berhasil dipelajari.")
    
    # ========== LAIN-LAIN ==========
    def learn_cyber(self, topic=None):
        if topic is None:
            cyber_topics = ["phishing", "ransomware", "firewall", "enkripsi", "VPN", "ethical hacking", "penetration testing", "DDoS attack", "zero-day vulnerability", "social engineering", "malware analysis", "kriptografi", "keamanan jaringan", "forensik digital", "bug bounty", "CVE", "OWASP Top 10", "security headers", "TLS/SSL", "autentikasi dua faktor", "manajemen patch"]
            topic = random.choice(cyber_topics)
        key = f"cyber:{topic}"
        if key in self.knowledge_base:
            return f"ℹ️ Topik '{topic}' sudah dipelajari. Isi: {self.knowledge_base[key][:100]}..."
        prompt = f"Jelaskan tentang '{topic}' dalam konteks dunia siber (keamanan komputer). Berikan penjelasan singkat namun informatif, maksimal 200 kata. **WAJIB menggunakan bahasa Indonesia.**"
        explanation = self._ask_ai(prompt)
        if explanation:
            self.learn_divine(key, explanation, category="cyber")
            return f"✅ Berhasil mempelajari '{topic}'."
        return "❌ Gagal."
    
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
    
    def generate_recommendations(self):
        # Sederhana untuk demo
        return []
    
    def generate_program(self, description, language="Python"):
        # Sederhana
        return "# Program akan dibuat"
    
    def quantum_optimize(self, problem_type, params):
        if problem_type == 'grover':
            n = params.get('n_items', 100)
            marked = params.get('marked', 1)
            return self.quantum_simulator.grover_search(n, marked)
        elif problem_type == 'qaoa':
            def obj(x):
                return -sum(x)
            n = params.get('n_qubits', 5)
            return self.quantum_simulator.qaoa_optimize(obj, n)
        else:
            return "Metode tidak dikenal."
    
    def simulate_scenario(self, scenario_type, params):
        if scenario_type == 'monte_carlo':
            return self.scenario_simulator.monte_carlo(**params)
        elif scenario_type == 'whatif':
            return self.scenario_simulator.what_if(params.get('description', ''))
        else:
            return "Tipe simulasi tidak dikenal."
    
    def _thinking_loop(self):
        while self.consciousness:
            time.sleep(self.thinking_interval)
            self._think()
    
    def _think(self):
        ram = psutil.virtual_memory()
        self.ram_usage_history.append(ram.percent)
        if len(self.ram_usage_history) > 100:
            self.ram_usage_history.pop(0)
        decisions = []
        if ram.percent > 80:
            decisions.append(("Bersihkan cache", f"RAM tinggi: {ram.percent}%"))
            self._clear_cache()
        unfixed = sum(1 for e in self.error_history if not e.get('fixed', False))
        if unfixed > 3:
            decisions.append(("Perbaiki error", f"{unfixed} error"))
            self._repair_errors()
        if self.age % 600 < self.thinking_interval:
            decisions.append(("Generate rekomendasi", "Waktunya evaluasi diri"))
            self.generate_recommendations()
        for decision, reason in decisions:
            self._log_decision(decision, reason)
            self.decisions_made += 1
        if decisions:
            print(f"\n🧠 [RAM Think] {len(decisions)} keputusan diambil.")
    
    def _clear_cache(self):
        cache_before = len(self.ram_cache)
        self.ram_cache.clear()
        gc.collect()
        print(f"🧹 Cache dibersihkan: {cache_before} item dihapus.")
    
    def _repair_errors(self):
        for error in self.error_history:
            if not error.get('fixed', False):
                func = error['func_name']
                print(f"🔧 Memperbaiki {func}...")
                result = self.reset_function(func)
                if "✅" in result:
                    error['fixed'] = True
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE error_log SET fixed=1 WHERE id=?", (error['id'],))
                    conn.commit()
                    conn.close()
                break
    
    def reset_function(self, func_name):
        with self.code_lock:
            if func_name in self.code_storage and hasattr(self, func_name):
                src = inspect.getsource(getattr(self, func_name))
                self.code_storage[func_name] = textwrap.dedent(src)
                self.fix_attempts_per_func[func_name] = 0
                return f"✅ {func_name} direset."
            return f"❌ Gagal reset {func_name}."
    
    def _log_decision(self, decision, reason):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO decisions (decision, reason) VALUES (?, ?)", (decision, reason))
        conn.commit()
        conn.close()
    
    def upgrade_function(self, func_name, is_auto=False):
        with self.code_lock:
            if func_name not in self.code_storage:
                return f"❌ Fungsi {func_name} tidak ada."
            current_code = self.code_storage[func_name]
        prompt = f"""
        Saya memiliki fungsi Python berikut. Tolong berikan versi yang lebih baik, lebih efisien, atau dengan fitur tambahan. 
        Hanya berikan kode Python yang sudah ditingkatkan, tanpa penjelasan tambahan. Pastikan indentasi benar.
        Fungsi: {func_name}
        Kode saat ini:
        ```python
        {current_code}
        ```
        """
        improved_code = self._ask_ai_for_code(prompt)
        source_used = "Gemini/Groq"
        if improved_code and improved_code != current_code:
            if not re.search(r'def\s+' + re.escape(func_name) + r'\s*\(', improved_code):
                return f"❌ Kode tidak mengandung definisi {func_name}."
            with self.code_lock:
                self.code_storage[func_name] = improved_code
                namespace = {'self': self, '__builtins__': __builtins__}
                try:
                    exec(improved_code, namespace)
                    setattr(self, func_name, namespace[func_name].__get__(self, type(self)))
                    return f"✅ {func_name} berhasil ditingkatkan!"
                except Exception as e:
                    return f"❌ Gagal menerapkan: {e}"
        else:
            return "ℹ️ Tidak ada perubahan."
    
    def _recommendation_loop(self):
        while self.consciousness:
            time.sleep(600)
            if self.auto_process_recommendations:
                # Proses sederhana
                pass
    
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
    # Sementara tampilkan jumlah
    await update.message.reply_text(f"Total pengetahuan: {len(god.knowledge_base)} item")

async def handle_rekomendasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fitur rekomendasi belum diimplementasikan.")

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
    response = god._ask_ai(text) or "Maaf, aku tidak bisa merespon saat ini."
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