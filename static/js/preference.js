function onRemoveRival(redirectUrl, rivalName) {
  onChangePreference(redirectUrl, null, rivalName);
}

function onChangePreference(redirectUrl, contestType = null, removeRivalName = null) {
  let params = {}
  // values
  for (const id of ["aoj_userid"]) {
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
  let rivalNames = new Set();
  for (const rivalElement of rivals) {
    rivalNames.add(rivalElement.value);
  }
  newRival = document.getElementById("rival_aoj_userid").value.trim()
  if (newRival !== "") {
    rivalNames.add(newRival);
  }
  if (removeRivalName !== null) {
    rivalNames.delete(removeRivalName);
  }
  params["rivals"] = [...rivalNames].join(",");

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
  for (const id of ["ja", "en", "hide_solved"]) {
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
