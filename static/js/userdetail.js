'use strict';
// function getEmployeeDetail(api) {
//     console.log('assssssssssssssssssssssssssssssssssssssssssssssssssssssssssss',api)
//     fetch(api)
//    .then(response => response.json())
//    .then(data => console.log(data));
// }
function userDetail() {
    const [data, setData] = React.useState({})
    const [reason, setReason] = React.useState('')
    const [date, setDate] = React.useState(new Date())
    const [state, setState] = React.useState([])

    const submitForm= () => {
        console.log('lllllllllllllllllllllllllllllll')
        if(!date) return
        setState((s) => [...s, {id: s.length, date:date, reason: reason}])
        setReason('')
        setDate(new Date())
    }

    const fetchEmployeeData = (api) => {
        fetch(api)
        .then(response => response.json())
        .then(data => setData(data));

    }
    $(function() {
        $("a.userlink").click(function (ev) {
          fetchEmployeeData(ev.target.href)
          ev.preventDefault();
        });
    });
    // console.log(state)
    if (Object.keys(data).length === 0){
        return false
    }else{
        return(<div>
            <h3> {data.fname} {data.lname} </h3>
            <br/>
            <h4> {data.title} </h4>
            <b>First name : </b> {data.fname}<br/>
            <b>Last name : </b>{data.lname}<br/>
            <b>Email : </b>{data.email}<br/>
            <b>Phone : </b>{data.phone}<br/><br/>
            <h4> Leave Detail </h4>
            <b>Taken : </b> {data.leaves_taken}<br/>
            <b>Remaining : </b>{data.total_leaves - data.leaves_taken}<br/>
            <b>Total : </b>{data.total_leaves}<br/>
            <br/>
            <h4>Leave Form</h4>
            <form action={`/leave/${data.id}`} method="post">
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
                <button type="submit" onClick={submitForm}>Submit</button>
            </form>
        </div>)
    }

}

const domContainer = document.getElementById('userdetail');
const root = ReactDOM.createRoot(domContainer);
root.render(React.createElement(userDetail));