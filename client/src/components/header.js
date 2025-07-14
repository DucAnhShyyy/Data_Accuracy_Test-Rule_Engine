import './header.css'

function Header(props) {
    return (
        <div className='header'>
            <header className='header-container'>
                <h1>Data Rules Engine</h1>
                <button className="login-btn" onClick={props.onLoginClick}>Login</button>
            </header>
        </div>
    );
}

export default Header;