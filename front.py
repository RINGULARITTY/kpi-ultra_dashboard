HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <title>KPI Ultra Booster</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .leaderboard-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .leaderboard-title {
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
        .leaderboards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .leaderboard {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .leaderboard h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .player-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 15px;
            margin: 8px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s;
        }
        .player-bar:hover { transform: translateX(5px); }
        .player-rank { font-weight: bold; margin-right: 10px; }
        .player-name { flex-grow: 1; }
        .player-elo { font-weight: bold; font-size: 1.1em; }
        .bottom-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .form-group { margin-bottom: 15px; }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .score-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-top: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button.danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .match-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .match-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .match-item button {
            width: auto;
            padding: 6px 12px;
            font-size: 0.9em;
            margin: 0;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .modal-content {
            background-color: white;
            margin: 15% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 400px;
            text-align: center;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .modal-buttons button { margin: 0; }
        .modal-content-large {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 900px;
            max-height: 85vh;
            overflow-y: auto;
            animation: slideIn 0.3s;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }

        .modal-header h2 {
            margin: 0;
            color: #667eea;
        }

        .btn-close {
            background: none;
            border: none;
            font-size: 2em;
            color: #999;
            cursor: pointer;
            padding: 0;
            width: auto;
            margin: 0;
        }

        .btn-close:hover {
            color: #667eea;
        }

        /* Grille de stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-label {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-green {
            color: #4caf50;
        }

        .stat-red {
            color: #f44336;
        }

        /* Sections de stats */
        .stats-sections {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .stats-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }

        .stats-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        /* Liste d'adversaires */
        .opponents-list, .match-history-list, .h2h-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .opponent-item, .history-item, .h2h-item {
            background: white;
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        .opponent-name, .history-opponent {
            font-weight: 600;
            flex: 1;
        }

        .opponent-record {
            color: #666;
            font-size: 0.9em;
        }

        .btn-small {
            padding: 5px 10px;
            font-size: 0.85em;
            width: auto;
            margin: 0;
        }

        /* Historique de matchs */
        .history-item.victory {
            border-left: 4px solid #4caf50;
        }

        .history-item.defeat {
            border-left: 4px solid #f44336;
        }

        .history-result {
            font-weight: bold;
            min-width: 80px;
        }

        .history-result.victory {
            color: #4caf50;
        }

        .history-result.defeat {
            color: #f44336;
        }

        .history-score {
            font-weight: 600;
            color: #667eea;
        }

        .history-date {
            color: #999;
            font-size: 0.9em;
        }

        /* Footer de modal */
        .modal-footer {
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Comparaison */
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 30px;
            align-items: center;
            margin-bottom: 30px;
        }

        .comparison-player {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
        }

        .comparison-player h3 {
            color: #667eea;
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .comp-stats {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .comp-stat {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }

        .comp-stat.highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .comp-label {
            font-size: 0.9em;
        }

        .comp-value {
            font-weight: bold;
            font-size: 1.2em;
        }

        .comparison-vs {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-align: center;
        }

        /* H2H Section */
        .h2h-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }

        .h2h-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .h2h-match {
            font-weight: 600;
            flex: 1;
        }

        .h2h-winner {
            color: #ffa726;
        }

        .h2h-date {
            color: #999;
            font-size: 0.9em;
            min-width: 100px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .stats-sections {
                grid-template-columns: 1fr;
            }

            .comparison-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .comparison-vs {
                font-size: 1.5em;
            }
        }
        
        .elo-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 5px;
        }

        .elo-positive {
            background: #e8f5e9;
            color: #2e7d32;
        }

        .elo-negative {
            background: #ffebee;
            color: #c62828;
        }

        .elo-neutral {
            background: #f5f5f5;
            color: #757575;
        }

        /* Amélioration de l'historique */
        .match-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .match-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .match-score {
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }

        .match-players {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 12px;
        }

        .player-info {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
        }

        .player-info.winner {
            background: #e8f5e9;
            border: 2px solid #4caf50;
        }

        .player-name-match {
            font-weight: 600;
            font-size: 1em;
            flex-grow: 1;
        }
        
        .player-score {
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
            margin-left: 10px;
        }

        .elo-changes {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            font-size: 0.85em;
        }
        
        .match-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
        }

        .match-date {
            color: #999;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .match-footer button {
            width: auto;
            padding: 8px 16px;
            font-size: 0.9em;
            margin: 0;
        }

        .match-actions {
            margin-top: 10px;
        }

        /* Amélioration des stats d'historique */
        .history-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .history-item.victory {
            border-left: 4px solid #4caf50;
        }

        .history-item.defeat {
            border-left: 4px solid #f44336;
        }

        .history-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        .history-elo-change {
            display: flex;
            gap: 5px;
            margin-top: 5px;
        }
        
        .chart-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .chart-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
            text-align: center;
        }

        .chart-container {
            position: relative;
            height: 350px;
            background: white;
            padding: 15px;
            border-radius: 8px;
        }

        .chart-legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 0.9em;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .legend-color {
            width: 20px;
            height: 3px;
            border-radius: 2px;
        }

        .legend-standard {
            background: #667eea;
        }

        .legend-score {
            background: #764ba2;
        }
        
        .prediction-section {
            margin: 25px 0;
        }

        .prediction-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.4em;
            text-align: center;
        }

        .prediction-cards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        /* Carte de prédiction individuelle */
        .prediction-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }

        .prediction-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }

        .prediction-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .prediction-header h4 {
            color: #667eea;
            margin: 0;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .confidence-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }

        /* Rating principal */
        .predicted-rating-display {
            text-align: center;
            margin: 20px 0;
        }

        .predicted-rating-value {
            font-size: 3.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
        }

        .rating-label {
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }

        /* Intervalle de confiance */
        .confidence-interval {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }

        .interval-label {
            color: #666;
            font-size: 0.85em;
            margin-bottom: 10px;
            text-align: center;
            font-weight: 500;
        }

        .interval-range {
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
        }

        .interval-value {
            font-size: 1.3em;
            font-weight: 600;
            color: #667eea;
            min-width: 60px;
            text-align: center;
        }

        .interval-bar {
            flex: 1;
            height: 8px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            margin: 0 15px;
            position: relative;
        }

        .interval-bar::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 12px;
            height: 12px;
            background: #764ba2;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        /* Barre de confiance principale */
        .confidence-meter {
            margin: 20px 0;
        }

        .confidence-meter-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .confidence-meter-label span:first-child {
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }

        .confidence-percentage {
            font-size: 1.4em;
            font-weight: bold;
            color: #667eea;
        }

        .confidence-bar-track {
            background: #e0e0e0;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }

        .confidence-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #f5576c 0%, #ffa726 35%, #4caf50 70%, #4caf50 100%);
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 15px;
            position: relative;
        }

        .confidence-bar-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3));
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0%, 100% { opacity: 0; }
            50% { opacity: 1; }
        }

        /* Facteurs de confiance (breakdown) */
        .confidence-factors {
            margin-top: 20px;
        }

        .factors-toggle {
            background: none;
            border: none;
            color: #667eea;
            font-weight: 600;
            cursor: pointer;
            padding: 8px 0;
            width: 100%;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            transition: color 0.3s;
        }

        .factors-toggle:hover {
            color: #764ba2;
        }

        .factors-toggle-icon {
            transition: transform 0.3s;
        }

        .factors-toggle-icon.open {
            transform: rotate(180deg);
        }

        .factors-list {
            display: none;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }

        .factors-list.open {
            display: block;
            animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .factor-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .factor-item:last-child {
            border-bottom: none;
        }

        .factor-label {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #666;
            font-size: 0.9em;
        }

        .factor-icon {
            font-size: 1.2em;
        }

        .factor-value-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .factor-bar {
            width: 60px;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
        }

        .factor-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.4s ease;
        }

        .factor-value {
            font-weight: 600;
            color: #667eea;
            min-width: 40px;
            text-align: right;
            font-size: 0.9em;
        }

        /* Info supplémentaire */
        .prediction-info {
            background: #f8f9fa;
            border-left: 3px solid #667eea;
            padding: 12px 15px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 0.85em;
            color: #666;
        }

        .prediction-info strong {
            color: #667eea;
        }

        /* Tooltip pour les détails */
        .factor-tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }

        .factor-tooltip:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            white-space: nowrap;
            font-size: 0.8em;
            z-index: 1000;
            margin-bottom: 5px;
        }

        .factor-tooltip:hover::before {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #333;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .prediction-cards {
                grid-template-columns: 1fr;
            }
            
            .predicted-rating-value {
                font-size: 2.5em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏓 Table Tennis Elo Ranking</h1>
        <div class="leaderboard-section">
            <h2 class="leaderboard-title">Classements</h2>
            <div class="leaderboards">
                <div class="leaderboard">
                    <h3>📊 Système Elo Standard (FFTT)</h3>
                    <div id="leaderboard-standard"></div>
                </div>
                <div class="leaderboard">
                    <h3>📈 Système Elo avec Score</h3>
                    <div id="leaderboard-score"></div>
                </div>
            </div>
        </div>
        <div class="bottom-section">
            <div class="card">
                <h2>⚔️ Gestion des Matchs</h2>
                <form id="match-form">
                    <div class="form-group">
                        <label>Joueur 1</label>
                        <select id="player1-select" required>
                            <option value="">Sélectionner un joueur</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Joueur 2</label>
                        <select id="player2-select" required>
                            <option value="">Sélectionner un joueur</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Scores</label>
                        <div class="score-inputs">
                            <input type="number" id="score1" placeholder="Score J1" min="0" required>
                            <input type="number" id="score2" placeholder="Score J2" min="0" required>
                        </div>
                    </div>
                    <button type="submit">Ajouter le Match</button>
                </form>
                <div class="match-list" id="match-list"></div>
            </div>
            <div class="card">
                <h2>👥 Gestion des Joueurs</h2>
                <form id="player-form">
                    <div class="form-group">
                        <label>Nom du joueur</label>
                        <input type="text" id="player-name" placeholder="Entrer un nom" required>
                    </div>
                    <button type="submit">Ajouter le Joueur</button>
                </form>
                <div class="form-group" style="margin-top: 20px;">
                    <label>Supprimer un joueur</label>
                    <select id="player-delete-select">
                        <option value="">Sélectionner un joueur</option>
                    </select>
                    <button class="danger" onclick="deletePlayer()">Supprimer</button>
                </div>
            </div>
        </div>
    </div>
    <div id="confirm-modal" class="modal">
        <div class="modal-content">
            <h3 id="modal-message"></h3>
            <div class="modal-buttons">
                <button onclick="closeModal()">Annuler</button>
                <button class="danger" onclick="confirmAction()">Confirmer</button>
            </div>
        </div>
    </div>
    <div id="player-stats-modal" class="modal">
        <div class="modal-content-large">
            <div class="modal-header">
                <h2>📊 Statistiques de <span id="stats-player-name"></span></h2>
                <button class="btn-close" onclick="closePlayerStats()">×</button>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Elo Standard</div>
                    <div class="stat-value" id="stats-elo-standard">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Elo avec Score</div>
                    <div class="stat-value" id="stats-elo-score">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Matchs Joués</div>
                    <div class="stat-value" id="stats-total-matches">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Victoires</div>
                    <div class="stat-value stat-green" id="stats-wins">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Défaites</div>
                    <div class="stat-value stat-red" id="stats-losses">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Taux de Victoire</div>
                    <div class="stat-value" id="stats-win-rate">-</div>
                </div>
            </div>
            
            <div class="prediction-section">
                <h3>🎯 Prédiction de Rating avec Niveau de Confiance</h3>
                
                <div class="prediction-cards">
                    <!-- Carte Elo Standard -->
                    <div class="prediction-card">
                        <div class="prediction-header">
                            <h4>
                                <span>📊</span>
                                Elo Standard
                            </h4>
                            <div class="confidence-badge" id="confidence-badge-standard">
                                -
                            </div>
                        </div>

                        <div class="predicted-rating-display">
                            <div class="predicted-rating-value" id="pred-rating-standard">
                                -
                            </div>
                            <div class="rating-label">Rating Prédit</div>
                        </div>

                        <div class="confidence-interval">
                            <div class="interval-label">Intervalle de confiance à 95%</div>
                            <div class="interval-range">
                                <div class="interval-value" id="interval-lower-standard">-</div>
                                <div class="interval-bar"></div>
                                <div class="interval-value" id="interval-upper-standard">-</div>
                            </div>
                        </div>

                        <div class="confidence-meter">
                            <div class="confidence-meter-label">
                                <span>Niveau de Confiance</span>
                                <span class="confidence-percentage" id="confidence-pct-standard">-</span>
                            </div>
                            <div class="confidence-bar-track">
                                <div class="confidence-bar-fill" id="confidence-bar-standard" style="width: 0%">
                                </div>
                            </div>
                        </div>

                        <div class="confidence-factors">
                            <button class="factors-toggle" onclick="toggleFactors('standard')">
                                <span>Voir les facteurs détaillés</span>
                                <span class="factors-toggle-icon" id="toggle-icon-standard">▼</span>
                            </button>
                            <div class="factors-list" id="factors-list-standard">
                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">📊</span>
                                        <span class="factor-tooltip" data-tooltip="Plus vous jouez, plus votre rating est fiable">
                                            Nombre de matchs
                                        </span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-matches-standard" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-matches-val-standard">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">📉</span>
                                        <span class="factor-tooltip" data-tooltip="Comparé au joueur le plus actif">
                                            Écart avec leader
                                        </span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-gap-standard" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-gap-val-standard">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">👥</span>
                                        <span class="factor-tooltip" data-tooltip="Diversité des adversaires affrontés">
                                            Diversité adversaires
                                        </span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-diversity-standard" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-diversity-val-standard">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">📈</span>
                                        <span class="factor-tooltip" data-tooltip="Stabilité de vos performances">
                                            Stabilité du rating
                                        </span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-stability-standard" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-stability-val-standard">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">🎯</span>
                                        <span class="factor-tooltip" data-tooltip="Niveau moyen de vos adversaires">
                                            Qualité adversaires
                                        </span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-schedule-standard" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-schedule-val-standard">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">✓</span>
                                        <span class="factor-tooltip" data-tooltip="Cohérence entre vos résultats et votre Elo">
                                            Consistance
                                        </span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-consistency-standard" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-consistency-val-standard">-</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="prediction-info">
                            <strong>RD: <span id="rd-value-standard">-</span></strong> • 
                            Basé sur <span id="matches-count-standard">-</span> matchs
                        </div>
                    </div>

                    <!-- Carte Elo avec Score (même structure) -->
                    <div class="prediction-card">
                        <div class="prediction-header">
                            <h4>
                                <span>📈</span>
                                Elo avec Score
                            </h4>
                            <div class="confidence-badge" id="confidence-badge-score">
                                -
                            </div>
                        </div>

                        <div class="predicted-rating-display">
                            <div class="predicted-rating-value" id="pred-rating-score">
                                -
                            </div>
                            <div class="rating-label">Rating Prédit</div>
                        </div>

                        <div class="confidence-interval">
                            <div class="interval-label">Intervalle de confiance à 95%</div>
                            <div class="interval-range">
                                <div class="interval-value" id="interval-lower-score">-</div>
                                <div class="interval-bar"></div>
                                <div class="interval-value" id="interval-upper-score">-</div>
                            </div>
                        </div>

                        <div class="confidence-meter">
                            <div class="confidence-meter-label">
                                <span>Niveau de Confiance</span>
                                <span class="confidence-percentage" id="confidence-pct-score">-</span>
                            </div>
                            <div class="confidence-bar-track">
                                <div class="confidence-bar-fill" id="confidence-bar-score" style="width: 0%">
                                </div>
                            </div>
                        </div>

                        <div class="confidence-factors">
                            <button class="factors-toggle" onclick="toggleFactors('score')">
                                <span>Voir les facteurs détaillés</span>
                                <span class="factors-toggle-icon" id="toggle-icon-score">▼</span>
                            </button>
                            <div class="factors-list" id="factors-list-score">
                                <!-- Même structure que standard -->
                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">📊</span>
                                        <span>Nombre de matchs</span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-matches-score" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-matches-val-score">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">📉</span>
                                        <span>Écart avec leader</span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-gap-score" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-gap-val-score">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">👥</span>
                                        <span>Diversité adversaires</span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-diversity-score" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-diversity-val-score">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">📈</span>
                                        <span>Stabilité du rating</span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-stability-score" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-stability-val-score">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">🎯</span>
                                        <span>Qualité adversaires</span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-schedule-score" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-schedule-val-score">-</span>
                                    </div>
                                </div>

                                <div class="factor-item">
                                    <div class="factor-label">
                                        <span class="factor-icon">✓</span>
                                        <span>Consistance</span>
                                    </div>
                                    <div class="factor-value-container">
                                        <div class="factor-bar">
                                            <div class="factor-bar-fill" id="factor-consistency-score" style="width: 0%"></div>
                                        </div>
                                        <span class="factor-value" id="factor-consistency-val-score">-</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="prediction-info">
                            <strong>RD: <span id="rd-value-score">-</span></strong> • 
                            Basé sur <span id="matches-count-score">-</span> matchs
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chart-section">
                <h3>📈 Évolution de l'Elo</h3>
                <div class="chart-container">
                    <canvas id="player-elo-chart"></canvas>
                </div>
            </div>

            <div class="stats-sections">
                <div class="stats-section">
                    <h3>🏆 Top Adversaires</h3>
                    <div id="stats-top-opponents" class="opponents-list"></div>
                </div>

                <div class="stats-section">
                    <h3>📜 Historique des Matchs</h3>
                    <div id="stats-match-history" class="match-history-list"></div>
                </div>
            </div>

            <div class="modal-footer">
                <button id="btn-compare-player" class="btn-primary">Comparer</button>
            </div>
        </div>
    </div>
    <div id="compare-modal" class="modal">
        <div class="modal-content">
            <h3>Comparer avec un adversaire</h3>
            <p>Joueur 1 : <strong id="compare-player1-name"></strong></p>

            <div class="form-group">
                <label>Joueur 2</label>
                <select id="compare-player2-select"></select>
            </div>

            <div class="modal-buttons">
                <button onclick="closeCompareModal()">Annuler</button>
                <button class="btn-primary" onclick="confirmComparison()">Comparer</button>
            </div>
        </div>
    </div>
    <div id="comparison-results-modal" class="modal">
        <div class="modal-content-large">
            <div class="modal-header">
                <h2>⚔️ Comparaison</h2>
                <button class="btn-close" onclick="closeComparisonResults()">×</button>
            </div>

            <div class="comparison-grid">
                <div class="comparison-player">
                    <h3 id="comp-p1-name">-</h3>
                    <div class="comp-stats">
                        <div class="comp-stat">
                            <span class="comp-label">Elo Standard</span>
                            <span class="comp-value" id="comp-p1-elo-std">-</span>
                        </div>
                        <div class="comp-stat">
                            <span class="comp-label">Elo Score</span>
                            <span class="comp-value" id="comp-p1-elo-score">-</span>
                        </div>
                        <div class="comp-stat highlight">
                            <span class="comp-label">Victoires (H2H)</span>
                            <span class="comp-value" id="comp-p1-wins">-</span>
                        </div>
                    </div>
                </div>

                <div class="comparison-vs">VS</div>

                <div class="comparison-player">
                    <h3 id="comp-p2-name">-</h3>
                    <div class="comp-stats">
                        <div class="comp-stat">
                            <span class="comp-label">Elo Standard</span>
                            <span class="comp-value" id="comp-p2-elo-std">-</span>
                        </div>
                        <div class="comp-stat">
                            <span class="comp-label">Elo Score</span>
                            <span class="comp-value" id="comp-p2-elo-score">-</span>
                        </div>
                        <div class="comp-stat highlight">
                            <span class="comp-label">Victoires (H2H)</span>
                            <span class="comp-value" id="comp-p2-wins">-</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="chart-section">
                <h3>📊 Évolution Comparative</h3>
                <div class="chart-container">
                    <canvas id="comparison-elo-chart"></canvas>
                </div>
            </div>

            <div class="h2h-section">
                <h3>📋 Confrontations Directes</h3>
                <div id="h2h-history" class="h2h-list"></div>
            </div>
        </div>
    </div>

    <script>
        let players = [];
        let matches = [];
        let pendingAction = null;
        let currentPlayerStats = null;
        let comparePlayer1Id = null;
        let comparePlayer2Id = null;
        let playerEloChart = null;
        let comparisonEloChart = null;

        async function loadData() {
            await loadPlayers();
            await loadMatches();
        }
        async function loadPlayers() {
            const response = await fetch('/api/players');
            players = await response.json();
            updateLeaderboards();
            updatePlayerSelects();
        }
        async function loadMatches() {
            const response = await fetch('/api/matches');
            matches = await response.json();
            updateMatchList();
        }
        function updateLeaderboards() {
            const standardBoard = document.getElementById('leaderboard-standard');
            const scoreBoard = document.getElementById('leaderboard-score');

            const sortedStandard = [...players].sort((a, b) => b.elo_standard - a.elo_standard);
            const sortedScore = [...players].sort((a, b) => b.elo_with_score - a.elo_with_score);

            // ⭐ AJOUT: style="cursor: pointer;" et onclick="showPlayerStats(...)"
            standardBoard.innerHTML = sortedStandard.map((p, i) => `
                <div class="player-bar" style="cursor: pointer;" onclick="showPlayerStats(${p.id})">
                    <span class="player-rank">#${i + 1}</span>
                    <span class="player-name">${p.name}</span>
                    <span class="player-elo">${p.elo_standard}</span>
                </div>
            `).join('');

            scoreBoard.innerHTML = sortedScore.map((p, i) => `
                <div class="player-bar" style="cursor: pointer;" onclick="showPlayerStats(${p.id})">
                    <span class="player-rank">#${i + 1}</span>
                    <span class="player-name">${p.name}</span>
                    <span class="player-elo">${p.elo_with_score}</span>
                </div>
            `).join('');
        }
        function updatePlayerSelects() {
            const selects = [
                document.getElementById('player1-select'),
                document.getElementById('player2-select'),
                document.getElementById('player-delete-select')
            ];
            selects.forEach(select => {
                const currentValue = select.value;
                select.innerHTML = '<option value="">Sélectionner un joueur</option>' +
                    players.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
                select.value = currentValue;
            });
        }
        function updateMatchList() {
            const matchList = document.getElementById('match-list');
            matchList.innerHTML = matches.map(m => {
                const p1Changes = m.player1_changes || { standard: 0, with_score: 0 };
                const p2Changes = m.player2_changes || { standard: 0, with_score: 0 };
                const winner = m.score1 > m.score2 ? 1 : 2;
                
                return `
                    <div class="match-item">
                        <div class="match-players">
                            <div class="player-info ${winner === 1 ? 'winner' : ''}">
                                <div class="player-header">
                                    <span class="player-name-match">
                                        ${winner === 1 ? '🏆 ' : ''}${m.player1}
                                    </span>
                                    <span class="player-score">${m.score1}</span>
                                </div>
                                <div class="elo-changes">
                                    <span class="elo-badge ${p1Changes.standard >= 0 ? 'elo-positive' : 'elo-negative'}">
                                        Std: ${p1Changes.standard >= 0 ? '+' : ''}${p1Changes.standard.toFixed(1)}
                                    </span>
                                    <span class="elo-badge ${p1Changes.with_score >= 0 ? 'elo-positive' : 'elo-negative'}">
                                        Score: ${p1Changes.with_score >= 0 ? '+' : ''}${p1Changes.with_score.toFixed(1)}
                                    </span>
                                </div>
                            </div>
                            <div class="player-info ${winner === 2 ? 'winner' : ''}">
                                <div class="player-header">
                                    <span class="player-name-match">
                                        ${winner === 2 ? '🏆 ' : ''}${m.player2}
                                    </span>
                                    <span class="player-score">${m.score2}</span>
                                </div>
                                <div class="elo-changes">
                                    <span class="elo-badge ${p2Changes.standard >= 0 ? 'elo-positive' : 'elo-negative'}">
                                        Std: ${p2Changes.standard >= 0 ? '+' : ''}${p2Changes.standard.toFixed(1)}
                                    </span>
                                    <span class="elo-badge ${p2Changes.with_score >= 0 ? 'elo-positive' : 'elo-negative'}">
                                        Score: ${p2Changes.with_score >= 0 ? '+' : ''}${p2Changes.with_score.toFixed(1)}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="match-footer">
                            <span class="match-date">
                                ${new Date(m.played_at).toLocaleDateString('fr-FR', {
                                    day: 'numeric',
                                    month: 'long',
                                    year: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </span>
                            <button class="danger" onclick="showDeleteMatchModal(${m.id})">
                                Supprimer
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }
        document.getElementById('player-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('player-name').value;
            const response = await fetch('/api/players', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            if (response.ok) {
                document.getElementById('player-name').value = '';
                await loadData();
            } else {
                alert('Erreur: Ce joueur existe déjà');
            }
        });
        document.getElementById('match-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const player1_id = document.getElementById('player1-select').value;
            const player2_id = document.getElementById('player2-select').value;
            const score1 = parseInt(document.getElementById('score1').value);
            const score2 = parseInt(document.getElementById('score2').value);
            if (player1_id === player2_id) {
                alert('Les deux joueurs doivent être différents');
                return;
            }
            const response = await fetch('/api/matches', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player1_id, player2_id, score1, score2 })
            });
            if (response.ok) {
                document.getElementById('score1').value = '';
                document.getElementById('score2').value = '';
                await loadData();
            }
        });
        function showDeleteMatchModal(matchId) {
            pendingAction = { type: 'match', id: matchId };
            document.getElementById('modal-message').textContent = 
                'Êtes-vous sûr de vouloir supprimer ce match ? Les classements seront recalculés.';
            document.getElementById('confirm-modal').style.display = 'block';
        }
        async function deletePlayer() {
            const playerId = document.getElementById('player-delete-select').value;
            if (!playerId) {
                alert('Veuillez sélectionner un joueur');
                return;
            }
            pendingAction = { type: 'player', id: playerId };
            const playerName = players.find(p => p.id == playerId).name;
            document.getElementById('modal-message').textContent = 
                `Êtes-vous sûr de vouloir supprimer ${playerName} ?`;
            document.getElementById('confirm-modal').style.display = 'block';
        }
        async function confirmAction() {
            if (pendingAction.type === 'match') {
                await fetch(`/api/matches?id=${pendingAction.id}`, { method: 'DELETE' });
            } else if (pendingAction.type === 'player') {
                const response = await fetch(`/api/players?id=${pendingAction.id}`, { method: 'DELETE' });
                if (!response.ok) {
                    const error = await response.json();
                    alert(`Impossible de supprimer: ${error.error}`);
                    closeModal();
                    return;
                }
            }
            closeModal();
            await loadData();
        }
        function closeModal() {
            document.getElementById('confirm-modal').style.display = 'none';
            pendingAction = null;
        }

        async function showPlayerStats(playerId) {
            const response = await fetch(`/api/player/${playerId}`);
            const data = await response.json();
            currentPlayerStats = data;

            document.getElementById('stats-player-name').textContent = data.player.name;
            document.getElementById('stats-elo-standard').textContent = data.player.elo_standard;
            document.getElementById('stats-elo-score').textContent = data.player.elo_with_score;
            document.getElementById('stats-total-matches').textContent = data.stats.total_matches;
            document.getElementById('stats-wins').textContent = data.stats.wins;
            document.getElementById('stats-losses').textContent = data.stats.losses;
            document.getElementById('stats-win-rate').textContent = data.stats.win_rate + '%';

            document.getElementById('stats-player-name').textContent = data.player.name;
            document.getElementById('stats-elo-standard').textContent = data.player.elo_standard;
            document.getElementById('stats-elo-score').textContent = data.player.elo_with_score;
            document.getElementById('stats-total-matches').textContent = data.stats.total_matches;
            document.getElementById('stats-wins').textContent = data.stats.wins;
            document.getElementById('stats-losses').textContent = data.stats.losses;
            document.getElementById('stats-win-rate').textContent = data.stats.win_rate + '%';

            // ⭐ Peupler les cartes de prédiction
            populatePredictionCard('standard', data.confidence.standard, data.stats.total_matches);
            populatePredictionCard('score', data.confidence.with_score, data.stats.total_matches);

            // Historique des matchs
            const historyHtml = data.matches_history.map(m => {
                const eloChange = m.elo_change || { standard: 0, with_score: 0 };
                return `
                    <div class="history-item ${m.result === 'Victoire' ? 'victory' : 'defeat'}">
                        <div class="history-details">
                            <span class="history-result ${m.result === 'Victoire' ? 'victory' : 'defeat'}">
                                ${m.result === 'Victoire' ? '✓' : '✗'} ${m.result}
                            </span>
                            <span class="history-opponent">${m.opponent}</span>
                            <span class="history-score">${m.score}</span>
                            <span class="history-date">${new Date(m.played_at).toLocaleDateString('fr-FR')}</span>
                        </div>
                        <div class="history-elo-change">
                            <span class="elo-badge ${eloChange.standard >= 0 ? 'elo-positive' : 'elo-negative'}">
                                Std: ${eloChange.standard >= 0 ? '+' : ''}${eloChange.standard.toFixed(1)}
                            </span>
                            <span class="elo-badge ${eloChange.with_score >= 0 ? 'elo-positive' : 'elo-negative'}">
                                Score: ${eloChange.with_score >= 0 ? '+' : ''}${eloChange.with_score.toFixed(1)}
                            </span>
                        </div>
                    </div>
                `;
            }).join('');
            document.getElementById('stats-match-history').innerHTML = historyHtml || '<p>Aucun match joué</p>';

            // Top adversaires
            const opponentsHtml = data.top_opponents.map(opp => `
                <div class="opponent-item">
                    <span class="opponent-name">${opp.name}</span>
                    <span class="opponent-record">${opp.wins}V - ${opp.losses}D (${opp.matches} matchs)</span>
                    <button onclick="startComparison(${data.player.id}, ${opp.id})" class="btn-small">Comparer</button>
                </div>
            `).join('');
            document.getElementById('stats-top-opponents').innerHTML = opponentsHtml || '<p>Aucun adversaire</p>';

            // Bouton comparer
            document.getElementById('btn-compare-player').onclick = () => selectPlayerForComparison(data.player.id);

            // ⭐ IMPORTANT: Afficher la modal AVANT de créer le graphique
            document.getElementById('player-stats-modal').style.display = 'block';
            
            // ⭐ Attendre que le DOM soit mis à jour avec un petit délai
            setTimeout(() => {
                loadPlayerEloChart(playerId);
            }, 1000);
        }
        
        async function loadPlayerEloChart(playerId) {
            try {
                const response = await fetch(`/api/player/${playerId}/history`);
                const data = await response.json();
                
                // ⭐ Vérifier que les données sont valides
                if (!data.history || data.history.length === 0) {
                    document.querySelector('#player-elo-chart').parentElement.innerHTML = 
                        '<p style="text-align: center; color: #999; padding: 40px;">Aucun historique de match disponible</p>';
                    return;
                }
                
                // Vérifier que les dates globales existent
                if (!data.global_date_range.min || !data.global_date_range.max) {
                    document.querySelector('#player-elo-chart').parentElement.innerHTML = 
                        '<p style="text-align: center; color: #999; padding: 40px;">Données insuffisantes pour afficher le graphique</p>';
                    return;
                }
                
                const ctx = document.getElementById('player-elo-chart').getContext('2d');
                
                // Détruire le graphique précédent s'il existe
                if (playerEloChart) {
                    playerEloChart.destroy();
                }
                
                playerEloChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        datasets: [
                            {
                                label: 'Elo Standard',
                                data: data.history.map(h => ({
                                    x: new Date(h.date),
                                    y: h.elo_standard
                                })),
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.3,
                                fill: true
                            },
                            {
                                label: 'Elo avec Score',
                                data: data.history.map(h => ({
                                    x: new Date(h.date),
                                    y: h.elo_with_score
                                })),
                                borderColor: '#764ba2',
                                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                                tension: 0.3,
                                fill: true
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            tooltip: {
                                callbacks: {
                                    title: function(context) {
                                        return new Date(context[0].parsed.x).toLocaleDateString('fr-FR');
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'day',
                                    displayFormats: {
                                        day: 'dd MMM'
                                    }
                                },
                                min: new Date(data.global_date_range.min),
                                max: new Date(data.global_date_range.max),
                                title: {
                                    display: true,
                                    text: 'Date'
                                }
                            },
                            y: {
                                beginAtZero: false,
                                title: {
                                    display: true,
                                    text: 'Elo'
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Erreur lors du chargement du graphique:', error);
                document.querySelector('#player-elo-chart').parentElement.innerHTML = 
                    '<p style="text-align: center; color: #f44336; padding: 40px;">Erreur lors du chargement du graphique</p>';
            }
        }

        function closePlayerStats() {
            if (playerEloChart) {
                playerEloChart.destroy();
                playerEloChart = null;
            }
            document.getElementById('player-stats-modal').style.display = 'none';
        }

        function selectPlayerForComparison(playerId) {
            comparePlayer1Id = playerId;
            document.getElementById('compare-player1-name').textContent = currentPlayerStats.player.name;

            // Remplir le select avec les autres joueurs
            const otherPlayers = players.filter(p => p.id !== playerId);
            document.getElementById('compare-player2-select').innerHTML = 
                '<option value="">Choisir un adversaire</option>' +
                otherPlayers.map(p => `<option value="${p.id}">${p.name}</option>`).join('');

            // Fermer la modal de stats, ouvrir celle de comparaison
            closePlayerStats();
            document.getElementById('compare-modal').style.display = 'block';
        }

        function startComparison(player1Id, player2Id) {
            comparePlayer1Id = player1Id;
            comparePlayer2Id = player2Id;
            closePlayerStats();
            showComparison();
        }

        async function confirmComparison() {
            comparePlayer2Id = document.getElementById('compare-player2-select').value;
            if (!comparePlayer2Id) {
                alert('Veuillez sélectionner un adversaire');
                return;
            }
            showComparison();
        }

        async function showComparison() {
            const response = await fetch(`/api/compare?player1=${comparePlayer1Id}&player2=${comparePlayer2Id}`);
            const data = await response.json();

            // Afficher les infos des joueurs
            document.getElementById('comp-p1-name').textContent = data.player1.name;
            document.getElementById('comp-p1-elo-std').textContent = data.player1.elo_standard;
            document.getElementById('comp-p1-elo-score').textContent = data.player1.elo_with_score;
            document.getElementById('comp-p1-wins').textContent = data.player1.wins_h2h;

            document.getElementById('comp-p2-name').textContent = data.player2.name;
            document.getElementById('comp-p2-elo-std').textContent = data.player2.elo_standard;
            document.getElementById('comp-p2-elo-score').textContent = data.player2.elo_with_score;
            document.getElementById('comp-p2-wins').textContent = data.player2.wins_h2h;

            // Historique des confrontations
            const h2hHtml = data.head_to_head.map(m => `
                <div class="h2h-item">
                    <span class="h2h-date">${new Date(m.played_at).toLocaleDateString('fr-FR')}</span>
                    <span class="h2h-match">${m.player1} ${m.score1} - ${m.score2} ${m.player2}</span>
                    <span class="h2h-winner">🏆 ${m.winner}</span>
                </div>
            `).join('');
            document.getElementById('h2h-history').innerHTML = h2hHtml || '<p>Aucune confrontation directe</p>';

            // ⭐ Fermer la modal de sélection, ouvrir celle des résultats
            document.getElementById('compare-modal').style.display = 'none';
            document.getElementById('comparison-results-modal').style.display = 'block';
            
            // ⭐ Charger le graphique APRÈS l'affichage avec un délai
            setTimeout(() => {
                loadComparisonChart(comparePlayer1Id, comparePlayer2Id, data.player1.name, data.player2.name);
            }, 1000);
        }
        
        async function loadComparisonChart(player1Id, player2Id, player1Name, player2Name) {
            try {
                const [response1, response2] = await Promise.all([
                    fetch(`/api/player/${player1Id}/history`),
                    fetch(`/api/player/${player2Id}/history`)
                ]);
                
                const [data1, data2] = await Promise.all([
                    response1.json(),
                    response2.json()
                ]);
                
                // ⭐ Vérifier que les données sont valides
                if (!data1.history || data1.history.length === 0 || !data2.history || data2.history.length === 0) {
                    document.querySelector('#comparison-elo-chart').parentElement.innerHTML = 
                        '<p style="text-align: center; color: #999; padding: 40px;">Historique insuffisant pour la comparaison</p>';
                    return;
                }
                
                const ctx = document.getElementById('comparison-elo-chart').getContext('2d');
                
                // Détruire le graphique précédent s'il existe
                if (comparisonEloChart) {
                    comparisonEloChart.destroy();
                }
                
                // Utiliser le range de dates global
                const globalMin = new Date(Math.min(
                    new Date(data1.global_date_range.min),
                    new Date(data2.global_date_range.min)
                ));
                const globalMax = new Date(Math.max(
                    new Date(data1.global_date_range.max),
                    new Date(data2.global_date_range.max)
                ));
                
                comparisonEloChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        datasets: [
                            {
                                label: `${player1Name} (Standard)`,
                                data: data1.history.map(h => ({
                                    x: new Date(h.date),
                                    y: h.elo_standard
                                })),
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.3,
                                borderWidth: 3
                            },
                            {
                                label: `${player1Name} (Score)`,
                                data: data1.history.map(h => ({
                                    x: new Date(h.date),
                                    y: h.elo_with_score
                                })),
                                borderColor: '#667eea',
                                backgroundColor: 'transparent',
                                borderDash: [5, 5],
                                tension: 0.3,
                                borderWidth: 2
                            },
                            {
                                label: `${player2Name} (Standard)`,
                                data: data2.history.map(h => ({
                                    x: new Date(h.date),
                                    y: h.elo_standard
                                })),
                                borderColor: '#f5576c',
                                backgroundColor: 'rgba(245, 87, 108, 0.1)',
                                tension: 0.3,
                                borderWidth: 3
                            },
                            {
                                label: `${player2Name} (Score)`,
                                data: data2.history.map(h => ({
                                    x: new Date(h.date),
                                    y: h.elo_with_score
                                })),
                                borderColor: '#f5576c',
                                backgroundColor: 'transparent',
                                borderDash: [5, 5],
                                tension: 0.3,
                                borderWidth: 2
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            tooltip: {
                                callbacks: {
                                    title: function(context) {
                                        return new Date(context[0].parsed.x).toLocaleDateString('fr-FR');
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'day',
                                    displayFormats: {
                                        day: 'dd MMM'
                                    }
                                },
                                min: globalMin,
                                max: globalMax,
                                title: {
                                    display: true,
                                    text: 'Date'
                                }
                            },
                            y: {
                                beginAtZero: false,
                                title: {
                                    display: true,
                                    text: 'Elo'
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Erreur lors du chargement du graphique de comparaison:', error);
                document.querySelector('#comparison-elo-chart').parentElement.innerHTML = 
                    '<p style="text-align: center; color: #f44336; padding: 40px;">Erreur lors du chargement du graphique</p>';
            }
        }

        function closeCompareModal() {
            document.getElementById('compare-modal').style.display = 'none';
        }

        function closeComparisonResults() {
            if (comparisonEloChart) {
                comparisonEloChart.destroy();
                comparisonEloChart = null;
            }
            document.getElementById('comparison-results-modal').style.display = 'none';
        }
        
        function toggleFactors(type) {
            const list = document.getElementById(`factors-list-${type}`);
            const icon = document.getElementById(`toggle-icon-${type}`);
            
            list.classList.toggle('open');
            icon.classList.toggle('open');
        }

        function getConfidenceLabel(confidence) {
            if (confidence >= 80) return '🟢 Élevée';
            if (confidence >= 60) return '🟡 Moyenne';
            if (confidence >= 40) return '🟠 Faible';
            return '🔴 Très faible';
        }

        function populatePredictionCard(type, confData, matchCount) {
            // Badge de confiance
            document.getElementById(`confidence-badge-${type}`).textContent = 
                getConfidenceLabel(confData.confidence);
            
            // Rating prédit
            document.getElementById(`pred-rating-${type}`).textContent = 
                confData.predicted_rating;
            
            // Intervalle
            document.getElementById(`interval-lower-${type}`).textContent = 
                confData.lower;
            document.getElementById(`interval-upper-${type}`).textContent = 
                confData.upper;
            
            // Pourcentage de confiance
            document.getElementById(`confidence-pct-${type}`).textContent = 
                confData.confidence.toFixed(0) + '%';
            
            // Barre de confiance avec animation
            setTimeout(() => {
                document.getElementById(`confidence-bar-${type}`).style.width = 
                    confData.confidence + '%';
            }, 100);
            
            // Facteurs détaillés
            if (confData.factors) {
                const factors = confData.factors;
                
                // Pour chaque facteur
                Object.keys(factors).forEach(key => {
                    const value = factors[key];
                    const factorKey = key.replace('_', '-');
                    
                    // Barre
                    setTimeout(() => {
                        const barElement = document.getElementById(`factor-${factorKey}-${type}`);
                        if (barElement) {
                            barElement.style.width = value + '%';
                        }
                    }, 200);
                    
                    // Valeur
                    const valElement = document.getElementById(`factor-${factorKey}-val-${type}`);
                    if (valElement) {
                        valElement.textContent = value.toFixed(0) + '%';
                    }
                });
            }
            
            // Info RD et matchs
            document.getElementById(`rd-value-${type}`).textContent = 
                confData.rd.toFixed(0);
            document.getElementById(`matches-count-${type}`).textContent = 
                matchCount;
        }

        loadData();
    </script>
</body>
</html>
"""