from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from matplotlib import patheffects

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Enhanced course database
COURSES = pd.DataFrame([
    {
        "code": "CS201", 
        "name": "Data Structures", 
        "match": 88, 
        "prereq": "CS101", 
        "category": "Core",
        "skills": ["Algorithm Design", "Memory Management", "Optimization"],
        "description": "Master low-level data organization for optimal system performance.",
        "syllabus": ["Bit Manipulation", "Quantum Arrays", "Neural Hashing"],
        "difficulty": "Intermediate",
        "workload": "Moderate",
        "popularity": "High"
    },
    {
        "code": "QC401", 
        "name": "Quantum Algorithms", 
        "match": 92, 
        "prereq": "CS201", 
        "category": "Advanced",
        "skills": ["Qubit Manipulation", "Superposition", "Entanglement"],
        "description": "Harness quantum phenomena for exponential speedups in computation.",
        "syllabus": ["Shor's Algorithm", "Grover's Search", "Quantum Fourier Transform"],
        "difficulty": "Expert",
        "workload": "High",
        "popularity": "Medium"
    },
    {
        "code": "AI301", 
        "name": "Neural Networks", 
        "match": 76, 
        "prereq": "CS201", 
        "category": "Advanced",
        "skills": ["Backpropagation", "Tensor Operations", "Model Tuning"],
        "description": "Design and train artificial neural networks for pattern recognition.",
        "syllabus": ["Perceptrons", "CNNs", "RNNs"],
        "difficulty": "Intermediate",
        "workload": "High",
        "popularity": "Very High"
    }
])

def create_pie_chart(recommendations):
    """Create cyberpunk-style pie chart with improved visibility"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='black')
    
    # Color scheme with better contrast
    colors = ['#00FF88', '#00CC66', '#009944']
    explode = [0.05] * len(recommendations)
    
    wedges, texts, autotexts = ax.pie(
        recommendations['match'],
        labels=recommendations['name'],
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
    ax.legend(wedges, recommendations['name'],
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
        recommendations['name'],
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
    categories = ['Match', 'Difficulty', 'Workload', 'Popularity']
    N = len(categories)
    
    # Convert qualitative data to numerical
    difficulty_map = {'Beginner': 30, 'Intermediate': 60, 'Expert': 90}
    workload_map = {'Low': 30, 'Moderate': 60, 'High': 90}
    popularity_map = {'Low': 30, 'Medium': 60, 'High': 80, 'Very High': 100}
    
    values = []
    for _, row in recommendations.iterrows():
        values.append([
            row['match'],
            difficulty_map.get(row['difficulty'], 60),
            workload_map.get(row['workload'], 60),
            popularity_map.get(row['popularity'], 60)
        ])
    
    # Calculate angles and complete the loop
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    # Plot each course with distinct colors
    colors = ['#00FF88', '#00CC66', '#009944']
    for i, (label, color) in enumerate(zip(recommendations['name'], colors)):
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
def handle_upload():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "NO FILE DETECTED", "recommendations": []})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "FILE CORRUPTED", "recommendations": []})

        # Process PDF
        with pdfplumber.open(file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        recommendations = COURSES.copy()
        
        # Generate all chart types
        pie_chart = create_pie_chart(recommendations)
        bar_chart = create_bar_chart(recommendations)
        radar_chart = create_radar_chart(recommendations)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations.to_dict('records'),
            "visualizations": {
                "pie": pie_chart,
                "bar": bar_chart,
                "radar": radar_chart
            },
            "error": None
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"SYSTEM ERROR: {str(e)}",
            "recommendations": [],
            "visualizations": None
        })

if __name__ == '__main__':
    app.run(port=5000, debug=True)