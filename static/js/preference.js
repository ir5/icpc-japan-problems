function onUpdatePreference(contestType = null) {
  let params = {}
  // values
  for (const id in ["aoj_userid", "point_lower_0", "point_upper_0", "point_lower_1", "point_upper_1"]) {
    params[id] = document.getElementById(id).value;
  }
  // checkboxes
  for (const id in ["ja", "en", "hide_solved"]) {
    params[id] = document.getElementById(id).checked ? 1 : 0;
  }

  if (contestType === null) {
    contestType = document.getElementById("contest_type").value;
  }
  params["contest_type"] = contestType;

  // rivals
  const rivals = document.querySelectorAll(".rival");
  rivalNames = []
  for (const rivalElement in rivals) {
    rivalNames.push(rivalElement.value);
  }
  newRival = document.getElementById("rival_aoj_userid").value.trim()
  if (newRival !== "") {
    rivalNames.push(newRival);
  }
  param["rivals"] = rivalNames.join(",");

  // compose param string
  let paramString = "";
  for (let key in params) {
    if (paramString !== "") {
      paramString += "&";
    }
    paramString += key + "=" + encodeURIComponent(params[key]);
  }

  // redirect to new page
  window.location.href = "/?" + paramString;
}
