"""Flask API: upload a transcript, get course recommendations and charts back.

Uploaded transcripts are processed in memory and never written to disk.
"""

import base64
import io
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # render charts without a display
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from matplotlib import patheffects

from recommender import CourseRecommender
from transcript_parser import extract_text, parse_courses

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
CATALOGUE = Path(__file__).parent / "catalogue.csv"
PALETTE = ['#00FF88', '#00CC66', '#009944', '#33FFAA', '#66FFCC']

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # reject uploads over 5 MB
CORS(app, origins=["http://localhost:3000"])          # only the local React app may call the API

recommender = CourseRecommender(CATALOGUE)


def error(message, status):
    return jsonify({"success": False, "error": message, "recommendations": []}), status


def create_pie_chart(recommendations):
    """Create cyberpunk-style pie chart with improved visibility"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='black')
    
    # Color scheme with better contrast
    colors = PALETTE[:len(recommendations)]
    explode = [0.05] * len(recommendations)
    
    wedges, texts, autotexts = ax.pie(
        recommendations['match'],
        labels=recommendations['title'],
        colors=colors,
        explode=explode,
        shadow=True,
        startangle=90,
        wedgeprops={'linewidth': 1, 'edgecolor': '#00FF41'},
        textprops={'color': '#00FFCC', 'fontsize': 10},
        autopct='%1.1f%%',
        pctdistance=0.85
    )
    
    # Improve visibility of text
    for text in texts:
        text.set_color('#00FFCC')
        text.set_fontweight('bold')
    
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    # Add glow effect with proper color format
    for wedge in wedges:
        wedge.set_path_effects([
            patheffects.withStroke(linewidth=3, foreground=wedge.get_facecolor())
        ])
    
    ax.set_title("COURSE MATCH DISTRIBUTION", color='#00FF41', pad=20, fontweight='bold')
    
    # Add legend with better visibility
    ax.legend(wedges, recommendations['title'],
              title="COURSES",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1),
              labelcolor='#00FFCC',
              edgecolor='#00FF41',
              facecolor='black')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='black')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def create_bar_chart(recommendations):
    """Create cyberpunk-style bar chart with improved visibility"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='black')
    
    # Color scheme with better contrast
    colors = ['#00FF88' if x > 80 else '#00CC66' for x in recommendations['match']]
    edge_colors = ['#00FF41'] * len(recommendations)
    
    bars = ax.bar(
        recommendations['title'],
        recommendations['match'],
        color=colors,
        edgecolor=edge_colors,
        linewidth=2,
        alpha=0.9
    )
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}%',
                ha='center', va='bottom',
                color='#00FFCC',
                fontweight='bold')
    
    # Customize axes for better visibility
    ax.set_ylabel('MATCH %', color='#00FFCC', fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 110, 10))
    ax.tick_params(axis='x', colors='#00FFCC', rotation=45)
    ax.tick_params(axis='y', colors='#00FFCC')
    
    # Grid and frame styling
    ax.grid(color='#008844', linestyle='--', linewidth=0.5, alpha=0.5)
    for spine in ax.spines.values():
        spine.set_edgecolor('#00FF41')
        spine.set_linewidth(2)
    
    ax.set_title("COURSE MATCH ANALYSIS", color='#00FF41', pad=20, fontweight='bold')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='black')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def create_radar_chart(recommendations):
    """Create cyberpunk-style radar chart with improved visibility"""
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(8, 8), facecolor='black')
    ax = fig.add_subplot(111, polar=True, facecolor='black')
    
    # Prepare data
    categories = ['Match', 'Difficulty', 'Workload']
    N = len(categories)
    
    # Convert qualitative data to numerical
    difficulty_map = {'Beginner': 30, 'Intermediate': 60, 'Advanced': 90}
    workload_map = {'Low': 30, 'Moderate': 60, 'High': 90}
        
    values = []
    for _, row in recommendations.iterrows():
        values.append([
            row['match'],
            difficulty_map.get(row['difficulty'], 60),
            workload_map.get(row['workload'], 60)
        ])
    
    # Calculate angles and complete the loop
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    # Plot each course with distinct colors
    colors = PALETTE[:len(recommendations)]
    for i, (label, color) in enumerate(zip(recommendations['title'], colors)):
        val = values[i] + values[i][:1]
        ax.plot(angles, val, linewidth=2, linestyle='solid', 
                label=label, color=color)
        ax.fill(angles, val, color=color, alpha=0.25)
        ax.scatter(angles[:-1], val[:-1], color=color, s=100, zorder=3)
    
    # Customize axes for better visibility
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color='#00FFCC', fontweight='bold')
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], color='#00FFCC')
    ax.set_ylim(0, 100)
    
    # Grid and frame styling
    ax.grid(color='#008844', linestyle='--', linewidth=0.5, alpha=0.5)
    
    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1),
             labelcolor='#00FFCC', edgecolor='#00FF41', facecolor='black')
    
    ax.set_title("COURSE ATTRIBUTES RADAR", color='#00FF41', pad=20, fontweight='bold')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='black')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    file = request.files.get('file')
    if file is None or file.filename == '':
        return error("No file uploaded", 400)
    if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        return error("Only .pdf and .txt transcripts are accepted", 400)

    try:
        text = extract_text(file.read(), file.filename)
    except Exception:
        return error("Could not read the file. Is it a valid PDF?", 400)

    taken = parse_courses(text)
    if not taken:
        return error("No courses found. Course lines should start with a code like CS101.", 422)

    recommendations = recommender.recommend(taken, top_n=5)
    return jsonify({
        "success": True,
        "error": None,
        "courses_found": taken,
        "recommendations": recommendations.to_dict('records'),
        "visualizations": {
            "pie": create_pie_chart(recommendations),
            "bar": create_bar_chart(recommendations),
            "radar": create_radar_chart(recommendations),
        },
    })


@app.errorhandler(413)
def too_large(_):
    return error("File too large (5 MB limit)", 413)


if __name__ == '__main__':
    # Debug mode exposes an interactive console, so it is opt-in only.
    app.run(port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
