(function () {
  if (window.__fikrlyUiEnhancementsBridgeLoaded) {
    return;
  }
  window.__fikrlyUiEnhancementsBridgeLoaded = true;

  var currentScript = document.currentScript;
  var query = "";

  if (currentScript && currentScript.src && currentScript.src.indexOf("?") !== -1) {
    query = currentScript.src.substring(currentScript.src.indexOf("?"));
  }

  var nextScript = document.createElement("script");
  nextScript.defer = true;
  nextScript.src = "/static/js/ui-enhancements.v2.js" + query;
  nextScript.onerror = function () {
    console.error("Failed to load /static/js/ui-enhancements.v2.js");
  };

  document.head.appendChild(nextScript);
})();
