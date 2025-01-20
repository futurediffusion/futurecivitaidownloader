import tkinter as tk
from tkinter import ttk
from extractor import ImageDownloaderTab
from prompt import PromptDownloaderTab
import sys  # Importación añadida

class SharedLog:
    def __init__(self):
        self.log_areas = []
        
    def add_log_area(self, log_area):
        self.log_areas.append(log_area)
        
    def write(self, string):
        for log_area in self.log_areas:
            log_area.insert('end', string)
            log_area.see('end')
            log_area.update()
            
    def flush(self):
        pass

class CivitAIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Future CivitAI Toolkit")
        self.root.geometry("1100x750")
        self.root.configure(bg='#1e1e1e')
        
        # Configurar estilo
        self.setup_styles()
        
        # Log compartido
        self.shared_log = SharedLog()
        
        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Añadir pestañas
        self.image_tab = ImageDownloaderTab(self.notebook, self.shared_log)
        self.prompt_tab = PromptDownloaderTab(self.notebook, self.shared_log)
        
        self.notebook.add(self.image_tab.frame, text="📷 Descargar Imágenes")
        self.notebook.add(self.prompt_tab.frame, text="📝 Descargar Prompts")
        
        # Redirigir stdout al log compartido
        sys.stdout = self.shared_log
        
        # Barra de estado
        self.status_bar = tk.Label(self.root, 
                                 text="🟢 Ready", 
                                 bd=1, 
                                 relief=tk.SUNKEN, 
                                 anchor=tk.W,
                                 bg='#333333',
                                 fg='white',
                                 font=('Arial', 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        # Configurar colores
        style.configure('TNotebook', 
                       background='#1e1e1e',
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#2d2d2d',
                       foreground='white',
                       padding=[15, 5],
                       font=('Arial', 12, 'bold'))
        style.map('TNotebook.Tab', 
                 background=[('selected', '#3e3e3e')],
                 foreground=[('selected', '#ffffff')])
        
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabel', background='#1e1e1e', foreground='white')
        style.configure('TButton', 
                       background='#333333',
                       foreground='white',
                       font=('Arial', 10),
                       padding=8,
                       borderwidth=1)
        style.map('TButton',
                 background=[('active', '#444444')],
                 foreground=[('active', 'white')])
        
        style.configure('TLabelframe', 
                      background='#1e1e1e',
                      foreground='white',
                      bordercolor='#444444')
        style.configure('TLabelframe.Label', 
                      background='#1e1e1e',
                      foreground='white')
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CivitAIApp()
    app.run()
