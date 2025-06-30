import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import threading
from modelo import entrenar_modelo, cargar_modelo
from youtube_analysis import analizar_video
import os
import datetime

# Inicializa la apariencia (CustomTkinter)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class SentimentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Análisis de Sentimientos de YouTube")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1000
        window_height = 600
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        self.modelo = None
        self.df_resultado = None
        self.current_comments_display_count = 0
        self.comments_per_load = 50

        # Sidebar de navegación
        self.sidebar = ctk.CTkFrame(
            self, width=180, fg_color=("gray75", "gray20"), corner_radius=10
        )
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="Menú", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(pady=20, padx=20)

        # Botones del menú
        self.btn_modelo = ctk.CTkButton(
            self.sidebar, text="Modelo", command=self.mostrar_modelo
        )
        self.btn_modelo.pack(pady=10, padx=20)

        self.btn_analizar = ctk.CTkButton(
            self.sidebar, text="Analizar YouTube", command=self.mostrar_analisis
        )
        self.btn_analizar.pack(pady=10, padx=20)

        self.btn_exportar = ctk.CTkButton(
            self.sidebar, text="Exportar CSV", command=self.exportar_csv
        )
        self.btn_exportar.pack(pady=10, padx=20)

        self.btn_instrucciones = ctk.CTkButton(
            self.sidebar, text="Instrucciones", command=self.mostrar_instrucciones
        )
        self.btn_instrucciones.pack(pady=10, padx=20)

        self.btn_acerca = ctk.CTkButton(
            self.sidebar, text="Acerca de", command=self.mostrar_acerca
        )
        self.btn_acerca.pack(pady=10, padx=20)

        # Área principal
        self.main_frame = ctk.CTkFrame(
            self, fg_color=("gray92", "gray14"), corner_radius=10
        )
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Variables para elementos de progreso y resultados (declaradas en __init__)
        self.progress_label_model = None
        self.progressbar_model = None
        self.progress_label_analysis = None
        self.progressbar_analysis = None

        self.load_more_button = None
        self.comments_count_label = None
        self.emoji_label = None
        self.text_area = None

        # Mostrar pantalla inicial (puedes cambiarla a instrucciones si prefieres)
        self.mostrar_modelo()

    def limpiar_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Función auxiliar para habilitar/deshabilitar todos los botones de navegación
    def toggle_buttons_state(self, state):
        self.btn_modelo.configure(state=state)
        self.btn_analizar.configure(state=state)
        self.btn_exportar.configure(state=state)
        self.btn_instrucciones.configure(state=state)
        self.btn_acerca.configure(state=state)

    def mostrar_modelo(self):
        self.limpiar_frame()
        self.current_comments_display_count = 0
        self.df_resultado = None

        ctk.CTkLabel(
            self.main_frame, text="Gestión del Modelo", font=("Arial", 20, "bold")
        ).pack(pady=20)

        ctk.CTkButton(
            self.main_frame,
            text="Entrenar Modelo",
            command=self.entrenar_modelo_ui,
            height=40,
        ).pack(pady=10)
        ctk.CTkButton(
            self.main_frame,
            text="Cargar Modelo",
            command=self.cargar_modelo_ui,
            height=40,
        ).pack(pady=10)

        self.progress_label_model = ctk.CTkLabel(
            self.main_frame, text="", font=("Arial", 14)
        )
        self.progress_label_model.pack(pady=5)

        self.progressbar_model = ctk.CTkProgressBar(
            self.main_frame, mode="indeterminate", height=10
        )
        self.progressbar_model.pack(pady=5, padx=20, fill="x")
        self.progressbar_model.set(0)

    def entrenar_modelo_ui(self):
        self.toggle_buttons_state("disabled")

        def entrenar():
            try:
                self.progress_label_model.configure(
                    text="Entrenando modelo... Esto puede tardar varios minutos."
                )
                self.progressbar_model.start()

                if self.progress_label_analysis:
                    self.progress_label_analysis.pack_forget()
                if self.progressbar_analysis:
                    self.progressbar_analysis.pack_forget()

                self.modelo = entrenar_modelo()
                messagebox.showinfo(
                    "Éxito", "Modelo entrenado y guardado correctamente"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error de Entrenamiento",
                    f"Ocurrió un error durante el entrenamiento: {str(e)}",
                )
            finally:
                self.progress_label_model.configure(text="")
                self.progressbar_model.stop()
                self.toggle_buttons_state("normal")

        threading.Thread(target=entrenar).start()

    def cargar_modelo_ui(self):
        try:
            self.modelo = cargar_modelo()
            messagebox.showinfo("Modelo", "Modelo cargado exitosamente")
        except FileNotFoundError:
            messagebox.showerror(
                "Error",
                "El archivo del modelo (sentiment_analysis_model.pkl) no se encontró. Entrena el modelo primero.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo: {str(e)}")

    def mostrar_analisis(self):
        self.limpiar_frame()
        self.current_comments_display_count = 0
        self.df_resultado = None

        ctk.CTkLabel(
            self.main_frame,
            text="Análisis de Video de YouTube",
            font=("Arial", 20, "bold"),
        ).pack(pady=20)

        self.link_entry = ctk.CTkEntry(
            self.main_frame, placeholder_text="Pega aquí el enlace del video", height=35
        )
        self.link_entry.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            self.main_frame, text="Analizar", command=self.analizar_video_ui, height=40
        ).pack(pady=10)

        self.progress_label_analysis = ctk.CTkLabel(
            self.main_frame, text="", font=("Arial", 14)
        )
        self.progress_label_analysis.pack(pady=5)

        self.progressbar_analysis = ctk.CTkProgressBar(
            self.main_frame, mode="indeterminate", height=10
        )
        self.progressbar_analysis.pack(pady=5, padx=20, fill="x")
        self.progressbar_analysis.set(0)

        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.text_area = ctk.CTkTextbox(
            self.results_frame, height=250, wrap="word", state="disabled"
        )
        self.text_area.pack(pady=10, fill="both", expand=True)

        self.load_more_button = ctk.CTkButton(
            self.results_frame,
            text="Cargar más comentarios",
            command=self.load_more_comments,
            state="disabled",
        )
        self.load_more_button.pack(pady=5)

        self.comments_count_label = ctk.CTkLabel(
            self.results_frame, text="", font=("Arial", 12)
        )
        self.comments_count_label.pack(pady=5)

        self.emoji_label = ctk.CTkLabel(
            self.results_frame, text="", font=("Arial", 30, "bold")
        )
        self.emoji_label.pack(pady=10)

    def analizar_video_ui(self):
        video_url = self.link_entry.get()
        if not self.modelo:
            messagebox.showerror("Error", "Primero debes cargar o entrenar un modelo")
            return

        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state="disabled")
        self.emoji_label.configure(text="")
        self.comments_count_label.configure(text="")
        self.load_more_button.configure(state="disabled")
        self.current_comments_display_count = 0

        self.toggle_buttons_state("disabled")

        def analizar():
            try:
                self.progress_label_analysis.configure(
                    text="Extrayendo comentarios y analizando sentimiento..."
                )
                self.progressbar_analysis.start()

                if self.progress_label_model:
                    self.progress_label_model.pack_forget()
                if self.progressbar_model:
                    self.progressbar_model.pack_forget()

                self.df_resultado = analizar_video(video_url, self.modelo)

                positivos = sum(self.df_resultado["sentiment"] == "positive")
                negativos = sum(self.df_resultado["sentiment"] == "negative")
                total_comentarios = len(self.df_resultado)

                if total_comentarios > 0:
                    porcentaje_pos = (positivos / total_comentarios) * 100
                    porcentaje_neg = (negativos / total_comentarios) * 100
                    self.emoji_label.configure(
                        text=f"😃 {porcentaje_pos:.1f}%   😠 {porcentaje_neg:.1f}%"
                    )
                else:
                    porcentaje_pos = 0.0
                    porcentaje_neg = 0.0
                    messagebox.showwarning(
                        "Advertencia",
                        "No se encontraron comentarios para analizar en este video.",
                    )
                    self.emoji_label.configure(text="😔 No hay comentarios")

                self.current_comments_display_count = 0
                self.load_more_comments()

            except ValueError as ve:
                messagebox.showerror("Error de URL", str(ve))
            except Exception as e:
                messagebox.showerror(
                    "Error durante el análisis",
                    f"Ocurrió un error: {str(e)}\nAsegúrate de tener una API Key válida y conexión a internet.",
                )
            finally:
                self.progress_label_analysis.configure(text="")
                self.progressbar_analysis.stop()
                self.toggle_buttons_state("normal")

        threading.Thread(target=analizar).start()

    def load_more_comments(self):
        if self.df_resultado is None or self.df_resultado.empty:
            self.comments_count_label.configure(text="No hay comentarios para mostrar.")
            self.load_more_button.configure(state="disabled")
            return

        total_comentarios = len(self.df_resultado)
        start_index = self.current_comments_display_count
        end_index = min(total_comentarios, start_index + self.comments_per_load)

        if start_index >= total_comentarios:
            self.comments_count_label.configure(
                text=f"Mostrando todos los {total_comentarios} comentarios."
            )
            self.load_more_button.configure(state="disabled")
            return

        comments_to_display = self.df_resultado.iloc[start_index:end_index]

        self.text_area.configure(state="normal")
        if start_index == 0:
            self.text_area.delete("1.0", "end")
            self.text_area.insert("end", "--- Comentarios Analizados ---\n\n")

        for index, row in comments_to_display.iterrows():
            sentiment_text = (
                "Positivo" if row["sentiment"] == "positive" else "Negativo"
            )
            self.text_area.insert("end", f"[{sentiment_text}] {row['comment']}\n\n")

        self.text_area.configure(state="disabled")

        self.current_comments_display_count = end_index
        self.comments_count_label.configure(
            text=f"Mostrando {self.current_comments_display_count} de {total_comentarios} comentarios."
        )

        if self.current_comments_display_count >= total_comentarios:
            self.load_more_button.configure(state="disabled")
        else:
            self.load_more_button.configure(state="normal")

    def exportar_csv(self):
        if self.df_resultado is None:
            messagebox.showwarning(
                "Aviso", "No hay comentarios analizados para exportar"
            )
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if archivo:
            self.df_resultado.to_csv(archivo, index=False)
            messagebox.showinfo("Éxito", "Comentarios exportados correctamente")

    def mostrar_instrucciones(self):
        self.limpiar_frame()
        ctk.CTkLabel(
            self.main_frame, text="Instrucciones", font=("Arial", 20, "bold")
        ).pack(pady=20)

        instructions_text = """
        ¡Bienvenid@!

        Sigue estos pasos para usar el programa:

        ===============================================================================
        Paso 1: Preparar el Modelo (Primera Vez o si el Modelo No Existe)
        ===============================================================================

        1.  Ve a la sección "Modelo".

        2.  Si es la primera vez que usas el programa o si no tienes el archivo
            'sentiment_analysis_model.pkl', haz clic en "Entrenar Modelo".
            Esto descargará recursos necesarios de NLTK y entrenará un modelo
            de Machine Learning usando el archivo 'IMDB_Dataset.csv'.
            Este proceso puede tardar varios minutos y se mostrará un mensaje
            de progreso.

        3.  Asegúrate de que 'IMDB_Dataset.csv' esté en la misma carpeta que 'modelo.py'.

        4.  Una vez entrenado, el modelo se guardará automáticamente como
            'sentiment_analysis_model.pkl' en la carpeta del proyecto.
          
        =============================================================================== 
        Paso 2: Cargar el Modelo (Si ya está entrenado)
        ===============================================================================

        1.  Si ya entrenaste el modelo anteriormente y tienes el archivo
            'sentiment_analysis_model.pkl' en la carpeta del proyecto,
            puedes hacer clic en "Cargar Modelo" en la sección "Modelo".
            Esto cargará el modelo pre-entrenado para su uso inmediato,
            ahorrándote el tiempo de entrenamiento.
           
        ===============================================================================   
        Paso 3: Analizar un Video de YouTube
        ===============================================================================

        1.  Ve a la sección "Analizar YouTube".

        2.  Pega el enlace completo de un video de YouTube en el campo de texto.

        3.  Haz clic en el botón "Analizar".

        4.  El programa extraerá los comentarios del video, los preprocesará y
            aplicará el modelo entrenado para determinar si cada comentario es
            "positivo" o "negativo".

        5.  Los resultados se mostrarán en la pantalla, incluyendo el porcentaje
            de comentarios positivos y negativos. Podrás cargar más comentarios
            si el video tiene muchos.

        6.  Necesitas tener una API Key de YouTube válida configurada en
            'youtube_analysis.py' para que esta función trabaje.
          
        ===============================================================================  
        Paso 4: Exportar Comentarios
        ===============================================================================

        1.  Después de analizar un video, puedes hacer clic en "Exportar CSV"
            para guardar todos los comentarios analizados y sus sentimientos
            en un archivo CSV en tu computadora.

        """
        # Usamos CTkTextbox para permitir el desplazamiento si el texto es largo
        # y para tener un poco más de control sobre el formato si se necesita.
        instructions_textbox = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            width=800,
            height=450,
            font=("Arial", 16),
            fg_color=("gray92", "gray18"),
            text_color=("gray10", "gray90"),
        )
        instructions_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        instructions_textbox.insert("1.0", instructions_text)
        instructions_textbox.configure(
            state="disabled"
        )  # Para que el usuario no pueda editar

    def mostrar_acerca(self):
        self.limpiar_frame()
        ctk.CTkLabel(
            self.main_frame, text="Acerca de este Programa", font=("Arial", 20, "bold")
        ).pack(pady=20)

        current_year = datetime.datetime.now().year

        acerca_text = """
        Este programa es una aplicación de escritorio diseñada para realizar
        Análisis de Sentimientos en comentarios de videos de YouTube.
        Combina la extracción de datos de la API de YouTube con técnicas de
        Machine Learning para clasificar automáticamente el tono emocional
        de los comentarios (positivo o negativo).

        El Modelo de Análisis de Sentimientos
        =====================================
        El corazón de esta aplicación es un modelo de Machine Learning entrenado
        para la clasificación de texto:

        Tipo de Modelo: Se utiliza un clasificador de REGRESIÓN LOGÍSTICA
            (Logistic Regression) de la librería Scikit-learn. Este es un algoritmo
            potente y eficiente para problemas de clasificación binaria (como
            positivo/negativo).

        Procesamiento del Texto (NLP - Procesamiento de Lenguaje Natural):
            Antes de que el modelo pueda entender el texto, los comentarios pasan
            por varias etapas de preprocesamiento:

            1.  Tokenización: El texto se divide en palabras individuales (tokens).

            2.  Minusculización: Todas las palabras se convierten a minúsculas.

            3.  Eliminación de Stop Words: Se eliminan palabras comunes que no aportan
                mucho significado al sentimiento (ej., "el", "la", "un", "y").

            4.  Lematización: Las palabras se reducen a su forma base (lema)
                (ej., "corriendo" -> "correr", "mejores" -> "bueno").

        Vectorización de Texto (TF-IDF): Para que el modelo pueda "entender"
            las palabras, los textos preprocesados se transforman en representaciones
            numéricas utilizando TF-IDF (Term Frequency-Inverse Document Frequency).
            TF-IDF asigna un peso numérico a cada palabra, reflejando su importancia
            en un comentario y en el conjunto total de comentarios.

        Conjunto de Datos de Entrenamiento: El modelo ha sido entrenado
            utilizando un conjunto de datos público de reseñas de películas de "IMDb"
            ('IMDB_Dataset.csv'), que contiene 50,000 reseñas etiquetadas como
            positivas o negativas. Esto permite que el modelo aprenda a distinguir
            sentimientos en un contexto similar al de los comentarios.

        Tecnologías Utilizadas
        ======================
        - Python: Lenguaje de programación principal.
        - CustomTkinter: Para la creación de la interfaz gráfica de usuario (GUI).
        - Scikit-learn: Librería de Machine Learning para el modelo.
        - NLTK (Natural Language Toolkit): Para el preprocesamiento del texto.
        - Google API Client Library for Python: Para interactuar con la API de YouTube.
        - Pandas: Para el manejo y análisis de datos.

        Autor: Ing. Nelmer Santiago Padrón.
        © 2023
        """
        acerca_textbox = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            width=800,
            height=450,
            font=("Arial", 16),
            fg_color=("gray92", "gray18"),
            text_color=("gray10", "gray90"),
        )
        acerca_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        acerca_textbox.insert("1.0", acerca_text)
        acerca_textbox.configure(
            state="disabled"
        )  # Para que el usuario no pueda editar


if __name__ == "__main__":
    app = SentimentApp()
    app.mainloop()
