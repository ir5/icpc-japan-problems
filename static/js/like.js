async function onClickLike(aojId) {
  const likeElement = document.getElementById("like-a-" + aojId);
  const hiddenElement = document.getElementById("like-" + aojId);
  const currentValue = hiddenElement.value;
  const updateValue = 1 - currentValue;
  if (updateValue < 0 || updateValue > 1) return;
  const url = likeApiUrl + "?aoj_id=" + aojId + "&value=" + updateValue;

  fetch(url, { method: "POST" })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      return response.json();
    })
    .then((response) => {
      if (response["value"]) {
        likeElement.innerHTML = String.fromCodePoint(0x1f497);
        likeElement.setAttribute("class", "liked")
      } else {
        likeElement.innerHTML = String.fromCodePoint(0x1f90d);
        likeElement.setAttribute("class", "")
      }
      likeElement.innerHTML += response["likes"];
      hiddenElement.setAttribute("value", "" + response["value"]);
    });
}
