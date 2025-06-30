import pandas as pd
import joblib
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
import nltk
import os

# Asegura que los recursos de NLTK estén disponibles
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("\n--- Descargando recurso NLTK: punkt... ---")
    nltk.download('punkt')
    print("--- Recurso 'punkt' descargado. ---\n")

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("\n--- Descargando recurso NLTK: stopwords... ---")
    nltk.download('stopwords')
    print("--- Recurso 'stopwords' descargado. ---\n")

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("\n--- Descargando recurso NLTK: wordnet... ---")
    nltk.download('wordnet')
    print("--- Recurso 'wordnet' descargado. ---\n")

# Preprocesamiento del texto
def preprocess_text(text):
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    return " ".join(lemmatized_words)

# Función para entrenar el modelo
def entrenar_modelo():
    print("\n--- Iniciando entrenamiento del modelo ---")
    print("Cargando dataset...")
    
    # Obtener la ruta absoluta del directorio actual del script (modelo.py)
    script_dir = os.path.dirname(__file__)
    # Construir la ruta completa al archivo CSV
    csv_path = os.path.join(script_dir, "IMDB_Dataset.csv")
    data = pd.read_csv(csv_path)

    print("Preprocesando comentarios del dataset...")
    data['review'] = data['review'].apply(preprocess_text)
    print("Preprocesamiento completado. Preparando datos para split...") 

    X_train, X_test, y_train, y_test = train_test_split(data['review'], data['sentiment'], test_size=0.2, random_state=42)
    print("Datos divididos. Inicializando pipeline...") 

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(solver='liblinear'))
    ])
    print("Pipeline inicializado. Preparando Grid Search...") 

    param_grid = {
        'clf__C': [1],
        'tfidf__ngram_range': [(1, 2)]
    }

    print("Entrenando el modelo (esto puede tardar)...") 
    grid_search = GridSearchCV(pipeline, param_grid, cv=3, verbose=1, n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print("Entrenamiento completado.") 

    print(f"\nMejor Score del modelo: {grid_search.best_score_:.2f}")

    # Guardamos el modelo entrenado
    model_path = os.path.join(script_dir, 'sentiment_analysis_model.pkl')
    joblib.dump(grid_search.best_estimator_, model_path)
    print(f"--- Modelo entrenado y guardado en '{model_path}' ---")
    return grid_search.best_estimator_

# Función para cargar el modelo desde archivo
def cargar_modelo():
    script_dir = os.path.dirname(__file__)
    model_path = os.path.join(script_dir, 'sentiment_analysis_model.pkl')
    if os.path.exists(model_path):
        print(f"\n--- Cargando modelo desde '{model_path}' ---")
        return joblib.load(model_path)
    else:
        raise FileNotFoundError("El modelo no ha sido entrenado aún. Ejecuta primero el entrenamiento.")

# Para pruebas manuales (opcional)
if __name__ == '__main__':
    try:
        modelo = entrenar_modelo()
    except Exception as e:
        print(f"Error al entrenar el modelo en modo manual: {e}")