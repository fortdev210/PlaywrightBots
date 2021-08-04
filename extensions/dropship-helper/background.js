// Proxy functionality for WebFactional
function gotoPage(url) {
  var fulurl = chrome.extension.getURL(url);
  chrome.tabs.getAllInWindow(undefined, function (tabs) {
    for (var i in tabs) {
      tab = tabs[i];
      if (tab.url == fulurl) {
        chrome.tabs.update(tab.id, { selected: true });
        return;
      }
    }
    chrome.tabs.getSelected(null, function (tab) {
      chrome.tabs.create({ url: url, index: tab.index + 1 });
    });
  });
}

function callbackFn(details) {
  var proxySetting = JSON.parse(localStorage.proxySetting);

  if (proxySetting) {
    var auth = proxySetting["auth"];
    var username = auth["user"];
    var password = auth["pass"];
  }

  if (proxySetting["auth"]["user"] == "" && proxySetting["auth"]["pass"] == "")
    return {};

  return details.isProxy === !0
    ? {
        authCredentials: {
          username: username,
          password: password,
        },
      }
    : {};
}

chrome.webRequest.onAuthRequired.addListener(
  callbackFn,
  { urls: ["<all_urls>"] },
  ["blocking"]
);

// Sync extension settings from Google Cloud
chrome.storage.sync.get("proxySetting", function (val) {
  if (typeof val.proxySetting !== "undefined")
    localStorage.proxySetting = val.proxySetting;
});

// Error handling
errCount = 0;
chrome.proxy.onProxyError.addListener(function (details) {
  errCount++;
  console.log("Continuous refusal to connect. Attempt " + errCount + "...");
  console.log("Full Error: " + details.error);
});

// Emergency Proxy Shutoff (in the event of bad proxy and cannot disable otherwise)
(function () {
  nextProxyOn = function () {
    proxyOffWebF();

    setTimeout(function () {
      chrome.storage.sync.get(
        {
          host: "admin.stlpro.com",
        },
        function (items) {
          var url =
            "http://" + items.host + "/products/getdsforchrome/next/ip/";
          var req = new XMLHttpRequest();
          req.open("GET", url, true);
          //set host to dom element
          req.onload = function (e) {
            var data = JSON.parse(e.target.responseText);

            proxySetting = {
              http_host: data["ip"],
              http_port: data["port"],
              proxy_rule: "singleProxy",
              auth: { enable: "", user: "", pass: "" },
            };

            localStorage.proxySetting = JSON.stringify(proxySetting);
            proxySetting = JSON.parse(localStorage.proxySetting);
            proxyRule = proxySetting["proxy_rule"];
            httpHost = proxySetting["http_host"];
            httpPort = proxySetting["http_port"];

            setTimeout(proxyOnWebF, 300);
          };
          req.send(null);
        }
      );
    }, 350);
  };

  chrome.contextMenus.create({
    title: "Proxy Next + On",
    contexts: ["browser_action"], // ContextType
    onclick: nextProxyOn, // A callback function
  });
}.call(this));

(function () {
  emergencyShutoff = function () {
    proxyOffWebF();
  };

  chrome.contextMenus.create({
    title: "Emergency Proxy Shutoff",
    contexts: ["browser_action"], // ContextType
    onclick: emergencyShutoff, // A callback function
  });
}.call(this));

chrome.runtime.onInstalled.addListener(function (details) {
  if (details.reason == "install" || details.reason == "update") {
    localStorage.supplierProxies = "B,W,T,H,G";
    localStorage.autoProxy = "enabled";
  }
});

chrome.runtime.onMessage.addListener(function (msg, sender) {
  if (msg.newOrderStarted !== true && msg.isGetOrders == true) {
    proxyOffWebF();
  } else {
    supplier = msg.orderSupplier;
    pulledIP_webF = msg.proxyIP;
    pulledPort_webF = msg.proxyPort;
    setProxyWebF();
  }
});

function setProxyWebF() {
  enabledSuppliers = localStorage.supplierProxies.split(",");
  console.log("enable syppliers ", enabledSuppliers);
  if (enabledSuppliers.indexOf(supplier) > -1) {
    proxySetting = {
      http_host: pulledIP_webF,
      http_port: pulledPort_webF,
      proxy_rule: "singleProxy",
      auth: { enable: "", user: "", pass: "" },
    };

    localStorage.proxySetting = JSON.stringify(proxySetting);
    proxySetting = JSON.parse(localStorage.proxySetting);
    proxyRule = proxySetting["proxy_rule"];
    httpHost = proxySetting["http_host"];
    httpPort = proxySetting["http_port"];

    if (localStorage.autoProxy == "enabled") {
      setTimeout(proxyOnWebF, 300);
    } else {
      // do nothing
    }
  }
}

// Turn on proxy provided by database
function proxyOnWebF() {
  chrome.browserAction.setBadgeText({
    text: "PRXY",
  }),
    chrome.browserAction.setBadgeBackgroundColor({
      color: [0, 0, 0, 0],
    });

  var config = {
    mode: "fixed_servers",
    rules: { bypassList: ["admin.stlpro.com/products/getdsforchrome/"] },
  };

  if (!httpHost) return;

  config["rules"][proxyRule] = {
    scheme: "http",
    host: httpHost,
    port: parseInt(httpPort),
  };

  chrome.proxy.settings.set(
    { value: config, scope: "regular" },
    function () {}
  );
}

// Turn off proxy
function proxyOffWebF() {
  chrome.browserAction.setBadgeText({
    text: "",
  }),
    chrome.browserAction.setBadgeBackgroundColor({
      color: [128, 128, 128, 200],
    });

  var config = {
    mode: "direct",
  };

  chrome.proxy.settings.set(
    { value: config, scope: "regular" },
    function () {}
  );
}
