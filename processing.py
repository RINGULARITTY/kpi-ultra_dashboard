import math
import numpy as np

from db import get_db_connection

def calculate_fftt_standard_elo(rating_diff, is_winner, is_upset):
    """
    Calcul du système Elo FFTT standard (coeff 1)
    """
    abs_diff = abs(rating_diff)

    # Grille FFTT
    if abs_diff < 25:
        normal_win, normal_loss, upset_win, upset_loss = 6, -5, 6, -5
    elif abs_diff < 50:
        normal_win, normal_loss, upset_win, upset_loss = 5.5, -4.5, 7, -6
    elif abs_diff < 100:
        normal_win, normal_loss, upset_win, upset_loss = 5, -4, 8, -7
    elif abs_diff < 150:
        normal_win, normal_loss, upset_win, upset_loss = 4, -3, 10, -8
    elif abs_diff < 200:
        normal_win, normal_loss, upset_win, upset_loss = 3, -2, 13, -10
    elif abs_diff < 300:
        normal_win, normal_loss, upset_win, upset_loss = 2, -1, 17, -12.5
    elif abs_diff < 400:
        normal_win, normal_loss, upset_win, upset_loss = 1, -0.5, 22, -16
    elif abs_diff < 500:
        normal_win, normal_loss, upset_win, upset_loss = 0.5, 0, 28, -20
    else:
        normal_win, normal_loss, upset_win, upset_loss = 0, 0, 40, -29

    if is_winner:
        return upset_win if is_upset else normal_win
    else:
        return upset_loss if is_upset else normal_loss

def calculate_elo_with_score(rating1, rating2, score1, score2):
    """
    Système Elo modifié prenant en compte la différence de score
    """
    K = 30

    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    expected2 = 1 - expected1

    total_points = score1 + score2
    winner = 1 if score1 > score2 else 2

    steepness = 5

    if winner == 1:
        margin_ratio = score1 / total_points
        normalized_margin = (margin_ratio - 0.5) * 2
        sigmoid_score = 1 / (1 + math.exp(-steepness * (normalized_margin - 0.5)))
        actual_score1 = expected1 + (1 - expected1) * sigmoid_score
        actual_score2 = 1 - actual_score1
    else:
        margin_ratio = score2 / total_points
        normalized_margin = (margin_ratio - 0.5) * 2
        sigmoid_score = 1 / (1 + math.exp(-steepness * (normalized_margin - 0.5)))
        actual_score2 = expected2 + (1 - expected2) * sigmoid_score
        actual_score1 = 1 - actual_score2

    rating_change1 = K * (actual_score1 - expected1)
    rating_change2 = K * (actual_score2 - expected2)

    return rating_change1, rating_change2

def get_changed_scores(c, player1_id, player2_id, score1, score2):
    c.execute("SELECT elo_standard, elo_with_score FROM players WHERE id = ?", (player1_id,))
    p1_standard, p1_with_score = c.fetchone()

    c.execute("SELECT elo_standard, elo_with_score FROM players WHERE id = ?", (player2_id,))
    p2_standard, p2_with_score = c.fetchone()
    
    rating_diff1 = p1_standard - p2_standard
    is_winner1 = score1 > score2
    is_upset1 = (rating_diff1 < 0 and is_winner1) or (rating_diff1 > 0 and not is_winner1)

    change1_standard = calculate_fftt_standard_elo(rating_diff1, is_winner1, is_upset1)
    
    is_upset2 = is_upset1  # L'upset est symétrique, mais rendre explicite
    change2_standard = calculate_fftt_standard_elo(-rating_diff1, not is_winner1, is_upset2)

    # Système avec score
    change1_with_score, change2_with_score = calculate_elo_with_score(
        p1_with_score, p2_with_score, score1, score2
    )
    
    return (
        p1_standard, p1_with_score, change1_standard, change1_with_score,
        p2_standard, p2_with_score, change2_standard, change2_with_score
    )

def update_ratings(player1_id, player2_id, score1, score2, match_id):
    """Met à jour les ratings Elo et sauvegarde les changements"""
    conn = get_db_connection()
    c = conn.cursor()

    # Récupère les données actuelles et calcule les changements
    (p1_standard, p1_with_score, change1_standard, change1_with_score,
     p2_standard, p2_with_score, change2_standard, change2_with_score
    ) = get_changed_scores(c, player1_id, player2_id, score1, score2)

    # Sauvegarde l'historique AVANT de modifier
    c.execute("""
        INSERT INTO match_elo_changes (
            match_id, player1_id, player2_id,
            p1_elo_standard_before, p1_elo_with_score_before,
            p1_change_standard, p1_change_with_score,
            p2_elo_standard_before, p2_elo_with_score_before,
            p2_change_standard, p2_change_with_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (match_id, player1_id, player2_id,
          p1_standard, p1_with_score, change1_standard, change1_with_score,
          p2_standard, p2_with_score, change2_standard, change2_with_score))

    # Met à jour les ratings
    c.execute("UPDATE players SET elo_standard = ?, elo_with_score = ? WHERE id = ?",
              (p1_standard + change1_standard, p1_with_score + change1_with_score, player1_id))

    c.execute("UPDATE players SET elo_standard = ?, elo_with_score = ? WHERE id = ?",
              (p2_standard + change2_standard, p2_with_score + change2_with_score, player2_id))

    conn.commit()
    conn.close()

def rollback_match_elo(match_id):
    """Inverse les changements d'Elo d'un match spécifique"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Récupère les changements du match à supprimer
    c.execute("""
        SELECT player1_id, player2_id,
               p1_change_standard, p1_change_with_score,
               p2_change_standard, p2_change_with_score
        FROM match_elo_changes
        WHERE match_id = ?
    """, (match_id,))
    
    changes = c.fetchone()
    if not changes:
        conn.close()
        return None
    
    p1_id, p2_id, p1_std, p1_score, p2_std, p2_score = changes
    
    # Inverse les changements en soustrayant les deltas
    c.execute("""
        UPDATE players 
        SET elo_standard = elo_standard - ?,
            elo_with_score = elo_with_score - ?
        WHERE id = ?
    """, (p1_std, p1_score, p1_id))
    
    c.execute("""
        UPDATE players 
        SET elo_standard = elo_standard - ?,
            elo_with_score = elo_with_score - ?
        WHERE id = ?
    """, (p2_std, p2_score, p2_id))
    
    conn.commit()
    
    # Récupère le timestamp pour savoir quels matchs recalculer
    c.execute("SELECT played_at FROM matches WHERE id = ?", (match_id,))
    played_at = c.fetchone()[0]
    
    conn.close()
    return played_at


def recalculate_after_timestamp(timestamp, excluded_match_id):
    """Recalcule tous les matchs après un timestamp donné"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Récupère tous les matchs après le timestamp (excluant le match supprimé)
    c.execute("""
        SELECT id, player1_id, player2_id, score1, score2
        FROM matches 
        WHERE played_at >= ? AND id != ?
        ORDER BY played_at ASC
    """, (timestamp, excluded_match_id))
    
    matches_to_recalc = c.fetchall()
    
    # Récupère tous les joueurs affectés
    affected_players = set()
    for _, p1, p2, _, _ in matches_to_recalc:
        affected_players.add(p1)
        affected_players.add(p2)
    
    # Inverse les changements de tous ces matchs
    for match_id, _, _, _, _ in matches_to_recalc:
        c.execute("SELECT player1_id, player2_id, p1_change_standard, p1_change_with_score, p2_change_standard, p2_change_with_score FROM match_elo_changes WHERE match_id = ?", (match_id,))
        result = c.fetchone()
        if result:
            p1_id, p2_id, p1_std, p1_score, p2_std, p2_score = result
            c.execute("UPDATE players SET elo_standard = elo_standard - ?, elo_with_score = elo_with_score - ? WHERE id = ?", 
                     (p1_std, p1_score, p1_id))
            c.execute("UPDATE players SET elo_standard = elo_standard - ?, elo_with_score = elo_with_score - ? WHERE id = ?",
                     (p2_std, p2_score, p2_id))
    
    # Supprime les anciens changements
    c.execute("""
        DELETE FROM match_elo_changes 
        WHERE match_id IN (
            SELECT id FROM matches 
            WHERE played_at >= ? AND id != ?
        )
    """, (timestamp, excluded_match_id))
    
    conn.commit()
    conn.close()
    
    # Recalcule tous ces matchs
    for match_id, p1_id, p2_id, s1, s2 in matches_to_recalc:
        update_ratings(p1_id, p2_id, s1, s2, match_id)

def calculate_advanced_confidence(player_data, all_players_data, all_matches):
    """
    Calcule un score de confiance multi-facteurs adapté au ping-pong
    
    Args:
        player_data: {id, num_matches, opponents_faced, elo_history, elo_current}
        all_players_data: Liste de tous les joueurs avec leurs stats
        all_matches: Tous les matchs de la base
    
    Returns:
        Dict avec predicted_rating, lower, upper, confidence, factors_breakdown
    """
    
    # 1. FACTEUR: Nombre de matchs (base Glicko modifiée)
    num_matches = player_data['num_matches']
    max_matches = max(p['num_matches'] for p in all_players_data)
    
    # Pénalité d'écart avec le joueur le plus actif
    match_gap_ratio = num_matches / max_matches if max_matches > 0 else 0
    # Fonction de pénalité douce : 50 matchs = ~90% confiance, 10 matchs = ~45%
    f_matches = 100 * (1 - math.exp(-num_matches / 30))
    f_gap = 100 * match_gap_ratio  # Pénalité linéaire sur l'écart
    
    
    # 2. FACTEUR: Diversité des adversaires
    total_players = len(all_players_data) - 1  # Exclure le joueur lui-même
    opponents_faced = len(player_data['opponents_faced'])
    
    diversity_ratio = opponents_faced / total_players if total_players > 0 else 0
    # Bonus pour avoir affronté beaucoup de joueurs différents
    f_diversity = 100 * diversity_ratio
    
    
    # 3. FACTEUR: Volatilité/Inertie du rating
    # Calcule l'écart-type des changements d'Elo récents
    if len(player_data['elo_changes']) > 5:
        recent_changes = player_data['elo_changes'][-20:]  # 20 derniers matchs
        volatility = np.std(recent_changes)
        
        # Normalisation : volatilité faible = confiance élevée
        # Pour le ping-pong, on s'attend à +/- 5-10 points par match
        # Volatilité > 15 = joueur instable, < 5 = très stable
        f_stability = 100 * (1 - min(volatility / 20, 1))
    else:
        # Pas assez de données, confiance moyenne
        f_stability = 50
    
    
    # 4. FACTEUR: Qualité des adversaires (Strength of Schedule)
    # Compare l'Elo moyen des adversaires avec l'Elo moyen global
    if player_data['avg_opponent_elo'] and all_players_data:
        global_avg_elo = np.mean([p['elo'] for p in all_players_data])
        opponent_quality = player_data['avg_opponent_elo'] / global_avg_elo
        
        # Bonus si on affronte des joueurs de niveau varié/élevé
        # Optimal si ratio proche de 1.0 (adversaires représentatifs)
        f_schedule = 100 * (1 - abs(1 - opponent_quality) * 0.5)
    else:
        f_schedule = 50
    
    
    # 5. FACTEUR: Consistance des performances
    # Analyse win_rate vs expected_win_rate (basé sur Elo des adversaires)
    if len(player_data['match_results']) > 10:
        actual_wins = sum(player_data['match_results'])
        expected_wins = sum(player_data['expected_win_probs'])
        
        # Performance conforme = confiance haute
        performance_diff = abs(actual_wins - expected_wins) / len(player_data['match_results'])
        f_consistency = 100 * (1 - performance_diff)
    else:
        f_consistency = 50
    
    
    # AGRÉGATION PONDÉRÉE des facteurs
    weights = {
        'matches': 0.25,      # Nombre absolu de matchs
        'gap': 0.15,          # Écart avec le plus actif
        'diversity': 0.20,    # Diversité des adversaires
        'stability': 0.20,    # Stabilité du rating
        'schedule': 0.10,     # Qualité des adversaires
        'consistency': 0.10   # Consistance performances
    }
    
    confidence_score = (
        weights['matches'] * f_matches +
        weights['gap'] * f_gap +
        weights['diversity'] * f_diversity +
        weights['stability'] * f_stability +
        weights['schedule'] * f_schedule +
        weights['consistency'] * f_consistency
    )
    
    # Calcul du RD adaptatif (plus conservateur que Glicko standard)
    # RD élevé = large intervalle de confiance
    base_rd = 350  # RD maximal pour nouveaux joueurs
    min_rd = 50    # RD minimal même pour joueurs expérimentés (ping-pong plus volatile)
    
    # RD inversement proportionnel à la confiance
    rd = base_rd - (base_rd - min_rd) * (confidence_score / 100)
    
    # Intervalle de confiance à 95%
    current_elo = player_data['elo_current']
    lower = current_elo - 1.96 * rd
    upper = current_elo + 1.96 * rd
    
    return {
        'predicted_rating': round(current_elo, 1),
        'lower': round(lower, 1),
        'upper': round(upper, 1),
        'rd': round(rd, 1),
        'confidence': round(confidence_score, 1),
        'factors': {
            'matches': round(f_matches, 1),
            'gap_penalty': round(f_gap, 1),
            'diversity': round(f_diversity, 1),
            'stability': round(f_stability, 1),
            'schedule': round(f_schedule, 1),
            'consistency': round(f_consistency, 1)
        }
    }
