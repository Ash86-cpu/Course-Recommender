import React, { useState } from 'react';
import './App.css';

function App() {
  const [state, setState] = useState({
    recommendations: [],
    coursesFound: [],
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
      coursesFound: [],
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
        coursesFound: data.courses_found,
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
              'SELECT TRANSCRIPT (.PDF / .TXT)'
            )}
            <input 
              type="file" 
              onChange={handleFileUpload} 
              accept=".pdf,.txt" 
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

        {state.coursesFound?.length > 0 && (
          <div className="recommendations-grid">
            <div className="panel-header">
              <span className="blink">▼</span> {`COURSES_FOUND_IN_TRANSCRIPT (${state.coursesFound.length})`}
            </div>
            <ul className="cyber-list">
              {state.coursesFound.map((c) => (
                <li key={c.code} className="cyber-list-item">• {c.code}: {c.title}</li>
              ))}
            </ul>
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
                <span className="blink">!</span> CLICK A COURSE CARD BELOW FOR DETAILS
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
                  <h4 className="cyber-text-alt">{course.title}</h4>
                  <p className="cyber-text-small">Because you took: {course.because_of}</p>
                  <div className="cyber-progress">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${course.match}%` }}
                    ></div>
                  </div>
                  <div className="card-footer">
                    <span className="difficulty-tag">{course.difficulty}</span>
                    <span className="difficulty-tag">
                      {course.prereqs_met ? 'PREREQS MET' : `NEEDS ${course.prerequisites.replaceAll(';', ', ')}`}
                    </span>
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
                <h3 className="cyber-text">{state.selectedCourse.code}: {state.selectedCourse.title}</h3>
                <div className="match-display">{state.selectedCourse.match}% MATCH</div>
              </div>
              
              <p className="cyber-desc">{state.selectedCourse.description}</p>
              
              <div className="cyber-columns">
                <div className="cyber-col">
                  <h4 className="cyber-text-alt">> SKILLS_ACQUIRED:</h4>
                  <ul className="cyber-list">
                    {state.selectedCourse.skills?.split(';').map((skill, i) => (
                      <li key={i} className="cyber-list-item">• {skill}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="cyber-col">
                  <h4 className="cyber-text-alt">> COURSE_INFO:</h4>
                  <ul className="cyber-list">
                    <li className="cyber-list-item">• Prerequisites: {state.selectedCourse.prerequisites ? state.selectedCourse.prerequisites.replaceAll(';', ', ') : 'None'}</li>
                    <li className="cyber-list-item">• Difficulty: {state.selectedCourse.difficulty}</li>
                    <li className="cyber-list-item">• Workload: {state.selectedCourse.workload}</li>
                    <li className="cyber-list-item">• Suggested because you took: {state.selectedCourse.because_of}</li>
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