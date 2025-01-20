import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import requests
import os
import json
from time import sleep
import sys
from pathlib import Path

class ImageDownloaderTab:
    def __init__(self, parent, shared_log):
        self.parent = parent
        self.shared_log = shared_log
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        
    def get_config_path(self):
        """Obtiene la ruta del archivo de configuración según el entorno"""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.getenv('APPDATA')) / 'FutureCivitDownloader'
        else:  # Linux/Mac
            config_dir = Path.home() / '.config' / 'FutureCivitDownloader'

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'

    def load_config(self):
        """Carga la configuración guardada"""
        self.api_key = ""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
        except Exception as e:
            print(f"Error cargando configuración: {e}")

    def save_api_key(self):
        """Guarda la API key en el archivo de configuración"""
        try:
            api_key = self.api_entry.get().strip()
            if api_key:
                config = {'api_key': api_key}
                with open(self.config_path, 'w') as f:
                    json.dump(config, f)
                print("API Key guardada correctamente")
            else:
                print("Por favor ingresa una API Key válida")
        except Exception as e:
            print(f"Error guardando API Key: {e}")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def get_user_images(self, model_id, headers):
        """Obtiene todas las imágenes generadas por usuarios"""
        images = []
        page = 1

        while True:
            api_url = f"https://civitai.com/api/v1/images"
            params = {
                'modelId': model_id,
                'limit': 100,
                'page': page
            }

            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Error obteniendo imágenes de usuarios: {response.status_code}")
                break

            data = response.json()
            current_images = data.get('items', [])
            if not current_images:
                break

            images.extend(current_images)
            total_items = data.get('metadata', {}).get('totalItems', 0)

            print(f"Obtenidas {len(images)} de {total_items} imágenes...")

            if len(images) >= total_items:
                break

            page += 1
            sleep(0.5)

        return images

    def download_images(self):
        api_key = self.api_entry.get().strip()
        if not api_key:
            print("Por favor, introduce una API Key válida")
            self.download_btn['state'] = 'normal'
            return

        url = self.url_entry.get()
        output_folder = self.folder_path.get()

        if not url or not output_folder:
            print("Por favor, introduce URL y carpeta de destino")
            self.download_btn['state'] = 'normal'
            return

        try:
            # Crear carpetas
            model_samples_folder = os.path.join(output_folder, "model_samples")
            user_images_folder = os.path.join(output_folder, "user_images")

            for folder in [model_samples_folder, user_images_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            # Extraer ID del modelo
            model_id = url.split('models/')[1].split('/')[0]
            version_id = url.split('modelVersionId=')[1] if 'modelVersionId=' in url else None

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Verificar API Key
            test_response = requests.get("https://civitai.com/api/v1/models", headers=headers)
            if test_response.status_code != 200:
                print("Error: API Key inválida")
                self.download_btn['state'] = 'normal'
                return

            print("\n=== Descargando imágenes de muestra del modelo ===")
            api_url = f"https://civitai.com/api/v1/models/{model_id}"
            response = requests.get(api_url, headers=headers)

            if response.status_code != 200:
                print(f"Error al obtener datos del modelo: {response.status_code}")
                return

            model_data = response.json()
            print(f"Modelo encontrado: {model_data['name']}")

            version = None
            for v in model_data['modelVersions']:
                if version_id and str(v['id']) == version_id:
                    version = v
                    break
            if not version:
                version = model_data['modelVersions'][0]

            print(f"Versión: {version['name']}")

            for idx, image in enumerate(version['images'], 1):
                image_url = image['url']
                filename = f"sample_{idx}.png"
                filepath = os.path.join(model_samples_folder, filename)

                print(f"Descargando muestra {idx}/{len(version['images'])}: {filename}")

                # No necesitamos headers para la descarga de imágenes
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"✓ Imagen guardada: {filename}")

                    meta_filepath = os.path.join(model_samples_folder, f"{filename}.json")
                    with open(meta_filepath, 'w') as f:
                        json.dump(image, f, indent=2)
                else:
                    print(f"✗ Error descargando: {filename}")

                sleep(0.5)

            print("\n=== Descargando imágenes generadas por usuarios ===")
            user_images = self.get_user_images(model_id, headers)

            print(f"\nEncontradas {len(user_images)} imágenes de usuarios")
            for idx, image in enumerate(user_images, 1):
                image_url = image['url']
                filename = f"user_image_{idx}.png"
                filepath = os.path.join(user_images_folder, filename)

                print(f"Descargando imagen de usuario {idx}/{len(user_images)}: {filename}")

                # No necesitamos headers para la descarga de imágenes
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"✓ Imagen guardada: {filename}")

                    meta_filepath = os.path.join(user_images_folder, f"{filename}.json")
                    with open(meta_filepath, 'w') as f:
                        json.dump(image, f, indent=2)
                else:
                    print(f"✗ Error descargando: {filename}")

                sleep(0.5)

            print("\n¡Descarga completada!")

        except Exception as e:
            print(f"Error: {str(e)}")

        self.download_btn['state'] = 'normal'

    def start_download(self):
        self.download_btn['state'] = 'disabled'
        self.log_area.delete(1.0, tk.END)
        threading.Thread(target=self.download_images, daemon=True).start()

    def setup_ui(self):
        # Configuración de archivo de configuración
        self.config_path = self.get_config_path()
        self.load_config()

        # Contenedor principal
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Sección de configuración
        config_frame = ttk.LabelFrame(main_container, 
                                    text=" Configuración ",
                                    padding=(15, 10))
        config_frame.pack(fill='x', pady=(0, 15))

        # API Key
        api_frame = ttk.Frame(config_frame)
        api_frame.pack(fill='x', pady=5)

        ttk.Label(api_frame, text="API Key:").pack(side='left', padx=(0, 10))
        self.api_entry = ttk.Entry(api_frame, width=50)
        self.api_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        if self.api_key:
            self.api_entry.insert(0, self.api_key)

        ttk.Button(api_frame, 
                  text="💾 Guardar", 
                  width=10,
                  command=self.save_api_key).pack(side='right')

        # URL y Carpeta
        url_frame = ttk.Frame(config_frame)
        url_frame.pack(fill='x', pady=5)

        ttk.Label(url_frame, text="URL del modelo:").pack(side='left', padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))

        folder_frame = ttk.Frame(config_frame)
        folder_frame.pack(fill='x', pady=5)

        ttk.Label(folder_frame, text="Carpeta de destino:").pack(side='left', padx=(0, 10))
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=40)
        self.folder_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        ttk.Button(folder_frame, 
                  text="📂 Explorar", 
                  command=self.browse_folder).pack(side='right')

        # Botón de descarga
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=(10, 15))
        self.download_btn = ttk.Button(button_frame,
                                     text="⬇️ Iniciar Descarga",
                                     style='Accent.TButton',
                                     command=self.start_download)
        self.download_btn.pack(fill='x')

        # Área de log
        log_frame = ttk.LabelFrame(main_container, 
                                 text=" Registro de Actividad ",
                                 padding=(10, 5))
        log_frame.pack(fill='both', expand=True)

        self.log_area = ScrolledText(log_frame,
                                   height=15,
                                   font=('Consolas', 10),
                                   bg='#2d2d2d',
                                   fg='white',
                                   insertbackground='white')
        self.log_area.pack(fill='both', expand=True)

        # Añadir el área de log al log compartido
        self.shared_log.add_log_area(self.log_area)

        # Configurar estilo adicional
        style = ttk.Style()
        style.configure('Accent.TButton', 
                      background='#0078d7',
                      foreground='white',
                      font=('Arial', 12, 'bold'),
                      padding=10)
        style.map('Accent.TButton',
                background=[('active', '#006cbd')],
                foreground=[('active', 'white')])
