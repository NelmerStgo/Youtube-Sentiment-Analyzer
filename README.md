
# YouTube Sentiment Analyzer

Una aplicación de escritorio desarrollada en Python para realizar **Análisis de Sentimientos** en comentarios de videos de YouTube. Utiliza técnicas de procesamiento de lenguaje natural (NLP) y un modelo de *Machine Learning* entrenado con reseñas de películas del dataset de IMDb.




## Features

- Entrenamiento o carga de un modelo de análisis de sentimientos.
- Análisis de comentarios de cualquier video público de YouTube.
- Visualización del porcentaje de comentarios **positivos** y **negativos** con emojis.
- Exportación de resultados en formato CSV.
- Interfaz gráfica moderna usando `customtkinter`.
- Sección de ayuda e información “Acerca de”.


## Instalación

Instala el proyecto:

```bash
  git clone https://github.com/NelmerStgo/Youtube-Sentiment-Analyzer.git
```
    
## Requisitos

- Python 3.8 o superior
- Bibliotecas necesarias (instalar con `pip install -r requirements.txt`):


```bash
    customtkinter
    nltk
    pandas
    scikit-learn
    google-api-python-client
    joblib
```
## DataSet (NO incluido en el proyecto)

El modelo se entrena con el dataset **IMDb Dataset of 50K Movie Reviews**, que puedes descargar desde:

```bash
https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
```

Una vez descargado, **coloca el archivo `IMDB_Dataset.csv` en la raíz del proyecto**, al mismo nivel que `modelo.py`.

Recuerda --> `IMDB_Dataset.csv`
## ⚠️ Entrenamiento Inicial Requerido

Este repositorio **no incluye el modelo preentrenado (`sentiment_analysis_model.pkl`)**. 

Por lo tanto:

1. Ejecuta la app `gui.py`.
2. Ve a la sección **“Modelo”** y haz clic en **“Entrenar Modelo”**.
3. Esto descargará los recursos necesarios y generará automáticamente el archivo `.pkl` para usar el clasificador.

Este proceso solo se realiza una vez, y puede tardar unos minutos dependiendo del equipo.

## Author

- [@NelmerStgo](https://github.com/NelmerStgo)

