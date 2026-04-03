import os
import json
# noinspection PyPackageRequirements
from google import genai
from dotenv import load_dotenv

# Se cargan las variables de entorno
load_dotenv()

# Configuramos la API de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("GEMINI_API_KEY no ha encontrado el archivo .env")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def get_listening_data(spotify_client):
    """Extrae el top de artistas y canciones en los 3 rangos de tiempo de Spotify"""
    artist_counts = {}
    unique_tracks = {}

    ranges = ['short_term','medium_term','long_term']

    for r in ranges:
        print(f"Analizando canciones ({r})...")
        tracks_data = spotify_client.current_user_top_tracks(limit=50, time_range= r)

        for track in tracks_data.get('items', []):
            track_name = track['name']
            artists = [a['name'] for a in track['artists']]

            # Guardamos la canción unica
            track_key = f"{track_name}|{artists[0]}"
            if track_key not in unique_tracks:
                unique_tracks[track_key] = f"{track_name} - {','.join(artists)}"

            # Se hace un conteo de las menciones de los artistas en las canciones
            for artist in artists:
                artist_counts[artist] = artist_counts.get(artist, 0) + 1

    for r in ranges:
        print(f"Analizando canciones ({r})...")
        artists_data = spotify_client.current_user_top_tracks(limit=50, time_range= r)

        # Contamos a los artistas principales directamente
        for artist in artists_data.get('items', []):
            name = artist['name']
            artist_counts[name] = artist_counts.get(name, 0) + 2

    # Ordenamos los artistas por frecuencia de mayor a menor y tomamos los top 40
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:40]
    top_artists_names = [artist[0] for artist in top_artists]

    # Tomamos una muestra de hasta 50 canciones únicas
    sample_tracks = list(unique_tracks.values())[:50]

    return top_artists_names, sample_tracks

def generate_genres_with_gemini(top_artists, sample_tracks):
    """Envia los datos a Gemini para obtener etiquetas de género musical."""

    artist_list = ",".join(top_artists)
    track_list = ",".join(sample_tracks)

    prompt = f"""Based on this Spotify listening data, generate a list of 5-8 genre/style tags that best describe this user's music taste. These tags will be used as Spotify search queries(e.g."genre:pop") to discover new music matching their taste.
        
    Top artists(ranked by listening frequency):
    {artist_list}
        
    Sample tracks:
    {track_list} 
        
    Requirements:
    -Return ONLY a JSON array of strings, nothing else
    -Use genres that work well as Spotify search queries
    -Be specific enough to be useful(e.g., "synth pop" not just "pop")
    -Cover the breadth of their taste, not just the most common genre
    -Use lowercase
        
    Example output format:
    ["synth pop", "indie rock", "electronic", "alt pop", "dance pop"]"""

    print("\n Pidiendo a Gemini que analice tus gustos...\n")

    # Usamos el modelo flash de gemini, que es rapido e ideal para estas tareas
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        output = response.text.strip()

        # Se limpia el formato markdown si Gemini lo incluye
        if output.startswith("```"):
            output = "\n".join(output.split("\n")[1:-1])

        genres = json.loads(output)
        return genres

    except Exception as e:
        print(f"Error al procesar la respuesta de Gemini: {e}")
        return []

def main_ai_profile(spotify_client):
    """Función principal que orquesta la recolección y el análisis."""
    print("\n Generador de Perfil Musical(Google Gemini) \n")

    top_artists, sample_tracks = get_listening_data(spotify_client)

    print(f"\n Top artistas detectados: {', '.join(top_artists[:10])}...")
    print(f"\n Canciones unicas analizadas: {len(sample_tracks)}")

    genres = generate_genres_with_gemini(top_artists, sample_tracks)

    if genres:
        print(f"\n Se detectaron {len(genres)} generos para ti:")
        for g in genres:
            print(f" -{g}")

        #Opcional: guarda los datos en un archivo json para que tu main.py lo lea despues
        with open('mis_generos.json', 'w', encoding='utf-8') as f:
            json.dump({"genres": genres}, f, indent=4)
        print("\n Generos guardados en 'mis_generos.json'")

    return genres

if __name__ == "__main__":
    import spotipy
    from spotipy.oauth2 import SpotifyPKCE

    # Inicializamos Spotify
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    auth_manager = SpotifyPKCE(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope='playlist-modify-public playlist-modify-private playlist-read-private user-top-read'
    )

    token_info = auth_manager.get_access_token()

    token = token_info['access_token'] if isinstance(token_info, dict) else token_info

    sp = spotipy.Spotify(auth=token)

    main_ai_profile(sp)