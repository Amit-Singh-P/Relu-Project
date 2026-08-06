import EnrichSection from './components/EnrichSection';
import ResultsSection from './components/ResultsSection';
import './App.css';

function App() {
  return (
    <div className="page">
      <header className="masthead">
        <h1 className="masthead-title">
          Company <span>Enrichment</span>
        </h1>
        <span className="masthead-meta">AI-powered company research</span>
      </header>

      <EnrichSection />
      <ResultsSection />

      <footer className="footer-note">Company Enrichment · MERN Stack</footer>
    </div>
  );
}

export default App;
