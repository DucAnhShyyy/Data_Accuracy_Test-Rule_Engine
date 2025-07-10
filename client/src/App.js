import Header from './components/header';
import TableInputForm from './components/table_input';
import './index.css';

function App() {
  return (
    <div className='container'>

      <Header />

      <div className='content'>
        <div className='set-rules'>
          <h3>Set Rules</h3>
        </div>
        
        <TableInputForm />

        <div className='result'>
          <h3>Result</h3>
        </div>
        <div className='print-result'>
          <p>Nothing</p>
        </div>
      </div>
    </div>
  );
}

export default App;