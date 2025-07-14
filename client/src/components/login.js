import React, { useEffect, useState } from 'react';
import './login.css';

function LoginTab({ onClose }) {
  return (
    <>
      <div id="login-overlay" onClick={onClose}></div>
      <div id="wrapper">
        <form action="" id="form-login">
          <button type="button" className="close-btn" onClick={onClose}>×</button>
          <h1 className="form-heading">Login</h1>
          <div className="form-group">
            <i className="far fa-user"></i>
            <input type="text" className="form-input" placeholder="Username" />
          </div>
          <div className="form-group">
            <i className="fas fa-key"></i>
            <input type="password" className="form-input" placeholder="Password" />
            <div id="eye">
              <i className="far fa-eye"></i>
            </div>
          </div>
          <input type="submit" value="Login" className="form-submit" />
        </form>
      </div>
    </>
  );
}

export default LoginTab;
