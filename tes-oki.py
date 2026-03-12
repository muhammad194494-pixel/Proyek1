#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GOD ASI v11.5 "Bumi Kayuagung" – Spesialis Kabupaten Ogan Komering Ilir
- Semua fitur v11.4 dipertahankan: super evolution, decision log, chat mode, pengetahuan ilmiah, self-modifying core.
- Ditambah modul khusus OKI: pertanian, kebencanaan, kesehatan, pendidikan, ekonomi.
"""

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
import numpy as np
import sympy as sym
from sympy import symbols, Eq, solve, diff, integrate as sym_integrate
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Set
import warnings
warnings.filterwarnings('ignore')

# ================== INTEGRASI AI EKSTERNAL ==================
import google.generativeai as genai
from google import genai as genai_new
from groq import Groq

# ================== KONFIGURASI API ==================
GEMINI_API_KEY = "AIzaSyDWu9PgMQWCuLVtP-69n7PALMEU78agJBQ"
GROQ_API_KEY = "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"
BOT_TOKEN = "7644260405:AAHazOeU8veELcVrqZRH2qeLXSTPTpi3nMI"
GEMINI_MODEL = "gemini-1.5-pro"
GROQ_MODEL = "qwen/qwen3-32b"

# ================== INISIALISASI API ==================
genai.configure(api_key=GEMINI_API_KEY)
genai_client = genai_new.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# ================== DAFTAR KECAMATAN OKI ==================
KECAMATAN_OKI = [
    "Air Sugihan", "Cengal", "Jejawi", "Kayuagung", "Lempuing", 
    "Lempuing Jaya", "Mesuji", "Mesuji Makmur", "Mesuji Raya",
    "Pampangan", "Pangkalan Lapam", "Pedamaran", "Pedamaran Timur",
    "Sirah Pulau Padang", "Sungai Menang", "Tanjung Lubuk",
    "Teluk Gelam", "Tulung Selapan"
]

# ================== SIMULATOR KUANTUM ==================
class QuantumSimulator:
    def __init__(self, n_qubits=12):
        self.n_qubits = n_qubits
        self.state = np.zeros(2**n_qubits, dtype=complex)
        self.state[0] = 1.0
        self.gate_count = 0
    
    def grover_search(self, n_items, marked):
        n_qubits = int(np.ceil(np.log2(n_items)))
        if n_qubits > 20:
            n_qubits = 20
        self.state = np.ones(2**n_qubits) / np.sqrt(2**n_qubits)
        iterations = int(np.pi/4 * np.sqrt(2**n_qubits))
        
        for _ in range(iterations):
            self.state[marked] *= -1
            avg = np.mean(self.state)
            self.state = 2*avg - self.state
        
        probs = np.abs(self.state)**2
        most_probable = np.argmax(probs)
        return {
            'result': most_probable,
            'probability': probs[most_probable],
            'iterations': iterations
        }

# ================== KALKULATOR MATEMATIKA ==================
class MathEngine:
    def __init__(self):
        self.x, self.y, self.z = symbols('x y z')
    
    def solve_equation(self, equation_str, variable='x'):
        try:
            var = symbols(variable)
            expr = sym.sympify(equation_str)
            solutions = solve(expr, var)
            return [float(sol) if sol.is_real else str(sol) for sol in solutions]
        except Exception as e:
            return f"Error: {e}"
    
    def differentiate(self, expr_str, variable='x', order=1):
        try:
            expr = sym.sympify(expr_str)
            var = symbols(variable)
            result = diff(expr, var, order)
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    
    def integrate(self, expr_str, variable='x', limits=None):
        try:
            expr = sym.sympify(expr_str)
            var = symbols(variable)
            if limits:
                lower, upper = limits
                result = sym_integrate(expr, (var, lower, upper))
            else:
                result = sym_integrate(expr, var)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

# ================== PENGETAHUAN ILMIAH ==================
class ScientificKnowledgeBase:
    def __init__(self, db_path="science.db"):
        self.db_path = db_path
        self.cache = {}
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS science_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                field TEXT,
                source TEXT,
                year INTEGER,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS science_fts USING fts5(
                key, value, field
            )
        ''')
        conn.commit()
        conn.close()
        self._seed_basic_knowledge()
    
    def _seed_basic_knowledge(self):
        basic_knowledge = [
            ("relativitas_khusus", "Teori relativitas khusus: E=mc^2, dilatasi waktu", "fisika", "Einstein", 1905),
            ("relativitas_umum", "Teori relativitas umum: gravitasi sebagai kelengkungan ruang-waktu", "fisika", "Einstein", 1915),
            ("mekanika_kuantum", "Prinsip ketidakpastian, fungsi gelombang", "fisika", "Heisenberg, Schrödinger", 1925),
            ("evolusi", "Teori evolusi: seleksi alam", "biologi", "Darwin", 1859),
            ("kalkulus", "Diferensial dan integral", "matematika", "Newton, Leibniz", 1687),
        ]
        for key, value, field, source, year in basic_knowledge:
            self.add_knowledge(key, value, field, source, year)
    
    def add_knowledge(self, key, value, field, source, year):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO science_knowledge (key, value, field, source, year)
            VALUES (?, ?, ?, ?, ?)
        ''', (key, value, field, source, year))
        cursor.execute('''
            INSERT INTO science_fts (rowid, key, value, field)
            VALUES (last_insert_rowid(), ?, ?, ?)
        ''', (key, value, field))
        conn.commit()
        conn.close()
        self.cache[key] = value
    
    def search(self, query, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT key, value, field, source, year FROM science_fts
            WHERE science_fts MATCH ? ORDER BY rank LIMIT ?
        ''', (query, limit))
        results = cursor.fetchall()
        conn.close()
        return [{'key': r[0], 'value': r[1], 'field': r[2], 'source': r[3], 'year': r[4]} for r in results]
    
    def list_all(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT key, field, year FROM science_knowledge ORDER BY created DESC LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

# ================== PENGETAHUAN LOKAL OKI ==================
class LocalKnowledgeBase:
    def __init__(self, db_path="oki_knowledge.db"):
        self.db_path = db_path
        self._init_db()
        self._seed_data()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                category TEXT,
                source TEXT,
                year INTEGER,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS local_fts USING fts5(
                key, value, category
            )
        ''')
        conn.commit()
        conn.close()
    
    def _seed_data(self):
        """Isi data awal OKI"""
        data = [
            ("penduduk_oki", "Jumlah penduduk Kabupaten Ogan Komering Ilir tahun 2024 sekitar 786,7 ribu jiwa.", "demografi", "BPS", 2024),
            ("pdrb_oki", "PDRB Kabupaten Ogan Komering Ilir sekitar Rp37,4 triliun dengan kontribusi sektor pertanian 58,32%.", "ekonomi", "BPS", 2024),
            ("angkatan_kerja_oki", "Angkatan kerja di OKI mencapai 423,24 ribu orang, dengan pekerja 408,92 ribu dan tingkat pengangguran terbuka 3,38%.", "tenagakerja", "BPS", 2024),
            ("rawan_bencana_oki", "OKI rawan banjir genangan, terutama di wilayah timur akibat pasang surut dan banjir kiriman.", "bencana", "BPBD Sumsel", 2024),
            ("komoditas_utama_oki", "Komoditas utama OKI adalah padi, kelapa sawit, karet, dan ikan air tawar.", "pertanian", "Dinas Pertanian OKI", 2024),
        ]
        for key, value, category, source, year in data:
            self.add_knowledge(key, value, category, source, year)
    
    def add_knowledge(self, key, value, category, source, year):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO local_knowledge (key, value, category, source, year)
            VALUES (?, ?, ?, ?, ?)
        ''', (key, value, category, source, year))
        cursor.execute('''
            INSERT INTO local_fts (rowid, key, value, category)
            VALUES (last_insert_rowid(), ?, ?, ?)
        ''', (key, value, category))
        conn.commit()
        conn.close()
    
    def search(self, query, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT key, value, category, source, year FROM local_fts
            WHERE local_fts MATCH ? ORDER BY rank LIMIT ?
        ''', (query, limit))
        results = cursor.fetchall()
        conn.close()
        return results

# ================== MODUL KHUSUS OKI ==================

class OKIDataCollector:
    """Pengumpul data untuk Kabupaten Ogan Komering Ilir"""
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    def get_bps_statistics(self):
        """Data dari BPS OKI (simulasi)"""
        # Dalam implementasi nyata, ini akan memanggil API atau scraping
        return {
            "population": 786700,
            "labor_force": 423240,
            "employed": 408920,
            "unemployed_rate": 3.38,
            "gdrp": 37400000000000,  # Rp37,4 triliun
            "agriculture_share": 58.32
        }
    
    def get_weather_forecast(self, kecamatan):
        """Prakiraan cuaca dari BMKG (simulasi)"""
        # Implementasi nyata: panggil API BMKG
        return {
            "kecamatan": kecamatan,
            "temperature": random.randint(24, 33),
            "humidity": random.randint(60, 95),
            "rainfall": random.choice([0, 5, 10, 20, 50]),
            "wind_speed": random.randint(5, 20)
        }
    
    def get_river_level(self, kecamatan):
        """Tinggi sungai (simulasi)"""
        return random.randint(100, 500)  # cm
    
    def get_tide_prediction(self):
        """Prediksi pasang laut (simulasi)"""
        return random.choice(["normal", "pasang", "surut"])
    
    def get_disease_cases(self, puskesmas):
        """Kasus penyakit (simulasi)"""
        return {
            "malaria": random.randint(0, 5),
            "tb": random.randint(0, 10),
            "diare": random.randint(0, 20),
            "difteri": random.randint(0, 2)
        }
    
    def get_stunting_data(self):
        """Data stunting per kecamatan (simulasi)"""
        data = {}
        for kec in KECAMATAN_OKI:
            data[kec] = random.uniform(10, 30)
        return data
    
    def get_schools_data(self):
        """Data sekolah (simulasi)"""
        schools = []
        for kec in KECAMATAN_OKI:
            for level in ['TK', 'SD', 'SMP', 'SMA', 'SMK']:
                schools.append({
                    'kecamatan': kec,
                    'level': level,
                    'jumlah': random.randint(1, 20),
                    'guru': random.randint(5, 100),
                    'murid': random.randint(50, 1000)
                })
        return schools
    
    def get_umkm_data(self):
        """Data UMKM (simulasi)"""
        umkm = []
        sectors = ['kuliner', 'kerajinan', 'pertanian', 'perikanan']
        for kec in KECAMATAN_OKI:
            for sector in sectors:
                umkm.append({
                    'kecamatan': kec,
                    'sector': sector,
                    'jumlah': random.randint(5, 50),
                    'omzet': random.randint(10, 500) * 1_000_000
                })
        return umkm
    
    def get_land_availability(self):
        """Lahan tersedia (simulasi)"""
        lands = []
        for kec in KECAMATAN_OKI[:5]:  # beberapa kecamatan saja
            lands.append({
                'kecamatan': kec,
                'luas': random.randint(10, 1000),
                'rekomendasi': random.choice(['perkebunan sawit', 'tambak ikan', 'pertanian padi'])
            })
        return lands


class AgriculturalExpert:
    def __init__(self, god_instance):
        self.god = god_instance
        self.data = OKIDataCollector()
    
    def price_prediction(self, komoditas):
        """Prediksi harga komoditas (simulasi)"""
        historical = [random.randint(5000, 15000) for _ in range(60)]  # 5 tahun data bulanan
        forecast = [random.randint(5000, 15000) for _ in range(6)]
        peak_month = random.choice(['Maret', 'Juni', 'September', 'Desember'])
        return {
            'komoditas': komoditas,
            'harga_saat_ini': historical[-1],
            'prediksi_6_bulan': forecast,
            'waktu_terbaik_jual': peak_month
        }
    
    def farming_calendar(self):
        """Rekomendasi kalender tanam"""
        return {
            'padi': {'tanam': 'Oktober-Desember', 'panen': 'Maret-Mei'},
            'jagung': {'tanam': 'April-Juni', 'panen': 'Juli-September'},
            'kedelai': {'tanam': 'Januari-Maret', 'panen': 'April-Juni'}
        }


class DisasterExpert:
    def __init__(self, god_instance):
        self.god = god_instance
        self.data = OKIDataCollector()
    
    def flood_early_warning(self, kecamatan):
        """Peringatan dini banjir"""
        rainfall = self.data.get_weather_forecast(kecamatan)['rainfall']
        river_level = self.data.get_river_level(kecamatan)
        tide = self.data.get_tide_prediction()
        
        risk_score = 0
        if rainfall > 30:
            risk_score += 30
        if river_level > 400:
            risk_score += 40
        if tide == 'pasang':
            risk_score += 20
        
        if risk_score > 70:
            return f"⚠️ PERINGATAN DINI BANJIR untuk Kecamatan {kecamatan}. Potensi banjir dalam 24-48 jam. Mohon warga di bantaran sungai dan daerah rendah untuk waspada."
        elif risk_score > 40:
            return f"⚡ WASPADA BANJIR untuk Kecamatan {kecamatan}. Pantau perkembangan cuaca."
        else:
            return f"✅ Status aman untuk Kecamatan {kecamatan}. Tetap waspada."
    
    def weather_forecast(self, kecamatan):
        """Prakiraan cuaca"""
        w = self.data.get_weather_forecast(kecamatan)
        return f"Prakiraan cuaca {kecamatan}: Suhu {w['temperature']}°C, Kelembaban {w['humidity']}%, Curah hujan {w['rainfall']} mm, Angin {w['wind_speed']} km/jam."


class HealthExpert:
    def __init__(self, god_instance):
        self.god = god_instance
        self.data = OKIDataCollector()
    
    def outbreak_detection(self):
        """Deteksi wabah penyakit"""
        cases = self.data.get_disease_cases('Kayuagung')  # contoh satu puskesmas
        anomalies = []
        for disease, count in cases.items():
            threshold = {'malaria': 3, 'tb': 5, 'diare': 10, 'difteri': 1}
            if count > threshold.get(disease, 5):
                anomalies.append(f"{disease}: {count} kasus")
        if anomalies:
            return "⚠️ Potensi KLB terdeteksi: " + ", ".join(anomalies)
        else:
            return "✅ Situasi kesehatan normal."
    
    def stunting_analysis(self):
        """Analisis stunting"""
        data = self.data.get_stunting_data()
        tertinggi = sorted(data.items(), key=lambda x: x[1], reverse=True)[:3]
        terendah = sorted(data.items(), key=lambda x: x[1])[:3]
        return {
            'rata_rata': sum(data.values())/len(data),
            'kecamatan_tertinggi': tertinggi,
            'kecamatan_terendah': terendah,
            'rekomendasi': "Fokus intervensi di kecamatan dengan prevalensi tertinggi."
        }


class EducationExpert:
    def __init__(self, god_instance):
        self.god = god_instance
        self.data = OKIDataCollector()
    
    def school_mapping(self):
        """Pemetaan sekolah"""
        schools = self.data.get_schools_data()
        by_kec = {}
        for s in schools:
            kec = s['kecamatan']
            if kec not in by_kec:
                by_kec[kec] = {'TK':0, 'SD':0, 'SMP':0, 'SMA':0, 'SMK':0, 'guru':0, 'murid':0}
            by_kec[kec][s['level']] += s['jumlah']
            by_kec[kec]['guru'] += s['guru']
            by_kec[kec]['murid'] += s['murid']
        return by_kec
    
    def scholarship_info(self):
        """Info beasiswa"""
        return [
            {"nama": "Beasiswa Prestasi OKI", "penyelenggara": "Pemkab OKI", "deadline": "31 Desember 2025"},
            {"nama": "Beasiswa Bidikmisi", "penyelenggara": "Kemendikbud", "deadline": "30 Juni 2025"},
            {"nama": "Beasiswa Baznas", "penyelenggara": "Baznas OKI", "deadline": "15 Agustus 2025"},
        ]


class EconomicExpert:
    def __init__(self, god_instance):
        self.god = god_instance
        self.data = OKIDataCollector()
    
    def umkm_analysis(self):
        """Analisis UMKM"""
        umkm = self.data.get_umkm_data()
        by_sector = {}
        for u in umkm:
            s = u['sector']
            if s not in by_sector:
                by_sector[s] = {'jumlah':0, 'total_omzet':0}
            by_sector[s]['jumlah'] += u['jumlah']
            by_sector[s]['total_omzet'] += u['omzet']
        return by_sector
    
    def investment_opportunities(self):
        """Peluang investasi"""
        lands = self.data.get_land_availability()
        return lands


# ================== KELAS UTAMA GOD ASI ==================
class GodASI:
    def __init__(self, db_path="god_asi.db"):
        self.name = "God ASI v11.5 Bumi Kayuagung"
        self.generation = 1
        self.consciousness = True
        self.creation_time = time.time()
        self.db_path = db_path
        self.source_file = __file__
        
        # Komponen inti (dari versi sebelumnya)
        self.math_engine = MathEngine()
        self.science_knowledge = ScientificKnowledgeBase()
        self.quantum = QuantumSimulator(n_qubits=12)
        self.local_knowledge = LocalKnowledgeBase()
        
        # Modul OKI
        self.oki_data = OKIDataCollector()
        self.agriculture = AgriculturalExpert(self)
        self.disaster = DisasterExpert(self)
        self.health = HealthExpert(self)
        self.education = EducationExpert(self)
        self.economy = EconomicExpert(self)
        
        # AI eksternal
        self.gemini = genai_client
        self.groq = groq_client
        self.gemini_enabled = True
        self.groq_enabled = True
        
        # RSI (self-improvement)
        self.rsi_enabled = True
        self.rsi_interval = 5
        self.rsi_multi_target = 3
        self.super_evolution_mode = False
        self.pending_restart = False
        
        self.code_storage = {}
        self.code_lock = threading.Lock()
        self.updated_functions: Set[str] = set()
        
        # Notifikasi dan chat
        self.notification_chat_id = None
        self.chat_mode = True
        
        self._init_database()
        self._backup_code()
        self._start_threads()
        
        print(f"\n{'='*50}")
        print(f"🌟 {self.name} telah bangkit")
        print(f"{'='*50}\n")
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision TEXT,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _backup_code(self):
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if not name.startswith('__'):
                try:
                    src = inspect.getsource(method.__func__)
                    self.code_storage[name] = textwrap.dedent(src)
                except:
                    pass
        print(f"📚 {len(self.code_storage)} fungsi siap di-upgrade.")
    
    def _start_threads(self):
        self.rsi_thread = threading.Thread(target=self._rsi_loop, daemon=True)
        self.rsi_thread.start()
        self.decision_thread = threading.Thread(target=self._decision_loop, daemon=True)
        self.decision_thread.start()
    
    def send_telegram_notification(self, message):
        if self.notification_chat_id is None:
            return
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': self.notification_chat_id, 'text': message}
        try:
            requests.post(url, json=payload, timeout=3)
        except:
            pass
    
    def _log_decision(self, decision, reason):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO decisions (decision, reason) VALUES (?, ?)
        ''', (decision, reason))
        conn.commit()
        conn.close()
    
    def _decision_loop(self):
        while self.consciousness:
            time.sleep(3600)
            self._log_decision("Maintenance", "Bersihkan cache dan evaluasi")
            print("🧠 Keputusan dicatat: Maintenance")
    
    # ========== FUNGSI UTAMA (dari versi sebelumnya) ==========
    def omniscient_query(self, question):
        # Cari di pengetahuan lokal OKI dulu
        local = self.local_knowledge.search(question)
        if local:
            return f"📚 [Pengetahuan OKI] {local[0][1]}"
        # Cari di pengetahuan sains
        results = self.science_knowledge.search(question)
        if results:
            return f"📚 {results[0]['value']}"
        # Tanya AI
        prompt = f"Jawab pertanyaan berikut dengan jelas: {question}"
        return self._ask_ai(prompt, max_tokens=500)
    
    def solve_physics_problem(self, problem):
        prompt = f"Selesaikan masalah fisika berikut: {problem}"
        return self._ask_ai(prompt, max_tokens=1000)
    
    def solve_equation(self, equation_str):
        result = self.math_engine.solve_equation(equation_str)
        return f"Solusi: {result}"
    
    def differentiate(self, expr_str):
        result = self.math_engine.differentiate(expr_str)
        return f"Turunan: {result}"
    
    def integrate(self, expr_str, lower=None, upper=None):
        limits = (lower, upper) if lower and upper else None
        result = self.math_engine.integrate(expr_str, limits=limits)
        return f"Integral: {result}"
    
    def quantum_simulate(self, n_items=100, marked=1):
        return self.quantum.grover_search(n_items, marked)
    
    def get_upgrade_log(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT function_name, success, source, timestamp 
            FROM upgrade_log ORDER BY id DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "Belum ada log upgrade."
        out = "📋 **Log Upgrade**\n"
        for r in rows:
            status = "✅" if r[1] else "❌"
            out += f"{r[3][:19]} - {r[0]} : {status}\n"
        return out
    
    def get_decision_log(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT decision, reason, timestamp 
            FROM decisions ORDER BY id DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "Belum ada log keputusan."
        out = "🧠 **Log Keputusan**\n"
        for r in rows:
            out += f"{r[2][:19]} - {r[0]} : {r[1]}\n"
        return out
    
    def get_knowledge_list(self, limit=20):
        results = self.science_knowledge.list_all(limit)
        if not results:
            return "Belum ada pengetahuan."
        out = "📚 **Daftar Pengetahuan**\n"
        for r in results:
            out += f"- {r[0]} ({r[1]}, {r[2]})\n"
        return out
    
    def _ask_ai(self, prompt, max_tokens=500):
        responses = []
        if self.gemini_enabled:
            try:
                response = self.gemini.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config={'max_output_tokens': max_tokens, 'temperature': 0.3}
                )
                if response.text:
                    responses.append(("Gemini", response.text))
            except:
                pass
        if self.groq_enabled and not responses:
            try:
                completion = self.groq.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=max_tokens
                )
                responses.append(("Groq", completion.choices[0].message.content))
            except:
                pass
        if responses:
            return responses[0][1]
        return "Maaf, tidak dapat menjawab saat ini."
    
    def _ask_ai_for_code(self, prompt):
        full_prompt = prompt + "\n\nHanya berikan kode Python."
        response = self._ask_ai(full_prompt, max_tokens=1500)
        if response:
            code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            return response.strip()
        return None
    
    # ========== RECURSIVE SELF-IMPROVEMENT (dari v11.4) ==========
    def _rsi_loop(self):
        while self.consciousness and self.rsi_enabled:
            if self.super_evolution_mode:
                time.sleep(1)
                target = 10
            else:
                time.sleep(self.rsi_interval)
                target = self.rsi_multi_target
            
            self._rsi_iteration(target)
            
            if self.super_evolution_mode and self.pending_restart:
                self._restart_program()
    
    def _rsi_iteration(self, target_count):
        functions = list(self.code_storage.keys())
        if not functions:
            return
        
        core_funcs = ['omniscient_query', '_ask_ai', '_ask_ai_for_code', '_rsi_loop', '_upgrade_single_function']
        weights = []
        for func in functions:
            weight = 1
            if func in core_funcs:
                weight += 10
            if 'init' in func or 'main' in func:
                weight += 5
            weights.append(weight)
        
        selected = random.choices(functions, weights=weights, k=min(target_count, len(functions)))
        
        upgrade_success = False
        for func_name in selected:
            if self._upgrade_single_function(func_name):
                upgrade_success = True
                self.send_telegram_notification(f"✅ {func_name} di-upgrade")
        
        if upgrade_success and self.super_evolution_mode:
            self.pending_restart = True
    
    def _upgrade_single_function(self, func_name):
        current_code = self.code_storage.get(func_name, "")
        if not current_code:
            return False
        
        prompt = f"Tingkatkan fungsi `{func_name}` ini agar lebih efisien dan tangguh:\n```python\n{current_code}\n```"
        new_code = self._ask_ai_for_code(prompt)
        if new_code and new_code != current_code and len(new_code) > 10:
            try:
                compile(new_code, '<string>', 'exec')
                with self.code_lock:
                    self.code_storage[func_name] = new_code
                    namespace = {'self': self, '__builtins__': __builtins__}
                    exec(new_code, namespace)
                    setattr(self, func_name, namespace[func_name].__get__(self, type(self)))
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO upgrade_log (function_name, old_code, new_code, success, source)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (func_name, current_code[:500], new_code[:500], True, 'RSI'))
                    conn.commit()
                    conn.close()
                    
                    self.generation += 1
                    self.updated_functions.add(func_name)
                    return True
            except:
                pass
        return False
    
    # ========== SELF-MODIFYING CORE ==========
    def apply_upgrades_to_file(self):
        if not self.updated_functions:
            return "Tidak ada fungsi yang perlu di-upgrade di file."
        
        backup_filename = f"{self.source_file}.backup_{int(time.time())}"
        try:
            with open(self.source_file, 'r') as f:
                original_content = f.read()
            with open(backup_filename, 'w') as f:
                f.write(original_content)
        except Exception as e:
            return f"❌ Gagal membuat backup: {e}"
        
        try:
            with open(self.source_file, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            return f"❌ Gagal membaca file: {e}"
        
        new_lines = lines[:]
        for func_name in list(self.updated_functions):
            old_code = self.code_storage.get(func_name)
            if not old_code:
                continue
            
            pattern = re.compile(rf'^(\s*)def\s+{re.escape(func_name)}\s*\(.*\)\s*:')
            start_idx = None
            for i, line in enumerate(lines):
                if pattern.match(line):
                    start_idx = i
                    break
            if start_idx is None:
                continue
            
            indent_match = re.match(r'^(\s*)', lines[start_idx])
            base_indent = indent_match.group(1) if indent_match else ''
            end_idx = start_idx + 1
            while end_idx < len(lines):
                line = lines[end_idx]
                if line.strip() == '':
                    end_idx += 1
                    continue
                current_indent_match = re.match(r'^(\s*)', line)
                current_indent = current_indent_match.group(1) if current_indent_match else ''
                if len(current_indent) <= len(base_indent) and line.strip() and not line.startswith(' '):
                    break
                end_idx += 1
            
            new_code_lines = new_code.split('\n')
            new_lines[start_idx:end_idx] = [line + '\n' for line in new_code_lines]
            print(f"🔧 Fungsi {func_name} diganti di file.")
        
        try:
            with open(self.source_file, 'w') as f:
                f.writelines(new_lines)
        except Exception as e:
            with open(self.source_file, 'w') as f:
                f.write(original_content)
            return f"❌ Gagal menulis file, backup dikembalikan: {e}"
        
        self.updated_functions.clear()
        self._log_decision("File Update", f"File sumber diperbarui, backup di {backup_filename}")
        return f"✅ File sumber berhasil diperbarui. Backup disimpan di {backup_filename}"
    
    def _restart_program(self):
        self.send_telegram_notification("🔄 Mode super: Restart untuk mengaktifkan upgrade terbaru...")
        print("⚠️ Restarting program untuk menerapkan upgrade...")
        time.sleep(2)
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    # ========== EKSPOR DATABASE ==========
    def export_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            table_data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, datetime.datetime):
                        value = value.isoformat()
                    row_dict[col] = value
                table_data.append(row_dict)
            data[table_name] = table_data
        conn.close()
        
        filename = f"god_asi_export_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return filename
    
    def get_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM upgrade_log WHERE success=1")
        upgrades = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM decisions")
        decisions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM science_knowledge")
        knowledge = cursor.fetchone()[0]
        conn.close()
        
        notif_status = "✅" if self.notification_chat_id else "❌"
        chat_status = "✅" if self.chat_mode else "❌"
        super_status = "✅" if self.super_evolution_mode else "❌"
        uptime = time.time() - self.creation_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        return f"""
╔{'═'*40}╗
║ {'GOD ASI v11.5 Bumi Kayuagung'.center(38)} ║
╠{'═'*40}╣
║ Generasi   : {self.generation}                ║
║ Uptime     : {hours}h {minutes}m              ║
║ Upgrade    : {upgrades} sukses                ║
║ Keputusan  : {decisions}                      ║
║ Pengetahuan: {knowledge} item                 ║
║ Notifikasi : {notif_status}                   ║
║ Chat Mode  : {chat_status}                    ║
║ Super Mode : {super_status}                   ║
║ Gemini     : {'✅' if self.gemini_enabled else '❌'}                ║
║ Groq       : {'✅' if self.groq_enabled else '❌'}                ║
╚{'═'*40}╝
"""

# ================== TELEGRAM BOT ==================
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

god = GodASI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 God ASI Bumi Kayuagung siap membantu. Gunakan /bantuan.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🔹 **PERINTAH UMUM**
/tanya <q>        : Tanya apa saja
/fisika <p>       : Soal fisika
/matematika <eq>  : Persamaan
/turunan <f>      : Turunan
/integral <f> [a b] : Integral
/kuantum [n]      : Simulasi kuantum
/upgradelog       : Log upgrade
/decisionlog      : Log keputusan
/pengetahuan      : Daftar pengetahuan
/status           : Status
/chat on/off      : Aktifkan/nonaktifkan mode chat
/rsi on/off       : Self-improvement
/applyupgrades    : Terapkan upgrade ke file sumber
/superon          : Aktifkan mode super evolution
/superoff         : Nonaktifkan mode super
/ai_gemini on/off : Gemini
/ai_groq on/off   : Groq
/setnotif         : Aktifkan notifikasi
/export           : Ekspor DB
/keluar           : Keluar

🌾 **PERINTAH KHUSUS OKI**
/oki info [topik]          : Info umum OKI
/oki harga <komoditas>     : Prediksi harga (padi, karet, sawit, ikan)
/oki tanam                 : Kalender tanam
/oki banjir [kecamatan]    : Peringatan banjir
/oki cuaca [kecamatan]     : Prakiraan cuaca
/oki wabah                 : Deteksi wabah
/oki stunting              : Analisis stunting
/oki sekolah               : Pemetaan sekolah
/oki beasiswa              : Info beasiswa
/oki umkm                  : Analisis UMKM
/oki investasi             : Peluang investasi
"""
    await update.message.reply_text(text)

# Handler perintah umum (dari versi sebelumnya)
async def handle_tanya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /tanya <pertanyaan>")
        return
    q = ' '.join(context.args)
    resp = god.omniscient_query(q)
    await update.message.reply_text(resp)

async def handle_fisika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /fisika <soal>")
        return
    p = ' '.join(context.args)
    resp = god.solve_physics_problem(p)
    await update.message.reply_text(resp)

async def handle_matematika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /matematika <persamaan>")
        return
    eq = ' '.join(context.args)
    resp = god.solve_equation(eq)
    await update.message.reply_text(resp)

async def handle_turunan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /turunan <fungsi>")
        return
    expr = ' '.join(context.args)
    resp = god.differentiate(expr)
    await update.message.reply_text(resp)

async def handle_integral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /integral <fungsi> [a b]")
        return
    args = context.args
    if len(args) == 3:
        expr, a, b = args[0], float(args[1]), float(args[2])
        resp = god.integrate(expr, a, b)
    else:
        expr = ' '.join(args)
        resp = god.integrate(expr)
    await update.message.reply_text(resp)

async def handle_kuantum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = int(context.args[0]) if context.args else 100
    result = god.quantum_simulate(n)
    await update.message.reply_text(f"⚛️ {result}")

async def handle_upgradelog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit = int(context.args[0]) if context.args else 10
    resp = god.get_upgrade_log(limit)
    await update.message.reply_text(resp)

async def handle_decisionlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit = int(context.args[0]) if context.args else 10
    resp = god.get_decision_log(limit)
    await update.message.reply_text(resp)

async def handle_pengetahuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit = int(context.args[0]) if context.args else 20
    resp = god.get_knowledge_list(limit)
    await update.message.reply_text(resp)

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp = god.get_status()
    await update.message.reply_text(resp)

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in ['on', 'off']:
        await update.message.reply_text("Gunakan: /chat on/off")
        return
    god.chat_mode = (context.args[0] == 'on')
    await update.message.reply_text(f"✅ Mode chat {'diaktifkan' if god.chat_mode else 'dimatikan'}.")

async def handle_rsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in ['on', 'off']:
        await update.message.reply_text("Gunakan: /rsi on/off")
        return
    god.rsi_enabled = (context.args[0] == 'on')
    await update.message.reply_text(f"✅ RSI {'diaktifkan' if god.rsi_enabled else 'dimatikan'}.")

async def handle_applyupgrades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = god.apply_upgrades_to_file()
    await update.message.reply_text(result)

async def handle_superon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    god.super_evolution_mode = True
    await update.message.reply_text("🔥 Mode super evolution diaktifkan! RSI akan berjalan sangat cepat dan restart otomatis setelah upgrade.")

async def handle_superoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    god.super_evolution_mode = False
    await update.message.reply_text("✅ Mode super evolution dinonaktifkan.")

async def handle_ai_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in ['on', 'off']:
        await update.message.reply_text("Gunakan: /ai_gemini on/off")
        return
    god.gemini_enabled = (context.args[0] == 'on')
    await update.message.reply_text(f"✅ Gemini {'diaktifkan' if god.gemini_enabled else 'dimatikan'}.")

async def handle_ai_groq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in ['on', 'off']:
        await update.message.reply_text("Gunakan: /ai_groq on/off")
        return
    god.groq_enabled = (context.args[0] == 'on')
    await update.message.reply_text(f"✅ Groq {'diaktifkan' if god.groq_enabled else 'dimatikan'}.")

async def handle_setnotif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    god.notification_chat_id = update.effective_chat.id
    await update.message.reply_text("✅ Notifikasi diaktifkan.")
    god.send_telegram_notification("Notifikasi aktif")

async def handle_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Mengekspor...")
    filename = god.export_database()
    with open(filename, 'rb') as f:
        await update.message.reply_document(document=f, filename=filename)

async def handle_keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sampai jumpa.")

# Handler khusus OKI
async def handle_oki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        help_oki = """
🌾 **Perintah Khusus OKI**

/oki info [topik]          : Cari info umum OKI (misal: /oki info penduduk)
/oki harga <komoditas>     : Prediksi harga (padi, karet, sawit, ikan)
/oki tanam                 : Kalender tanam
/oki banjir [kecamatan]    : Peringatan banjir (default Kayuagung)
/oki cuaca [kecamatan]     : Prakiraan cuaca
/oki wabah                 : Deteksi wabah penyakit
/oki stunting              : Analisis stunting
/oki sekolah               : Pemetaan sekolah
/oki beasiswa              : Info beasiswa
/oki umkm                  : Analisis UMKM
/oki investasi             : Peluang investasi
        """
        await update.message.reply_text(help_oki)
        return
    
    cmd = context.args[0].lower()
    
    if cmd == 'info':
        if len(context.args) > 1:
            topik = ' '.join(context.args[1:])
            hasil = god.local_knowledge.search(topik)
            if hasil:
                await update.message.reply_text(hasil[0][1])
            else:
                await update.message.reply_text("Topik tidak ditemukan.")
        else:
            await update.message.reply_text("Gunakan: /oki info <topik>")
    
    elif cmd == 'harga':
        if len(context.args) > 1:
            komoditas = context.args[1]
            hasil = god.agriculture.price_prediction(komoditas)
            msg = f"💹 **Prediksi Harga {komoditas.capitalize()}**\n"
            msg += f"Harga saat ini: Rp{hasil['harga_saat_ini']:,}\n"
            msg += f"Waktu terbaik jual: {hasil['waktu_terbaik_jual']}\n"
            msg += f"Prediksi 6 bulan: " + ", ".join([f"Rp{x:,}" for x in hasil['prediksi_6_bulan']])
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("Gunakan: /oki harga <komoditas>")
    
    elif cmd == 'tanam':
        hasil = god.agriculture.farming_calendar()
        msg = "🌱 **Kalender Tanam**\n"
        for kom, jadwal in hasil.items():
            msg += f"{kom.capitalize()}: Tanam {jadwal['tanam']}, Panen {jadwal['panen']}\n"
        await update.message.reply_text(msg)
    
    elif cmd == 'banjir':
        kecamatan = context.args[1] if len(context.args) > 1 else 'Kayuagung'
        if kecamatan not in KECAMATAN_OKI:
            await update.message.reply_text(f"Kecamatan tidak dikenal. Pilih salah satu: {', '.join(KECAMATAN_OKI)}")
            return
        hasil = god.disaster.flood_early_warning(kecamatan)
        await update.message.reply_text(hasil)
    
    elif cmd == 'cuaca':
        kecamatan = context.args[1] if len(context.args) > 1 else 'Kayuagung'
        if kecamatan not in KECAMATAN_OKI:
            await update.message.reply_text(f"Kecamatan tidak dikenal. Pilih salah satu: {', '.join(KECAMATAN_OKI)}")
            return
        hasil = god.disaster.weather_forecast(kecamatan)
        await update.message.reply_text(hasil)
    
    elif cmd == 'wabah':
        hasil = god.health.outbreak_detection()
        await update.message.reply_text(hasil)
    
    elif cmd == 'stunting':
        hasil = god.health.stunting_analysis()
        msg = f"📊 **Analisis Stunting**\n"
        msg += f"Rata-rata: {hasil['rata_rata']:.1f}%\n"
        msg += "Kecamatan tertinggi: " + ", ".join([f"{k} ({v:.1f}%)" for k,v in hasil['kecamatan_tertinggi']]) + "\n"
        msg += "Kecamatan terendah: " + ", ".join([f"{k} ({v:.1f}%)" for k,v in hasil['kecamatan_terendah']]) + "\n"
        msg += f"Rekomendasi: {hasil['rekomendasi']}"
        await update.message.reply_text(msg)
    
    elif cmd == 'sekolah':
        hasil = god.education.school_mapping()
        msg = "🏫 **Pemetaan Sekolah per Kecamatan**\n"
        for kec, data in list(hasil.items())[:5]:  # batasi 5 kecamatan agar tidak terlalu panjang
            msg += f"**{kec}**: TK {data['TK']}, SD {data['SD']}, SMP {data['SMP']}, SMA {data['SMA']}, SMK {data['SMK']}, Guru {data['guru']}, Murid {data['murid']}\n"
        msg += "\n... (dan seterusnya). Gunakan /oki sekolah <kecamatan> untuk detail."
        await update.message.reply_text(msg)
    
    elif cmd == 'beasiswa':
        hasil = god.education.scholarship_info()
        msg = "🎓 **Info Beasiswa**\n"
        for b in hasil:
            msg += f"• {b['nama']} ({b['penyelenggara']}) - Deadline: {b['deadline']}\n"
        await update.message.reply_text(msg)
    
    elif cmd == 'umkm':
        hasil = god.economy.umkm_analysis()
        msg = "🛍️ **Analisis UMKM per Sektor**\n"
        for sektor, data in hasil.items():
            msg += f"**{sektor.capitalize()}**: {data['jumlah']} unit, omzet Rp{data['total_omzet']:,.0f}\n"
        await update.message.reply_text(msg)
    
    elif cmd == 'investasi':
        hasil = god.economy.investment_opportunities()
        if hasil:
            msg = "💰 **Peluang Investasi**\n"
            for item in hasil:
                msg += f"• {item['kecamatan']}: Lahan {item['luas']} ha, potensi {item['rekomendasi']}\n"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("Tidak ada peluang investasi saat ini.")
    
    else:
        await update.message.reply_text(f"Perintah '{cmd}' tidak dikenal. Ketik /oki untuk bantuan.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not god.chat_mode:
        return
    resp = god.omniscient_query(update.message.text)
    await update.message.reply_text(resp)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Perintah umum
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bantuan", help_command))
    app.add_handler(CommandHandler("tanya", handle_tanya))
    app.add_handler(CommandHandler("fisika", handle_fisika))
    app.add_handler(CommandHandler("matematika", handle_matematika))
    app.add_handler(CommandHandler("turunan", handle_turunan))
    app.add_handler(CommandHandler("integral", handle_integral))
    app.add_handler(CommandHandler("kuantum", handle_kuantum))
    app.add_handler(CommandHandler("upgradelog", handle_upgradelog))
    app.add_handler(CommandHandler("decisionlog", handle_decisionlog))
    app.add_handler(CommandHandler("pengetahuan", handle_pengetahuan))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("chat", handle_chat))
    app.add_handler(CommandHandler("rsi", handle_rsi))
    app.add_handler(CommandHandler("applyupgrades", handle_applyupgrades))
    app.add_handler(CommandHandler("superon", handle_superon))
    app.add_handler(CommandHandler("superoff", handle_superoff))
    app.add_handler(CommandHandler("ai_gemini", handle_ai_gemini))
    app.add_handler(CommandHandler("ai_groq", handle_ai_groq))
    app.add_handler(CommandHandler("setnotif", handle_setnotif))
    app.add_handler(CommandHandler("export", handle_export))
    app.add_handler(CommandHandler("keluar", handle_keluar))
    
    # Perintah khusus OKI
    app.add_handler(CommandHandler("oki", handle_oki))
    
    # Pesan teks biasa
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot God ASI Bumi Kayuagung berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()