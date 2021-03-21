function change() // no ';' here
{
  var x = document.getElementById("policy_enable");
  if (x.innerHTML === "Turn off scaler policy") {
    x.innerHTML = "Turn on scaler policy!";
  } else {
    x.innerHTML = "Turn off scaler policy";
  }
}
