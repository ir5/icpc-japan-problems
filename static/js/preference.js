function onChangePreference(redirectUrl, contestType = null) {
  let params = {}
  // values
  for (const id of ["aoj_userid", "level_lower_0", "level_lower_1"]) {
    params[id] = document.getElementById(id).value;
  }
  // checkboxes
  for (const id of ["ja", "en", "hide_solved"]) {
    params[id] = document.getElementById(id).checked ? 1 : 0;
  }

  if (contestType === null) {
    contestType = document.getElementById("contest_type").value;
  }
  params["contest_type"] = contestType;

  // rivals
  const rivals = document.querySelectorAll(".rival");
  rivalNames = []
  for (const rivalElement of rivals) {
    rivalNames.push(rivalElement.value);
  }
  newRival = document.getElementById("rival_aoj_userid").value.trim()
  if (newRival !== "") {
    rivalNames.push(newRival);
  }
  params["rivals"] = rivalNames.join(",");

  // compose param string
  let paramString = "";
  for (let key in params) {
    if (!params.hasOwnProperty(key)) continue;
    if (paramString !== "") {
      paramString += "&";
    }
    paramString += key + "=" + encodeURIComponent(params[key]);
  }

  // redirect to new page
  window.location.href = redirectUrl + "?" + paramString;
}

function setEvents(redirectUrl) {
  for (const id of ["ja", "en", "hide_solved", "level_lower_0", "level_lower_1"]) {
    let element = document.getElementById(id);
    element.addEventListener("change", function() { onChangePreference(redirectUrl); });
  }

  for (const id of ["aoj_userid", "rival_aoj_userid"]) {
    let element = document.getElementById(id);
    element.addEventListener("keydown", function(event) {
      if (event.keyCode == 13) onChangePreference(redirectUrl);
    });
  }

  for (const contestType of [0, 1]) {
    let element = document.getElementById("contest_type_" + contestType);
    element.addEventListener("click", function() { onChangePreference(redirectUrl, contestType); });
  }
}
