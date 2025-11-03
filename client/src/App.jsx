import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import AIAssistant from './components/AIAssistant';
import Dashboard from './pages/Dashboard';
import Actions from './pages/Actions';
import Meetings from './pages/Meetings';
import Comments from './pages/Comments';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="actions" element={<Actions />} />
            <Route path="meetings" element={<Meetings />} />
            <Route path="comments" element={<Comments />} />
          </Route>
        </Routes>
        <AIAssistant />
        <ToastContainer position="top-right" autoClose={3000} />
      </Router>
    </ThemeProvider>
  );
}

export default App;
