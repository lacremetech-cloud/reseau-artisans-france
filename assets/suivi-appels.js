/* Suivi des appels Google Ads + consentement cookies.
   Tant que ADS_ID est vide, rien n'est chargé et aucun bandeau ne s'affiche.
   À remplir avec les valeurs des actions de conversion du compte Google Ads 584-705-5791 :
   - ADS_ID      : identifiant du tag, ex. "AW-123456789"
   - LABEL_CLIC  : libellé de la conversion « Clic sur le numéro » (clic sur un lien tel:)
   - LABEL_WA    : libellé de la conversion « Contact WhatsApp » (facultatif)
   - LABEL_APPEL : libellé de la conversion « Appel depuis le site » (numéro de transfert Google)
   Le tag Google n'est chargé qu'après « Accepter » (mode de consentement de base). */
(function(){
  var ADS_ID="AW-18282575612", LABEL_CLIC="6WyhCOHqzLIdEPzt541E", LABEL_WA="Y0iUCOTqzLIdEPzt541E", LABEL_APPEL="6FL2CPi9p6gdEPzt541E";
  var NUMERO="06 23 83 20 29", CLE="raf-consent";
  /* Microsoft Clarity (enregistrement anonyme des visites) : identifiant du projet, vide = désactivé. */
  var CLARITY_ID="";
  /* Pixel Meta (Facebook / Instagram) : mesure les visites et les contacts venus des pubs Meta. */
  var META_PIXEL="1937671093866512";
  if(!ADS_ID) return;
  document.querySelectorAll(".js-cookies").forEach(function(l){l.hidden=false;});

  window.dataLayer=window.dataLayer||[];
  function gtag(){dataLayer.push(arguments);}
  window.gtag=gtag;
  var charge=false;

  function lireChoix(){try{return localStorage.getItem(CLE);}catch(e){return null;}}
  function ecrireChoix(v){try{localStorage.setItem(CLE,v);}catch(e){}}

  function charger(){
    if(charge) return; charge=true;
    gtag("consent","default",{ad_storage:"granted",ad_user_data:"granted",ad_personalization:"denied",analytics_storage:"denied"});
    var s=document.createElement("script");
    s.async=true; s.src="https://www.googletagmanager.com/gtag/js?id="+ADS_ID;
    document.head.appendChild(s);
    if(CLARITY_ID){
      (function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script",CLARITY_ID);
      window.clarity("consent");
    }
    if(META_PIXEL){
      !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
      n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");
      window.fbq("init",META_PIXEL);
      window.fbq("track","PageView");
    }
    gtag("js",new Date());
    gtag("config",ADS_ID);
    if(LABEL_APPEL){
      /* Remplace le numéro affiché par un numéro de transfert Google pour compter les appels issus des annonces. */
      gtag("config",ADS_ID+"/"+LABEL_APPEL,{
        phone_conversion_number:NUMERO,
        phone_conversion_callback:function(formate,brut){
          document.querySelectorAll(".js-num").forEach(function(el){el.textContent=formate;});
          document.querySelectorAll("a.js-call").forEach(function(a){a.href="tel:"+brut;});
        }
      });
    }
  }

  function meta(canal){
    if(charge&&META_PIXEL&&window.fbq) window.fbq("track","Contact",{content_name:canal});
  }

  function conversion(label){
    if(!charge||!label) return;
    gtag("event","conversion",{send_to:ADS_ID+"/"+label});
  }

  document.addEventListener("click",function(e){
    var a=e.target.closest&&e.target.closest("a");
    if(!a) return;
    var h=a.getAttribute("href")||"";
    if(h.indexOf("tel:")===0){conversion(LABEL_CLIC);meta("telephone");}
    else if(h.indexOf("wa.me")>-1){conversion(LABEL_WA);meta("whatsapp");}
    else if(a.classList.contains("js-cookies")){e.preventDefault();bandeau();}
  });

  function bandeau(){
    var old=document.getElementById("cookie-bar"); if(old) old.remove();
    var d=document.createElement("div");
    d.id="cookie-bar"; d.setAttribute("role","dialog"); d.setAttribute("aria-label","Cookies");
    d.innerHTML='<p>Nous utilisons des cookies Google Ads, Meta (Facebook, Instagram) et Microsoft Clarity pour savoir quelles annonces génèrent des appels et améliorer le site. <a href="/confidentialite.html">En savoir plus</a></p>'+
      '<div><button type="button" data-v="refuse">Refuser</button><button type="button" data-v="accept">Accepter</button></div>';
    d.addEventListener("click",function(e){
      var v=e.target.getAttribute&&e.target.getAttribute("data-v"); if(!v) return;
      ecrireChoix(v); d.remove();
      if(v==="accept") charger();
    });
    document.body.appendChild(d);
  }

  var choix=lireChoix();
  if(choix==="accept") charger();
  else if(!choix) bandeau();
})();
