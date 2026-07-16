import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime, sys
import json, os, random
from dotenv import load_dotenv

# Importamos el modulo de IA
# import taste_profile

# Load environment variables from .env file
load_dotenv()

# Get the credentials from environment variables
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

# Set up Spotify API credentials and authenticate
auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='playlist-modify-public playlist-modify-private playlist-read-private user-top-read'
)

sp = spotipy.Spotify(auth_manager=auth_manager)

# Cargar configuración desde el archivo JSON
def load_config():
    with open('./config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    # Filtrar los podcasts (mantener el orden original del archivo)
    config["podcasts"] = [pod for pod in config["podcasts"] if not pod.get("ignore", False)]

    return config

def get_recent_episodes_from_podcast(sp, podcast_id):
    """Obtiene el episodio más reciente del podcast dado (solo el URI y nombre)."""
    try:
        # Obtenemos los detalles del podcast para conseguir su nombre
        podcast = sp.show(podcast_id)
        podcast_name = podcast['name']  # Nombre del podcast

        # Obtenemos los episodios más recientes del podcast (primero con limit=1)
        episodes = sp.show_episodes(podcast_id, limit=1, market="ES")
        
        # Si no hay episodios, probamos con limit=2 => Esta no te la sabes
        # Esto es porque tendrán episodios nuevos subidos pero no públicos todavía
        if not episodes or 'items' not in episodes or episodes['items'][0] is None:
            print(f"⚠️ No se encontró un episodio válido con limit=1. Intentando con limit=2...")
            episodes = sp.show_episodes(podcast_id, limit=2, market="ES")
        
        # Si aún no hay episodios, probamos con limit=3 => No es el fin del mundo
        # Esto es porque tendrán episodios nuevos subidos pero no públicos todavía
        if not episodes or 'items' not in episodes or episodes['items'][0] is None:
            print(f"⚠️ No se encontró un episodio válido con limit=2. Intentando con limit=3...")
            episodes = sp.show_episodes(podcast_id, limit=3, market="ES")
        
        if not episodes or 'items' not in episodes or not any(episodes['items']):
            print(f"⚠️ No se encontraron episodios para el podcast {podcast_name}.")
            return []
        
        # Filtramos el primer episodio válido
        recent_episode = next((episode for episode in episodes['items'] if episode), None)
        if not recent_episode:
            print(f"⚠️ No se encontraron episodios válidos para el podcast {podcast_name}.")
            return []

        # Sacamos el URI y nombre del episodio más reciente
        recent_episode_uri = recent_episode['uri']
        recent_episode_name = recent_episode['name']  # Nombre del episodio
        
        # Mostrar el nombre del podcast y el nombre del episodio
        print(f"🎧 Podcast: {podcast_name} | Episodio más reciente: {recent_episode_name}")
        
        return [recent_episode_uri]
    
    except spotipy.exceptions.SpotifyException as e:
        print(f"⚠️ Error al obtener episodios del podcast {podcast_id}: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")
        return []

def get_playlist_episodes(sp, playlist_id):
    """Obtiene las URL de los episodios actuales de la playlist."""
    try:
        # Obtenemos las pistas de la playlist
        episodes = sp.playlist_items(playlist_id)
        # print(f"Respuesta de la API para la playlist {episodes}")
        
        if not episodes or 'items' not in episodes or not episodes['items']:
            print(f"⚠️ No se encontraron episodios en la playlist {playlist_id}.")
            return []
        
        # Extraemos solo las URL de los episodios (campo 'uri' dentro de 'track' o 'episode')
        episode_uris = [
            episode['track']['uri'] if episode.get('track') else episode['episode']['uri']
            for episode in episodes['items']
            if episode.get('track') or episode.get('episode')
        ]
        return episode_uris
        
    except spotipy.exceptions.SpotifyException as e:
        print(f"⚠️ Error al obtener episodios de la playlist: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Error inesperado al obtener episodios de la playlist: {e}")
        return []

def get_favorite_tracks(sp, total_needed):
    """Obtiene las canciones más escuchadas del usuario en un lapso de tiempo(personalizable): short_term."""
    try:
        print(f"🎵 Buscando {total_needed} canciones favoritas...")
        # time_range='short_term' trae lo que más has escuchado en las últimas 4 semanas
        results = sp.current_user_top_tracks(limit=total_needed, time_range='short_term')

        if not results or 'items' not in results:
            print("⚠️ No se encontraron canciones favoritas.")
            return []

        track_uris = [track['uri'] for track in results['items']]
        return track_uris

    except Exception as e:
        print(f"⚠️ Error al obtener tus canciones favoritas: {e}")
        return []

def get_discovery_tracks(sp, genres, total_needed):
    """Busca canciones nuevas en Spotify basándose en las etiquetas de Gemini."""
    try:
        print(f"🎵 Buscando {total_needed} canciones nuevas basandose en IA..")
        track_uris=[]

        if not genres:
            print("⚠️ No se recibieron géneros de la IA.Tomando el Flujo Clasico...")
            return get_favorite_tracks(sp, total_needed)

        # Calculando cuantas canciones buscar por cada género para tern variedad
        limit_per_genre = max(1, (total_needed // len(genres)) + 2)

        for genre in genres:
            # Buscando en todo Spotify usando el filtro de género específico
            query = f'genre: "{genre}"'
            results = sp.search(q=query, type='track', limit=limit_per_genre)

            for item in results['tracks']['items']:
                track_uris.append(item['uri'])

        # Eliminamos canciones duplicadas(por si un artista encaja en dos géneros
        track_uris  = list(set(track_uris))

        # Mezclamos la lista de forma aleatoria para que los géneros no queden agrupados
        random.shuffle(track_uris)

        # Cortamos la lista para devolver exactamente el número que necesitamos
        return  track_uris[:total_needed]

    except Exception as e:
        print(f"⚠️ Error al buscar canciones para descubrimiento: {e}")
        return []

def build_ruta_diaria(episode_uris, track_uris, tracks_per_episode=5):
    """Intercala episodios y canciones en un solo arreglo."""
    ruta_diaria = []
    track_index = 0
    total_tracks = len(track_uris)

    for episode in episode_uris:
        # 1. Agregamos el episodio de noticias
        ruta_diaria.append(episode)

        # 2. Agregamos las 5 canciones siguientes
        for _ in range(tracks_per_episode):
            if track_index < total_tracks:
                ruta_diaria.append(track_uris[track_index])
                track_index += 1
            else:
                break  # Se nos acabaron las canciones disponibles

    return ruta_diaria

def update_playlist(sp, playlist_id, episode_ids):
    """Reemplaza los episodios en la playlist con los nuevos episodios."""
    try:
        # Eliminamos todos los episodios actuales de la playlist
        current_tracks = get_playlist_episodes(sp, playlist_id)
        print(f"🚫 Eliminando episodios anteriores de la playlist...")
        if current_tracks:
            sp.playlist_replace_items(playlist_id, episode_ids)
        else:
            print(f"❌ No se encontraron episodios previos para eliminar.")
        
        # Añadimos los nuevos episodios a la playlist
        print(f"🔄 Añadiendo episodios a la playlist...")
        response = sp.playlist_replace_items(playlist_id, episode_ids)
        print(f"✅ Respuesta del API: {response}")
    except Exception as e:
        print(f"⚠️ Error al actualizar la playlist: {e}")

def save_weekly_stats_if_friday(sp):
    """Obtiene el top 40 de la semana y lo guarda en un .md si es viernes"""
    today = datetime.datetime.now(datetime.UTC)

    # En Python, el lunes es 0 y el viernes es 4
    if today.weekday() != 4:
        print("🗓️ Hoy no es viernes, omitiendo la recolección de estadísticas.")
        return False

    try:
        print("Es viernes!! Recopilando tu top 40 semanal...")
        results = sp.current_user_top_tracks(limit=40, time_range='short_term')

        if not results or 'items' not in results:
            print("No se encontraron canciones para las estadísticas.")
            return False

        date_str = today.strftime("%Y-%m-%d")
        # Guardaremos todo ordenado en una carpeta 'stas'
        os.makedirs('stats', exist_ok=True)
        filename = f"stats/top_40_{date_str}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Top 40 - Semana de {date_str}\n\n")
            f.write("| Rank | Canción | Artista | Album |\n")
            f.write("|---|---|---|---|\n")

            for i, track in enumerate(results['items'], 1):
                name = track['name'],
                artist = track['artists'][0]['name'],
                album = track['album']['name'],
                f.write(f"| {i} | {name} | {artist} | {album} |\n")

        print(f"Estadisticas guardadas exitosamente en {filename}.")
        return True

    except Exception as e:
        print(f"Error al guardar estadisticas: {e}", file=sys.stderr)
        return False

def main():

    # Remove the status.log file
    open('./status.log', 'w').close()

    # Cargar los valores
    config = load_config()

    # Extraer los valores de la configuración
    PLAYLIST_ID = config['playlist']['id']
    PODCAST_IDS = [podcast['id'] for podcast in config['podcasts']]

    # Ahora puedes usar PODCAST_IDS y PLAYLIST_ID en tu código
    print("Podcast IDs:", PODCAST_IDS)
    print("Playlist ID:", PLAYLIST_ID)
    
    # Obtenemos los episodios más recientes de cada podcast
    # TODO: obtener un episodio en concreto por su nombre (e.g. "Las tres noticias de Carlos Alsina" de "Más de uno")
    episode_ids = []
    for podcast_id in PODCAST_IDS:
        recent_episodes = get_recent_episodes_from_podcast(sp, podcast_id)
        episode_ids.extend(recent_episodes)

    if episode_ids:
        # Calculamos cuántas canciones necesitamos en total (5 por cada episodio encontrado)
        canciones_necesarias = len(episode_ids) * 5

        # ==================================================
        # SELECCIÓN DEL FLUJO MUSICAL
        # ==================================================

        # OPCIÓN 1
        # Extrae tus géneros con Gemini y busca música 100% nueva
        # mis_generos = taste_profile.main_ai_profile(sp)
        # mis_canciones = get_discovery_tracks(sp, mis_generos, canciones_necesarias)

        # OPCIÓN 2
        # Si prefieres escuchar tus canciones más repetidas descomenta las líneas de arriba y descomenta la línea de abajo
        # Obtenemos ese número exacto de canciones favoritas
        mis_canciones = get_favorite_tracks(sp, canciones_necesarias)

        # =================================================

        lista_final = build_ruta_diaria(episode_ids, mis_canciones, tracks_per_episode=5)

        # Actualizamos la playlist con el nuevo arreglo mixto
        update_playlist(sp, PLAYLIST_ID, lista_final)
        save_weekly_stats_if_friday(sp)
    else:
        print("⚠️ No se obtuvieron episodios para actualizar la playlist.")

if __name__ == "__main__":
    main()
