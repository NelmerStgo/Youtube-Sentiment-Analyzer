from googleapiclient.discovery import build
import pandas as pd
from modelo import preprocess_text
import re

# Reemplaza esto con tu clave real (o mejor aún, usa variables de entorno)
API_KEY = "YOUR_API_KEY"

def extraer_video_id(url):
    # Extrae el ID del video de la URL de YouTube
    # Se ha mejorado la expresión regular para ser más flexible
    match = re.search(r"(?:v=|youtu\.be/|youtube\.com/(?:embed/|v/|watch\?v=|watch\?feature=player_embedded&v=))([\w-]{11})(?:\S+)?", url)
    return match.group(1) if match else None

def obtener_comentarios(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    comments = []
    next_page_token = None

    while True:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments

def analizar_video(url, modelo):
    video_id = extraer_video_id(url)
    if not video_id:
        raise ValueError("No se pudo extraer el ID del video del enlace proporcionado. Asegúrate de que sea un enlace válido de YouTube.")
    
    comentarios = obtener_comentarios(video_id)
    if not comentarios:
        raise ValueError("No se pudieron obtener comentarios para este video, o el video no tiene comentarios. Puede que los comentarios estén deshabilitados o que la API de YouTube tenga restricciones.")
        
    df = pd.DataFrame(comentarios, columns=["comment"])
    df["preprocessed_comment"] = df["comment"].apply(preprocess_text)
    # Asegúrate de que 'modelo' tenga un método 'predict'
    if hasattr(modelo, 'predict'):
        df["sentiment"] = modelo.predict(df["preprocessed_comment"])
    else:
        raise TypeError("El objeto 'modelo' no tiene un método 'predict'. Asegúrate de que un modelo válido haya sido cargado o entrenado.")
    return df