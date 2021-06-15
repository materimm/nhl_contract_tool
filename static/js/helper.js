function getPlayers() {
  //hide results area
  $("#results").hide();

  //get value from team select
  team = $("#teams").val();
  //send API request to get players on team
  $.ajax({
    type:"GET",
    dataType: "json",
    data:{'team': team},
    url: "/get_players",
    success: function(data) {
      //empty players from dropdown and add the players recieved from the api
      $("#players").empty();
      $('#players').append($('<option>', {
        value: "player",
        text: 'Select a player'
      }));

      $.each(data.players, function(key, value) {
        $('#players')
          .append($("<option></option>")
          .attr("value", value)
          .text(value));
      });

      //enable the players drop down
      $('#players').prop('disabled', false);
    }
  });
}


function getContract() {
  team = $("#teams").val();
  player = $("#players").val();
  $.ajax({
    type:"GET",
    dataType: "json",
    data:{'player': player, 'team' : team},
    url: "/get_contract",
    success: function(data) {
      $("#name").text(data.player);
      $("#position").text(data.position);
      $("#teamName").text($("#teams option:selected").text());
      $("#age").text(data.age + " years old");
      $("#teamLogo").attr("src", data.logo);
      $("#gp").text(data.stats.gp + " GP");
      $("#goals").text(data.stats.goals + " G");
      $("#assists").text(data.stats.assists + " A");
      $("#points").text(data.stats.points + " P");
      $("#aav").text(data.aav);
      $("#results").removeAttr("style");
    }});
}
