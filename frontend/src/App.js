import React, { useState } from 'react';
import './App.css';

function App() {
  const [state, setState] = useState({
    recommendations: [],
    visualizations: null,
    isLoading: false,
    error: null,
    selectedCourse: null,
    activeChart: 'pie'
  });

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setState(prev => ({ 
      ...prev, 
      isLoading: true, 
      error: null,
      recommendations: [],
      visualizations: null
    }));

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/api/recommend', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (!data.success) throw new Error(data.error || 'SYSTEM ANALYSIS FAILED');

      setState(prev => ({
        ...prev,
        recommendations: data.recommendations,
        visualizations: data.visualizations,
        isLoading: false
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err.message,
        isLoading: false
      }));
    }
  };

  const changeChart = (type) => {
    setState(prev => ({ ...prev, activeChart: type }));
  };

  return (
    <div className="cyber-container">
      {/* Terminal Header */}
      <header className="cyber-header">
        <div className="scanline"></div>
        <h1 className="cyber-title">>_ COURSE_OPTIMIZER.EXE</h1>
        <p className="cyber-subtitle">// UPLOAD TRANSCRIPT FOR ANALYSIS</p>
        
        <div className="upload-interface">
          <label className={`cyber-button ${state.isLoading ? 'processing' : ''}`}>
            {state.isLoading ? (
              <>
                <span className="blink">PROCESSING...</span>
                <div className="cyber-loader"></div>
              </>
            ) : (
              'SELECT TRANSCRIPT_FILE.PDF'
            )}
            <input 
              type="file" 
              onChange={handleFileUpload} 
              accept=".pdf" 
              disabled={state.isLoading}
            />
          </label>
        </div>
      </header>

      {/* Main Display */}
      <main className="cyber-main">
        {state.error && (
          <div className="cyber-error">
            <span className="blink">⚠️</span> {state.error}
          </div>
        )}

        {state.visualizations && (
          <div className="visualization-section">
            <div className="chart-selector">
              <button 
                className={`chart-btn ${state.activeChart === 'pie' ? 'active' : ''}`}
                onClick={() => changeChart('pie')}
              >
                PIE CHART
              </button>
              <button 
                className={`chart-btn ${state.activeChart === 'bar' ? 'active' : ''}`}
                onClick={() => changeChart('bar')}
              >
                BAR CHART
              </button>
              <button 
                className={`chart-btn ${state.activeChart === 'radar' ? 'active' : ''}`}
                onClick={() => changeChart('radar')}
              >
                RADAR CHART
              </button>
            </div>
            
            <div className="visualization-panel">
              <div className="panel-header">
                <span className="blink">▼</span> {`${state.activeChart.toUpperCase()}_ANALYSIS`}
              </div>
              <img 
                src={`data:image/png;base64,${state.visualizations[state.activeChart]}`} 
                alt={`Course ${state.activeChart} analysis`} 
                className="cyber-chart"
              />
              <div className="chart-instructions">
                <span className="blink">!</span> HOVER OVER CHART ELEMENTS FOR DETAILS
              </div>
            </div>
          </div>
        )}

        {state.recommendations?.length > 0 && (
          <div className="recommendations-grid">
            <div className="panel-header">
              <span className="blink">▼</span> RECOMMENDED_COURSES.LIST
            </div>
            <div className="cyber-cards">
              {state.recommendations.map((course) => (
                <div 
                  key={course.code}
                  className={`cyber-card ${state.selectedCourse?.code === course.code ? 'active' : ''}`}
                  onClick={() => setState(prev => ({ ...prev, selectedCourse: course }))}
                >
                  <div className="card-header">
                    <h3 className="cyber-text">{course.code}</h3>
                    <span className="match-value">{course.match}%</span>
                  </div>
                  <h4 className="cyber-text-alt">{course.name}</h4>
                  <div className="cyber-progress">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${course.match}%` }}
                    ></div>
                  </div>
                  <div className="card-footer">
                    <span className="difficulty-tag">{course.difficulty}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Course Detail Panel */}
        {state.selectedCourse && (
          <div className="cyber-modal" onClick={() => setState(prev => ({ ...prev, selectedCourse: null }))}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <button className="cyber-close" onClick={() => setState(prev => ({ ...prev, selectedCourse: null }))}>
                [X]
              </button>
              
              <div className="modal-header">
                <h3 className="cyber-text">{state.selectedCourse.code}: {state.selectedCourse.name}</h3>
                <div className="match-display">{state.selectedCourse.match}% MATCH</div>
              </div>
              
              <p className="cyber-desc">{state.selectedCourse.description}</p>
              
              <div className="cyber-columns">
                <div className="cyber-col">
                  <h4 className="cyber-text-alt">> SKILLS_ACQUIRED:</h4>
                  <ul className="cyber-list">
                    {state.selectedCourse.skills?.map((skill, i) => (
                      <li key={i} className="cyber-list-item">• {skill}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="cyber-col">
                  <h4 className="cyber-text-alt">> SYLLABUS_MODULES:</h4>
                  <ul className="cyber-list">
                    {state.selectedCourse.syllabus?.map((topic, i) => (
                      <li key={i} className="cyber-list-item">• {topic}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="cyber-footer">
        <div className="scanline"></div>
        <p className="cyber-text-small">SYSTEM STATUS: OPERATIONAL</p>
      </footer>
    </div>
  );
}

export default App;