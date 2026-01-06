import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
from datetime import datetime


# Após os imports, adicionar:
COUNTRIES = {
    'US': 'United States',
    'BR': 'Brazil',
    'GB': 'United Kingdom',
    'IN': 'India',
    'DE': 'Germany',
    'FR': 'France',
    'ES': 'Spain',
    'IT': 'Italy',
    'CA': 'Canada',
    'AU': 'Australia',
    'JP': 'Japan',
    'KR': 'South Korea',
    'RU': 'Russia',
    'MX': 'Mexico',
    'PT': 'Portugal',
    'NL': 'Netherlands',
    'SE': 'Sweden',
    'NO': 'Norway',
    'DK': 'Denmark',
    'FI': 'Finland',
    'PL': 'Poland',
    'TR': 'Turkey',
    'SA': 'Saudi Arabia',
    'AE': 'United Arab Emirates',
    'SG': 'Singapore',
    'MY': 'Malaysia',
    'ID': 'Indonesia',
    'PH': 'Philippines',
    'VN': 'Vietnam',
    'TH': 'Thailand',
    'CN': 'China',
    'HK': 'Hong Kong',
    'TW': 'Taiwan',
    'IL': 'Israel',
    'ZA': 'South Africa',
    'EG': 'Egypt',
    'NG': 'Nigeria',
    'KE': 'Kenya',
    'AR': 'Argentina',
    'CL': 'Chile',
    'CO': 'Colombia',
    'PE': 'Peru',
    'VE': 'Venezuela',
    'UA': 'Ukraine',
    'GR': 'Greece',
    'CZ': 'Czech Republic',
    'HU': 'Hungary',
    'RO': 'Romania',
    'BG': 'Bulgaria',
    'RS': 'Serbia',
    'HR': 'Croatia',
    'SI': 'Slovenia',
    'SK': 'Slovakia',
    'AT': 'Austria',
    'CH': 'Switzerland',
    'BE': 'Belgium',
    'IE': 'Ireland',
}




# Adicionar a pasta atual ao path para importar nossos módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Tentar importar nossos módulos
try:
    from youtube_api import YouTubeAPI
    from data_handler import DataHandler
except ImportError:
    # Criar os arquivos de módulo se não existirem
    with open('youtube_api.py', 'w') as f:
        f.write("# YouTube API module\n")
    with open('data_handler.py', 'w') as f:
        f.write("# Data handler module\n")
    
    # Importar novamente
    from youtube_api import YouTubeAPI
    from data_handler import DataHandler

class YouTubeCrawlerApp:
    def __init__(self, root):
        
        # --- PARTE 1: Configurações Iniciais ---
        self.root = root
        self.root.title("YouTube Channel Crawler v1.0")
        self.root.geometry("1000x800")
        
        # Variáveis de controle
        self.is_running = False
        self.stop_requested = False
        self.api = None
        self.master = root 

        # --- PARTE 2: Definição de Cores (Dicionários) ---
        # Definimos os dicionários aqui para estarem disponíveis
        self.light_colors = {
            'bg_dark': '#ffffff', 'bg_light': '#f0f0f0', 'accent': '#ff3333',
            'accent_dark': '#cc0000', 'text': '#000000', 'text_secondary': '#555555',
            'entry_bg': '#ffffff', 'success': '#00aa55', 'error': '#ff4444', 
            'warning': '#ff8800'
        }
        self.dark_colors = {
            'bg_dark': '#0a0a0a', 'bg_light': '#1a1a1a', 'accent': '#ff3333',
            'accent_dark': '#cc0000', 'text': '#ffffff', 'text_secondary': '#cccccc',
            'entry_bg': '#2a2a2a', 'success': '#00cc66', 'error': '#ff6666', 
            'warning': '#ff9966'
        }
        
        # Tema Inicial
        self.is_dark_mode = True 
        self.load_theme_preference()  # Carrega preferência
        self.setup_dark_theme()       # Aplica o tema (agora vai funcionar porque está separado)

        # --- PARTE 3: Correção do Caminho e DataHandler ---
        BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.EXPORT_DIR = os.path.join(BASE_DIR, "exports")
        
        # Criar pasta de exportação se não existir
        if not os.path.exists(self.EXPORT_DIR):
            os.makedirs(self.EXPORT_DIR, exist_ok=True)
        
        # Inicializa o DataHandler com o caminho correto
        self.data_handler = DataHandler(export_path=self.EXPORT_DIR)

        # --- PARTE 4: Inicialização da UI e API ---
        self.setup_ui()
        self.load_api_key()
        self.initialize_settings()

        # No __init__, após setup_ui():
        self.root.after(1000, self.test_estimate)  # Testar após 1s


    def initialize_settings(self):
        """Garante que arquivo de configuração existe"""
        try:
            # Isso força a criação do arquivo se não existir
            current_setting = self.load_cleanup_setting()
            # Se retornou True (padrão) mas arquivo não existe, cria
            config_file = os.path.join(os.path.dirname(__file__), 'config', 'cleanup_settings.json')
            if not os.path.exists(config_file):
                self.save_cleanup_setting(True)  # Cria com valor padrão
        except Exception as e:
            pass



    def test_estimate(self):
        """Teste rápido da estimativa"""
        try:
            estimate = self.calculate_quota_estimate()
            
            # Atualizar label manualmente
            self.estimate_label.config(
                text=f"Estimate: {estimate['estimate_text']}",
                fg=self.colors['accent']
            )
        except Exception as e:
            pass



    # --- FIM DO __INIT__ ---
    # --- INÍCIO DE OUTROS MÉTODOS (Fora do init, alinhado à esquerda na classe) ---

    def setup_dark_theme(self):
        """Configura o tema dark vermelho/preto"""
        self.colors = self.dark_colors
        
        # Configurar cor de fundo da janela principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configurar estilo para widgets ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar cores para widgets ttk
        self.style.configure('TFrame', background=self.colors['bg_dark'])
        self.style.configure('TLabel', background=self.colors['bg_dark'], 
                            foreground=self.colors['text'])
        self.style.configure('TLabelframe', background=self.colors['bg_dark'],
                            foreground=self.colors['text'])
        self.style.configure('TLabelframe.Label', background=self.colors['bg_dark'],
                            foreground=self.colors['accent'])


    def load_theme_preference(self):
        """Carrega preferência de tema salva"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), 'config')
            theme_file = os.path.join(config_dir, 'theme.json')
            
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    data = json.load(f)
                    self.is_dark_mode = data.get('dark_mode', True)
                    
                    if not self.is_dark_mode:
                        self.colors = self.light_colors
        except:
            pass

    def save_theme_preference(self):
        """Salva preferência de tema"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), 'config')
            os.makedirs(config_dir, exist_ok=True)
            
            theme_file = os.path.join(config_dir, 'theme.json')
            with open(theme_file, 'w') as f:
                json.dump({'dark_mode': self.is_dark_mode}, f)
        except:
            pass

    def toggle_theme(self):
        """Alterna entre light e dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            self.colors = self.dark_colors
            self.theme_btn.config(text='☀️ Light Mode')
        else:
            self.colors = self.light_colors
            self.theme_btn.config(text='🌙 Dark Mode')
        
        # Aplicar novo tema a todos os widgets
        self.apply_theme()
        self.save_theme_preference()

    def apply_theme(self):
        """Aplica o tema atual a todos os widgets"""
        # Atualizar cores da janela principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Função recursiva para atualizar todos os widgets
        def update_widget(widget):
            if isinstance(widget, tk.Label):
                if 'bg' in widget.keys():
                    widget.configure(bg=self.colors['bg_dark'], fg=self.colors['text'])
            elif isinstance(widget, tk.Button):
                if widget['text'] not in ['▶  START CRAWLING', '⏹  STOP']:
                    widget.configure(bg=self.colors['bg_light'], fg=self.colors['text'])
            elif isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                widget.configure(bg=self.colors['bg_dark'])
                if hasattr(widget, 'children'):
                    for child in widget.children.values():
                        update_widget(child)
            
            # Processar filhos
            for child in widget.winfo_children():
                update_widget(child)
        
        update_widget(self.root)


        
    def load_api_key(self):
        """Carrega a chave da API do arquivo de configuração"""
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        key_file = os.path.join(config_dir, 'api_key.txt')
        
        # Criar pasta config se não existir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        # Criar arquivo de chave se não existir
        if not os.path.exists(key_file):
            with open(key_file, 'w') as f:
                f.write("# Paste your YouTube Data API key here\n")
                f.write("# Get it from: https://console.cloud.google.com\n")
                f.write("YOUR_API_KEY_HERE\n")
            
            self.log("API key file created. Please add your key to config/api_key.txt", "WARNING")
            self.api_key = None
        else:
            # Ler chave
            with open(key_file, 'r') as f:
                lines = f.readlines()
                # Pegar primeira linha que não é comentário
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.api_key = line
                        break
                else:
                    self.api_key = None
            
            if self.api_key and self.api_key != "YOUR_API_KEY_HERE":
                try:
                    self.api = YouTubeAPI(self.api_key)


                    if hasattr(self, 'api_key_var'):
                        self.api_key_var.set(self.api_key)  # ← Preenche o campo Entry

                    self.log(f"API loaded successfully", "SUCCESS")
                    self.update_quota_display(0)
                except Exception as e:
                    self.log(f"Error loading API: {e}", "ERROR")
                    self.api = None
            else:
                self.log("Please add your API key to config/api_key.txt", "WARNING")


    def open_country_selector(self):
        """Abre janela de seleção de países"""
        selector = tk.Toplevel(self.root)
        selector.title("Select Countries")
        selector.geometry("500x600")
        selector.configure(bg=self.colors['bg_dark'])
        selector.transient(self.root)
        selector.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(selector, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Barra de busca
        search_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", bg=self.colors['bg_dark'], 
                fg=self.colors['text']).pack(side='left', padx=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, 
                            bg=self.colors['entry_bg'], fg=self.colors['text'],
                            width=30)
        search_entry.pack(side='left')
        search_entry.focus()
        
        # Frame para checkboxes com scroll
        checkbox_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        checkbox_frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(checkbox_frame, bg=self.colors['bg_dark'], 
                        highlightthickness=0)
        scrollbar = tk.Scrollbar(checkbox_frame, orient='vertical', 
                            command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Variáveis para checkboxes
        country_vars = {}
        checkboxes = {}
        
        # Criar checkboxes
        def create_checkboxes(country_list):
            # Limpar frame
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            # Botões Select All/None
            btn_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'])
            btn_frame.pack(fill='x', pady=(0, 10))
            
            tk.Button(btn_frame, text="✓ Select All", 
                    command=lambda: select_all(True),
                    bg=self.colors['accent'], fg='white',
                    padx=10, pady=3).pack(side='left', padx=5)
            
            tk.Button(btn_frame, text="✗ Select None", 
                    command=lambda: select_all(False),
                    bg=self.colors['bg_light'], fg=self.colors['text'],
                    padx=10, pady=3).pack(side='left', padx=5)
            
            # Checkboxes
            for code, name in country_list:
                var = tk.BooleanVar(value=(code in self.selected_countries))
                country_vars[code] = var
                
                cb = tk.Checkbutton(scrollable_frame, text=f"{code} - {name}",
                                variable=var, bg=self.colors['bg_dark'],
                                fg=self.colors['text'], selectcolor=self.colors['bg_light'],
                                anchor='w')
                cb.pack(fill='x', padx=5, pady=2)
                checkboxes[code] = cb
        
        def select_all(state):
            for var in country_vars.values():
                var.set(state)
        
        def filter_countries(*args):
            search_text = search_var.get().lower()
            filtered = [(code, name) for code, name in COUNTRIES.items() 
                    if search_text in code.lower() or search_text in name.lower()]
            create_checkboxes(sorted(filtered))
        
        # Inicializar
        if not hasattr(self, 'selected_countries'):
            self.selected_countries = []
        
        search_var.trace_add('write', filter_countries)
        filter_countries()  # Carregar todos inicialmente
        
        # Botões de ação
        action_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        action_frame.pack(fill='x', pady=(10, 0))
        
        def apply_selection():
            self.selected_countries = [code for code, var in country_vars.items() 
                                    if var.get()]
            selector.destroy()
            self.update_country_display()
        
        tk.Button(action_frame, text="Apply", command=apply_selection,
                bg=self.colors['accent'], fg='white', padx=20).pack(side='right')
        
        tk.Button(action_frame, text="Cancel", command=selector.destroy,
                bg=self.colors['bg_light'], fg=self.colors['text'], 
                padx=20).pack(side='right', padx=10)

    def update_country_display(self):
        """Atualiza display de países selecionados"""
        if hasattr(self, 'country_display'):
            if self.selected_countries:
                display_text = f"Selected: {len(self.selected_countries)} countries"
                if len(self.selected_countries) <= 3:
                    names = [COUNTRIES.get(code, code) for code in self.selected_countries[:3]]
                    display_text += f" ({', '.join(names)})"
            else:
                display_text = "All countries (default)"
            
            self.country_display.config(text=display_text)

    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal com scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="▸ CRAWLER",
            font=('Consolas', 18, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(pady=(0, 20))


        # Frame para API Key
        api_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        api_frame.pack(fill='x', pady=(0, 10))



        tk.Label(api_frame, text="YouTube API Key:", 
                fg=self.colors['text'], bg=self.colors['bg_dark'],
                font=('Consolas', 9)).pack(side='left', padx=(0, 10))

        # Entry (oculto por padrão)
        self.api_key_var = tk.StringVar()
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var,
                            width=40, show="*",
                            bg=self.colors['entry_bg'], fg=self.colors['text'])
        api_entry.pack(side='left')

        # Botão show/hide
        def toggle_show():
            current_show = api_entry.cget("show")
            api_entry.config(show="" if current_show == "*" else "*")
            show_btn.config(text="👁️ Show" if current_show == "*" else "👁️‍🗨️ Hide")

        show_btn = tk.Button(api_frame, text="👁️ Show",
                            command=toggle_show,
                            bg=self.colors['bg_light'], fg=self.colors['text'],
                            font=('Consolas', 8), padx=8)
        show_btn.pack(side='left', padx=5)

        # Botão save
        def save_key():
            key = self.api_key_var.get().strip()
            if key:
                self.save_api_key(key)
                self.log(f"API Key saved", "SUCCESS")

        save_btn = tk.Button(api_frame, text="💾 Save",
                            command=save_key,
                            bg=self.colors['accent'], fg='white',
                            font=('Consolas', 8), padx=10)
        save_btn.pack(side='left', padx=5)

        # Carregar key existente se houver
        if hasattr(self, 'api_key') and self.api_key:
            self.api_key_var.set(self.api_key)
    

        # ========== SEARCH SETTINGS ==========
        # No setup_ui(), modificar o search_frame:
        search_frame = tk.LabelFrame(
            main_frame,
            text=" SEARCH SETTINGS ",
            font=('Consolas', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            relief='groove',
            borderwidth=2
        )
        search_frame.pack(fill='x', pady=(0, 15))

        # Usar grid com 2 colunas
        search_frame.columnconfigure(0, weight=1)
        search_frame.columnconfigure(1, weight=1)

        # ===== COLUNA 1: Search Terms =====
        terms_label = tk.Label(
            search_frame,
            text="Search Terms (one per line):",
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 9)
        )
        terms_label.grid(row=0, column=0, sticky='w', padx=15, pady=(12, 5))

        self.terms_text = scrolledtext.ScrolledText(
            search_frame,
            height=6,
            bg=self.colors['entry_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            font=('Consolas', 9)
        )
        self.terms_text.grid(row=1, column=0, padx=15, pady=(0, 10), sticky='nsew')

        # ===== COLUNA 2: Country Picker =====
        country_label = tk.Label(
            search_frame,
            text="Search Countries (multi-select):",
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 9)
        )
        country_label.grid(row=0, column=1, sticky='w', padx=15, pady=(12, 5))

        # Frame para o country picker
        country_picker_frame = tk.Frame(
            search_frame,
            bg=self.colors['bg_light'],
            relief='sunken',
            borderwidth=1
        )
        country_picker_frame.grid(row=1, column=1, padx=15, pady=(0, 10), sticky='nsew')

        # Barra de busca para países
        search_country_frame = tk.Frame(country_picker_frame, bg=self.colors['bg_light'])
        search_country_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(search_country_frame, text="🔍", 
                bg=self.colors['bg_light'], fg=self.colors['text']).pack(side='left')

        self.country_search_var = tk.StringVar()
        country_search_entry = tk.Entry(
            search_country_frame,
            textvariable=self.country_search_var,
            bg=self.colors['entry_bg'],
            fg=self.colors['text'],
            width=20
        )
        country_search_entry.pack(side='left', padx=5)

        # Frame para checkboxes com scroll
        checkbox_container = tk.Frame(country_picker_frame, bg=self.colors['bg_light'])
        checkbox_container.pack(fill='both', expand=True, padx=5, pady=(0, 5))

        # Canvas e scrollbar
        canvas = tk.Canvas(checkbox_container, bg=self.colors['bg_light'], height=120)
        scrollbar = tk.Scrollbar(checkbox_container, orient='vertical', command=canvas.yview)
        self.country_checkbox_frame = tk.Frame(canvas, bg=self.colors['bg_light'])

        self.country_checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.country_checkbox_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Botões Select All/None
        select_btn_frame = tk.Frame(country_picker_frame, bg=self.colors['bg_light'])
        select_btn_frame.pack(fill='x', padx=5, pady=(0, 5))

        tk.Button(select_btn_frame, text="✓ Select All", 
                command=lambda: self.toggle_all_countries(True),
                bg=self.colors['accent'], fg='white',
                font=('Consolas', 8), padx=8, pady=2).pack(side='left', padx=2)

        tk.Button(select_btn_frame, text="✗ Select None", 
                command=lambda: self.toggle_all_countries(False),
                bg=self.colors['bg_light'], fg=self.colors['text'],
                font=('Consolas', 8), padx=8, pady=2).pack(side='left', padx=2)

        tk.Button(select_btn_frame, text="🌍 Popular", 
                command=self.select_popular_countries,
                bg=self.colors['bg_light'], fg=self.colors['text'],
                font=('Consolas', 8), padx=8, pady=2).pack(side='left', padx=2)

        # Status dos países selecionados
        self.country_status_label = tk.Label(
            country_picker_frame,
            text="No countries selected (global search)",
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light'],
            font=('Consolas', 8)
        )
        self.country_status_label.pack(fill='x', padx=5, pady=(0, 5))

        # Inicializar variáveis
        self.country_vars = {}
        self.selected_countries = []
        self.country_search_var.trace_add('write', self.filter_countries)


        # Carregar países
        self.load_country_checkboxes()

        # ===== VIDEOS PER TERM (abaixo das duas colunas) =====
        videos_frame = tk.Frame(search_frame, bg=self.colors['bg_dark'])
        videos_frame.grid(row=2, column=0, columnspan=2, sticky='w', padx=15, pady=(0, 15))

        tk.Label(videos_frame, text="Videos per term:", fg=self.colors['text'],
                bg=self.colors['bg_dark'], font=('Consolas', 9)).pack(side='left', padx=(0, 10))

        self.videos_var = tk.IntVar(value=10)
        self.videos_slider = tk.Scale(
            videos_frame,
            from_=1,
            to=50,
            variable=self.videos_var,
            orient='horizontal',
            length=250,
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            troughcolor=self.colors['bg_light'],
            command=self.on_slider_change
        )
        self.videos_slider.pack(side='left')

        self.videos_display = tk.Label(
            videos_frame,
            text=str(self.videos_var.get()),
            fg=self.colors['accent'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 11, 'bold')
        )
        self.videos_display.pack(side='left', padx=10)





        
        
        # ========== EXPORT SETTINGS ==========
        export_frame = tk.LabelFrame(
            main_frame,
            text=" EXPORT SETTINGS ",
            font=('Consolas', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            relief='groove',
            borderwidth=2
        )
        export_frame.pack(fill='x', pady=(0, 15))
        
        # File format
        tk.Label(
            export_frame,
            text="Export format:",
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 9)
        ).grid(row=0, column=0, sticky='w', padx=15, pady=12)
        
        self.format_var = tk.StringVar(value="excel")
        
        format_frame = tk.Frame(export_frame, bg=self.colors['bg_dark'])
        format_frame.grid(row=0, column=1, padx=10, pady=12, sticky='w')
        
        tk.Radiobutton(
            format_frame,
            text="Excel (.xlsx)",
            variable=self.format_var,
            value="excel",
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            selectcolor=self.colors['bg_light'],
            activebackground=self.colors['bg_dark'],
            activeforeground=self.colors['accent'],
            font=('Consolas', 9)
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            format_frame,
            text="CSV (.csv)",
            variable=self.format_var,
            value="csv",
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            selectcolor=self.colors['bg_light'],
            activebackground=self.colors['bg_dark'],
            activeforeground=self.colors['accent'],
            font=('Consolas', 9)
        ).pack(side='left', padx=10)
        
        # File name
        tk.Label(
            export_frame,
            text="File name:",
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 9)
        ).grid(row=1, column=0, sticky='w', padx=15, pady=(0, 12))
        
        self.filename_var = tk.StringVar(value=f"youtube_channels_{datetime.now().strftime('%Y%m%d')}")
        
        filename_entry = tk.Entry(
            export_frame,
            textvariable=self.filename_var,
            bg=self.colors['entry_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            font=('Consolas', 9),
            relief='flat',
            width=40
        )
        filename_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 12), sticky='w')








        # ========== CONTROL BUTTONS ==========
        # Linha 1: Botões principais
        btn_frame1 = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        btn_frame1.pack(pady=(10, 5))

        # Botão START
        self.start_btn = tk.Button(btn_frame1, text="▶ START CRAWLING",
                                command=self.start_crawl,
                                bg=self.colors['accent'], fg='white',
                                font=('Consolas', 11, 'bold'),
                                padx=25, pady=10, cursor='hand2')
        self.start_btn.pack(side='left', padx=5)

        # Botão STOP
        self.stop_btn = tk.Button(btn_frame1, text="⏹ STOP",
                                command=self.stop_crawl,
                                bg='#555555', fg='white',
                                font=('Consolas', 11),
                                padx=25, pady=10, state='disabled',
                                cursor='hand2')
        self.stop_btn.pack(side='left', padx=5)

        # Linha 2: Botões utilitários (alinhados à direita)
        btn_frame2 = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        btn_frame2.pack(fill='x', pady=(0, 10))


        # Container para botões à direita
        utils_frame = tk.Frame(btn_frame2, bg=self.colors['bg_dark'])
        utils_frame.pack(side='right')

        # Botão OPEN EXPORTS
        export_btn = tk.Button(utils_frame, text="📁 OPEN EXPORTS",
                            command=self.open_export_folder,
                            bg=self.colors['bg_light'], fg=self.colors['text'],
                            font=('Consolas', 9), padx=15, pady=6)
        export_btn.pack(side='left', padx=5)

        # Botão THEME TOGGLE
        self.theme_btn = tk.Button(utils_frame,
                                text="🌙 DARK MODE" if self.is_dark_mode else "☀️ LIGHT MODE",
                                command=self.toggle_theme,
                                bg=self.colors['bg_light'], fg=self.colors['text'],
                                font=('Consolas', 9), padx=15, pady=6)
        self.theme_btn.pack(side='left', padx=5)


        # Botão VIEW HISTORY
        view_history_btn = tk.Button(utils_frame, text="📋 HISTORY",
                                    command=self.view_history,
                                    bg=self.colors['bg_light'], fg=self.colors['text'],
                                    font=('Consolas', 9), padx=15, pady=6)
        view_history_btn.pack(side='left', padx=5)

        # Botão CLEAR HISTORY
        self.clear_btn = tk.Button(utils_frame, text="🗑️ CLEAR",
                                command=self.safe_clear_history,
                                bg=self.colors['bg_light'], fg=self.colors['text'],
                                font=('Consolas', 9), padx=15, pady=6)
        self.clear_btn.pack(side='left', padx=5)




        # ========== PROGRESS SECTION ==========
        progress_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        progress_frame.pack(fill='x', pady=(15, 10))
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        
        # Container da barra de progresso com borda
        progress_container = tk.Frame(
            progress_frame,
            bg=self.colors['bg_light'],
            highlightthickness=1,
            highlightbackground=self.colors['accent']
        )
        progress_container.pack(fill='x', padx=20, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_container,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', padx=2, pady=2)
        
        # Status label
        self.status_label = tk.Label(
            progress_frame,
            text="🟢 Ready to start",
            fg=self.colors['success'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 10)
        )
        self.status_label.pack()
        
        # ========== LOG DISPLAY ==========
        log_frame = tk.LabelFrame(
            main_frame,
            text=" EXECUTION LOG ",
            font=('Consolas', 11, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['bg_dark'],
            relief='groove'
        )
        log_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Área de log
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            font=('Consolas', 9),
            relief='flat'
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurar tags para cores no log
        self.log_text.tag_config('info', foreground=self.colors['text'])
        self.log_text.tag_config('success', foreground=self.colors['success'])
        self.log_text.tag_config('warning', foreground=self.colors['warning'])
        self.log_text.tag_config('error', foreground=self.colors['error'])
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])  # ← CRIAR OU USAR EXISTENTE
        footer_frame.pack(fill='x', side='bottom', pady=(10, 0))

        # Frame de quota
        quota_frame = tk.Frame(footer_frame, bg=self.colors['bg_dark'])
        quota_frame.pack(side='left')

        # Label de quota atual
        self.quota_label = tk.Label(quota_frame,
            text="Quota: 0 / 10,000 units | Channels: 0",
            fg=self.colors['success'], bg=self.colors['bg_dark'],
            font=('Consolas', 9))
        self.quota_label.pack(side='left', padx=(0, 10))

        # Barra de progresso da quota
        self.quota_bar = ttk.Progressbar(quota_frame, length=100, mode='determinate')
        self.quota_bar.pack(side='left')
        self.quota_bar['value'] = 0




        # No setup_ui, na seção de botões utilitários:
        refresh_btn = tk.Button(footer_frame, text="🔄 Quota",
                            command=lambda: self.update_quota_display(),
                            bg=self.colors['bg_light'], fg=self.colors['text'],
                            font=('Consolas', 8), padx=8, pady=2)
        refresh_btn.pack(side='left', padx=2)












        # Separador
        tk.Label(footer_frame, text=" | ", 
                fg=self.colors['text_secondary'], bg=self.colors['bg_dark'],
                font=('Consolas', 9)).pack(side='left', padx=5)

        # Label de estimativa
        self.estimate_label = tk.Label(footer_frame,
            text="Estimate: -- units",
            fg=self.colors['text_secondary'], bg=self.colors['bg_dark'],
            font=('Consolas', 8))
        self.estimate_label.pack(side='left', padx=5)

        # Botão para recalcular estimativa
        tk.Button(footer_frame, text="📊", 
                command=self.calculate_quota_estimate,
                bg=self.colors['bg_light'], fg=self.colors['text'],
                font=('Consolas', 8), padx=3).pack(side='left', padx=2)

        # Versão
        version_label = tk.Label(
            footer_frame,
            text="v1.0 | YouTube Data API",
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_dark'],
            font=('Consolas', 8)
        )
        version_label.pack(side='right')



    def save_api_key(self, key=None):
        """Salva API key do campo na interface"""
        if key is None:
            key = self.api_key_var.get().strip()
        
        if not key:
            self.log("❌ API Key cannot be empty", "ERROR")
            return
        
        try:
            # Salvar em arquivo
            config_dir = os.path.join(os.path.dirname(__file__), 'config')
            os.makedirs(config_dir, exist_ok=True)
            
            key_file = os.path.join(config_dir, 'api_key.txt')
            with open(key_file, 'w') as f:
                f.write(key)
            
            # Atualizar variáveis
            self.api_key = key
            self.api = YouTubeAPI(key)
            
            self.update_quota_display(0, 0)         
            self.log("✅ API Key saved and validated", "SUCCESS")
            messagebox.showinfo("Success", "API Key saved successfully!")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            messagebox.showerror("API Error", f"Invalid API Key or connection error:\n{str(e)}")


        
    def on_slider_change(self, value):
        """Atualiza o display do slider"""
        self.videos_display.config(text=str(int(float(value))))
    
    def log(self, message, level="INFO"):
        """Adiciona mensagem ao log com cores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, f"{formatted_msg}\n", level.lower())
        self.log_text.see(tk.END)
        
        # Atualizar interface imediatamente
        self.root.update_idletasks()

        

    def update_quota_display(self, quota_used=None, channels_found=0):
        """Atualiza display de quota - CORRIGIDO"""
        try:
            # Se não passou quota_used, pega do API se existir
            if quota_used is None:
                if hasattr(self, 'api') and self.api:
                    quota_used = self.api.get_quota_used()
                else:
                    quota_used = 0
            
            quota_total = 10000
            percent = min(100, (quota_used / quota_total) * 100) if quota_total > 0 else 0
            
            # Atualizar label
            self.quota_label.config(
                text=f"Quota: {quota_used:,} / {quota_total:,} units | Channels: {channels_found}"
            )
            
            # Atualizar barra de progresso
            self.quota_bar['value'] = percent
            
            # Cores por uso
            if percent > 90:
                color = self.colors['error']
            elif percent > 70:
                color = self.colors['warning']
            else:
                color = self.colors['success']
            
            self.quota_label.config(fg=color)
            
            # Forçar atualização da interface
            self.root.update_idletasks()
            
        except Exception as e:
            pass



    def safe_clear_history(self):
        """Limpa histórico com confirmação - usar esta como callback do botão"""
        stats = self.data_handler.get_history_stats()
        
        if not stats['history_exists'] and stats['cache_count'] == 0:
            messagebox.showinfo("Info", "No history or cache to clear.")
            return
        
        confirm_msg = f"""
        You are about to clear:
        
        • Crawler History: {stats['session_count']} entries
        • Channel Cache: {stats['cache_count']} cached channel IDs
        
        This action cannot be undone!
        
        Are you sure you want to proceed?
        """
        
        if messagebox.askyesno("⚠️ WARNING", confirm_msg, icon='warning'):
            self.open_clear_dialog()




    def open_clear_dialog(self):
        """Abre diálogo para limpar histórico/cache com informações de expiração"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Clear History & Cache")
        dialog.geometry("600x550")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Título
        tk.Label(main_frame, text="🗑️ CLEAR HISTORY & CACHE", 
                font=('Consolas', 12, 'bold'),
                fg=self.colors['accent'],
                bg=self.colors['bg_dark']).pack(pady=(0, 20))
        
        # ========== PRIMEIRO: DEFINIR TODAS AS VARIÁVEIS ==========
        clear_history_var = tk.BooleanVar(value=True)
        clear_cache_var = tk.BooleanVar(value=True)
        saved_setting = self.load_cleanup_setting()  # ← LÊ do arquivo
        auto_cleanup_var = tk.BooleanVar(value=saved_setting)  # ← USA valor salvo



        clear_old_var = tk.BooleanVar(value=False)
        
        # ========== DEPOIS: OBTER ESTATÍSTICAS ==========
        stats = self.data_handler.get_history_stats()
        
        # ========== AGORA SIM: TEXTO COM AS VARIÁVEIS ==========
        if stats['history_exists']:
            stats_text = f"""
            Current Status:

            • Crawler History: {stats['session_count']} sessions
            - Oldest: {stats.get('oldest_session', 'N/A')} ({stats.get('days_oldest', 0)} days)
            - {stats['sessions_to_expire']} sessions will auto-expire soon

            • Channel Cache: {stats['cache_count']} unique channels

            • Auto-cleanup: {'✅ Enabled' if auto_cleanup_var.get() else '❌ Disabled'}
            - Sessions older than {stats['cleanup_days']} days are auto-removed
            """
        else:
            stats_text = "No history or cache found."
        
        stats_label = tk.Label(main_frame, text=stats_text,
                            justify='left',
                            fg=self.colors['text_secondary'],
                            bg=self.colors['bg_dark'],
                            font=('Consolas', 9))
        stats_label.pack(pady=(0, 20))
        
        # ========== CHECKBOXES (usam variáveis já definidas) ==========
        options_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        options_frame.pack(pady=(0, 20))
        
        # Checkboxes
        history_cb = tk.Checkbutton(options_frame, text="Clear Crawler History",
                                variable=clear_history_var,
                                bg=self.colors['bg_dark'],
                                fg=self.colors['text'],
                                selectcolor=self.colors['bg_light'],
                                font=('Consolas', 9))
        history_cb.pack(anchor='w', pady=5)
        
        cache_cb = tk.Checkbutton(options_frame, text="Clear Channel Cache",
                                variable=clear_cache_var,
                                bg=self.colors['bg_dark'],
                                fg=self.colors['text'],
                                selectcolor=self.colors['bg_light'],
                                font=('Consolas', 9))
        cache_cb.pack(anchor='w', pady=5)
        
        # Checkbox para toggle auto-cleanup
        auto_cleanup_cb = tk.Checkbutton(options_frame, 
                                    text="Enable Auto-Cleanup (>30 days)",
                                    variable=auto_cleanup_var,
                                    bg=self.colors['bg_dark'],
                                    fg=self.colors['text'],
                                    selectcolor=self.colors['bg_light'],
                                    font=('Consolas', 9))
        auto_cleanup_cb.pack(anchor='w', pady=5)
        
        # Opção para limpar apenas sessões antigas
        if stats['sessions_to_expire'] > 0:
            old_cb = tk.Checkbutton(options_frame, 
                                text=f"Clear only OLD sessions (>30 days) [{stats['sessions_to_expire']} sessions]",
                                variable=clear_old_var,
                                bg=self.colors['bg_dark'],
                                fg=self.colors['warning'],
                                selectcolor=self.colors['bg_light'],
                                font=('Consolas', 9))
            old_cb.pack(anchor='w', pady=5)
        
        # ========== BOTÕES ==========
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        btn_frame.pack(fill='x', pady=(10, 0))
        
        def perform_clear():
            results = []
            
            # 1. Aplicar configuração do auto-cleanup
            auto_cleanup_enabled = auto_cleanup_var.get()
            self.save_cleanup_setting(auto_cleanup_enabled)
            results.append(f"{'✅' if auto_cleanup_enabled else '❌'} Auto-cleanup: {'Enabled' if auto_cleanup_enabled else 'Disabled'}")
            
            # 2. Limpar apenas sessões antigas (se selecionado)
            if clear_old_var.get() and stats['sessions_to_expire'] > 0:
                success, message = self.data_handler.cleanup_old_sessions_only()
                icon = "✅" if success else "❌"
                results.append(f"{icon} {message}")
            
            # 3. Limpar histórico completo (se selecionado)
            elif clear_history_var.get():
                success, message = self.data_handler.clear_history()
                icon = "✅" if success else "❌"
                results.append(f"{icon} {message}")
            
            # 4. Limpar apenas cache (se apenas cache selecionado)
            if clear_cache_var.get() and not clear_history_var.get() and not clear_old_var.get():
                success, message = self.data_handler.clear_cache()
                icon = "✅" if success else "❌"
                results.append(f"{icon} {message}")
            
            # Mostrar resultado
            result_text = "\n".join(results)
            messagebox.showinfo("Clear Results", result_text)
            
            # Atualizar log
            for result in results:
                if "✅" in result:
                    self.log(result.replace("✅ ", ""), "SUCCESS")
                else:
                    self.log(result.replace("❌ ", ""), "ERROR")
            
            dialog.destroy()
        
        tk.Button(btn_frame, text="OK",
                command=perform_clear,
                bg=self.colors['accent'], fg='white',
                font=('Consolas', 9, 'bold'),
                padx=20, pady=8).pack(side='right', padx=5)
        
        tk.Button(btn_frame, text="CANCEL",
                command=dialog.destroy,
                bg=self.colors['bg_light'], fg=self.colors['text'],
                font=('Consolas', 9),
                padx=20, pady=8).pack(side='right', padx=5)







        
        def perform_clear():
            results = []
            
            # 1. Aplicar configuração do auto-cleanup
            # (Aqui você precisa salvar essa preferência)
            auto_cleanup_enabled = auto_cleanup_var.get()
            self.save_cleanup_setting(auto_cleanup_enabled)  # Você precisa criar este método
            results.append(f"{'✅' if auto_cleanup_enabled else '❌'} Auto-cleanup: {'Enabled' if auto_cleanup_enabled else 'Disabled'}")
            
            # 2. Limpar apenas sessões antigas (se selecionado)
            if clear_old_var.get() and stats['sessions_to_expire'] > 0:
                success, message = self.data_handler.cleanup_old_sessions_only()
                icon = "✅" if success else "❌"
                results.append(f"{icon} {message}")
            
            # 3. Limpar histórico completo (se selecionado)
            elif clear_history_var.get():
                success, message = self.data_handler.clear_history()
                icon = "✅" if success else "❌"
                results.append(f"{icon} {message}")
            
            # 4. Limpar apenas cache (se apenas cache selecionado)
            if clear_cache_var.get() and not clear_history_var.get() and not clear_old_var.get():
                success, message = self.data_handler.clear_cache()
                icon = "✅" if success else "❌"
                results.append(f"{icon} {message}")
            
            # Mostrar resultado
            result_text = "\n".join(results)
            messagebox.showinfo("Clear Results", result_text)
            
            # Atualizar log
            for result in results:
                if "✅" in result:
                    self.log(result.replace("✅ ", ""), "SUCCESS")
                else:
                    self.log(result.replace("❌ ", ""), "ERROR")
            
            dialog.destroy()









    def save_cleanup_setting(self, enabled):
        """Salva configuração do auto-cleanup"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), 'config')
            os.makedirs(config_dir, exist_ok=True)
            
            settings_file = os.path.join(config_dir, 'cleanup_settings.json')
            settings = {
                'auto_cleanup_enabled': enabled,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            pass




    def load_cleanup_setting(self):
        """Carrega a configuração do auto-cleanup"""
        try:
            settings_file = os.path.join(os.path.dirname(__file__), 'config', 'cleanup_settings.json')
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('auto_cleanup_enabled', True)  # Padrão: ativado
            return True  # Padrão se não existir arquivo
            
        except Exception as e:
            return True  # Padrão se erro












    def calculate_quota_estimate(self):
        """Estimativa de quota no PIOR CENÁRIO (tudo novo)."""
        
        # 1. Configurações básicas
        terms = [t for t in self.terms_text.get("1.0", tk.END).strip().split('\n') if t.strip()]
        countries = len([c for c, var in self.country_vars.items() if var.get()]) or 1
        per_term = self.videos_var.get()
        
        # 2. Cálculo SEM CACHE - PIOR CENÁRIO
        total_searches = len(terms) * countries
        search_cost = total_searches * 100  # Fixo: 100 por busca
        
        # PIOR CENÁRIO: TODOS os canais são NOVOS
        total_possible_channels = total_searches * per_term
        
        # Custo POR CANAL NO PIOR CENÁRIO:
        # 1) Detalhes do canal (1 unidade por lote de 50) ~1
        # 2) Último vídeo (activities.list): +1
        # 3) Duração do vídeo (videos.list): +1
        # TOTAL: 3 unidades por canal NOVO
        channel_cost_max = total_possible_channels * 3
        
        # 3. TOTAL MÁXIMO
        total_max = search_cost + channel_cost_max
        
        # 4. Interface com avisos CLAROS
        estimate_text = f"MAX: ~{total_max:,} units"
        
        # Cores e avisos por limite
        label_color = "white"
        if total_max > 8000:
            estimate_text += " ⚠️ HIGH"
            label_color = "orange"
        if total_max > 10000:
            estimate_text = f"❌ EXCEEDS QUOTA: {total_max:,} units"
            label_color = "red"
        
        if hasattr(self, 'estimate_label'):
            self.estimate_label.config(
                text=f"Estimate: {estimate_text}",
                fg=label_color
            )
        
        # 5. Retorno compatível
        return {
            'total_estimate': total_max,
            'estimate_text': estimate_text,
            'warning': total_max > 8000,
            'exceeds': total_max > 10000
        }














    def view_history(self):
        """Visualiza o histórico de crawlers - VERSÃO CORRIGIDA"""
        try:
            history_file = self.data_handler.history_file
            
            if not os.path.exists(history_file):
                messagebox.showinfo("History", "No crawler history found.")
                return
            
            with open(history_file, 'r') as f:
                try:
                    history_data = json.load(f)
                except json.JSONDecodeError:
                    messagebox.showinfo("History", "History file is empty or corrupted.")
                    return
            
            # ===== CORREÇÃO CRÍTICA =====
            # history_data pode ser lista (antigo) ou dicionário (novo)
            
            if isinstance(history_data, dict):
                # Formato NOVO: dicionário com chave 'sessions'
                sessions = history_data.get('sessions', [])
            else:
                # Formato ANTIGO: lista direta de sessões
                sessions = history_data  # já é a lista
            
            if not sessions:
                messagebox.showinfo("History", "No crawler history found.")
                return
            
            # Criar janela para visualização
            history_window = tk.Toplevel(self.root)
            history_window.title(f"Crawler History ({len(sessions)} sessions)")
            history_window.geometry("900x600")
            history_window.configure(bg=self.colors['bg_dark'])
            
            # Frame principal com scroll
            main_frame = tk.Frame(history_window, bg=self.colors['bg_dark'])
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Text widget para exibir
            text_widget = scrolledtext.ScrolledText(
                main_frame,
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                font=('Consolas', 9),
                width=100,
                height=30
            )
            text_widget.pack(fill='both', expand=True)
            
            # Formatar e exibir histórico
            for i, entry in enumerate(reversed(sessions), 1):
                text_widget.insert(tk.END, f"\n{'='*80}\n")
                text_widget.insert(tk.END, f"SESSION #{i}\n")
                text_widget.insert(tk.END, f"{'='*80}\n\n")
                
                # Informações básicas
                text_widget.insert(tk.END, f"Timestamp: {entry.get('timestamp', 'N/A')}\n")
                text_widget.insert(tk.END, f"Filename: {entry.get('filename', 'N/A')}\n")
                text_widget.insert(tk.END, f"Format: {entry.get('format', 'N/A')}\n")
                text_widget.insert(tk.END, f"Total Channels: {entry.get('channel_count', 0)}\n")
                text_widget.insert(tk.END, f"Channels with Email: {entry.get('channels_with_email', 0)}\n")
                text_widget.insert(tk.END, f"Quota Used: {entry.get('quota_used', 0)} units\n\n")
                
                # Preview dos dados se existir
                if 'data_preview' in entry and entry['data_preview']:
                    text_widget.insert(tk.END, "Sample Channels (first 5):\n")
                    text_widget.insert(tk.END, "-"*40 + "\n")
                    for idx, channel in enumerate(entry['data_preview'][:5], 1):
                        text_widget.insert(tk.END, f"{idx}. {channel.get('title', 'N/A')}\n")
                        text_widget.insert(tk.END, f"   ID: {channel.get('channel_id', 'N/A')}\n")
                        text_widget.insert(tk.END, f"   Subs: {channel.get('subscriber_count', 'N/A')}\n")
                        text_widget.insert(tk.END, f"   Email: {'✅' if channel.get('has_email') else '❌'}\n")
                        text_widget.insert(tk.END, "\n")
            
            text_widget.insert(tk.END, f"\n{'='*80}\n")
            text_widget.insert(tk.END, f"Total Sessions: {len(sessions)}\n")
            
            # Desabilitar edição
            text_widget.config(state='disabled')
            
            # Botão de fechar
            tk.Button(main_frame, text="Close",
                    command=history_window.destroy,
                    bg=self.colors['accent'], fg='white',
                    font=('Consolas', 9),
                    padx=20, pady=5).pack(pady=10)
            
            text_widget.see('1.0')
            
        except Exception as e:
            self.log(f"Error viewing history: {e}", "ERROR")
            messagebox.showerror("Error", f"Could not view history: {str(e)}")



    def load_country_checkboxes(self):
        """Carrega checkboxes de países"""
        # Limpar frame
        for widget in self.country_checkbox_frame.winfo_children():
            widget.destroy()
        
        self.country_vars = {}
        
        # Países ordenados por nome
        sorted_countries = sorted(COUNTRIES.items(), key=lambda x: x[1])
        
        for code, name in sorted_countries:
            var = tk.BooleanVar(value=False)
            self.country_vars[code] = var
            
            # Checkbox com código e nome
            cb_text = f"{code} - {name[:20]}{'...' if len(name) > 20 else ''}"
            cb = tk.Checkbutton(
                self.country_checkbox_frame,
                text=cb_text,
                variable=var,
                command=self.update_country_selection,
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                selectcolor=self.colors['bg_dark'],
                anchor='w',
                font=('Consolas', 8)
            )
            cb.pack(fill='x', padx=2, pady=1)

    def filter_countries(self, *args):
        """Filtra países pelo texto da busca"""
        search_text = self.country_search_var.get().lower()
        
        for widget in self.country_checkbox_frame.winfo_children():
            widget_text = widget.cget('text').lower()
            if search_text in widget_text:
                widget.pack(fill='x', padx=2, pady=1)
            else:
                widget.pack_forget()

    def toggle_all_countries(self, state):
        """Seleciona/desceleciona todos os países"""
        for var in self.country_vars.values():
            var.set(state)
        self.update_country_selection()

    def select_popular_countries(self):
        """Seleciona países populares"""
        popular = ['US', 'BR', 'GB', 'IN', 'DE', 'FR', 'ES', 'IT', 'CA', 'AU', 'MX', 'JP', 'KR']
        for code, var in self.country_vars.items():
            var.set(code in popular)
        self.update_country_selection()

    def update_country_selection(self):
        """Atualiza lista de países selecionados"""
        self.selected_countries = [
            code for code, var in self.country_vars.items() 
            if var.get()
        ]
        
        # Atualizar status
        if not self.selected_countries:
            self.country_status_label.config(
                text="No countries selected (global search)",
                fg=self.colors['text_secondary']
            )
        elif len(self.selected_countries) <= 3:
            names = [COUNTRIES.get(code, code) for code in self.selected_countries[:3]]
            self.country_status_label.config(
                text=f"Selected: {', '.join(names)}",
                fg=self.colors['success']
            )
        else:
            self.country_status_label.config(
                text=f"Selected: {len(self.selected_countries)} countries",
                fg=self.colors['success']
            )

   
    def update_progress(self, value, status_text):
        """Atualiza barra de progresso e status"""
        self.progress_var.set(value)
        self.status_label.config(text=status_text)
        self.root.update_idletasks()
    



    def start_crawl(self):
        """Inicia o processo de crawling após validação da API Key e de termos."""
        
        # ========== VERIFICAÇÃO MELHORADA ==========
        
        # Cenário A: API já foi carregada do arquivo (self.api existe)
        if hasattr(self, 'api') and self.api:
            self.log("✅ API already loaded from the configuration file", "SUCCESS")
            # Pode prosseguir sem pedir para salvar novamente
            
        # Cenário B: Tem chave no campo mas diferente da salva
        else:
            current_key = self.api_key_var.get().strip()
            key_stored = getattr(self, 'api_key', '').strip()
            
            if current_key:
                key_needs_saving = current_key != key_stored or not hasattr(self, 'api')
                
                if key_needs_saving:
                    response = messagebox.askyesno("API Key Found", 
                        "You entered an API Key, but it's different from the one saved.\n\n"
                        "Do you want to save it now before starting the search?")
                    if response:
                        self.save_api_key(current_key) 
                        if not hasattr(self, 'api') or not self.api: 
                            self.log("🔴 Failed to initialize API after saving.", "ERROR")
                            return 
                    else:
                        return 
            else:
                messagebox.showwarning("API Key Required", 
                    "Please enter and save your YouTube API Key first.")
                return
            
        # 2. Verificação de Termos e Países
        terms = self.terms_text.get("1.0", tk.END).strip().split('\n')
        terms = [t.strip() for t in terms if t.strip()]
        countries_to_search = [c for c, var in self.country_vars.items() if var.get()] 
        
        if not terms:
            self.log("🔴 Search terms missing.", "WARNING")
            messagebox.showwarning("Input Error", "Please enter at least one search term.")
            return
            
        # 3. Verificação de Estado de Execução (USANDO is_running)
        if self.is_running: 
            self.log("The crawl is already underway.", "INFO")
            return
            
        # 4. Logs e Estimativas
        videos_per_term = self.videos_var.get()
        country_factor = len(countries_to_search) if countries_to_search else 1 
        total_estimated = len(terms) * videos_per_term * country_factor

        self.log(f"Starting crawl session", "SUCCESS")
        self.log(f"• Search Terms: {len(terms)}", "INFO")
        self.log(f"• Selected Countries: {len(countries_to_search) if countries_to_search else 'None (Global)'}", "INFO")
        self.log(f"• Channels by Term: {videos_per_term}", "INFO")
        self.log(f"• Estimated Channels: ~{total_estimated}", "INFO")

        # 5. Atualizar interface (USANDO is_running e start_btn)
        self.is_running = True 
        self.stop_requested = False
        self.start_btn.config(state='disabled') # <--- CORRIGIDO
        self.stop_btn.config(state='normal') 
        self.update_progress(0, "🟡 Starting search...")

        # 6. Executar em thread
        self.crawl_thread = threading.Thread(target=self.run_crawl)
        self.crawl_thread.daemon = True
        self.crawl_thread.start()


    def run_crawl(self):
        """
        Executa a busca e coleta de dados em um thread separado.
        Implementa controle estrito de cota e filtragem de histórico.
        """
        MAX_SEARCH_CALLS = 80 

        try:  # <- Este try PRECISA ter except/finally

            # --- ADICIONAR LOGS DE CACHE AQUI ---
            self.log("=== DEBUG CACHE ===", "INFO")
            
            # Verificar histórico antes
            if os.path.exists(self.data_handler.history_file):
                with open(self.data_handler.history_file, 'r') as f:
                    history = json.load(f)
                    self.log(f"Current history: {len(history)} sessions", "INFO")
            
            cached_ids = self.data_handler.load_all_crawled_ids()
            self.log(f"Cached IDs: {len(cached_ids)} channels", "INFO")
            
            if cached_ids:
                sample_ids = list(cached_ids)[:3]
                self.log(f"Example of cached IDs: {sample_ids}", "INFO")

            # --- 1. Validação e Leitura da UI ---
            api_key = self.api_key_var.get().strip()
            if not api_key:
                messagebox.showerror("Error", "An API key is required.")
                self.update_progress(0, "🔴 Error: Missing API Key.")
                return

            terms = [t.strip() for t in self.terms_text.get('1.0', tk.END).split('\n') if t.strip()]
            countries_to_search = [c for c, var in self.country_vars.items() if var.get()]
            videos_per_term = self.videos_var.get()

            if not terms:
                messagebox.showerror("Error", "Define Search Terms.")
                self.update_progress(0, "🔴 Error: Missing configuration.")
                return

            # 2. Inicialização e Histórico
            self.api = YouTubeAPI(api_key)
            all_channels_data = []

            # CARREGAR CACHE DO HISTÓRICO
            previously_crawled_ids = self.data_handler.load_all_crawled_ids()
            self.log(f"Loaded cache: {len(previously_crawled_ids)} Unique channels in history.", "INFO")
            
            total_search_calls = 0
            
            # Se não houver países selecionados, faça uma única iteração com lista vazia
            if not countries_to_search:
                country_list_to_iterate = [None] 
            else:
                country_list_to_iterate = countries_to_search
                
            total_steps = len(terms) * len(country_list_to_iterate)
            
            # 3. Loop Principal com Controle de Cota
            for i, term in enumerate(terms):
                if self.stop_requested: break
                
                for country_code in country_list_to_iterate:
                    if self.stop_requested: break
                    
                    current_step = total_search_calls + 1
                    
                    # Checagem de Cota antes de cada chamada de 100 unidades
                    if total_search_calls >= MAX_SEARCH_CALLS:
                        self.log(f"🔴 SEARCH LIMIT REACHED. Maximum safe level: {MAX_SEARCH_CALLS} calls. Interrupting.", "ERROR")
                        self.stop_requested = True
                        break
                    
                    country_name = COUNTRIES.get(country_code, 'Global')
                    self.log(f"Searching ({current_step}/{total_steps}): '{term}' in {country_name}...", "INFO")
                    
                    # Chamada de Busca (Custo: 100 unidades)
                    channel_ids = self.api.search_channels_by_keyword(
                        term, 
                        videos_per_term,
                        region_code=country_code,
                        detect_shorts=True
                    )
                    total_search_calls += 1

                    # Processar cada canal encontrado na busca
                    # INICIALIZAR cache para esta busca
                    search_shorts_info_cache = {}
                    
                    for channel_id in channel_ids:
                        # Obter detalhes da busca
                        search_details = self.api.get_search_result_details(channel_id)
                        
                        # Extrair info de shorts da busca
                        if search_details:
                            search_shorts_info_cache[channel_id] = {  # ← Usar o cache correto
                                'search_video_is_shorts_url': search_details.get('search_video_is_shorts_url', False),
                                'search_video_is_shorts_thumb': search_details.get('search_video_is_shorts_thumb', False),
                                'search_video_is_shorts_keyword': search_details.get('search_video_is_shorts_keyword', False),
                                'search_video_shorts_score': search_details.get('search_video_shorts_score', 0)
                            }

                    # FILTRAGEM AVANÇADA COM CACHE COMPLETO
                    cached_channels, uncached_ids = self.data_handler.get_cached_channel_data(channel_ids)
                    cache_hits = len(cached_channels)
                    new_ids_count = len(uncached_ids)

                    self.log(f"Found: {len(channel_ids)} channels. Cache: {cache_hits} Full channels. New: {new_ids_count}.", "INFO")

                    # Adicionar canais do cache
                    all_channels_data.extend(cached_channels)

                    # Buscar apenas canais NÃO cacheados
                    if uncached_ids:
                        # Filtragem adicional: remover IDs já no histórico
                        truly_new_ids = set(uncached_ids) - previously_crawled_ids
                        duplicate_count = len(uncached_ids) - len(truly_new_ids)
                        
                        if duplicate_count > 0:
                            self.log(f"Additional savings: {duplicate_count} Channels already in the history (avoids searching for the last video).", "INFO")
                        
                        if truly_new_ids:
                            # Preparar mapa de shorts info apenas para os canais que serão buscados
                            shorts_info_map = {}
                            for channel_id in truly_new_ids:
                                if channel_id in search_shorts_info_cache:
                                    shorts_info_map[channel_id] = search_shorts_info_cache[channel_id]
                            
                            # Buscar detalhes dos canais passando a info de shorts
                            new_channels_data = self.api.get_channels_details(list(truly_new_ids), shorts_info_map)
                            all_channels_data.extend(new_channels_data)
                            
                            # Atualizar histórico com NOVOS IDs
                            previously_crawled_ids.update(truly_new_ids)

                    # Atualização de progresso (FORA do loop interno de channel_ids)
                    progress_percent = int((current_step / total_steps) * 100)
                    self.update_progress(progress_percent, f"🌐 {len(all_channels_data)} Single channels. Quota: {self.api.get_quota_used()} units.")


            # --- 4. Pós-Processamento e Exportação ---
            if all_channels_data:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"Youtube_Crawl_{timestamp}"
                
                exported_file = self.data_handler.export_channels(
                    all_channels_data, 
                    filename, 
                    self.format_var.get()
                )
                
                history_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'filename': filename,
                    'format': self.format_var.get(),
                    'channel_count': len(all_channels_data),
                    'channels_with_email': sum(1 for c in all_channels_data if c.get('has_email')),
                    'quota_used': self.api.get_quota_used(),
                    'data_preview': all_channels_data 
                }
                self.data_handler.save_history(history_entry)
                
                self.log(f"✅ Crawl Completed. Total Unique Channels: {len(all_channels_data)}.", "SUCCESS")
                self.log(f"📊 Master file updated with new channels", "INFO")
                self.log(f"Total quota consumed: {self.api.get_quota_used()} units.", "SUCCESS")
                if exported_file:
                    self.log(f"Exported file: {exported_file}", "INFO")

        except Exception as e:  # <- AQUI ESTÁ O except QUE FALTAVA
            self.log(f"🔴 Critical error: {e}", "ERROR")
            self.update_progress(0, "🔴 Crawl error.")
            
        finally:  # <- E O finally
            # Atualizar quota REAL na interface
            if hasattr(self, 'api') and self.api:
                quota_used = self.api.get_quota_used()
                self.update_quota_display(quota_used, len(all_channels_data) if 'all_channels_data' in locals() else 0)
            
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            if not self.stop_requested:
                self.update_progress(100, "🟢 Ready for the next search.")
            else:
                self.update_progress(0, "🟡 Crawl interrupted.")




    def stop_crawl(self):
        """Para o crawling"""
        self.stop_requested = True
        self.log("Stop requested - finishing current operation...", "WARNING")
        self.stop_btn.config(state='disabled')
    
    def crawl_finished(self):
        """Finaliza o crawling e reseta a interface"""
        self.is_running = False
        self.stop_requested = False
        
        # Reativar botões
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if not self.stop_requested:
            self.update_progress(100, "🟢 Ready for next search")
        else:
            self.update_progress(0, "🟡 Crawl stopped")
    
    def open_export_folder(self):
        """Abre a pasta de exports no explorador de arquivos"""
        exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
        
        # Criar pasta se não existir
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
            self.log("Created exports folder", "INFO")
        
        # Abrir no explorador
        try:
            if os.name == 'nt':  # Windows
                os.startfile(exports_dir)
            elif os.name == 'posix':  # macOS, Linux
                import subprocess
                subprocess.call(['open', exports_dir] if sys.platform == 'darwin' else ['xdg-open', exports_dir])
            
            self.log(f"Opened exports folder: {exports_dir}", "INFO")
        except Exception as e:
            self.log(f"Could not open folder: {e}", "ERROR")




    def open_export_folder(self): # <--- Esta é a função vinculada ao botão
            """Abre a pasta de exportação, usando o caminho mestre self.EXPORT_DIR."""
            
            if not os.path.exists(self.EXPORT_DIR):
                try:
                    os.makedirs(self.EXPORT_DIR)
                    self.log(f"Created exports folder: {self.EXPORT_DIR}", "INFO")
                except Exception as e:
                    self.log(f"Could not create export folder: {e}", "ERROR")
                    messagebox.showerror("Error", f"Could not create export folder on:\n{self.EXPORT_DIR}")
                    return
                
            try:
                # Abre o explorador de arquivos no caminho correto
                os.startfile(self.EXPORT_DIR)
                self.log(f"Opened exports folder: {self.EXPORT_DIR}", "INFO")
            except Exception as e:
                self.log(f"Could not open folder: {e}", "ERROR")
                messagebox.showerror("Error", f"Could not open folder:\n{self.EXPORT_DIR}")

            

def main():
    """Função principal"""
    root = tk.Tk()
    app = YouTubeCrawlerApp(root)
    
    # Centralizar na tela
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()