import React, { useState } from 'react';
import Header from './components/header';
import TableInputForm from './components/table_input';
import LoginTab from './components/login';
import './index.css';

function App() {
  const [showLogin, setShowLogin] = useState(false);

  const handleLoginClick = () => {
    setShowLogin(true);
  }

  const handleCloseLogin = () => {
    setShowLogin(false);
  }

  return (
    <div className='container'>

      <Header onLoginClick={handleLoginClick} />
      {showLogin && <LoginTab onClose={handleCloseLogin} />}

      <div className='content'>
        <div className='set-rules'>
          <h3>Set Rules</h3>
        </div>
        
        <TableInputForm />

        <div className='result'>
          <h3>Result</h3>
        </div>
        <div className='print-result'>

        </div>
      </div>
    </div>
  );
}

export default App;