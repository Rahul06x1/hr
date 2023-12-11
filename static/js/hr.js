function gotEmployees(data) {
    $("span.info")[0].innerHTML = "";
    var index = data.user_list.indexOf(data.id);

    if (data.user_list[index - 1]){
      $("#usercol").find('.prev').css( "display", "block" );
      $("#usercol").find('.prev').val(`/employees/${data.user_list[index - 1]}`);
    }
    else{
      $("#usercol").find('.prev').css( "display", "none" );
    }

    if (data.user_list[index + 1]){
      $("#usercol").find('.next').css( "display", "block" );
      $("#usercol").find('.next').val(`/employees/${data.user_list[index + 1]}`);
    }
    else{
      $("#usercol").find('.next').css( "display", "none" );
    }

    $("#userdetails")[0].innerHTML=`<h3> ${data.fname} ${data.lname}</h3>
    <h4> ${data.title} </h4>
    <table>
      <tr>
        <th> First name </th>
        <td> ${data.fname}</td>
      </tr>
      <tr>
        <th> Last name </th>
        <td> ${data.lname}</td>
      </tr>
      <tr>
        <th> Email </th>
        <td> ${data.email}</td>
      </tr>

      <tr>
        <th> Phone </th>
        <td> ${data.phone}</td>
      </tr>
    </table>

    <h4> Leave Detail </h4>
    <table>
      <tr>
        <th> Taken </th>
        <td> ${data.leaves_taken}</td>
      </tr>
      <tr>
        <th> Remaining </th>
        <td> ${data.leaves_remaining}</td>
      </tr>
      <tr>
        <th> Total </th>
        <td> ${data.total_leaves}</td>
      </tr>
    </table>
    <h4>Leave Form</h4>
    <form action="/leave/${data.id}" method="post">
      <label for="date"><b>Date</b></label>
      <br>
      <input type="date" name="date" id="date" required></input>
      <br>
      <label for="reason"><b>Reason</b></label>
      <br>
      <textarea type="text" name="reason" placeholder="Reason" id="reason"></textarea>
      <br>
      <button type="submit" class="btn btn-dark">Submit</button>
    </form>
  </div>
</div>
`
}


$(function() {
    $("a.userlink").click(function (ev) {
      $("div.flash-messages")[0].innerHTML = "";
      $("span.info")[0].innerHTML = `<div class="spinner-border" role="status">
    </div>`
      $.get(ev.target.href, gotEmployees);
      $(this).addClass("disabled");
      $(".userlink").not(this).removeClass("disabled");
      ev.preventDefault();
    });
});

$(function() {
  $("button.navigation-btn").click(function (ev) {
      var targetTag = $( `a[href*="${ev.target.value}"]`)[0]
      $(targetTag).addClass("disabled");
      $(".userlink").not(targetTag).removeClass("disabled");
      $.get(ev.target.value, gotEmployees);
      ev.preventDefault();
      });
});