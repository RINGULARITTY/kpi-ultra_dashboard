import functions_framework
from flask import jsonify
import os

from front import HEADERS
from db import init_db, LOCAL_DB_PATH, get_db_connection
from gcs import download_db_from_storage, upload_db_to_storage
from elements_requests.landing_page import landing_page
from elements_requests.players import players, get_player, compare_players, get_player_elo_history
from elements_requests.matches import matches

def ensure_db_loaded():   
    db_exists = os.path.exists(LOCAL_DB_PATH)

    if not db_exists:
        downloaded = download_db_from_storage()

        if not downloaded:
            init_db()
            upload_db_to_storage()

@functions_framework.http
def table_tennis_elo(request):
    ensure_db_loaded()
    
    if request.method == 'OPTIONS':
        return ('', 204, HEADERS)

    conn = get_db_connection()
    c = conn.cursor()

    infos = {"request": request, "conn": conn, "c": c}

    if request.path == '/':
        return landing_page(**infos)

    if request.path == '/api/players':
        return players(**infos)

    if request.path == '/api/matches':
        return matches(**infos)

    if request.path.startswith('/api/player/') and '/history' in request.path and request.method == 'GET':
        return get_player_elo_history(**infos)

    if request.path.startswith('/api/player/') and request.method == 'GET':
        return get_player(**infos)

    if request.path == '/api/compare' and request.method == 'GET':
        return compare_players(**infos)

    conn.close()
    return (jsonify({'error': 'Not found'}), 404, HEADERS)
