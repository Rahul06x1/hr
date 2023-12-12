'use strict';
function qwe(api) {
console.log('assssssssssssssssssssssssssssssssssssssssssssssssssssssssssss',api)
}
function Like() {
    const [reason, setReason] = React.useState('')
    const [date, setDate] = React.useState(new Date())
    const [state, setState] = React.useState([])

    const submitForm= () => {
        if(!date) return
        setState((s) => [...s, {id: s.length, date:date, reason: reason}])
        setReason('')
        setDate(new Date())
    }
    fetch('http://127.0.0.1:5000/employees/6')
   .then(response => response.json())
   .then(data => console.log(data));
    console.log(state)
    return(<div>
        <form >
                <label>
                    Reason : <br/>
                    <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} required/><br/>
                </label>
                <br/>
                <label>
                    Date : <br/>
                    <input type="date" value={date} onChange={(e) => setDate(e.target.value)} /><br/>
                </label>
                <br/>
                <button onClick={submitForm}>Submit</button>
            </form>
    </div>)

}

const domContainer = document.getElementById('root');
const root = ReactDOM.createRoot(domContainer);
root.render(React.createElement(Like));