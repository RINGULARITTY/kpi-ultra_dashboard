import sqlite3
from flask import jsonify

from front import HEADERS
from gcs import upload_db_to_storage
from processing import calculate_advanced_confidence

def players(request, conn, c):
    if request.method == 'GET':
        return get_players(request, conn, c)
    elif request.method == 'POST':
        return set_players(request, conn, c)
    elif request.method == 'DELETE':
        return delete_players(request, conn, c)

def get_players(request, conn, c):
    if request.method == 'GET':
        c.execute("SELECT id, name, elo_standard, elo_with_score FROM players ORDER BY elo_standard DESC")
        players = [
            {
                'id': r[0], 
                'name': r[1], 
                'elo_standard': round(r[2], 1), 
                'elo_with_score': round(r[3], 1)
            } 
            for r in c.fetchall()
        ]
        conn.close()
        return (jsonify(players), 200, HEADERS)

def set_players(request, conn, c):
    data = request.get_json()
    try:
        c.execute("INSERT INTO players (name) VALUES (?)", (data['name'],))
        conn.commit()
        player_id = c.lastrowid
        conn.close()

        upload_db_to_storage()

        return (jsonify({'id': player_id, 'name': data['name']}), 201, HEADERS)
    except sqlite3.IntegrityError:
        conn.close()
        return (jsonify({'error': 'Player already exists'}), 400, HEADERS)

def delete_players(request, conn, c):
    player_id = request.args.get('id')
    c.execute("SELECT COUNT(*) FROM matches WHERE player1_id = ? OR player2_id = ?", 
                (player_id, player_id))
    match_count = c.fetchone()[0]

    if match_count > 0:
        conn.close()
        return (jsonify({
            'error': 'Cannot delete player with matches', 
            'match_count': match_count
        }), 400, HEADERS)

    c.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()

    upload_db_to_storage()

    return (jsonify({'success': True}), 200, HEADERS)

def get_player(request, conn, c):
    """Récupère les statistiques détaillées d'un joueur"""
    
    player_id = request.path.split("/api/player/")[-1]
    
    # Infos du joueur
    c.execute("SELECT id, name, elo_standard, elo_with_score FROM players WHERE id = ?", (player_id,))
    player = c.fetchone()
    
    if not player:
        conn.close()
        return (jsonify({'error': 'Player not found'}), 404, HEADERS)
    
    # Historique des matchs avec changements d'Elo
    c.execute("""
        SELECT 
            m.id,
            CASE 
                WHEN m.player1_id = ? THEN p2.name 
                ELSE p1.name 
            END as opponent,
            CASE 
                WHEN m.player1_id = ? THEN m.score1 
                ELSE m.score2 
            END as player_score,
            CASE 
                WHEN m.player1_id = ? THEN m.score2 
                ELSE m.score1 
            END as opponent_score,
            CASE 
                WHEN (m.player1_id = ? AND m.score1 > m.score2) OR 
                     (m.player2_id = ? AND m.score2 > m.score1) 
                THEN 'Victoire' 
                ELSE 'Défaite' 
            END as result,
            m.played_at,
            CASE 
                WHEN m.player1_id = ? THEN mec.p1_change_standard 
                ELSE mec.p2_change_standard 
            END as change_standard,
            CASE 
                WHEN m.player1_id = ? THEN mec.p1_change_with_score 
                ELSE mec.p2_change_with_score 
            END as change_with_score
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.id
        JOIN players p2 ON m.player2_id = p2.id
        LEFT JOIN match_elo_changes mec ON m.id = mec.match_id
        WHERE m.player1_id = ? OR m.player2_id = ?
        ORDER BY m.played_at DESC
        LIMIT 50
    """, (player_id, player_id, player_id, player_id, player_id, player_id, player_id, player_id, player_id))
    
    matches_history = [
        {
            'id': r[0],
            'opponent': r[1],
            'score': f"{r[2]} - {r[3]}",
            'result': r[4],
            'played_at': r[5],
            'elo_change': {
                'standard': round(r[6], 1) if r[6] is not None else 0,
                'with_score': round(r[7], 1) if r[7] is not None else 0
            }
        }
        for r in c.fetchall()
    ]
    
    # Statistiques générales
    total_matches = len(matches_history)
    wins = sum(1 for m in matches_history if m['result'] == 'Victoire')
    losses = total_matches - wins
    win_rate = round((wins / total_matches * 100) if total_matches > 0 else 0, 1)
    
    # Top adversaires
    c.execute("""
        SELECT 
            CASE 
                WHEN m.player1_id = ? THEN p2.id
                ELSE p1.id
            END as opponent_id,
            CASE 
                WHEN m.player1_id = ? THEN p2.name
                ELSE p1.name
            END as opponent_name,
            COUNT(*) as matches,
            SUM(CASE 
                WHEN (m.player1_id = ? AND m.score1 > m.score2) OR 
                     (m.player2_id = ? AND m.score2 > m.score1) 
                THEN 1 ELSE 0 
            END) as wins,
            SUM(CASE 
                WHEN (m.player1_id = ? AND m.score1 < m.score2) OR 
                     (m.player2_id = ? AND m.score2 < m.score1) 
                THEN 1 ELSE 0 
            END) as losses
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.id
        JOIN players p2 ON m.player2_id = p2.id
        WHERE m.player1_id = ? OR m.player2_id = ?
        GROUP BY opponent_id, opponent_name
        ORDER BY matches DESC
        LIMIT 10
    """, (player_id, player_id, player_id, player_id, player_id, player_id, player_id, player_id))
    
    top_opponents = [
        {
            'id': r[0],
            'name': r[1],
            'matches': r[2],
            'wins': r[3],
            'losses': r[4]
        }
        for r in c.fetchall()
    ]
    
    player_conf_data_std = prepare_player_confidence_data(c, player_id, player[2])
    all_players = get_all_players_summary(c)
    
    if player_conf_data_std:
        confidence_standard = calculate_advanced_confidence(
            player_conf_data_std, 
            all_players,
            None  # all_matches pas nécessaire pour l'instant
        )
    else:
        # Joueur sans matchs
        confidence_standard = {
            'predicted_rating': player[2],
            'lower': player[2] - 350,
            'upper': player[2] + 350,
            'rd': 350,
            'confidence': 0,
            'factors': {}
        }
    
    # Même chose pour Elo avec Score
    player_conf_data_score = prepare_player_confidence_data(c, player_id, player[3])
    if player_conf_data_score:
        player_conf_data_score['elo_current'] = player[3]
        confidence_with_score = calculate_advanced_confidence(
            player_conf_data_score,
            all_players,
            None
        )
    else:
        confidence_with_score = {
            'predicted_rating': player[3],
            'lower': player[3] - 350,
            'upper': player[3] + 350,
            'rd': 350,
            'confidence': 0,
            'factors': {}
        }
    
    conn.close()
    
    return (jsonify({
        'player': {
            'id': player[0],
            'name': player[1],
            'elo_standard': round(player[2], 1),
            'elo_with_score': round(player[3], 1)
        },
        'stats': {
            'total_matches': total_matches,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate
        },
        'confidence': {
            'standard': confidence_standard,
            'with_score': confidence_with_score
        },
        'matches_history': matches_history,
        'top_opponents': top_opponents
    }), 200, HEADERS)

def get_player_elo_history(request, conn, c):
    """Récupère l'historique complet de l'Elo d'un joueur"""
    
    player_id = int(request.path.split('/')[3])
    
    # Récupère l'Elo initial
    c.execute("SELECT created_at FROM players WHERE id = ?", (player_id,))
    player_created = c.fetchone()
    
    if not player_created:
        conn.close()
        return (jsonify({'error': 'Player not found'}), 404, HEADERS)
    
    # Récupère tous les matchs du joueur avec les changements
    c.execute("""
        SELECT 
            m.played_at,
            CASE 
                WHEN m.player1_id = ? THEN mec.p1_elo_standard_before + mec.p1_change_standard
                ELSE mec.p2_elo_standard_before + mec.p2_change_standard
            END as elo_standard_after,
            CASE 
                WHEN m.player1_id = ? THEN mec.p1_elo_with_score_before + mec.p1_change_with_score
                ELSE mec.p2_elo_with_score_before + mec.p2_change_with_score
            END as elo_with_score_after
        FROM matches m
        JOIN match_elo_changes mec ON m.id = mec.match_id
        WHERE m.player1_id = ? OR m.player2_id = ?
        ORDER BY m.played_at ASC
    """, (player_id, player_id, player_id, player_id))
    
    history = [
        {
            'date': r[0],
            'elo_standard': round(r[1], 1),
            'elo_with_score': round(r[2], 1)
        }
        for r in c.fetchall()
    ]
    
    # Ajoute le point de départ si il y a des matchs
    if history:
        # Récupère les premières valeurs avant le premier match
        c.execute("""
            SELECT 
                CASE 
                    WHEN m.player1_id = ? THEN mec.p1_elo_standard_before
                    ELSE mec.p2_elo_standard_before
                END as elo_standard_before,
                CASE 
                    WHEN m.player1_id = ? THEN mec.p1_elo_with_score_before
                    ELSE mec.p2_elo_with_score_before
                END as elo_with_score_before,
                m.played_at
            FROM matches m
            JOIN match_elo_changes mec ON m.id = mec.match_id
            WHERE m.player1_id = ? OR m.player2_id = ?
            ORDER BY m.played_at ASC
            LIMIT 1
        """, (player_id, player_id, player_id, player_id))
        
        first_match = c.fetchone()
        if first_match:
            history.insert(0, {
                'date': first_match[2],
                'elo_standard': round(first_match[0], 1),
                'elo_with_score': round(first_match[1], 1)
            })
    
    # Récupère le range de dates global (tous les matchs de la base)
    c.execute("SELECT MIN(played_at), MAX(played_at) FROM matches")
    date_range = c.fetchone()
    
    conn.close()
    
    # ⭐ Gérer le cas où il n'y a pas de matchs du tout dans la base
    if not date_range[0] or not date_range[1]:
        return (jsonify({
            'history': history,
            'global_date_range': {
                'min': None,
                'max': None
            }
        }), 200, HEADERS)
    
    return (jsonify({
        'history': history,
        'global_date_range': {
            'min': date_range[0],
            'max': date_range[1]
        }
    }), 200, HEADERS)

def compare_players(request, conn, c):
    player1_id = request.args.get('player1')
    player2_id = request.args.get('player2')

    if not player1_id or not player2_id:
        conn.close()
        return (jsonify({'error': 'Missing player IDs'}), 400, HEADERS)

    # Infos des deux joueurs
    c.execute("SELECT id, name, elo_standard, elo_with_score FROM players WHERE id IN (?, ?)", 
                (player1_id, player2_id))
    players = c.fetchall()

    if len(players) != 2:
        conn.close()
        return (jsonify({'error': 'One or both players not found'}), 404, HEADERS)

    # Matchs directs entre ces deux joueurs
    c.execute("""
        SELECT 
            p1.name, p2.name, m.score1, m.score2, m.played_at
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.id
        JOIN players p2 ON m.player2_id = p2.id
        WHERE (m.player1_id = ? AND m.player2_id = ?) OR (m.player1_id = ? AND m.player2_id = ?)
        ORDER BY m.played_at DESC
    """, (player1_id, player2_id, player2_id, player1_id))

    head_to_head = []
    p1_wins = 0
    p2_wins = 0

    for row in c.fetchall():
        p1_name, p2_name, s1, s2, played_at = row
        winner = p1_name if s1 > s2 else p2_name

        # Compter les victoires
        if winner == players[0][1]:
            p1_wins += 1
        else:
            p2_wins += 1

        head_to_head.append({
            'player1': p1_name,
            'player2': p2_name,
            'score1': s1,
            'score2': s2,
            'winner': winner,
            'played_at': played_at
        })

    conn.close()

    return (jsonify({
        'player1': {
            'id': players[0][0],
            'name': players[0][1],
            'elo_standard': round(players[0][2], 1),
            'elo_with_score': round(players[0][3], 1),
            'wins_h2h': p1_wins
        },
        'player2': {
            'id': players[1][0],
            'name': players[1][1],
            'elo_standard': round(players[1][2], 1),
            'elo_with_score': round(players[1][3], 1),
            'wins_h2h': p2_wins
        },
        'head_to_head': head_to_head,
        'total_matches': len(head_to_head)
    }), 200, HEADERS)


def prepare_player_confidence_data(c, player_id, player_elo):
    """Prépare les données nécessaires pour le calcul de confiance"""
    
    # Récupère tous les matchs du joueur avec détails
    c.execute("""
        SELECT 
            m.played_at,
            CASE WHEN m.player1_id = ? THEN p2.id ELSE p1.id END as opponent_id,
            CASE WHEN m.player1_id = ? THEN p2.elo_standard ELSE p1.elo_standard END as opponent_elo,
            CASE WHEN m.player1_id = ? THEN mec.p1_change_standard ELSE mec.p2_change_standard END as elo_change,
            CASE 
                WHEN (m.player1_id = ? AND m.score1 > m.score2) OR 
                     (m.player2_id = ? AND m.score2 > m.score1) 
                THEN 1 ELSE 0 
            END as won
        FROM matches m
        JOIN players p1 ON m.player1_id = p1.id
        JOIN players p2 ON m.player2_id = p2.id
        LEFT JOIN match_elo_changes mec ON m.id = mec.match_id
        WHERE m.player1_id = ? OR m.player2_id = ?
        ORDER BY m.played_at ASC
    """, (player_id, player_id, player_id, player_id, player_id, player_id, player_id))
    
    matches = c.fetchall()
    
    if not matches:
        return None
    
    # Calcule les probabilités de victoire attendues (formule Elo standard)
    def expected_score(player_elo, opponent_elo):
        return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    
    opponents_faced = set()
    elo_changes = []
    match_results = []
    expected_probs = []
    opponent_elos = []
    
    for match in matches:
        opponents_faced.add(match[1])
        opponent_elos.append(match[2])
        elo_changes.append(match[3] if match[3] is not None else 0)
        match_results.append(match[4])
        expected_probs.append(expected_score(player_elo, match[2]))
    
    return {
        'num_matches': len(matches),
        'opponents_faced': opponents_faced,
        'elo_changes': elo_changes,
        'match_results': match_results,
        'expected_win_probs': expected_probs,
        'avg_opponent_elo': sum(opponent_elos) / len(opponent_elos) if opponent_elos else None,
        'elo_current': player_elo
    }


def get_all_players_summary(c):
    """Récupère un résumé de tous les joueurs pour comparaison"""
    c.execute("""
        SELECT 
            p.id,
            p.elo_standard,
            COUNT(DISTINCT m.id) as num_matches
        FROM players p
        LEFT JOIN matches m ON p.id = m.player1_id OR p.id = m.player2_id
        GROUP BY p.id
    """)
    
    return [
        {
            'id': r[0],
            'elo': r[1],
            'num_matches': r[2]
        }
        for r in c.fetchall()
    ]