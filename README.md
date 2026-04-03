# Tu Ruta Diaria
Este proyecto de Python automatiza la creacion de una lista de reproduccion en **Spotify** que intercala los episodios mas recientes de tus podcast de noticias favoritos con tus canciones mas escuchadas.

Basicamente, recrea la difunta funcion de **"Ruta Diaria"** de Spotify, dandote control total sobre tus fuentes de informacion y sin depender de algoritmos.

# Reconocimientos
Este proyecto es un fork adaptado del repositorio original `spotify-latest-episodes` creado por **Jaime Barranco Hernández**.

El repositorio original sento las bases logicas para la extraccion automatizada de episodios usando un **Servidor** y **Docker**. Esta version modifica el motor de autenticacion para cumplir con los estandares de seguridad modernos de Spotify, añade la logica matematica para intercalar musica personalizada(_Tracks_) entre las noticias(_Episodios_) y esta optimizado para ejecutarse localmente mediante tareas programadas.

# ¿Cómo funciona?
El script opera como un pequeño proceso **ETL**(Extract, Transform, Load) que se comunica directamente con la API de Spotify:
1. **Extraccion de Noticias:** Lee tu archivo de configuracionm, busca los podcasts que le indicaste y extrae la URI del episodio más reciente de cada uno(implementado reintentos en caso de que los creadores suban episodios programados ocultos).
2. **Extraccion de Musica:** Consulta tiu perfil personal de Spotify para obtener tus _Top Tracks_ de las ultimas 4 semanas. Calcula exactamente cuántas canciones necesitas(por defecto, 5 canciones por cada noticia).
3. **Transformacion(_La Mezcla_):** Toma ambos arreglos de datos y los fusiona en la memoria RAM, creando una estructura ordenada:`[Noticia 1, Cancion 1 Cancion 2,..., Noticia 2, Cancion 6, ..]`.
4. **Carga:** Se conecta a una lsita de reproduccion vacia que tu hayas definido, borra su contenido anterior y sobreescribe la lista con tu nueva **"Ruta Diaria"** recien creada.
---
# La nueva API de Spotify(Aviso para Desarrolladores)
Si has intentado usar scripts anmtiguos de Spotify y te has encontrado con el mensaje `server-error`, se debe a que la API de Spotify ha endurecido sus politicas de seguridad para nuevas aplicaciones. Este repositorio esta actualizado para cumplir con las mejores practicas vigentes:
- **Flujo PKCE(Proof Key for Code Exchange):** Ya no se utiliza el obsoleto `SpotifyOAuth` con un `Client Secret` estatico para scritps locales. Esate proyecto usa `SpotifyPKCE`, generando claves criptograficas dinamicas en cada inicio de sesion, lo cual evita bloqueos del servidor.
- **Endpoints Modernos:** Spotify ha marcado `/playlists/{id}/tracks` como obsoleto. Este codigo utiliza el endpoint recomendado `/playlist/{id}/items`, que permite manejar colecciones mixtas de episodios y canciones sin problemas.
- **Redireccion Estricta:** La API ya no perdona errores de sintaxis en el `Redirect URI`. Se requiere coincidencia absoluta(_sin slashes al final_).

# Requisitos Tecnicos
Para correr este proyecto en tu maquina local, necesitas:
- **Python 3.10 o superior** instalado en tu sistema(si es tu primera vez progamando, usando python o usando este tipo de herramientas basta con que instales **PyCharm**, el IDE se encargara de instalar Python por ti si no se encuentra en tu maquina).
- Una cuenta en **[Spotify for Developers](https://developer.spotify.com/)**(Es gratis con tu usuario normal de Spotify, aunque necesitas ser usuario premium de spotify para poder hacer uso de la API).
- Un **[IDE](https://www.jetbrains.com/pycharm/?_gl=1*1tjouby*_gcl_au*MTEzNjMwMzA3Ni4xNzcyMzI2MTU3LjE1MDUyNTY1MzcuMTc3MjMyNzg4My4xNzcyMzI4NTY1*FPAU*MTEzNjMwMzA3Ni4xNzcyMzI2MTU3*_ga*MzgwNDYxNjczLjE3NzIzMjYxNTc.*_ga_9J976DJZ68*czE3NzIzMjYxNTckbzEkZzEkdDE3NzIzMjk1MjUkajIzJGwwJGgw)** o **[Editor de Codigo](https://code.visualstudio.com/)** de tu preferencia, para ejecutar comandos basicos.
- Opcional: **[Git](https://git-scm.com/)**.
___
# Guia de Instalacion y Uso
1. **Configura tu App en Spotify Developer**
    1. Ve a [Spotify Dashboard]() y crea una nueva App.
   2. Ve a los **Settings** de tu App y en la seccion **Redirect URIs** añade exactamente esto: `https://127.0.0.1:8000`.
   3. En la seccion **User Managment**, añade el correo electronico asociado a tu cuenta de Spotify.
   4. Copia tu **Client ID**.
2. **Clona el Repositorio e Instala Dependencias**
Abre la terminal de **git** y ejecuta:
```
git clone https://github.com/tu-usuario/mi-ruta-diaria.git
cd mi-ruta-diaria
pip install -r requirements.txt
```
O puedes descargar directamente el proyecto en tu maquina.

3. **Configura tus Variables de Entorno**
Crea un archivo llamado `.env` en la raiz del proyecto con la siguiente estructura:
```
SPOTIFY_CLIENTE_ID=pega_tu_cliente_id_aqui
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000
```
4. **Configura tus Podcast y Playlist**(config.json)
1. 
5. **Primera Ejecucion**