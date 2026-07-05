/* OpenMandriva mirror portal — highlight the active nav item by URL */
(function(){
  function norm(u){ try{ return (u||"").replace(/\/+$/,""); }catch(e){ return u; } }
  var here = norm(location.origin + location.pathname + location.search);
  var links = document.querySelectorAll(".om-nav a[href]");
  for (var i=0;i<links.length;i++){
    if (norm(links[i].href) === here){ links[i].classList.add("active"); }
  }
})();
