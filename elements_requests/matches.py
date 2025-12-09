from flask import jsonify

from front import HEADERS
from gcs import upload_db_to_storage
from processing import update_ratings, rollback_match_elo, recalculate_after_timestamp
from db import get_db_connection

def matches(request, conn, c):
    if request.method == 'GET':
        return get_matches(request, conn, c)
    elif request.method == 'POST':
        return set_matches(request, conn, c)
    elif request.method == 'DELETE':
        return delete_matches(request, conn, c)

def get_matches(request, conn, c):
    c.execute("""
        SELECT m.id, p1.name, p2.name, m.score1, m.score2, m.played_at,
               mec.p1_change_standard, mec.p1_change_with_score,
               mec.p2_change_standard, mec.p2_change_with_score
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.id
        JOIN players p2 ON m.player2_id = p2.id
        LEFT JOIN match_elo_changes mec ON m.id = mec.match_id
        ORDER BY m.played_at DESC LIMIT 20
    """)
    matches = [
        {
            'id': r[0],
            'player1': r[1],
            'player2': r[2],
            'score1': r[3],
            'score2': r[4],
            'played_at': r[5],
            'player1_changes': {
                'standard': round(r[6], 1) if r[6] is not None else 0,
                'with_score': round(r[7], 1) if r[7] is not None else 0
            },
            'player2_changes': {
                'standard': round(r[8], 1) if r[8] is not None else 0,
                'with_score': round(r[9], 1) if r[9] is not None else 0
            }
        }
        for r in c.fetchall()
    ]
    conn.close()
    return (jsonify(matches), 200, HEADERS)


def set_matches(request, conn, c):
    data = request.get_json()
    c.execute("INSERT INTO matches (player1_id, player2_id, score1, score2) VALUES (?, ?, ?, ?)",
                (data['player1_id'], data['player2_id'], data['score1'], data['score2']))
    conn.commit()
    match_id = c.lastrowid
    conn.close()

    update_ratings(data['player1_id'], data['player2_id'], data['score1'], data['score2'], match_id)
    upload_db_to_storage()

    return (jsonify({'id': match_id}), 201, HEADERS)


def delete_matches(request, conn, c):
    match_id = int(request.args.get('id'))
    
    # Étape 1: Inverse les changements du match à supprimer
    played_at = rollback_match_elo(match_id)
    
    if played_at is None:
        # Le match n'a pas d'historique, on peut le supprimer directement
        c.execute("DELETE FROM matches WHERE id = ?", (match_id,))
        conn.commit()
        conn.close()
        upload_db_to_storage()
        return (jsonify({'success': True}), 200, HEADERS)
    
    # Étape 2: Recalcule tous les matchs suivants
    conn.close()
    recalculate_after_timestamp(played_at, match_id)
    
    # Étape 3: Supprime le match et son historique
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM match_elo_changes WHERE match_id = ?", (match_id,))
    c.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()

    upload_db_to_storage()
    return (jsonify({'success': True}), 200, HEADERS)