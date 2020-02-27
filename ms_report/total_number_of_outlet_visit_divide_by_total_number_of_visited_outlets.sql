<!DOCTYPE HTML>
<!-- saved from url=(0031)http://127.0.0.1:49209/browser/ -->
<!DOCTYPE html PUBLIC "" ""><!--[if lt IE 7]>
<html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]--><!--[if IE 7]>
<html class="no-js lt-ie9 lt-ie8"> <![endif]--><!--[if IE 8]>
<html class="no-js lt-ie9"> <![endif]--><!--[if gt IE 8]><!--><HTML 
class="no-js"><!--<![endif]--><HEAD><META content="IE=11.0000" 
http-equiv="X-UA-Compatible">
     
<META charset="utf-8">     
<META http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">     
<TITLE>pgAdmin 4</TITLE>     
<META name="viewport" content="width=device-width, initial-scale=1">     <!-- To set pgAdmin4 shortcut icon in browser --> 
    <LINK href="/favicon.ico?ver=41600" rel="shortcut icon">     <!-- Base template stylesheets --> 
    <LINK href="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/style.css" 
rel="stylesheet" type="text/css">     <LINK href="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/pgadmin.style.css" 
rel="stylesheet" type="text/css">     <LINK href="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/pgadmin.css" 
rel="stylesheet" type="text/css">      <!--View specified stylesheets-->     
<LINK href="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/browser.css" 
rel="stylesheet" type="text/css">     
<SCRIPT>
        /* This is used to change publicPath of webpack at runtime */
        window.getChunkURL = function() {
            return "/static/js/generated/";
        };
    </SCRIPT>
     <!-- Base template scripts -->     
<SCRIPT src="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/require.min.js" type="text/javascript"></SCRIPT>
     
<SCRIPT type="text/javascript">
            require.config({
                baseUrl: '',
                urlArgs: 'ver=41600',
                waitSeconds: 0,
                shim: {},
                paths: {
                    sources: "/static/js",
                    datagrid: "/static/js/generated/datagrid",
                    sqleditor: "/static/js/generated/sqleditor",
                    'pgadmin.browser.utils': "/browser/" + "js/utils",
                    'pgadmin.browser.endpoints': "/browser/" + "js/endpoints",
                    'pgadmin.browser.messages': "/browser/" + "js/messages",
                    'pgadmin.server.supported_servers': "/browser/" + "server/supported_servers",
                    'pgadmin.user_management.current_user': "/user_management/" + "current_user",
                    'translations': "/tools/" + "translations"
                }
            });

    </SCRIPT>
     <!-- View specified scripts -->     
<SCRIPT src="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/vendor.main.js" type="text/javascript"></SCRIPT>
     
<SCRIPT src="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/vendor.others.js" type="text/javascript"></SCRIPT>
     
<SCRIPT src="total_number_of_outlet_visit_divide_by_total_number_of_visited_outlets_files/pgadmin_commons.js" type="text/javascript"></SCRIPT>
 
<META name="GENERATOR" content="MSHTML 11.00.9600.19597"></HEAD> 
<BODY><!--[if lt IE 7]>
<p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade
    your browser</a> to improve your experience.</p>
<![endif]--> 
<DIV class="pg-sp-container" id="pg-spinner">
<DIV class="pg-sp-content">
<DIV class="row">
<DIV class="col-12 pg-sp-icon"></DIV></DIV>
<DIV class="row">
<DIV class="col-12 pg-sp-text">Loading pgAdmin 4 
v4.16...</DIV></DIV></DIV></DIV><NAV class="navbar fixed-top navbar-expand-lg navbar-dark pg-navbar"><A 
title="pgAdmin 4 logo" class="navbar-brand pgadmin_header_logo" aria-label="{ config.APP_NAME }} logo" 
onclick="return false;" href="http://127.0.0.1:49209/browser/#"><I class="app-icon pg-icon" 
aria-hidden="true"></I>     </A>     <BUTTON class="navbar-toggler collapsed" 
aria-controls="navbar-menu" type="button" data-toggle="collapse" data-target="#navbar-menu"><SPAN 
class="sr-only">Toggle navigation</SPAN>         <SPAN class="navbar-toggler-icon"></SPAN> 
    </BUTTON>     
<DIV class="collapse navbar-collapse" id="navbar-menu" role="navigation">
<UL class="navbar-nav mr-auto">
  <LI class="nav-item active dropdown d-none" id="mnu_file"><A class="nav-link dropdown-toggle" 
  role="button" aria-expanded="false" href="http://127.0.0.1:49209/browser/#" 
  data-toggle="dropdown">File <SPAN class="caret"></SPAN></A>
  <UL class="dropdown-menu" role="menu"></UL></LI>
  <LI class="nav-item active dropdown " id="mnu_obj"><A class="nav-link dropdown-toggle" 
  role="button" aria-expanded="false" href="http://127.0.0.1:49209/browser/#" 
  data-toggle="dropdown">Object <SPAN class="caret"></SPAN></A>
  <UL class="dropdown-menu" role="menu"></UL></LI>
  <LI class="nav-item active dropdown d-none" id="mnu_management"><A class="nav-link dropdown-toggle" 
  role="button" aria-expanded="false" href="http://127.0.0.1:49209/browser/#" 
  data-toggle="dropdown">Management <SPAN class="caret"></SPAN></A>
  <UL class="dropdown-menu" role="menu"></UL></LI>
  <LI class="nav-item active dropdown d-none" id="mnu_tools"><A class="nav-link dropdown-toggle" 
  role="button" aria-expanded="false" href="http://127.0.0.1:49209/browser/#" 
  data-toggle="dropdown">Tools <SPAN class="caret"></SPAN></A>
  <UL class="dropdown-menu" role="menu"></UL></LI>
  <LI class="nav-item active dropdown d-none" id="mnu_help"><A class="nav-link dropdown-toggle" 
  role="button" aria-expanded="false" href="http://127.0.0.1:49209/browser/#" 
  data-toggle="dropdown">Help <SPAN class="caret"></SPAN></A>
  <UL class="dropdown-menu" role="menu"></UL></LI></UL></DIV></NAV> 
<DIV class="pg-docker" id="dockerContainer"></DIV>
<SCRIPT>
            try {
require(
['sources/generated/app.bundle', 'sources/generated/codemirror', 'sources/generated/browser_nodes'],
function() {
},
function() {
/* TODO:: Show proper error dialog */
console.log(arguments);
});
} catch (err) {
/* Show proper error dialog */
console.log(err);
}
/*
 * Show loading spinner till every js module is loaded completely
 * Referenced url:
 * http://stackoverflow.com/questions/15581563/requirejs-load-script-progress
 * Little bit tweaked as per need
 */
require.onResourceLoad = function (context, map, depMaps) {
  var loadingStatusEl = panel = document.getElementById('pg-spinner');
  if (loadingStatusEl) {
    if (!context) {
      // we will call onResourceLoad(false) by ourselves when requirejs
      // is not loading anything d-none the indicator and exit
      setTimeout(function() {
        if (panel != null) {
            try{
                $(panel).remove();
            }
            catch(e){
                panel.outerHTML = "";
                delete panel;
            }
          return;
        }
      }, 500);
    }

    // show indicator when any module is loaded and
    // shedule requirejs status (loading/idle) check
    panel.style.display = "";
    clearTimeout(panel.ttimer);
    panel.ttimer = setTimeout(function () {
      var context = require.s.contexts._;
      var inited = true;
      for (name in context.registry) {
        var m = context.registry[name];
        if (m.inited !== true) {
          inited = false;
          break;
        }
      }

      // here the "inited" variable will be true, if requirejs is "idle",
      // false if "loading"
      if (inited) {
        // will fire if module loads in 400ms. TODO: reset this timer
        // for slow module loading
        require.onResourceLoad(false);
      }
    }, 400)
  }
};


</SCRIPT>
 </BODY></HTML>
