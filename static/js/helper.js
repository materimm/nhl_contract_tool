function getPlayers() {
  team = $("#teams").val();
  // $.ajax({
  //   type:"GET",
  //   dataType: "json",
  //   data:{'team': team},
  //   url: "/get_players",
  //   success: function(data){
  //       console.log(data);
  //   }
  // });
  fetch("/get_players", {
    headers : {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    method: 'GET',
    dataType: 'json',
    data: {'team': team}
  }).then(function (data) {
    console.log(data);
  });

}
