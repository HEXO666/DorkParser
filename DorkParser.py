#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# ULTRA-FAST DORK PARSER GUI - Cyberpunk Style

import sys
import os
import subprocess
import time
import threading
import queue
import hashlib
import random
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# GUI Imports
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
import customtkinter as ctk

# Search Engine Imports
try:
    import requests
    from bs4 import BeautifulSoup
    import urllib.parse
    print("[+] Core search modules loaded ✓")
except ImportError as e:
    print(f"[!] Missing module: {e}")
    sys.exit(1)

# ==============================================
# CYBERPUNK THEME CONFIGURATION
# ==============================================
class CyberpunkTheme:
    # Colors
    BG_PRIMARY = "#0a0a0f"  # Deep space black
    BG_SECONDARY = "#101020"  # Dark blue-black
    BG_TERTIARY = "#1a1a2e"  # Dark navy
    
    ACCENT_BLUE = "#00ccff"  # Bright cyan/blue
    ACCENT_PURPLE = "#9d00ff"  # Electric purple
    ACCENT_PINK = "#ff00cc"  # Hot pink
    ACCENT_GREEN = "#00ff9d"  # Neon green
    
    TEXT_PRIMARY = "#ffffff"  # White
    TEXT_SECONDARY = "#cccccc"  # Light gray
    TEXT_DISABLED = "#666666"  # Gray
    
    BORDER_COLOR = "#00ccff"
    HOVER_COLOR = "#0055ff"
    
    # Fonts
    TITLE_FONT = ("Consolas", 20, "bold")
    HEADER_FONT = ("Consolas", 14, "bold")
    BODY_FONT = ("Consolas", 11)
    MONO_FONT = ("Consolas", 10)
    
    # Styles
    GLOW_EFFECT = {"relief": "flat", "borderwidth": 1, "highlightthickness": 1}
    PANEL_STYLE = {"bg": BG_SECONDARY, "relief": "flat", "bd": 0}

# ==============================================
# SETUP ENVIRONMENT
# ==============================================
def setup_environment():
    """Setup required dependencies"""
    try:
        import colorama
        print("[+] colorama loaded ✓")
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "colorama", "--quiet"])
    
    try:
        import customtkinter
        print("[+] customtkinter loaded ✓")
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "customtkinter", "--quiet"])
    
    # Install search dependencies
    dependencies = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "duckduckgo-search>=4.1.0",
        "googlesearch-python>=1.2.3"
    ]
    
    print("[+] Installing dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep.split('>=')[0], "--quiet"])
        except:
            pass
    
    return True

# ==============================================
# ULTRA-FAST SEARCH ENGINE
# ==============================================
class TurboSearchEngine:
    def __init__(self):
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=2)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]
    
    def url_valid(self, url):
        """Fast URL validation"""
        return url and (url.startswith('http://') or url.startswith('https://'))
    
    def duckduckgo_turbo(self, dork, max_results=10):
        """Turbo DuckDuckGo search"""
        urls = set()
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(dork, max_results=max_results))
                for r in results:
                    if 'href' in r and self.url_valid(r['href']):
                        urls.add(r['href'])
        except:
            pass
        return urls
    
    def bing_turbo(self, dork, max_results=10):
        """Turbo Bing search"""
        urls = set()
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            query = urllib.parse.quote(dork)
            url = f"https://www.bing.com/search?q={query}&count={max_results}"
            
            response = self.session.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http') and 'bing.com' not in href and self.url_valid(href):
                        urls.add(href)
                        if len(urls) >= max_results:
                            break
        except:
            pass
        return urls
    
    def google_turbo(self, dork, max_results=10):
        """Optimized Google search"""
        urls = set()
        try:
            from googlesearch import search as google_search
            results = list(google_search(dork, num_results=min(max_results, 20), sleep_interval=0.1))
            for url in results:
                if self.url_valid(url):
                    urls.add(url)
        except:
            pass
        return urls
    
    def brave_turbo(self, dork, max_results=10):
        """Turbo Brave search"""
        urls = set()
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            query = urllib.parse.quote(dork)
            url = f"https://search.brave.com/search?q={query}"
            
            response = self.session.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select('a[data-testid="result-title-a"]'):
                    href = a.get('href')
                    if href and self.url_valid(href) and 'brave.com' not in href:
                        urls.add(href)
                        if len(urls) >= max_results:
                            break
        except:
            pass
        return urls
    
    def yandex_turbo(self, dork, max_results=10):
        """Turbo Yandex search"""
        urls = set()
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            query = urllib.parse.quote(dork)
            url = f"https://yandex.com/search/?text={query}"
            
            response = self.session.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select('a.Link, a.serp-item__title-link'):
                    href = a.get('href')
                    if href and 'yandex' not in href and self.url_valid(href):
                        urls.add(href)
                        if len(urls) >= max_results:
                            break
        except:
            pass
        return urls
    
    def yahoo_turbo(self, dork, max_results=10):
        """Turbo Yahoo search"""
        urls = set()
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            query = urllib.parse.quote(dork)
            url = f"https://search.yahoo.com/search?p={query}&b=1"
            
            response = self.session.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select('a.ac-algo'):
                    href = a.get('href')
                    if href:
                        if '/RU=' in href:
                            try:
                                actual_url = href.split('/RU=')[1].split('/RK=')[0]
                                actual_url = urllib.parse.unquote(actual_url)
                                if self.url_valid(actual_url):
                                    urls.add(actual_url)
                            except:
                                pass
                        elif self.url_valid(href):
                            urls.add(href)
                        
                        if len(urls) >= max_results:
                            break
        except:
            pass
        return urls
    
    def yahoo_jp_turbo(self, dork, max_results=10):
        """Turbo Yahoo Japan search"""
        urls = set()
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            query = urllib.parse.quote(dork)
            url = f"https://search.yahoo.co.jp/search?p={query}&b=1"
            
            response = self.session.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select('a.sw-Card__link, a.Algo'):
                    href = a.get('href')
                    if href:
                        if 'https://rdsig.yahoo.co.jp' in href:
                            try:
                                actual_url = href.split('/RD=')[1].split('/R=')[0]
                                actual_url = urllib.parse.unquote(actual_url)
                                if self.url_valid(actual_url):
                                    urls.add(actual_url)
                            except:
                                pass
                        elif self.url_valid(href) and 'yahoo.co.jp' not in href:
                            urls.add(href)
                        
                        if len(urls) >= max_results:
                            break
        except:
            pass
        return urls

# ==============================================
# CYBERPUNK GUI APPLICATION
# ==============================================
class CyberpunkDorkSearcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("⚡ CYBER-DORK PARSER v4.0")
        self.geometry("1400x900")
        self.configure(fg_color=CyberpunkTheme.BG_PRIMARY)
        
        # Initialize search engine
        self.searcher = TurboSearchEngine()
        
        # Statistics
        self.processed_count = 0
        self.failed_count = 0
        self.found_urls = set()
        self.start_time = time.time()
        self.is_running = False
        self.current_output_file = ""
        
        # Setup GUI
        self.setup_gui()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Setup the cyberpunk GUI interface"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(2, weight=0)  # Status bar
        
        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_SECONDARY, height=100)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title with cyberpunk style
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ CYBER-DORK PARSER v4.0 ⚡",
            font=("Consolas", 28, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        )
        title_label.grid(row=0, column=0, pady=(20, 5))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="ULTRA-FAST SEARCH ENGINE QUERY TOOL",
            font=("Consolas", 12),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # ========== MAIN CONTENT ==========
        main_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_TERTIARY)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(main_frame, fg_color=CyberpunkTheme.BG_TERTIARY)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add tabs
        self.notebook.add("🚀 Single Search")
        self.notebook.add("💥 Mass Search")
        self.notebook.add("⚙️ Settings")
        self.notebook.add("📊 Results")
        
        # Configure tab colors
        self.notebook.configure(segmented_button_selected_color=CyberpunkTheme.ACCENT_BLUE,
                               segmented_button_selected_hover_color=CyberpunkTheme.HOVER_COLOR,
                               segmented_button_unselected_color=CyberpunkTheme.BG_SECONDARY,
                               text_color=CyberpunkTheme.TEXT_PRIMARY)
        
        # Setup each tab
        self.setup_single_search_tab()
        self.setup_mass_search_tab()
        self.setup_settings_tab()
        self.setup_results_tab()
        
        # ========== STATUS BAR ==========
        status_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_SECONDARY, height=40)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="🚀 Ready for cyber operations...",
            font=("Consolas", 10),
            text_color=CyberpunkTheme.ACCENT_GREEN
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.stats_label = ctk.CTkLabel(
            status_frame,
            text="Processed: 0 | URLs: 0 | Speed: 0.0/s",
            font=("Consolas", 10),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.stats_label.grid(row=0, column=1, padx=20, pady=10, sticky="e")
    
    def setup_single_search_tab(self):
        """Setup single dork search tab"""
        tab = self.notebook.tab("🚀 Single Search")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Main container
        container = ctk.CTkFrame(tab, fg_color=CyberpunkTheme.BG_SECONDARY)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        container.grid_columnconfigure(0, weight=1)

        container.grid_rowconfigure(0, weight=0)  # dork
        container.grid_rowconfigure(1, weight=0)  # engines
        container.grid_rowconfigure(2, weight=0)  # search options
        container.grid_rowconfigure(3, weight=0)  # action buttons
        container.grid_rowconfigure(4, weight=1)  # ✅ spacer (EMPTY)



        # ===== DORK INPUT =====
        dork_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        dork_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        dork_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            dork_frame,
            text="🔍 DORK QUERY",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        self.single_dork_entry = ctk.CTkEntry(
            dork_frame,
            placeholder_text="Enter your search dork here...",
            font=("Consolas", 12),
            height=40,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            border_color=CyberpunkTheme.BORDER_COLOR,
            text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        self.single_dork_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # ===== SEARCH ENGINES =====
        engines_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        engines_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(
            engines_frame,
            text="⚡ SEARCH ENGINES",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self.engine_vars = {}
        engines = [
            ("DuckDuckGo", "ddg", True),
            ("Bing", "bing", True),
            ("Google", "google", False),
            ("Brave", "brave", True),
            ("Yandex", "yandex", True),
            ("Yahoo", "yahoo", True),
            ("Yahoo JP", "yahoojp", True)
        ]
        for i, (name, key, default) in enumerate(engines):
            var = tk.BooleanVar(value=default)
            self.engine_vars[key] = var

            cb = ctk.CTkCheckBox(
                engines_frame,
                text=name,
                variable=var,
                font=("Consolas", 11),
                text_color=CyberpunkTheme.TEXT_PRIMARY,
                fg_color=CyberpunkTheme.ACCENT_BLUE,
                hover_color=CyberpunkTheme.HOVER_COLOR
            )
            cb.grid(row=1 + (i // 4), column=i % 4, padx=20, pady=5, sticky="w")

# ===== SEARCH OPTIONS =====
        options_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        options_frame.grid_columnconfigure(0, weight=0)
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(
            options_frame,
            text="⚙️ SEARCH OPTIONS",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))



        

        
        # Results per engine
        ctk.CTkLabel(
            options_frame,
            text="Results per engine:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.results_slider = ctk.CTkSlider(
            options_frame,
            from_=1,
            to=50,
            number_of_steps=49,
            width=200,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            progress_color=CyberpunkTheme.ACCENT_BLUE,
            button_color=CyberpunkTheme.ACCENT_PURPLE,
            button_hover_color=CyberpunkTheme.HOVER_COLOR
        )
        self.results_slider.set(20)
        self.results_slider.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        self.results_label = ctk.CTkLabel(
            options_frame,
            text="20",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.ACCENT_GREEN
        )
        self.results_label.grid(row=1, column=2, padx=(0, 20), pady=5, sticky="w")
        
        # Threads
        ctk.CTkLabel(
            options_frame,
            text="Threads:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.threads_slider = ctk.CTkSlider(
            options_frame,
            from_=1,
            to=50,
            number_of_steps=49,
            width=200,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            progress_color=CyberpunkTheme.ACCENT_BLUE,
            button_color=CyberpunkTheme.ACCENT_PURPLE,
            button_hover_color=CyberpunkTheme.HOVER_COLOR
        )
        self.threads_slider.set(10)
        self.threads_slider.grid(row=2, column=1, padx=20, pady=5, sticky="w")
        
        self.threads_label = ctk.CTkLabel(
            options_frame,
            text="10",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.ACCENT_GREEN
        )
        self.threads_label.grid(row=2, column=2, padx=(0, 20), pady=5, sticky="w")
        
        # Output file
        ctk.CTkLabel(
            options_frame,
            text="Output file:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=3, column=0, padx=20, pady=5, sticky="w")
        
        self.output_entry = ctk.CTkEntry(
            options_frame,
            placeholder_text="results_{timestamp}.txt",
            font=("Consolas", 11),
            width=300,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            border_color=CyberpunkTheme.BORDER_COLOR,
            text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        self.output_entry.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        
        browse_btn = ctk.CTkButton(
            options_frame,
            text="📁",
            width=40,
            command=self.browse_output_file,
            font=("Consolas", 12),
            fg_color=CyberpunkTheme.ACCENT_PURPLE,
            hover_color=CyberpunkTheme.HOVER_COLOR
        )
        browse_btn.grid(row=3, column=2, padx=(0, 20), pady=5, sticky="w")
        
        # ===== ACTION BUTTONS =====
        action_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        action_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        
        self.start_btn = ctk.CTkButton(
            action_frame,
            text="🚀 START SEARCH",
            command=self.start_single_search,
            font=("Consolas", 14, "bold"),
            height=50,
            fg_color=CyberpunkTheme.ACCENT_BLUE,
            hover_color=CyberpunkTheme.HOVER_COLOR,
            text_color=CyberpunkTheme.BG_PRIMARY
        )
        self.start_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            action_frame,
            text="⏹️ STOP",
            command=self.stop_search,
            font=("Consolas", 14, "bold"),
            height=50,
            fg_color=CyberpunkTheme.ACCENT_PURPLE,
            hover_color=CyberpunkTheme.HOVER_COLOR,
            text_color=CyberpunkTheme.BG_PRIMARY,
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        
        # Bind slider updates
        self.results_slider.configure(command=self.update_results_label)
        self.threads_slider.configure(command=self.update_threads_label)
    
    def setup_mass_search_tab(self):
        """Setup mass dork search tab"""
        tab = self.notebook.tab("💥 Mass Search")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        container = ctk.CTkFrame(tab, fg_color=CyberpunkTheme.BG_SECONDARY)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_columnconfigure(0, weight=1)
        
        # ===== DORK FILE SELECTION =====
        file_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        file_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        file_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            file_frame,
            text="📁 DORK FILE",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        file_select_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_select_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        file_select_frame.grid_columnconfigure(0, weight=1)
        
        self.file_entry = ctk.CTkEntry(
            file_select_frame,
            placeholder_text="Select dorks file...",
            font=("Consolas", 11),
            height=35,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            border_color=CyberpunkTheme.BORDER_COLOR,
            text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_file_btn = ctk.CTkButton(
            file_select_frame,
            text="📂 Browse",
            width=100,
            command=self.browse_dork_file,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.ACCENT_PURPLE,
            hover_color=CyberpunkTheme.HOVER_COLOR
        )
        browse_file_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.file_info_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            font=("Consolas", 10),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.file_info_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # ===== BATCH OPTIONS =====
        batch_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        batch_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        batch_frame.grid_columnconfigure(0, weight=1)
        batch_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            batch_frame,
            text="⚙️ BATCH OPTIONS",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        # Line range
        ctk.CTkLabel(
            batch_frame,
            text="Process lines:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        range_frame = ctk.CTkFrame(batch_frame, fg_color="transparent")
        range_frame.grid(row=1, column=1, sticky="w", padx=20, pady=5)
        
        self.start_line_entry = ctk.CTkEntry(
            range_frame,
            placeholder_text="Start",
            width=80,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.BG_PRIMARY,
            border_color=CyberpunkTheme.BORDER_COLOR
        )
        self.start_line_entry.grid(row=0, column=0, padx=(0, 10))
        
        ctk.CTkLabel(
            range_frame,
            text="to",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=0, column=1, padx=10)
        
        self.end_line_entry = ctk.CTkEntry(
            range_frame,
            placeholder_text="End",
            width=80,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.BG_PRIMARY,
            border_color=CyberpunkTheme.BORDER_COLOR
        )
        self.end_line_entry.grid(row=0, column=2)
        
        # Batch size
        ctk.CTkLabel(
            batch_frame,
            text="Batch size:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.batch_slider = ctk.CTkSlider(
            batch_frame,
            from_=100,
            to=10000,
            number_of_steps=99,
            width=200,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            progress_color=CyberpunkTheme.ACCENT_BLUE,
            button_color=CyberpunkTheme.ACCENT_PURPLE
        )
        self.batch_slider.set(1000)
        self.batch_slider.grid(row=2, column=1, padx=20, pady=5, sticky="w")
        
        self.batch_label = ctk.CTkLabel(
            batch_frame,
            text="1000",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.ACCENT_GREEN
        )
        self.batch_label.grid(row=2, column=2, padx=(0, 20), pady=5, sticky="w")
        
        # ===== MASS ACTION BUTTONS =====
        mass_action_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        mass_action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        mass_action_frame.grid_columnconfigure(0, weight=1)
        mass_action_frame.grid_columnconfigure(1, weight=1)
        
        self.mass_start_btn = ctk.CTkButton(
            mass_action_frame,
            text="💥 START MASS SEARCH",
            command=self.start_mass_search,
            font=("Consolas", 14, "bold"),
            height=50,
            fg_color=CyberpunkTheme.ACCENT_PURPLE,
            hover_color=CyberpunkTheme.HOVER_COLOR,
            text_color=CyberpunkTheme.BG_PRIMARY
        )
        self.mass_start_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.mass_stop_btn = ctk.CTkButton(
            mass_action_frame,
            text="⏹️ STOP",
            command=self.stop_search,
            font=("Consolas", 14, "bold"),
            height=50,
            fg_color=CyberpunkTheme.ACCENT_PINK,
            hover_color=CyberpunkTheme.HOVER_COLOR,
            text_color=CyberpunkTheme.BG_PRIMARY,
            state="disabled"
        )
        self.mass_stop_btn.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        
        # Bind slider
        self.batch_slider.configure(command=self.update_batch_label)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        tab = self.notebook.tab("⚙️ Settings")
        tab.grid_columnconfigure(0, weight=1)
        
        container = ctk.CTkFrame(tab, fg_color=CyberpunkTheme.BG_SECONDARY)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_columnconfigure(0, weight=1)
        
        # Performance settings
        perf_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        perf_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            perf_frame,
            text="⚡ PERFORMANCE SETTINGS",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Timeout
        ctk.CTkLabel(
            perf_frame,
            text="Request timeout (seconds):",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.timeout_slider = ctk.CTkSlider(
            perf_frame,
            from_=1,
            to=30,
            number_of_steps=29,
            width=200,
            fg_color=CyberpunkTheme.BG_PRIMARY,
            progress_color=CyberpunkTheme.ACCENT_BLUE
        )
        self.timeout_slider.set(10)
        self.timeout_slider.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        # Cache settings
        ctk.CTkLabel(
            perf_frame,
            text="Enable cache:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.cache_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            perf_frame,
            text="",
            variable=self.cache_var,
            fg_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=2, column=1, padx=20, pady=5, sticky="w")
        
        # Output settings
        output_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        output_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(
            output_frame,
            text="💾 OUTPUT SETTINGS",
            font=("Consolas", 14, "bold"),
            text_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Auto-save
        ctk.CTkLabel(
            output_frame,
            text="Auto-save results:",
            font=("Consolas", 11),
            text_color=CyberpunkTheme.TEXT_SECONDARY
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.autosave_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            output_frame,
            text="",
            variable=self.autosave_var,
            fg_color=CyberpunkTheme.ACCENT_BLUE
        ).grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        # Clear cache button
        clear_frame = ctk.CTkFrame(container, fg_color=CyberpunkTheme.BG_TERTIARY)
        clear_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        ctk.CTkButton(
            clear_frame,
            text="🗑️ Clear Cache",
            command=self.clear_cache,
            font=("Consolas", 12),
            fg_color=CyberpunkTheme.ACCENT_PINK,
            hover_color=CyberpunkTheme.HOVER_COLOR
        ).grid(row=0, column=0, padx=20, pady=20)
        
        ctk.CTkButton(
            clear_frame,
            text="🔄 Reset Statistics",
            command=self.reset_stats,
            font=("Consolas", 12),
            fg_color=CyberpunkTheme.ACCENT_PURPLE,
            hover_color=CyberpunkTheme.HOVER_COLOR
        ).grid(row=0, column=1, padx=20, pady=20)
    
    def setup_results_tab(self):
        """Setup results display tab"""
        tab = self.notebook.tab("📊 Results")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Results container
        results_container = ctk.CTkFrame(tab, fg_color=CyberpunkTheme.BG_SECONDARY)
        results_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        results_container.grid_columnconfigure(0, weight=1)
        results_container.grid_rowconfigure(0, weight=1)
        
        # Results text area with scrollbar
        self.results_text = ctk.CTkTextbox(
            results_container,
            font=("Consolas", 10),
            fg_color=CyberpunkTheme.BG_PRIMARY,
            text_color=CyberpunkTheme.ACCENT_GREEN,
            border_color=CyberpunkTheme.BORDER_COLOR,
            border_width=2
        )
        self.results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Results action buttons
        action_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        ctk.CTkButton(
            action_frame,
            text="📋 Copy Results",
            command=self.copy_results,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.ACCENT_BLUE,
            hover_color=CyberpunkTheme.HOVER_COLOR
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️ Clear Results",
            command=self.clear_results,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.ACCENT_PINK,
            hover_color=CyberpunkTheme.HOVER_COLOR
        ).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="💾 Save to File",
            command=self.save_results_to_file,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.ACCENT_PURPLE,
            hover_color=CyberpunkTheme.HOVER_COLOR
        ).grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="📊 Export Stats",
            command=self.export_stats,
            font=("Consolas", 11),
            fg_color=CyberpunkTheme.ACCENT_GREEN,
            hover_color=CyberpunkTheme.HOVER_COLOR
        ).grid(row=0, column=3, padx=5, pady=5)
    
    # ==============================================
    # GUI HELPER METHODS
    # ==============================================
    def update_results_label(self, value):
        self.results_label.configure(text=str(int(float(value))))
    
    def update_threads_label(self, value):
        self.threads_label.configure(text=str(int(float(value))))
    
    def update_batch_label(self, value):
        self.batch_label.configure(text=str(int(float(value))))
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)
    
    def browse_dork_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            # Count lines
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
                self.file_info_label.configure(text=f"Lines: {line_count:,} | Ready")
            except:
                self.file_info_label.configure(text="Error reading file")
    
    # ==============================================
    # SEARCH ENGINE METHODS
    # ==============================================
    def start_single_search(self):
        """Start single dork search"""
        dork = self.single_dork_entry.get().strip()
        if not dork:
            messagebox.showwarning("Warning", "Please enter a dork query!")
            return
        
        # Get selected engines
        selected_engines = []
        for key, var in self.engine_vars.items():
            if var.get():
                selected_engines.append(key)
        
        if not selected_engines:
            messagebox.showwarning("Warning", "Please select at least one search engine!")
            return
        
        # Get parameters
        max_results = int(self.results_slider.get())
        max_threads = int(self.threads_slider.get())
        
        # Get output file
        output_file = self.output_entry.get().strip()
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"single_search_{timestamp}.txt"
            self.output_entry.insert(0, output_file)
        
        self.current_output_file = output_file
        
        # Reset stats
        self.processed_count = 0
        self.failed_count = 0
        self.found_urls.clear()
        self.start_time = time.time()
        
        # Update UI
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.mass_start_btn.configure(state="disabled")
        self.mass_stop_btn.configure(state="disabled")
        
        self.status_label.configure(text="🚀 Starting single dork search...")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"🔍 Searching: {dork}\n")
        self.results_text.insert("2.0", f"📁 Output: {output_file}\n")
        self.results_text.insert("3.0", "═" * 80 + "\n\n")
        
        # Start search in thread
        thread = threading.Thread(
            target=self.run_single_search,
            args=(dork, selected_engines, max_results, max_threads, output_file),
            daemon=True
        )
        thread.start()
    
    def run_single_search(self, dork, engines, max_results, max_threads, output_file):
        """Run single search in background thread"""
        try:
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = []
                
                for engine in engines:
                    future = executor.submit(
                        self.search_worker,
                        dork,
                        engine,
                        max_results,
                        output_file
                    )
                    futures.append(future)
                
                # Wait for completion
                for future in as_completed(futures):
                    try:
                        future.result(timeout=30)
                    except:
                        pass
            
            # Search complete
            elapsed = time.time() - self.start_time
            speed = self.processed_count / elapsed if elapsed > 0 else 0
            
            self.after(0, self.update_status, 
                      f"✅ Search complete! Found {len(self.found_urls)} URLs in {elapsed:.1f}s")
            
            # Save results if autosave enabled
            if self.autosave_var.get() and self.found_urls:
                self.save_results()
                
        except Exception as e:
            self.after(0, self.update_status, f"❌ Error: {str(e)}")
        
        finally:
            self.after(0, self.search_complete)
    
    def search_worker(self, dork, engine, max_results, output_file):
        """Search worker for threading"""
        try:
            # Get engine function
            if engine == "ddg":
                urls = self.searcher.duckduckgo_turbo(dork, max_results)
            elif engine == "bing":
                urls = self.searcher.bing_turbo(dork, max_results)
            elif engine == "google":
                urls = self.searcher.google_turbo(dork, max_results)
            elif engine == "brave":
                urls = self.searcher.brave_turbo(dork, max_results)
            elif engine == "yandex":
                urls = self.searcher.yandex_turbo(dork, max_results)
            elif engine == "yahoo":
                urls = self.searcher.yahoo_turbo(dork, max_results)
            elif engine == "yahoojp":
                urls = self.searcher.yahoo_jp_turbo(dork, max_results)
            else:
                urls = set()
            
            # Update statistics
            self.processed_count += 1
            if urls:
                self.found_urls.update(urls)
                
                # Display results in GUI
                engine_name = engine.upper() if engine != "yahoojp" else "YJP"
                for url in urls:
                    self.after(0, self.add_result, f"[{engine_name}] {url}")
                
                # Save to file
                if output_file:
                    try:
                        with open(output_file, 'a', encoding='utf-8') as f:
                            for url in urls:
                                f.write(f"{url}\n")
                    except:
                        pass
            else:
                self.failed_count += 1
            
            # Update stats display
            self.after(0, self.update_stats_display)
            
        except Exception:
            self.processed_count += 1
            self.failed_count += 1
            self.after(0, self.update_stats_display)
    
    def start_mass_search(self):
        """Start mass dork search"""
        filename = self.file_entry.get().strip()
        if not filename or not os.path.exists(filename):
            messagebox.showwarning("Warning", "Please select a valid dork file!")
            return
        
        # Get parameters
        try:
            start_line = int(self.start_line_entry.get() or 1)
            end_line = int(self.end_line_entry.get() or 0)
        except:
            start_line = 1
            end_line = 0
        
        batch_size = int(self.batch_slider.get())
        
        # Get selected engines
        selected_engines = []
        for key, var in self.engine_vars.items():
            if var.get():
                selected_engines.append(key)
        
        if not selected_engines:
            messagebox.showwarning("Warning", "Please select at least one search engine!")
            return
        
        # Count lines
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
        except:
            messagebox.showerror("Error", "Could not read file!")
            return
        
        if end_line <= 0 or end_line > total_lines:
            end_line = total_lines
        
        total_dorks = end_line - start_line + 1
        
        if total_dorks <= 0:
            messagebox.showwarning("Warning", "Invalid line range!")
            return
        
        # Ask for confirmation
        if total_dorks > 1000:
            confirm = messagebox.askyesno(
                "Confirmation",
                f"Process {total_dorks:,} dorks?\nThis may take a while and use significant resources."
            )
            if not confirm:
                return
        
        # Get output file
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"mass_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not output_file:
            return
        
        self.current_output_file = output_file
        
        # Reset stats
        self.processed_count = 0
        self.failed_count = 0
        self.found_urls.clear()
        self.start_time = time.time()
        
        # Update UI
        self.is_running = True
        self.mass_start_btn.configure(state="disabled")
        self.mass_stop_btn.configure(state="normal")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        
        self.status_label.configure(text="💥 Starting mass search...")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"📁 Processing: {filename}\n")
        self.results_text.insert("2.0", f"📊 Dorks: {total_dorks:,} | Engines: {len(selected_engines)}\n")
        self.results_text.insert("3.0", f"💾 Output: {output_file}\n")
        self.results_text.insert("4.0", "═" * 80 + "\n\n")
        
        # Start mass search in thread
        thread = threading.Thread(
            target=self.run_mass_search,
            args=(filename, start_line, end_line, selected_engines, batch_size, output_file),
            daemon=True
        )
        thread.start()
    
    def run_mass_search(self, filename, start_line, end_line, engines, batch_size, output_file):
        """Run mass search in background thread"""
        try:
            # Read dorks in batches
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                # Skip to start line
                for _ in range(start_line - 1):
                    try:
                        next(f)
                    except StopIteration:
                        break
                
                current_line = start_line
                batch = []
                
                while current_line <= end_line and self.is_running:
                    line = f.readline()
                    if not line:
                        break
                    
                    line = line.strip()
                    if line and not line.startswith('#'):
                        batch.append(line)
                    
                    current_line += 1
                    
                    # Process batch
                    if len(batch) >= batch_size or current_line > end_line:
                        if batch:
                            self.process_batch(batch, engines, output_file)
                            batch = []
                        
                        # Update status
                        progress = ((current_line - start_line) / (end_line - start_line + 1)) * 100
                        self.after(0, self.update_status, 
                                  f"📊 Processing: {current_line-start_line:,}/{end_line-start_line+1:,} ({progress:.1f}%)")
            
            # Mass search complete
            elapsed = time.time() - self.start_time
            speed = self.processed_count / elapsed if elapsed > 0 else 0
            
            self.after(0, self.update_status,
                      f"✅ Mass search complete! Processed {self.processed_count:,} dorks, found {len(self.found_urls):,} URLs")
            
            # Save results if autosave enabled
            if self.autosave_var.get() and self.found_urls:
                self.save_results()
                
        except Exception as e:
            self.after(0, self.update_status, f"❌ Error: {str(e)}")
        
        finally:
            self.after(0, self.search_complete)
    
    def process_batch(self, dorks, engines, output_file):
        """Process a batch of dorks"""
        max_threads = int(self.threads_slider.get())
        max_results = int(self.results_slider.get())
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            
            for dork in dorks:
                if not self.is_running:
                    break
                
                for engine in engines:
                    future = executor.submit(
                        self.search_worker,
                        dork,
                        engine,
                        max_results,
                        output_file
                    )
                    futures.append(future)
            
            # Wait for batch completion
            for future in as_completed(futures):
                try:
                    future.result(timeout=60)
                except:
                    pass
    
    def stop_search(self):
        """Stop current search operation"""
        self.is_running = False
        self.status_label.configure(text="⏹️ Search stopped by user")
    
    def search_complete(self):
        """Cleanup after search completion"""
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.mass_start_btn.configure(state="normal")
        self.mass_stop_btn.configure(state="disabled")
        
        # Update final stats
        elapsed = time.time() - self.start_time
        speed = self.processed_count / elapsed if elapsed > 0 else 0
        
        stats_text = (f"\n{'═' * 80}\n"
                     f"📊 SEARCH COMPLETE\n"
                     f"{'═' * 80}\n"
                     f"✅ Processed: {self.processed_count:,} dorks\n"
                     f"❌ Failed: {self.failed_count:,} dorks\n"
                     f"🔗 URLs found: {len(self.found_urls):,}\n"
                     f"⏱️ Time: {elapsed:.1f} seconds\n"
                     f"⚡ Speed: {speed:.1f} dorks/second\n"
                     f"📁 Output: {self.current_output_file}")
        
        self.results_text.insert(tk.END, stats_text)
    
    # ==============================================
    # UI UPDATE METHODS
    # ==============================================
    def update_status(self, message):
        self.status_label.configure(text=message)
    
    def update_stats_display(self):
        elapsed = time.time() - self.start_time
        speed = self.processed_count / elapsed if elapsed > 0 else 0
        
        stats_text = f"Processed: {self.processed_count} | URLs: {len(self.found_urls)} | Speed: {speed:.1f}/s"
        self.stats_label.configure(text=stats_text)
    
    def add_result(self, result):
        self.results_text.insert(tk.END, result + "\n")
        # Auto-scroll to bottom
        self.results_text.see(tk.END)
    
    # ==============================================
    # UTILITY METHODS
    # ==============================================
    def save_results(self):
        """Save results to file"""
        if not self.found_urls:
            return
        
        try:
            with open(self.current_output_file, 'w', encoding='utf-8') as f:
                for url in self.found_urls:
                    f.write(f"{url}\n")
            
            file_size = os.path.getsize(self.current_output_file)
            self.add_result(f"\n💾 Results saved to: {self.current_output_file} ({file_size:,} bytes)")
        except Exception as e:
            self.add_result(f"\n❌ Error saving results: {str(e)}")
    
    def save_results_to_file(self):
        """Save current results to a file"""
        if not self.found_urls:
            messagebox.showwarning("Warning", "No results to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"dork_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for url in self.found_urls:
                        f.write(f"{url}\n")
                
                messagebox.showinfo("Success", f"Results saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    def copy_results(self):
        """Copy results to clipboard"""
        if not self.found_urls:
            messagebox.showwarning("Warning", "No results to copy!")
            return
        
        urls_text = "\n".join(self.found_urls)
        self.clipboard_clear()
        self.clipboard_append(urls_text)
        self.update_status("📋 Results copied to clipboard!")
    
    def clear_results(self):
        """Clear results display"""
        self.results_text.delete("1.0", tk.END)
        self.update_status("🗑️ Results cleared")
    
    def export_stats(self):
        """Export statistics to JSON file"""
        stats = {
            "processed": self.processed_count,
            "failed": self.failed_count,
            "urls_found": len(self.found_urls),
            "elapsed_time": time.time() - self.start_time,
            "speed": self.processed_count / (time.time() - self.start_time) if (time.time() - self.start_time) > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "output_file": self.current_output_file
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2)
                messagebox.showinfo("Success", f"Statistics exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export stats:\n{str(e)}")
    
    def clear_cache(self):
        """Clear search cache"""
        self.searcher.cache.clear()
        self.update_status("🗑️ Cache cleared")
    
    def reset_stats(self):
        """Reset statistics"""
        self.processed_count = 0
        self.failed_count = 0
        self.found_urls.clear()
        self.start_time = time.time()
        self.update_stats_display()
        self.update_status("🔄 Statistics reset")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            if messagebox.askyesno("Quit", "Search is running. Are you sure you want to quit?"):
                self.is_running = False
                self.destroy()
        else:
            self.destroy()

# ==============================================
# MAIN EXECUTION
# ==============================================
if __name__ == "__main__":
    print("⚡ CYBER-DORK PARSER v4.0")
    print("🚀 Starting cyberpunk GUI...\n")
    
    # Run setup if needed
    try:
        import customtkinter
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing required dependencies...")
        setup_environment()
    
    # Configure customtkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    ctk.set_widget_scaling(0.7)

    # Create and run app
    app = CyberpunkDorkSearcher()
    app.mainloop()