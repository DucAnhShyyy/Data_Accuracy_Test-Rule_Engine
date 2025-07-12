import React, {useState} from 'react';
import './table_input.css';

function TableInputForm() {
    // Value Range states
    const [age_from, setAgeFrom] = useState('');
    const [age_to, setAgeTo] = useState('');
    const [balance_from, setBalanceFrom] = useState('');
    const [balance_to, setBalanceTo] = useState('');
    const [transaction_amount_from, setTransactionAmountFrom] = useState('');
    const [transaction_amount_to, setTransactionAmountTo] = useState('');
    const [card_expiry_from, setCardExpiryFrom] = useState('');
    const [card_expiry_to, setCardExpiryTo] = useState('');

    // Regex / Template states
    const [phone, setPhone] = useState(''); 
    const [email, setEmail] =  useState('');
    const [ssn_format, setSsnFormat] = useState('');
    const [card_number_format, setCardNumberFormat] = useState('');
    const [account_number_format, setAccountNumberFormat] = useState('');
    const [transaction_id_format, setTransactionIdFormat] = useState('');

    // Continuity states
    const [transaction_datetime_start, setTransactionDatetimeStart] = useState('');
    const [transaction_datetime_end, setTransactionDatetimeEnd] = useState('');
    const [account_reg_date, setAccountRegDate] = useState('');
    const [account_open_date, setAccountOpenDate] = useState('');

    // Statistical Same States
    const [check_duplicate_ssn, setCheckDuplicateSsn] = useState(false);
    const [check_duplicate_email, setCheckDuplicateEmail] = useState(false);
    const [check_duplicate_phone, setCheckDuplicatePhone] = useState(false);
    const [check_duplicate_account, setCheckDuplicateAccount] = useState(false);
    const [check_duplicate_card, setCheckDuplicateCard] = useState(false);

    // Statistical Different States
    const [compare_balance_transaction, setCompareBalanceTransaction] = useState(false);
    const [compare_age_account_type, setCompareAgeAccountType] = useState(false);
    const [compare_branch_customer_city, setCompareBranchCustomerCity] = useState(false);
    const [compare_transaction_type_amount, setCompareTransactionTypeAmount] = useState(false);

    // Account Type and Status Options
    const [account_type, setAccountType] = useState('');
    const [account_status, setAccountStatus] = useState('');
    const [card_type, setCardType] = useState('');
    const [card_status, setCardStatus] = useState('');
    const [transaction_type, setTransactionType] = useState('');
    const [transaction_status, setTransactionStatus] = useState('');
    const [gender, setGender] = useState('');

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Collect all form data
        const formData = {
            // Value Range
            value_range: {
                age: { from: age_from, to: age_to },
                balance: { from: balance_from, to: balance_to },
                transaction_amount: { from: transaction_amount_from, to: transaction_amount_to },
                card_expiry: { from: card_expiry_from, to: card_expiry_to }
            },
            // Regex/Template
            regex_template: {
                phone,
                email,
                ssn_format,
                card_number_format,
                account_number_format,
                transaction_id_format
            },
            // Continuity
            continuity: {
                transaction_datetime: { start: transaction_datetime_start, end: transaction_datetime_end },
                account_registration: { reg_date: account_reg_date, open_date: account_open_date }
            },
            // Statistical Same
            statistical_same: {
                check_duplicate_ssn,
                check_duplicate_email,
                check_duplicate_phone,
                check_duplicate_account,
                check_duplicate_card
            },
            // Statistical Different
            statistical_different: {
                compare_balance_transaction,
                compare_age_account_type,
                compare_branch_customer_city,
                compare_transaction_type_amount
            },
            // Categories
            categories: {
                account_type,
                account_status,
                card_type,
                card_status,
                transaction_type,
                transaction_status,
                gender
            }
        };

        console.log('Complete form data:', formData);

        try {
            // First validate formats if provided
            const formatData = {
                email: formData.regex_template.email,
                phone: formData.regex_template.phone
            };

            // Only validate if email or phone is provided
            if (formatData.email || formatData.phone) {
                console.log('Validating formats:', formatData);
                
                const validationResponse = await fetch('http://localhost:5000/validation/check-format', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formatData),
                });

                if (!validationResponse.ok) {
                    const errorData = await validationResponse.json();
                    alert(`Server cannot validate format: ${errorData.error || validationResponse.statusText}`);
                    return;
                }

                const validationResults = await validationResponse.json();
                console.log('Validation Results:', validationResults);

                let validationFailed = false;
                let errorMessage = '';

                if (formatData.email && !validationResults.email_valid) {
                    errorMessage += validationResults.email_message + '\n';
                    validationFailed = true;
                }

                if (formatData.phone && !validationResults.phone_number_valid) {
                    errorMessage += validationResults.phone_number_message + '\n';
                    validationFailed = true;
                }

                if (validationFailed) {
                    alert('Please check information:\n' + errorMessage);
                    return;
                }
            }

            // Submit the complete form data
            console.log('Submitting form data to server...');
            const response = await fetch('http://localhost:5000/api/save-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Server response:', result);
                alert('Rules saved successfully!');
                // Reset form
                resetForm();

                // Call the SQL generation endpoint
                fetch('http://localhost:5000/sql/generate')
                    .then(res => res.json())
                    .then(data => {
                        console.log('Đã sinh SQL script:', data.message);
                    });

            } else {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                alert(`Something went wrong when saving rules: ${errorData.error || response.statusText}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Cannot connect to server or something went wrong');
        }
    };

    // Reset form function
    const resetForm = () => {
        // Reset all states
        setAgeFrom(''); setAgeTo(''); setBalanceFrom(''); setBalanceTo('');
        setTransactionAmountFrom(''); setTransactionAmountTo('');
        setCardExpiryFrom(''); setCardExpiryTo('');
        setPhone(''); setEmail(''); setSsnFormat('');
        setCardNumberFormat(''); setAccountNumberFormat('');
        setTransactionIdFormat('');
        setTransactionDatetimeStart(''); setTransactionDatetimeEnd('');
        setAccountRegDate(''); setAccountOpenDate('');
        setCheckDuplicateSsn(false); setCheckDuplicateEmail(false);
        setCheckDuplicatePhone(false); setCheckDuplicateAccount(false);
        setCheckDuplicateCard(false); setCompareBalanceTransaction(false);
        setCompareAgeAccountType(false); setCompareBranchCustomerCity(false);
        setCompareTransactionTypeAmount(false);
        setAccountType(''); setAccountStatus(''); setCardType('');
        setCardStatus(''); setTransactionType(''); setTransactionStatus('');
        setGender('');
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* ACCOUNT RULES */}
            <div className='table-wrap'>
                <table className='rules-table'>
                    <thead>
                        <tr className='table-head'>
                            <td colSpan="6">ACCOUNT RULES</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className='table-body'>
                            <td>
                                <strong>Balance Range</strong><br/>
                                From: <input type='number' placeholder='0' value={balance_from} onChange={(e) => setBalanceFrom(e.target.value)} />
                                To: <input type='number' placeholder='1000000' value={balance_to} onChange={(e) => setBalanceTo(e.target.value)} />
                            </td>
                            <td>
                                <strong>Account Type</strong><br/>
                                <select value={account_type} onChange={(e) => setAccountType(e.target.value)}>
                                    <option value="">Select Account Type</option>
                                    <option value="Checking Account">Checking Account</option>
                                    <option value="Savings Account">Savings Account</option>
                                    <option value="Money Market Account">Money Market Account</option>
                                    <option value="Certificate of Deposit (CD)">Certificate of Deposit (CD)</option>
                                </select>
                            </td>
                            <td>
                                <strong>Account Status</strong><br/>
                                <select value={account_status} onChange={(e) => setAccountStatus(e.target.value)}>
                                    <option value="">Select Account Status</option>
                                    <option value="Active">Active</option>
                                    <option value="Inactive">Inactive</option>
                                    <option value="Closed">Closed</option>
                                    <option value="Suspended">Suspended</option>
                                </select>
                            </td>
                            <td>
                                <strong>Account Number Format</strong><br/>
                                <input type='text' placeholder='987654321' value={account_number_format} onChange={(e) => setAccountNumberFormat(e.target.value)} />
                            </td>
                            <td>
                                <strong>Account Registration</strong><br/>
                                Reg: <input type='date' value={account_reg_date} onChange={(e) => setAccountRegDate(e.target.value)} />
                                Open: <input type='date' value={account_open_date} onChange={(e) => setAccountOpenDate(e.target.value)} />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* CUSTOMER RULES */}
            <div className='table-wrap'>
                <table className='rules-table'>
                    <thead>
                        <tr className='table-head'>
                            <td colSpan="6">CUSTOMER RULES</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className='table-body'>
                            <td>
                                <strong>Age Range</strong><br/>
                                From: <input type='number' placeholder='18' value={age_from} onChange={(e) => setAgeFrom(e.target.value)} />
                                To: <input type='number' placeholder='100' value={age_to} onChange={(e) => setAgeTo(e.target.value)} />
                            </td>
                            <td>
                                <strong>Phone Format</strong><br/>
                                <input type='text' placeholder='+84901234567' value={phone} onChange={(e) => setPhone(e.target.value)} />
                            </td>
                            <td>
                                <strong>Email Format</strong><br/>
                                <input type='email' placeholder='example@gmail.com' value={email} onChange={(e) => setEmail(e.target.value)} />
                            </td>
                            <td>
                                <strong>SSN Format</strong><br/>
                                <input type='text' placeholder='SSN1001' value={ssn_format} onChange={(e) => setSsnFormat(e.target.value)} />
                            </td>
                            <td>
                                <strong>Gender</strong><br/>
                                <select value={gender} onChange={(e) => setGender(e.target.value)}>
                                    <option value="">Select Gender</option>
                                    <option value="M">Male</option>
                                    <option value="F">Female</option>
                                </select>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* TRANSACTION RULES */}
            <div className='table-wrap'>
                <table className='rules-table'>
                    <thead>
                        <tr className='table-head'>
                            <td colSpan="6">TRANSACTION RULES</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className='table-body'>
                            <td>
                                <strong>Amount Range</strong><br/>
                                From: <input type='number' placeholder='1000' value={transaction_amount_from} onChange={(e) => setTransactionAmountFrom(e.target.value)} />
                                To: <input type='number' placeholder='100000' value={transaction_amount_to} onChange={(e) => setTransactionAmountTo(e.target.value)} />
                            </td>
                            <td>
                                <strong>DateTime Range</strong><br/>
                                Start: <input type='datetime-local' value={transaction_datetime_start} onChange={(e) => setTransactionDatetimeStart(e.target.value)} />
                                End: <input type='datetime-local' value={transaction_datetime_end} onChange={(e) => setTransactionDatetimeEnd(e.target.value)} />
                            </td>
                            <td>
                                <strong>Type Validation</strong><br/>
                                <select value={transaction_type} onChange={(e) => setTransactionType(e.target.value)}>
                                    <option value="">Select Transaction Type</option>
                                    <option value="Deposit">Deposit</option>
                                    <option value="Withdraw">Withdraw</option>
                                    <option value="Transfer">Transfer</option>
                                    <option value="Payment">Payment</option>
                                </select>
                            </td>
                            <td>
                                <strong>Status Check</strong><br/>
                                <select value={transaction_status} onChange={(e) => setTransactionStatus(e.target.value)}>
                                    <option value="">Select Transaction Status</option>
                                    <option value="Completed">Completed</option>
                                    <option value="Pending">Pending</option>
                                    <option value="Failed">Failed</option>
                                    <option value="Cancelled">Cancelled</option>
                                </select>
                            </td>
                            <td>
                                <strong>Transaction ID Format</strong><br/>
                                <input type='text' placeholder='TXN001' value={transaction_id_format} onChange={(e) => setTransactionIdFormat(e.target.value)} />
                            </td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* CARD RULES */}
            <div className='table-wrap'>
                <table className='rules-table'>
                    <thead>
                        <tr className='table-head'>
                            <td colSpan="6">CARD RULES</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className='table-body'>
                            <td>
                                <strong>Number Format</strong><br/>
                                <input type='text' placeholder='1234567890123456' value={card_number_format} onChange={(e) => setCardNumberFormat(e.target.value)} />
                            </td>
                            <td>
                                <strong>Expiry Range</strong><br/>
                                From: <input type='month' value={card_expiry_from} onChange={(e) => setCardExpiryFrom(e.target.value)} />
                                To: <input type='month' value={card_expiry_to} onChange={(e) => setCardExpiryTo(e.target.value)} />
                            </td>
                            <td>
                                <strong>Status Check</strong><br/>
                                <select value={card_status} onChange={(e) => setCardStatus(e.target.value)}>
                                    <option value="">Select Card Status</option>
                                    <option value="Active">Active</option>
                                    <option value="Inactive">Inactive</option>
                                    <option value="Blocked">Blocked</option>
                                    <option value="Expired">Expired</option>
                                </select>
                            </td>
                            <td>
                                <strong>Card Type</strong><br/>
                                <select value={card_type} onChange={(e) => setCardType(e.target.value)}>
                                    <option value="">Select Card Type</option>
                                    <option value="Debit">Debit</option>
                                    <option value="Credit">Credit</option>
                                    <option value="Prepaid">Prepaid</option>
                                </select>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div className='search-btn'>
                <button type='submit'>Submit</button>
                <button type='button' onClick={resetForm} style={{marginLeft: '10px'}}>Reset Form</button>
            </div>
        </form>
    );
}

export default TableInputForm;