function getPlayers() {
  team = $("#teams").val();
  console.log(team);
  $.ajax({
    type:"GET",
    dataType: "json",
    data:{'team': team},
    url: "/get_players",
    success: function(data){
        console.log(data);
    }
  });
}
