import React, {useState} from 'react';
import './table_input.css';

function TableInputForm() {
    const [age_from, setAgeFrom] = useState('');
    const [age_to, setAgeTo] = useState('');
    const [phone, setPhone] = useState(''); 
    const [email, setEmail] =  useState('');
    const [customer_since, setCusS] = useState('');
    const [expires_end, setExpEnd] = useState('');

    const handleSubmit = async(e) => {
        e.preventDefault();
        const dataToSend = {age_from, age_to, phone, email, customer_since, expires_end};
        console.log('Sending...', dataToSend);

        try {
            const response = await fetch('http://localhost:5000/api/save-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend),
            });

            if (response.ok) {
                alert('Searching success !');
                setAgeFrom('');
                setAgeTo('');
                setPhone('');
                setEmail('');
                setCusS('');
                setExpEnd('');
            } else {
                alert('Something went wrong when searching');
            }
        } catch (error) {
            console.log.error('Error when sending data:', error);
            alert('Cannot connect to server');
        }
    };

    return(
        <form onSubmit={handleSubmit}>
            <div className='table-wrap'>
            <table className='rules-table'>
                <thead>
                  <tr className='table-head'>
                    <td>Age</td>
                    <td>Phone Number</td>
                    <td>Email</td>
                    <td>Customer Since</td>
                    <td>Expires End</td>
                    </tr>
                </thead>
                <tbody>
                  <tr className='table-body'>
                    <td>From: <input type='number' placeholder='18' value={age_from} onChange={(e) => setAgeFrom(e.target.value)}></input> To:<input type='number' placeholder='100' value={age_to} onChange={(e) => setAgeTo(e.target.value)}></input></td>
                    <td><input type='number' placeholder='+84' value={phone} onChange={(e) => setPhone(e.target.value)}></input></td>
                    <td><input type='email' placeholder='+@gmail.com' value={email} onChange={(e) => setEmail(e.target.value)}></input></td>
                    <td><input type='number' placeholder='YY (Ex: 2000)' value={customer_since} onChange={(e) => setCusS(e.target.value)}></input></td>
                    <td><input type='month' placeholder='MM / YY' value={expires_end} onChange={(e) => setExpEnd(e.target.value)}></input></td>
                  </tr>
                </tbody>
            </table>
          </div>
            <div className='search-btn'>
                <button type='submit'>Search</button>
            </div>
        </form>
    );
}

export default TableInputForm;