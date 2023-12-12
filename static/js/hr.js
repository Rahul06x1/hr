function gotEmployees(data) {
      $("span.info")[0].innerHTML = "";


      $("#usercol").find('.prev').css( "display", "block" );
      $("#usercol").find('.prev').val(`/employees/${data.prev}`);

      $("#usercol").find('.next').css( "display", "block" );
      $("#usercol").find('.next').val(`/employees/${data.next}`);

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
        <td> ${data.total_leaves - data.leaves_taken}</td>
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
      var targetTag = $(`a[href="${ev.target.value}"]`).filter(function() {
        return $(this).attr('href') === ev.target.value;
      });
      $(targetTag).addClass("disabled");
      $(".userlink").not(targetTag).removeClass("disabled");
      $.get(ev.target.value, gotEmployees);
      ev.preventDefault();
      });
});