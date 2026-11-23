// „Adresse kopieren“: legt die https-Adresse des Kalenders in die Zwischenablage und bestätigt das im Knopf.
document.addEventListener("click", function (ereignis) {
  var knopf = ereignis.target.closest("button[data-adresse]");
  if (!knopf) { return; }
  var adresse = new URL(knopf.dataset.adresse, document.baseURI).href;
  var fertig = function (text) {
    var vorher = knopf.dataset.text || knopf.textContent;
    knopf.dataset.text = vorher;
    knopf.textContent = text;
    knopf.classList.add("fertig");
    window.setTimeout(function () { knopf.textContent = vorher; knopf.classList.remove("fertig"); }, 2000);
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(adresse).then(function () { fertig("Kopiert"); }, function () { window.prompt("Adresse kopieren:", adresse); });
  } else {
    window.prompt("Adresse kopieren:", adresse);
  }
});
