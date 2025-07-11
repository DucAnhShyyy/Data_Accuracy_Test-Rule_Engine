import React, {useState} from 'react';
import './table_input.css';

function TableInputForm() {
    const [age_from, setAgeFrom] = useState('');
    const [age_to, setAgeTo] = useState('');
    const [phone, setPhone] = useState(''); 
    const [email, setEmail] =  useState('');
    const [customer_since, setCusS] = useState('');
    const [expires_end, setExpEnd] = useState('');

    // Check validation first then submit
    const handleSubmit = async(e) => {
        e.preventDefault();

        let response;

        // Check format
        const dataToValidate = {email, phone};
        console.log('Validating...', dataToValidate);

        try {
            const validationResponse = await fetch('http://localhost:5000/validation/check-format', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToValidate),
            });

            if (!validationResponse.ok) {
                const errorData = await validationResponse.json();
                alert('Server cannot validate format: ${errorData.error || validationResponse.statusText}');
                console.error('Error feedback from Validation API', errorData)
                return; // Stop if cannot validate format
            }

            const validationResults = await validationResponse.json();
            console.log('Validation Results:', validationResults);

            let validationFailed = false;
            let errorMessage = '';
        
            if (!validationResults.email_valid) {
                errorMessage += validationResults.email_message + '\n';
                validationFailed = true;
            }

            if (!validationResults.phone_number_valid) {
                errorMessage += validationResults.phone_number_message + '\n';
                validationFailed = true;
            }

            if (validationFailed) {
                alert('Please check information:\n' + errorMessage);
                return; // Stop if wrong format
            }

            // Submit after checking validation
            const dataToSend = {age_from, age_to, phone, email, customer_since, expires_end};
            console.log('Format valid, sending...', dataToSend);

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
                const errorData = await response.json();
                alert('Something went wrong when searching: ${errorData.error || response.statusText}');
                console.error('Error response from API save data:', errorData);
            }
        } catch (error) {
            console.error('Error connecting or sending data:', error);
            if (error instanceof TypeError && error.message.includes("Failed  to fetch")) {
                alert('Cannot connect to server or something wrong');
            } else {
                alert('Something wrong when handling data')
            }
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