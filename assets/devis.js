/* Formulaire de devis des landings : envoi vers Make (Telegram + e-mail), événement Lead Meta. */
(function(){
  var HOOK = "https://hook.eu2.make.com/2qll6fh58q8x5hluifvh60yct3lijsd5";
  var form = document.getElementById("devis");
  if (!form) return;
  var err = form.querySelector(".err"), btn = form.querySelector(".submit");

  function source(){
    try{
      var q = new URLSearchParams(location.search), parts = [];
      ["utm_source","utm_campaign","utm_content"].forEach(function(k){ if(q.get(k)) parts.push(k.replace("utm_","")+"="+q.get(k)); });
      if (q.get("fbclid")) parts.push("fbclid");
      return parts.join(" · ") || document.referrer || "direct";
    }catch(e){ return "direct"; }
  }

  form.addEventListener("submit", function(e){
    e.preventDefault();
    err.style.display = "none";
    var fd = new FormData(form);
    if (fd.get("site")) return; // pot de miel anti-robots
    var tel = (fd.get("tel")||"").replace(/[^\d+]/g,"");
    if (!fd.get("projet")) { err.textContent = "Choisissez votre projet."; err.style.display = "block"; return; }
    if (tel.replace("+33","0").length < 10) { err.textContent = "Indiquez un numéro de téléphone valide."; err.style.display = "block"; return; }
    if (!(fd.get("nom")||"").trim() || !(fd.get("ville")||"").trim()) { err.textContent = "Indiquez votre nom et votre commune."; err.style.display = "block"; return; }

    var body = new URLSearchParams();
    body.set("page", form.dataset.page);
    ["nom","tel","ville","projet","delai","message"].forEach(function(k){ body.set(k, (fd.get(k)||"").toString().trim()); });
    body.set("source", source());
    var eventId = "lead-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8);
    try{
      var q = new URLSearchParams(location.search);
      body.set("utm_source", q.get("utm_source") || (q.get("fbclid") ? "meta" : (q.get("gclid") ? "google" : "")));
      body.set("utm_campaign", q.get("utm_campaign") || "");
      body.set("utm_content", q.get("utm_content") || "");
      /* Mesure Meta (API Conversions) : seulement si la case est cochée ou si les cookies ont été acceptés. */
      var cookies = false; try{ cookies = localStorage.getItem("raf-consent") === "accept"; }catch(e){}
      var accord = fd.get("mesure") === "oui" || cookies;
      body.set("mesure", accord ? "oui" : "non");
      if (accord) {
        var ck = function(n){ var m = document.cookie.match("(?:^|; )" + n + "=([^;]*)"); return m ? m[1] : ""; };
        var fbc = ck("_fbc") || (q.get("fbclid") ? "fb.1." + Date.now() + "." + q.get("fbclid") : "");
        body.set("event_id", eventId);
        body.set("fbc", fbc);
        body.set("fbp", ck("_fbp"));
        body.set("url", location.origin + location.pathname);
        body.set("ua", navigator.userAgent);
      }
    }catch(e){}

    btn.disabled = true; btn.textContent = "Envoi…";
    fetch(HOOK, {method:"POST", mode:"no-cors", body: body})
      .then(function(){
        if (window.fbq) window.fbq("track","Lead",{content_name: form.dataset.page},{eventID: eventId});
        form.querySelector(".fields").style.display = "none";
        form.querySelector(".thanks").style.display = "block";
        form.scrollIntoView({behavior:"smooth", block:"center"});
      })
      .catch(function(){
        btn.disabled = false; btn.textContent = form.dataset.cta;
        err.textContent = "L'envoi n'a pas marché. Appelez-nous au 06 23 83 20 29.";
        err.style.display = "block";
      });
  });

  /* Barre d'action mobile : visible une fois le formulaire dépassé */
  var card = document.querySelector(".form-card");
  if (card && "IntersectionObserver" in window) {
    new IntersectionObserver(function(en){
      document.body.classList.toggle("show-bar", !en[0].isIntersecting && en[0].boundingClientRect.top < 0);
    }).observe(card);
  }
})();
