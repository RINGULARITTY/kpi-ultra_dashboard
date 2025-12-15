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
        
        .prediction-section { margin: 25px 0; }
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

        .prediction-card {
        background: #fff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.10);
        position: relative;
        overflow: hidden;
        }

        .prediction-card:before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }

        .prediction-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
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
        color: #fff;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9em;
        }

        .predicted-rating-display { text-align: center; margin: 10px 0 14px; }
        .predicted-rating-value {
        font-size: 3.2em;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.0;
        }

        /* =========================================================
        Intervalles: règle (valeurs uniquement, pas de 50/75/95 affichés)
        ========================================================= */
        .ci-block {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 14px 14px 12px;
        margin: 10px 0 16px;
        }

        .interval-label {
        color: #666;
        font-size: 0.90em;
        margin-bottom: 10px;
        text-align: center;
        font-weight: 650;
        }

        .ci-axis {
        position: relative;
        height: 58px;
        border-radius: 12px;
        }

        .ci-line{
        position: absolute;
        left: 6%;
        right: 6%;
        top: 40px;               /* ligne de référence */
        height: 2px;
        background: rgba(102,126,234,0.45);
        border-radius: 999px;
        z-index: 2;
        }
        
        .ci-band{
        position: absolute;
        top: 37px;               /* centrées autour de la ligne */
        height: 8px;
        border-radius: 999px;
        z-index: 1;
        transition: left .35s ease, width .35s ease;
        }
        .ci-band-95{ background: rgba(102,126,234,0.18); }
        .ci-band-75{ background: rgba(118,75,162,0.22); }
        .ci-band-50{ background: rgba(102,126,234,0.55); }

        .ci-tick{
        position: absolute;
        top: 40px;               /* ancre sur la ligne */
        transform: translateX(-50%);
        width: 72px;
        text-align: center;
        z-index: 3;
        pointer-events: none;
        }

        /* Valeur au-dessus du point */
        .ci-value{
        position: absolute;
        left: 50%;
        top: -28px;
        transform: translateX(-50%);
        font-size: 0.90em;
        font-weight: 800;
        color: #333;
        margin: 0;
        }

        .ci-tick::after{
        content: "";
        position: absolute;
        left: 50%;
        top: 0;
        transform: translate(-50%, -50%);
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #667eea;
        border: 2px solid #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }

        .ci-tick-95::after{ background: rgba(102,126,234,0.55); }
        .ci-tick-75::after{ background: rgba(118,75,162,0.55); }
        .ci-tick-50::after{ background: rgba(102,126,234,0.95); }

        .ci-tick-cur::after{
        width: 12px;
        height: 12px;
        background: #764ba2;
        box-shadow: 0 3px 10px rgba(0,0,0,0.16);
        }

        .ci-value {
        font-size: 0.90em;
        font-weight: 800;
        color: #333;
        margin-top: 6px;
        }


        /* =========================================================
        Confiance: suppression de l'ancien "confidence-meter" + jauge
        ========================================================= */
        /* Désactive la grosse barre gradient existante (si encore dans le DOM) */
        .confidence-meter,
        .confidence-bar-track,
        .confidence-bar-fill {
        display: none !important;
        }

        /* Nouveau panel (jauge + 3 KPIs) */
        .confidence-panel {
        display: grid;
        grid-template-columns: 92px 1fr;
        gap: 14px;
        align-items: center;
        margin: 6px 0 10px;
        padding: 12px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid rgba(102,126,234,0.12);
        }

        .confidence-gauge {
        --p: 0; /* 0..100, set par JS */
        width: 92px;
        height: 92px;
        border-radius: 50%;
        background:
            conic-gradient(
            #4caf50 calc(var(--p) * 1%),
            rgba(224,224,224,0.92) 0
            );
        display: grid;
        place-items: center;
        position: relative;
        }

        .confidence-gauge::before {
        content: "";
        position: absolute;
        inset: 8px;
        background: #fff;
        border-radius: 50%;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.03);
        }

        .confidence-gauge-inner {
        position: relative;
        text-align: center;
        padding-top: 2px;
        }

        .confidence-gauge-pct {
        font-size: 1.25em;
        font-weight: 900;
        color: #667eea;
        line-height: 1.0;
        }

        .confidence-gauge-label {
        font-size: 0.78em;
        color: #888;
        font-weight: 700;
        margin-top: 4px;
        }

        .confidence-kpis {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        }

        .confidence-kpi {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        }

        .confidence-kpi-label {
        font-size: 0.78em;
        color: #777;
        font-weight: 700;
        }

        .confidence-kpi-value {
        font-size: 1.05em;
        color: #333;
        font-weight: 900;
        margin-top: 3px;
        }


        /* =========================================================
        Facteurs: toujours visibles (sans bouton)
        ========================================================= */
        /* Cache le bouton si présent */
        .factors-toggle { display: none !important; }

        /* Force l'affichage de la liste */
        .factors-list { display: block !important; }
        .factors-list.open { display: block !important; }

        .confidence-factors { margin-top: 10px; }

        /* Reprise/raffinage des items */
        .factor-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        }

        .factor-item:last-child { border-bottom: none; }

        .factor-label {
        display: flex;
        align-items: center;
        gap: 25px;
        color: #666;
        font-size: 0.92em;
        }

        .factor-icon { font-size: 1.1em; }

        .factor-value-container {
        display: flex;
        align-items: center;
        gap: 10px;
        }

        .factor-bar {
        width: 72px;
        height: 7px;
        background: #e0e0e0;
        border-radius: 999px;
        overflow: hidden;
        }

        .factor-bar-fill {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.45s ease;
        }

        .factor-value {
        font-weight: 800;
        color: #667eea;
        min-width: 46px;
        text-align: right;
        font-size: 0.92em;
        }

        /* =========================================================
        Tooltips (tu les as déjà, mais je garde une version compacte)
        ========================================================= */
        .factor-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        }

        .factor-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 120%;
        left: 50%;
        transform: translateX(-50%);
        background: #333;
        color: #fff;
        padding: 8px 12px;
        border-radius: 6px;
        white-space: nowrap;
        font-size: 0.80em;
        z-index: 1000;
        box-shadow: 0 8px 20px rgba(0,0,0,0.20);
        }

        .factor-tooltip:hover::before {
        content: "";
        position: absolute;
        bottom: 110%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: #333;
        z-index: 1001;
        }


        /* =========================================================
        Responsive
        ========================================================= */
        @media (max-width: 900px) {
        .prediction-cards { grid-template-columns: 1fr; }
        .predicted-rating-value { font-size: 2.6em; }

        .confidence-panel { grid-template-columns: 86px 1fr; }
        .confidence-gauge { width: 86px; height: 86px; }

        .ci-tick { width: 64px; }
        .ci-value { font-size: 0.85em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏓 Legends Tournament</h1>
        <div class="leaderboard-section">
            <h2 class="leaderboard-title">Ranking</h2>
            <div class="leaderboards">
                <div class="leaderboard">
                    <h3>📊 Standard ELO</h3>
                    <div id="leaderboard-standard"></div>
                </div>
                <div class="leaderboard">
                    <h3>📈 Score ELO</h3>
                    <div id="leaderboard-score"></div>
                </div>
            </div>
        </div>
        <div class="bottom-section">
            <div class="card">
                <h2>⚔️ Matchs</h2>
                <form id="match-form">
                    <div class="form-group">
                        <label>Player 1</label>
                        <select id="player1-select" required>
                            <option value="">Select player</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Player 2</label>
                        <select id="player2-select" required>
                            <option value="">Select player</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Scores</label>
                        <div class="score-inputs">
                            <input type="number" id="score1" placeholder="Score J1" min="0" required>
                            <input type="number" id="score2" placeholder="Score J2" min="0" required>
                        </div>
                    </div>
                    <button type="submit">Add</button>
                </form>
                <div class="match-list" id="match-list"></div>
            </div>
            <div class="card">
                <h2>👥 Players</h2>
                <form id="player-form">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="player-name" required>
                    </div>
                    <button type="submit">Add</button>
                </form>
                <div class="form-group" style="margin-top: 20px;">
                    <label>Delete player</label>
                    <select id="player-delete-select">
                        <option value="">Select player</option>
                    </select>
                    <button class="danger" onclick="deletePlayer()">Delete</button>
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
                <h2>📊 <span id="stats-player-name"></span></h2>
                <button class="btn-close" onclick="closePlayerStats()">×</button>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">ELO</div>
                    <div class="stat-value" id="stats-elo-standard">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Score</div>
                    <div class="stat-value" id="stats-elo-score">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Played matchs</div>
                    <div class="stat-value" id="stats-total-matches">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Wins</div>
                    <div class="stat-value stat-green" id="stats-wins">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Looses</div>
                    <div class="stat-value stat-red" id="stats-losses">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Win rate</div>
                    <div class="stat-value" id="stats-win-rate">-</div>
                </div>
            </div>
            
            <div class="prediction-section">
                <h3>Ranking Prediction</h3>

                <div class="prediction-cards">

                    <!-- ===================== -->
                    <!-- Carte Elo Standard     -->
                    <!-- ===================== -->
                    <div class="prediction-card">
                    <div class="prediction-header">
                        <h4><span>📊</span> ELO</h4>
                        <div class="confidence-badge" id="confidence-badge-standard">-</div>
                    </div>

                    <div class="predicted-rating-display">
                        <div class="predicted-rating-value" id="pred-rating-standard">-</div>
                    </div>

                    <!-- Intervalles : règle (valeurs uniquement) -->
                    <div class="confidence-interval ci-block">
                        <div class="interval-label">50% / 75% / 95% confidence intervals</div>

                        <div class="ci-axis">
                        <div class="ci-line"></div>

                        <div class="ci-tick ci-tick-95" id="ci-tick-l95-standard"><div class="ci-value" id="ci-v-l95-standard">-</div></div>
                        <div class="ci-tick ci-tick-75" id="ci-tick-l75-standard"><div class="ci-value" id="ci-v-l75-standard">-</div></div>
                        <div class="ci-tick ci-tick-50" id="ci-tick-l50-standard"><div class="ci-value" id="ci-v-l50-standard">-</div></div>

                        <div class="ci-tick ci-tick-cur" id="ci-tick-cur-standard"><div class="ci-value" id="ci-v-cur-standard">-</div></div>

                        <div class="ci-tick ci-tick-50" id="ci-tick-r50-standard"><div class="ci-value" id="ci-v-r50-standard">-</div></div>
                        <div class="ci-tick ci-tick-75" id="ci-tick-r75-standard"><div class="ci-value" id="ci-v-r75-standard">-</div></div>
                        <div class="ci-tick ci-tick-95" id="ci-tick-r95-standard"><div class="ci-value" id="ci-v-r95-standard">-</div></div>
                        </div>
                    </div>

                    <!-- Confiance : jauge + stats utiles -->
                    <div class="confidence-panel">
                        <div class="confidence-gauge" id="confidence-gauge-standard">
                        <div class="confidence-gauge-inner">
                            <div class="confidence-gauge-pct" id="confidence-pct-standard">-</div>
                            <div class="confidence-gauge-label">Confidence</div>
                        </div>
                        </div>

                        <div class="confidence-kpis">
                        <div class="confidence-kpi">
                            <div class="confidence-kpi-label">Rating Deviation</div>
                            <div class="confidence-kpi-value"><span id="rd-value-standard">-</span></div>
                        </div>
                        <div class="confidence-kpi">
                            <div class="confidence-kpi-label">Effective matches</div>
                            <div class="confidence-kpi-value"><span id="effective-matches-standard">-</span></div>
                        </div>
                        <div class="confidence-kpi">
                            <div class="confidence-kpi-label">Matchs</div>
                            <div class="confidence-kpi-value"><span id="matches-count-standard">-</span></div>
                        </div>
                        </div>
                    </div>

                    <!-- Facteurs (toujours visibles) -->
                    <div class="confidence-factors">
                        <div class="factors-list open" id="factors-list-standard">
                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">📊</span><span class="factor-tooltip" data-tooltip="The more you play, the more your rating is correct">Matchs amount</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-matches-standard" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-matches-val-standard">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">👥</span><span class="factor-tooltip" data-tooltip="Diversity of your opponents">Opponents diversity</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-diversity-standard" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-diversity-val-standard">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">📈</span><span class="factor-tooltip" data-tooltip="The more you're playing vs same opponent over days, the lower confidence is">Same opponent nerf</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-repeat-standard" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-repeat-val-standard">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">✓</span><span class="factor-tooltip" data-tooltip="50/50 matches are more informative">50/50 matches</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-info-standard" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-info-val-standard">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">🎯</span><span class="factor-tooltip" data-tooltip="Confidence of opponents">Opponenents confidence</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-opponents-standard" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-opponents-val-standard">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">📉</span><span class="factor-tooltip" data-tooltip="The more rank is diffrerent, the less it's confident">Rank gap nerf</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-gap-standard" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-gap-val-standard">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">↔</span><span class="factor-tooltip" data-tooltip="ABS Average with opponents">Opponent average gap</span></div>
                            <div class="factor-value-container">
                            <span class="factor-value" id="mean-gap-standard">-</span>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>

                    <!-- ===================== -->
                    <!-- Carte Elo avec Score   -->
                    <!-- ===================== -->
                    <div class="prediction-card">
                    <div class="prediction-header">
                        <h4><span>📈</span> Score</h4>
                        <div class="confidence-badge" id="confidence-badge-score">-</div>
                    </div>

                    <div class="predicted-rating-display">
                        <div class="predicted-rating-value" id="pred-rating-score">-</div>
                    </div>

                    <div class="confidence-interval ci-block">
                        <div class="interval-label">50% / 75% / 95% confidence intervals</div>

                        <div class="ci-axis">
                        <div class="ci-line"></div>

                        <div class="ci-tick ci-tick-95" id="ci-tick-l95-score"><div class="ci-value" id="ci-v-l95-score">-</div></div>
                        <div class="ci-tick ci-tick-75" id="ci-tick-l75-score"><div class="ci-value" id="ci-v-l75-score">-</div></div>
                        <div class="ci-tick ci-tick-50" id="ci-tick-l50-score"><div class="ci-value" id="ci-v-l50-score">-</div></div>

                        <div class="ci-tick ci-tick-cur" id="ci-tick-cur-score"><div class="ci-value" id="ci-v-cur-score">-</div></div>

                        <div class="ci-tick ci-tick-50" id="ci-tick-r50-score"><div class="ci-value" id="ci-v-r50-score">-</div></div>
                        <div class="ci-tick ci-tick-75" id="ci-tick-r75-score"><div class="ci-value" id="ci-v-r75-score">-</div></div>
                        <div class="ci-tick ci-tick-95" id="ci-tick-r95-score"><div class="ci-value" id="ci-v-r95-score">-</div></div>
                        </div>
                    </div>

                    <div class="confidence-panel">
                        <div class="confidence-gauge" id="confidence-gauge-score">
                        <div class="confidence-gauge-inner">
                            <div class="confidence-gauge-pct" id="confidence-pct-score">-</div>
                            <div class="confidence-gauge-label">Confidence</div>
                        </div>
                        </div>

                        <div class="confidence-kpis">
                        <div class="confidence-kpi">
                            <div class="confidence-kpi-label">Rating Deviation</div>
                            <div class="confidence-kpi-value"><span id="rd-value-score">-</span></div>
                        </div>
                        <div class="confidence-kpi">
                            <div class="confidence-kpi-label">Effective matches</div>
                            <div class="confidence-kpi-value"><span id="effective-matches-score">-</span></div>
                        </div>
                        <div class="confidence-kpi">
                            <div class="confidence-kpi-label">Matchs</div>
                            <div class="confidence-kpi-value"><span id="matches-count-score">-</span></div>
                        </div>
                        </div>
                    </div>

                    <div class="confidence-factors">
                        <div class="factors-list open" id="factors-list-score">
                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">📊</span><span class="factor-tooltip" data-tooltip="The more you play, the more your rating is correct">Matchs amount</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-matches-score" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-matches-val-score">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">👥</span><span class="factor-tooltip" data-tooltip="Diversity of your opponents">Opponents diversity</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-diversity-score" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-diversity-val-score">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">📈</span><span class="factor-tooltip" data-tooltip="The more you're playing vs same opponent over days, the lower confidence is">Same opponent nerf</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-repeat-score" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-repeat-val-score">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">✓</span><span class="factor-tooltip" data-tooltip="50/50 matches are more informative">50/50 matches</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-info-score" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-info-val-score">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">🎯</span><span class="factor-tooltip" data-tooltip="Confidence of opponents">Opponenents confidence</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-opponents-score" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-opponents-val-score">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">📉</span><span class="factor-tooltip" data-tooltip="The more rank is diffrerent, the less it's confident">Rank gap nerf</span></div>
                            <div class="factor-value-container">
                            <div class="factor-bar"><div class="factor-bar-fill" id="factor-gap-score" style="width:0%"></div></div>
                            <span class="factor-value" id="factor-gap-val-score">-</span>
                            </div>
                        </div>

                        <div class="factor-item">
                            <div class="factor-label"><span class="factor-icon">↔</span><span class="factor-tooltip" data-tooltip="ABS Average with opponents">Opponent average gap</span></div>
                            <div class="factor-value-container">
                            <span class="factor-value" id="mean-gap-score">-</span>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>

                </div>
            </div>
            
            <div class="chart-section">
                <h3>📈 Rank Evolution</h3>
                <div class="chart-container">
                    <canvas id="player-elo-chart"></canvas>
                </div>
            </div>

            <div class="stats-sections">
                <div class="stats-section">
                    <h3>🏆 Best opponents</h3>
                    <div id="stats-top-opponents" class="opponents-list"></div>
                </div>

                <div class="stats-section">
                    <h3>📜 Matchs history</h3>
                    <div id="stats-match-history" class="match-history-list"></div>
                </div>
            </div>

            <div class="modal-footer">
                <button id="btn-compare-player" class="btn-primary">Compare</button>
            </div>
        </div>
    </div>
    <div id="compare-modal" class="modal">
        <div class="modal-content">
            <h3>Compare with opponent</h3>
            <p>Player 1 : <strong id="compare-player1-name"></strong></p>

            <div class="form-group">
                <label>Player 2</label>
                <select id="compare-player2-select"></select>
            </div>

            <div class="modal-buttons">
                <button onclick="closeCompareModal()">Cancel</button>
                <button class="btn-primary" onclick="confirmComparison()">Compare</button>
            </div>
        </div>
    </div>
    <div id="comparison-results-modal" class="modal">
        <div class="modal-content-large">
            <div class="modal-header">
                <h2>⚔️ Compare</h2>
                <button class="btn-close" onclick="closeComparisonResults()">×</button>
            </div>

            <div class="comparison-grid">
                <div class="comparison-player">
                    <h3 id="comp-p1-name">-</h3>
                    <div class="comp-stats">
                        <div class="comp-stat">
                            <span class="comp-label">ELO</span>
                            <span class="comp-value" id="comp-p1-elo-std">-</span>
                        </div>
                        <div class="comp-stat">
                            <span class="comp-label">Score</span>
                            <span class="comp-value" id="comp-p1-elo-score">-</span>
                        </div>
                        <div class="comp-stat highlight">
                            <span class="comp-label">Wins</span>
                            <span class="comp-value" id="comp-p1-wins">-</span>
                        </div>
                    </div>
                </div>

                <div class="comparison-vs">VS</div>

                <div class="comparison-player">
                    <h3 id="comp-p2-name">-</h3>
                    <div class="comp-stats">
                        <div class="comp-stat">
                            <span class="comp-label">ELO</span>
                            <span class="comp-value" id="comp-p2-elo-std">-</span>
                        </div>
                        <div class="comp-stat">
                            <span class="comp-label">Score</span>
                            <span class="comp-value" id="comp-p2-elo-score">-</span>
                        </div>
                        <div class="comp-stat highlight">
                            <span class="comp-label">Wins</span>
                            <span class="comp-value" id="comp-p2-wins">-</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="chart-section">
                <h3>📊 Ranking evolution</h3>
                <div class="chart-container">
                    <canvas id="comparison-elo-chart"></canvas>
                </div>
            </div>

            <div class="h2h-section">
                <h3>📋 Direct matchs</h3>
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
                select.innerHTML = '<option value="">Select player</option>' +
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
                                        ELO: ${p1Changes.standard >= 0 ? '+' : ''}${p1Changes.standard.toFixed(1)}
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
                                        ELO: ${p2Changes.standard >= 0 ? '+' : ''}${p2Changes.standard.toFixed(1)}
                                    </span>
                                    <span class="elo-badge ${p2Changes.with_score >= 0 ? 'elo-positive' : 'elo-negative'}">
                                        Score: ${p2Changes.with_score >= 0 ? '+' : ''}${p2Changes.with_score.toFixed(1)}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="match-footer">
                            <span class="match-date">
                                ${new Date(m.played_at).toLocaleDateString('en-US', {
                                    day: 'numeric',
                                    month: 'long',
                                    year: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </span>
                            <button class="danger" onclick="showDeleteMatchModal(${m.id})">
                                Delete
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
                'Are you sure to delete this match ?';
            document.getElementById('confirm-modal').style.display = 'block';
        }
        async function deletePlayer() {
            const playerId = document.getElementById('player-delete-select').value;
            if (!playerId) {
                alert('Plz, select a player');
                return;
            }
            pendingAction = { type: 'player', id: playerId };
            const playerName = players.find(p => p.id == playerId).name;
            document.getElementById('modal-message').textContent = 
                `Are you sure to delete ${playerName} ?`;
            document.getElementById('confirm-modal').style.display = 'block';
        }
        async function confirmAction() {
            if (pendingAction.type === 'match') {
                await fetch(`/api/matches?id=${pendingAction.id}`, { method: 'DELETE' });
            } else if (pendingAction.type === 'player') {
                const response = await fetch(`/api/players?id=${pendingAction.id}`, { method: 'DELETE' });
                if (!response.ok) {
                    const error = await response.json();
                    alert(`Cannot delete: ${error.error}`);
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
                    <div class="history-item ${m.result === 'Win' ? 'victory' : 'defeat'}">
                        <div class="history-details">
                            <span class="history-result ${m.result === 'Win' ? 'victory' : 'defeat'}">
                                ${m.result === 'Win' ? '✓' : '✗'} ${m.result}
                            </span>
                            <span class="history-opponent">${m.opponent}</span>
                            <span class="history-score">${m.score}</span>
                            <span class="history-date">${new Date(m.played_at).toLocaleDateString('fr-FR')}</span>
                        </div>
                        <div class="history-elo-change">
                            <span class="elo-badge ${eloChange.standard >= 0 ? 'elo-positive' : 'elo-negative'}">
                                ELO: ${eloChange.standard >= 0 ? '+' : ''}${eloChange.standard.toFixed(1)}
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
                    <button onclick="startComparison(${data.player.id}, ${opp.id})" class="btn-small">Compare</button>
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
                alert('Plz, select an opponent');
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
            document.getElementById('h2h-history').innerHTML = h2hHtml || '<p>No match found</p>';

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
                                label: `${player1Name} (ELO)`,
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
                                label: `${player2Name} (ELO)`,
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
                                        return new Date(context[0].parsed.x);
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
                                        day: 'dd/MM'
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
                console.error('Error while loading graph', error);
                document.querySelector('#comparison-elo-chart').parentElement.innerHTML = 
                    '<p style="text-align: center; color: #f44336; padding: 40px;">Error while loading graph</p>';
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

        function clamp(x, lo, hi) {
            return Math.max(lo, Math.min(hi, x));
        }

        function getConfidenceLabel(confidencePct) {
            const c = Number(confidencePct);
            if (c >= 80) return '🟢 High Confidence';
            if (c >= 60) return '🟡 Medium Confidence';
            if (c >= 40) return '🟠 Low Confidence';
            return '🔴 Really Low Confidence';
        }

        function populatePredictionCard(type, confData, matchCount) {
            if (!confData) return;

            const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

            // ---- Badge + rating ----
            const badge = document.getElementById(`confidence-badge-${type}`);
            if (badge) badge.textContent = getConfidenceLabel(confData.confidence);

            const pred = document.getElementById(`pred-rating-${type}`);
            if (pred) pred.textContent = confData.predicted_rating ?? "-";

            // ---- Intervals data (50/75/95) ----
            const i50 = confData.intervals?.["50"];
            const i75 = confData.intervals?.["75"];
            const i95 = confData.intervals?.["95"];

            // Fallback 95 si le backend n'envoie pas "intervals" (ancien format)
            const fallback95 =
                (!i95 && confData.lower != null && confData.upper != null)
                ? { lower: confData.lower, upper: confData.upper }
                : null;

            const i95ok = i95 ?? fallback95;
            if (!i95ok || i95ok.lower == null || i95ok.upper == null) return;

            const fmt = (x) => {
                const n = Number(x);
                return (x === undefined || x === null || Number.isNaN(n)) ? "-" : n.toFixed(1);
            };

            // ---- Valeurs (texte) sous les ticks ----
            const setText = (id, txt) => {
                const el = document.getElementById(id);
                if (el) el.textContent = txt;
            };

            setText(`ci-v-l95-${type}`, fmt(i95ok.lower));
            setText(`ci-v-l75-${type}`, fmt(i75?.lower));
            setText(`ci-v-l50-${type}`, fmt(i50?.lower));
            setText(`ci-v-cur-${type}`, fmt(confData.predicted_rating));
            setText(`ci-v-r50-${type}`, fmt(i50?.upper));
            setText(`ci-v-r75-${type}`, fmt(i75?.upper));
            setText(`ci-v-r95-${type}`, fmt(i95ok.upper));

            // ---- Positionnement (EN ELO) ----
            // On place tout sur une échelle [lower95, upper95] => [0..1]
            const minX = Number(i95ok.lower);
            const maxX = Number(i95ok.upper);
            const range = Math.max(1e-9, maxX - minX);

            const pos01 = (val) => (Number(val) - minX) / range;

            // Padding visuel (doit matcher ton CSS .ci-line left/right)
            const pad = 6;         // %
            const span = 100 - 2 * pad;
            const toPct = (x01) => `${pad + clamp(x01, 0, 1) * span}%`;

            const setLeft = (id, x01) => {
                const el = document.getElementById(id);
                if (el) el.style.left = toPct(x01);
            };

            // Ticks (si valeur absente, on ne bouge pas)
            setLeft(`ci-tick-l95-${type}`, pos01(i95ok.lower));
            setLeft(`ci-tick-r95-${type}`, pos01(i95ok.upper));

            if (i75?.lower != null) setLeft(`ci-tick-l75-${type}`, pos01(i75.lower));
            if (i75?.upper != null) setLeft(`ci-tick-r75-${type}`, pos01(i75.upper));

            if (i50?.lower != null) setLeft(`ci-tick-l50-${type}`, pos01(i50.lower));
            if (i50?.upper != null) setLeft(`ci-tick-r50-${type}`, pos01(i50.upper));

            if (confData.predicted_rating != null) {
                setLeft(`ci-tick-cur-${type}`, pos01(confData.predicted_rating));
            }

            // ---- Bandes (optionnel si tu as ajouté ci-band-95/75/50 dans le HTML) ----
            const setBand = (id, leftVal, rightVal) => {
                const el = document.getElementById(id);
                if (!el || leftVal == null || rightVal == null) return;

                const l = pad + clamp(pos01(leftVal), 0, 1) * span;
                const r = pad + clamp(pos01(rightVal), 0, 1) * span;

                el.style.left = `${l}%`;
                el.style.width = `${Math.max(0, r - l)}%`;
            };

            setBand(`ci-band-95-${type}`, i95ok.lower, i95ok.upper);
            setBand(`ci-band-75-${type}`, i75?.lower, i75?.upper);
            setBand(`ci-band-50-${type}`, i50?.lower, i50?.upper);

            // ---- Confiance : jauge ----
            const pct = clamp(Number(confData.confidence ?? 0), 0, 100);

            const gauge = document.getElementById(`confidence-gauge-${type}`);
            if (gauge) gauge.style.setProperty('--p', pct);

            const confPct = document.getElementById(`confidence-pct-${type}`);
            if (confPct) confPct.textContent = `${pct.toFixed(0)}%`;

            // ---- KPIs ----
            const rdEl = document.getElementById(`rd-value-${type}`);
            if (rdEl) rdEl.textContent = Number(confData.rd ?? 0).toFixed(0);

            const factors = confData.factors || {};

            const effEl = document.getElementById(`effective-matches-${type}`);
            if (effEl) {
                effEl.textContent =
                (factors.effective_matches == null) ? "-" : Number(factors.effective_matches).toFixed(1);
            }

            const mcEl = document.getElementById(`matches-count-${type}`);
            if (mcEl) mcEl.textContent = matchCount ?? "-";

            // ---- Factors (toujours visibles) ----
            const factorMap = {
                matches: "matches",
                diversity: "diversity",
                repeat_penalty: "repeat",
                informativeness: "info",
                opponents_reliability: "opponents",
                gap_penalty: "gap",
            };

            Object.entries(factorMap).forEach(([backendKey, domKey]) => {
                const raw = factors[backendKey];
                if (raw === undefined || raw === null || Number.isNaN(Number(raw))) return;

                const fpct = clamp(Number(raw) * 100, 0, 100);

                const barEl = document.getElementById(`factor-${domKey}-${type}`);
                if (barEl) barEl.style.width = `${fpct}%`;

                const valEl = document.getElementById(`factor-${domKey}-val-${type}`);
                if (valEl) valEl.textContent = `${fpct.toFixed(0)}%`;
            });

            const gapEl = document.getElementById(`mean-gap-${type}`);
            if (gapEl) {
                gapEl.textContent =
                (factors.mean_gap == null) ? "-" : Number(factors.mean_gap).toFixed(0);
            }
        }

        loadData();
    </script>
</body>
</html>
"""