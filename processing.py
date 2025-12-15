import math
from collections import defaultdict

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

def calculate_advanced_confidence(player_id, player_data, all_players_data, all_matches,
                                 aim_matches=50,
                                 rd_min=25, rd_max=250,
                                 gap_scale=200.0,
                                 eff_decay=15.0):
    """
    Heuristique adaptée petit pool (<=15), adversaires répétés, écarts de niveau fréquents.

    Renvoie:
    - predicted_rating
    - rd
    - confidence (0..100)
    - lower/upper (compat: 95%)
    - intervals: { "50": {lower, upper, z}, "75": ..., "95": ... }
    - factors (0..1 + valeurs brutes)
    """
    def clamp(x, lo=0.0, hi=1.0):
        return max(lo, min(hi, x))

    current_elo = float(player_data.get("elo_current", 0.0))
    num_matches = int(player_data.get("num_matches", 0))
    opponents_faced = set(player_data.get("opponents_faced", set()) or set())

    # Index joueurs (elo + volume) pour les adversaires
    by_id = {p["id"]: p for p in all_players_data if "id" in p}
    pool_size = len(by_id)

    # Compter les matchs vs chaque adversaire (à partir de all_matches)
    vs_counts = defaultdict(int)
    for m in all_matches:
        p1, p2 = m.get("player1_id"), m.get("player2_id")
        if p1 == player_id and p2 in by_id:
            vs_counts[p2] += 1
        elif p2 == player_id and p1 in by_id:
            vs_counts[p1] += 1

    # ----- FACTEURS EXPLICATIFS (0..1) -----

    # 1) Volume brut (saturant vite pour convergence pragmatique)
    f_matches = 1.0 - math.exp(-num_matches / max(1.0, aim_matches))

    # 2) Diversité (sur un petit pool, c'est très important pour "caler" le niveau)
    denom = max(1, pool_size - 1)
    f_diversity = clamp(len(opponents_faced) / denom)

    # 3) Répétition (pénalise si on joue toujours la même personne)
    if num_matches <= 0 or len(vs_counts) == 0:
        f_repeat = 0.0
    else:
        ps = [c / num_matches for c in vs_counts.values()]
        hhi = sum(p * p for p in ps)  # 1 => tout sur un seul adversaire
        k = max(1, len(vs_counts))
        f_repeat = 0.0 if k == 1 else clamp(1.0 - (hhi - 1.0 / k) / (1.0 - 1.0 / k))

    # 4) Informativité (max si p≈0.5, min si match "joué d'avance")
    probs = player_data.get("expected_win_probs") or []
    if probs:
        info_vals = [4.0 * p * (1.0 - p) for p in probs]
        f_info = clamp(sum(info_vals) / len(info_vals))
    else:
        f_info = 0.5  # fallback neutre

    # 5) Fiabilité adversaires (proxy simple = leur volume)
    if opponents_faced:
        rels = []
        for oid in opponents_faced:
            opp = by_id.get(oid)
            if not opp:
                continue
            rels.append(clamp(float(opp.get("num_matches", 0)) / max(1.0, aim_matches)))
        f_opponents = sum(rels) / len(rels) if rels else 0.0
    else:
        f_opponents = 0.0

    # 6) Pénalité écart de niveau
    if opponents_faced:
        gaps = []
        for oid in opponents_faced:
            opp = by_id.get(oid)
            if not opp:
                continue
            gaps.append(abs(current_elo - float(opp.get("elo", current_elo))))
        mean_gap = (sum(gaps) / len(gaps)) if gaps else 0.0
    else:
        mean_gap = 0.0
    f_gap = math.exp(-mean_gap / max(1.0, gap_scale))

    # ----- MATCHS EFFECTIFS -----
    effective_matches = (
        num_matches
        * (0.30 + 0.70 * f_info)
        * (0.20 + 0.80 * f_diversity)
        * (0.35 + 0.65 * f_repeat)
        * (0.35 + 0.65 * f_opponents)
        * (0.50 + 0.50 * f_gap)
    )

    # ----- RD -----
    rd = rd_min + (rd_max - rd_min) * math.exp(-effective_matches / max(1e-9, eff_decay))

    # ----- Intervalles (centraux) -----
    # z pour intervalles centraux 50/75/95%
    z_map = {
        "50": 0.67448975,
        "75": 1.15034938,
        "95": 1.95996398,
    }

    intervals = {}
    for p_str, z in z_map.items():
        lower = current_elo - z * rd
        upper = current_elo + z * rd
        intervals[p_str] = {
            "p": int(p_str),
            "z": round(z, 6),
            "lower": round(lower, 1),
            "upper": round(upper, 1),
        }

    # compat: lower/upper = 95%
    lower_95 = intervals["95"]["lower"]
    upper_95 = intervals["95"]["upper"]

    # Confidence (0..100) : projection de RD
    confidence_score = 100.0 * (rd_max - rd) / max(1e-9, (rd_max - rd_min))
    confidence_score = clamp(confidence_score / 100.0) * 100.0

    return {
        "predicted_rating": round(current_elo, 1),
        "lower": lower_95,
        "upper": upper_95,
        "rd": round(rd, 1),
        "confidence": round(confidence_score, 1),
        "intervals": intervals,
        "factors": {
            "matches": round(f_matches, 3),
            "diversity": round(f_diversity, 3),
            "repeat_penalty": round(f_repeat, 3),
            "informativeness": round(f_info, 3),
            "opponents_reliability": round(f_opponents, 3),
            "gap_penalty": round(f_gap, 3),
            "effective_matches": round(effective_matches, 2),
            "mean_gap": round(mean_gap, 1),
        },
    }
