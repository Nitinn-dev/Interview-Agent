import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [skills, setSkills] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult('');
    let res;
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      res = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        body: formData,
      });
    } else if (skills) {
      res = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills }),
      });
    } else {
      setResult('Please upload a file or enter your skills.');
      setLoading(false);
      return;
    }

    if (res.ok) {
      const data = await res.json();
      setResult(data.result);
    } else {
      const data = await res.text();
      setResult(data);
    }
    setLoading(false);
  };

  const handleDownload = () => {
    const blob = new Blob([result], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'interview_prep.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="app-bg">
      <div className="main-card">
        <h1 className="title">🧑‍💻 AI Interview Preparation Agent</h1>
        <form onSubmit={handleSubmit} className="form-section">
          <label className="label">Upload Resume (PDF/DOCX):</label>
          <input type="file" accept=".pdf,.docx" onChange={e => setFile(e.target.files[0])} className="input" />
          <div className="or">or</div>
          <label className="label">Enter Technical Skillset:</label>
          <textarea
            className="input textarea"
            placeholder="Or enter your skills"
            value={skills}
            onChange={e => setSkills(e.target.value)}
          />
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Processing...' : 'Submit'}
          </button>
        </form>
        {result && (
          <div className="output-section">
            <h3 className="output-title">AI Output:</h3>
            <div className="markdown-output">
              <ReactMarkdown>{result}</ReactMarkdown>
            </div>
            <button className="download-btn" onClick={handleDownload}>Download as .txt</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
