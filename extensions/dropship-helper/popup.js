document.addEventListener("DOMContentLoaded", function () {
  // Pull info from database
  chrome.storage.sync.get(
    {
      host: "admin.stlpro.com",
    },
    function (items) {
      var url = "http://" + items.host + "/products/getdsforchrome/";

      var req = new XMLHttpRequest();
      req.open("GET", url, true);
      //set host to dom element
      req.onload = function (e) {
        document.getElementById("dsaddress").innerHTML = e.target.responseText;
        document
          .getElementById("dsaddress")
          .setAttribute("data-host", "http://" + items.host);
        onOrdersLoaded();
        setProxy();
        startObservers();
      };
      req.send(null);
    }
  );
});

// Setup proxy parameters/functions
function setProxy() {
  if (
    document.querySelector("body").innerText ==
    "There is no picked orders OR your orders are finalized"
  ) {
    proxyOff();
  } else {
    enabledSuppliers = localStorage.supplierProxies.split(",");
    supplier = document.querySelector('[id="supplierCode"]').innerHTML;
    if (enabledSuppliers.indexOf(supplier) > -1) {
      proxySetting = {
        http_host: pulledIP,
        http_port: pulledPort,
        proxy_rule: "singleProxy",
        auth: { enable: "", user: "", pass: "" },
      };

      localStorage.proxySetting = JSON.stringify(proxySetting);
      proxySetting = JSON.parse(localStorage.proxySetting);
      proxyRule = proxySetting["proxy_rule"];
      httpHost = proxySetting["http_host"];
      httpPort = proxySetting["http_port"];
      if (
        document.querySelector("#proxyOnButton") !== null &&
        supplier !== "T"
      ) {
        document
          .querySelector("#proxyOnButton")
          .addEventListener("click", proxyOn);
        document
          .querySelector("#proxyOffButton")
          .addEventListener("click", proxyOff);
        document
          .querySelector("#proxyNextButton")
          .addEventListener("click", proxyNext);
      } else {
        if (
          document.querySelector("#proxyOnButton") !== null &&
          supplier == "T"
        ) {
          document
            .querySelector('button[class="dsbutton btn"]')
            .addEventListener("click", proxyOn);
          document
            .querySelector("#proxyOnButton")
            .addEventListener("click", proxyOn);
          document
            .querySelector("#proxyOffButton")
            .addEventListener("click", proxyOff);
          document
            .querySelector("#proxyNextButton")
            .addEventListener("click", proxyNext);
        }
      }
    }
  }
}

// Turn on proxy provided by database
function proxyOn() {
  chrome.browserAction.setBadgeText({
    text: "PRXY",
  }),
    chrome.browserAction.setBadgeBackgroundColor({
      color: [0, 0, 0, 0],
    });

  var config = {
    mode: "fixed_servers",
    rules: {},
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
function proxyOff() {
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

// Get next proxy in rotation
function proxyNext() {
  chrome.storage.sync.get(
    {
      host: "admin.stlpro.com",
    },
    function (items) {
      var url = "http://" + items.host + "/products/getdsforchrome/next/ip/";
      var req = new XMLHttpRequest();
      req.open("GET", url, true);
      //set host to dom element
      req.onload = function (e) {
        var data = JSON.parse(e.target.responseText);
        document.getElementById("picked_ip").innerHTML = data["ip"];
      };
      req.send(null);
    }
  );
}

// Get next credit card in rotation
function cardNext() {
  chrome.storage.sync.get(
    {
      host: "admin.stlpro.com",
    },
    function (items) {
      var url = "http://" + items.host + "/products/getdsforchrome/next/card/";
      var req = new XMLHttpRequest();
      req.open("GET", url, true);
      //set host to dom element
      req.onload = function (e) {
        var data = JSON.parse(e.target.responseText);
        ccArray = data["credit_card"];
        ccArray = ccArray.split("|");
        document.getElementById("display_cc").innerText =
          ccArray[0] + ", " + ccArray[7];
        document.getElementById("picked_credit_card").value =
          data["credit_card"];
      };
      req.send(null);
    }
  );
}

function accountNext() {
  alert("FUCKING POP");
  chrome.storage.sync.get(
    {
      host: "admin.stlpro.com",
    },
    function (items) {
      var url =
        "http://" + items.host + "/products/getdsforchrome/next/account/";
      var req = new XMLHttpRequest();
      req.open("GET", url, true);
      //set host to dom element
      req.onload = function (e) {
        var data = JSON.parse(e.target.responseText);
        document.getElementById("picked_username").innerText = data["username"];
        document.getElementById("picked_password").innerText = data["password"];
      };
      req.send(null);
    }
  );
}

// Reload popup to activate new proxy/credit card
function DOMReload() {
  window.location.reload();
}

// IP and Credit Card MutationObservers (detect popup changes and refresh page)
function startObservers() {
  observer1 = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      setTimeout(DOMReload, 100);
    });
  });
  observer2 = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      setTimeout(proxyOn, 450);
      setTimeout(DOMReload, 600);
    });
  });
  observer3 = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      setTimeout(proxyOn, 450);
      setTimeout(DOMReload, 600);
    });
  });

  if (document.querySelector('[id="picked_port"]') !== null) {
    detectNextPort = document.querySelector('[id="picked_port"]');

    ipConfig = {
      attributes: true,
      childList: true,
      characterData: true,
    };

    observer3.observe(detectNextPort, ipConfig);
  }

  if (document.querySelector('[id="picked_ip"]') !== null) {
    detectNextIP = document.querySelector('[id="picked_ip"]');

    ipConfig = {
      attributes: true,
      childList: true,
      characterData: true,
    };

    observer2.observe(detectNextIP, ipConfig);
  }

  if (document.querySelector("#cardNextButton") !== null) {
    detectNextCC = document.querySelector('[id="picked_credit_card"]');

    ccConfig = {
      attributes: true,
      childList: true,
      characterData: true,
    };

    observer1.observe(detectNextCC, ccConfig);
  }

  if (document.querySelector("#giftCardNextButton") == null) {
    // detectNextGC = document.querySelector('[id="picked_gift_cards"]');
    detectNextGC = document.querySelector('[id="picked_credit_card"]');
    gcConfig = {
      attributes: true,
      childList: true,
      characterData: true,
    };

    observer1.observe(detectNextGC, gcConfig);
  }
}

// Error handling
errCount = 0;
chrome.proxy.onProxyError.addListener(function (details) {
  errCount++;
  console.log("Continuous refusal to connect. Attempt " + errCount + "...");
  console.log("Full Error: " + details.error);
});

function genFirstGC() {
  chrome.storage.sync.get(
    {
      host: "admin.stlpro.com",
    },
    function (items) {
      var url =
        "http://" + items.host + "/products/getdsforchrome/next/gift_card/";
      var req = new XMLHttpRequest();
      req.open("GET", url, true);
      //set host to dom element
      req.onload = function (e) {
        var data = JSON.parse(e.target.responseText);

        if (document.getElementById("usedGCs").innerHTML == "") {
          document.getElementById(
            "usedGCs"
          ).innerHTML = document.getElementById("picked_gift_cards").innerText;
        } else {
          document.getElementById("usedGCs").innerHTML =
            document.getElementById("usedGCs").innerHTML +
            "\n" +
            document.getElementById("picked_gift_cards").innerText;
        }

        if (supplier !== "T") {
          document.getElementById("picked_gift_cards").innerText =
            data["gift_card"];
          document.getElementById("giftCardUseButton").click();
        } else {
          document.getElementById("picked_gift_cards").innerText =
            data["gift_card"].substr(0, 15) + data["gift_card"].substr(26, 9);
          gcRaw = data["gift_card"].substr(0, 26);
          document.getElementById("giftCardUseButton").click();
        }
      };
      req.send(null);
    }
  );
}

// Send GC info to WebFactional
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  supplier = document.querySelector('[id="supplierCode"]').innerHTML;
  if (supplier == "W") {
    console.log("Message from Content Script to Popup received.");

    function sendToWebF_WM_SST() {
      dataToSend = JSON.stringify({
        supplier_site_total: order_total,
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log(
            "Supplier site total successfully sent to WebFactional! Requesting GiftCard..."
          );

          genFirstGC();
        },
      });
    }

    if (request.totalGrabbed !== true) {
      // do nothing
    } else {
      order_total = request.order_total;
      sendToWebF_WM_SST();
    }

    function sendToWebF_WM_GCD() {
      gcArray = gift_card_num.split(",");
      gc_num_length = gcArray[0].length;
      gcLastFour = gcArray[0].substr(gc_num_length - 4, gc_num_length);

      gcScrapedLength = gc_applied_info.length;

      for (var x = 0; x < gcScrapedLength; x++) {
        if (gcLastFour == gc_applied_info[x][1]) {
          gc_amount_used = gc_applied_info[x][0];
        }
      }

      dataToSend = JSON.stringify({
        gift_cards: [
          {
            card_number: gcArray[0],
            amount: gc_amount_used,
          },
        ],
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log("GiftCard info successfully sent to WebFactional!");
        },
      });
    }

    if (request.infoGrabbed !== true) {
      // do nothing
    } else {
      gc_applied_info = request.gc_applied_info;
      gc_total = request.gc_total;
      order_total = request.order_total;

      sendToWebF_WM_GCD();
    }
  }

  if (supplier == "H") {
    console.log("Message from Content Script to Popup received.");

    function sendToWebF_KOHLS_SST() {
      dataToSend = JSON.stringify({
        supplier_site_total: order_total,
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log(
            "Supplier site total successfully sent to WebFactional! Requesting GiftCard..."
          );

          genFirstGC();
        },
      });
    }

    if (request.totalGrabbed !== true) {
      // do nothing
    } else {
      order_total = request.order_total;

      sendToWebF_KOHLS_SST();
    }

    function sendToWebF_KOHLS_GCD() {
      gcArray = gift_card_num.split(",");
      gc_num_length = gcArray[0].length;
      gcLastFour = gcArray[0].substr(gc_num_length - 4, gc_num_length);

      gcScrapedLength = gc_applied_info.length;

      for (var x = 0; x < gcScrapedLength; x++) {
        if (gcLastFour == gc_applied_info[x][1]) {
          gc_amount_used = gc_applied_info[x][0];
        }
      }

      dataToSend = JSON.stringify({
        gift_cards: [
          {
            card_number: gcArray[0],
            amount: gc_amount_used,
          },
        ],
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log("GiftCard info successfully sent to WebFactional!");
        },
      });
    }

    if (request.infoGrabbed !== true) {
      // do nothing
    } else {
      gc_applied_info = request.gc_applied_info;
      gc_total = request.gc_total;
      order_total = request.order_total;

      sendToWebF_KOHLS_GCD();
    }
  }

  if (supplier == "B") {
    console.log("Message from Content Script to Popup received.");

    function sendToWebF_BBY_SST() {
      dataToSend = JSON.stringify({
        supplier_site_total: order_total,
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log(
            "Supplier site total successfully sent to WebFactional! Requesting GiftCard..."
          );

          genFirstGC();
        },
      });
    }

    if (request.totalGrabbed !== true) {
      // do nothing
    } else {
      order_total = request.order_total;

      sendToWebF_BBY_SST();
    }

    function sendToWebF_BBY_GCD() {
      gcArray = gift_card_num.split(",");
      gc_num_length = gcArray[0].length;
      gcLastFour = gcArray[0].substr(gc_num_length - 4, gc_num_length);

      gcScrapedLength = gc_applied_info.length;

      for (var x = 0; x < gcScrapedLength; x++) {
        if (gcLastFour == gc_applied_info[x][1]) {
          gc_amount_used = gc_applied_info[x][0];
        }
      }

      dataToSend = JSON.stringify({
        gift_cards: [
          {
            card_number: gcArray[0],
            amount: gc_amount_used,
          },
        ],
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log("GiftCard info successfully sent to WebFactional!");
        },
      });
    }

    if (request.infoGrabbed !== true) {
      // do nothing
    } else {
      gc_applied_info = request.gc_applied_info;
      gc_total = request.gc_total;
      order_total = request.order_total;

      sendToWebF_BBY_GCD();
    }
  }

  if (supplier == "P") {
    console.log("Message from Content Script to Popup received.");

    function sendToWebF_HD_SST() {
      dataToSend = JSON.stringify({
        supplier_site_total: order_total,
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log(
            "Supplier site total successfully sent to WebFactional! Requesting GiftCard..."
          );

          genFirstGC();
        },
      });
    }

    if (request.totalGrabbed !== true) {
      // do nothing
    } else {
      order_total = request.order_total;

      sendToWebF_HD_SST();
    }

    function sendToWebF_HD_GCD() {
      gcArray = gift_card_num.split(",");
      gc_num_length = gcArray[0].length;
      gcLastFour =
        gcArray[0].substr(gc_num_length - 4, gc_num_length) + "," + gcArray[1];

      gcScrapedLength = gc_applied_info.length;

      for (var x = 0; x < gcScrapedLength; x++) {
        if (gcLastFour == gc_applied_info[x][1]) {
          gc_amount_used = gc_applied_info[x][0];
        }
      }

      dataToSend = JSON.stringify({
        gift_cards: [
          {
            card_number: gcArray[0],
            amount: gc_amount_used,
          },
        ],
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log("GiftCard info successfully sent to WebFactional!");
        },
      });
    }

    if (request.infoGrabbed !== true) {
      // do nothing
    } else {
      gc_applied_info = request.gc_applied_info;
      gc_total = request.gc_total;
      order_total = request.order_total;
      order_number = request.order_number;

      sendToWebF_HD_GCD();
    }
  }

  if (supplier == "T") {
    console.log("Message from Content Script to Popup received.");

    function sendToWebF_Targ_SST() {
      dataToSend = JSON.stringify({
        supplier_site_total: order_total,
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log(
            "Supplier site total successfully sent to WebFactional! Requesting GiftCard..."
          );

          genFirstGC();
        },
      });
    }

    if (request.totalGrabbed !== true) {
      // do nothing
    } else {
      order_total = request.order_total;

      sendToWebF_Targ_SST();
    }

    function sendToWebF_Targ_GCD() {
      gcArray = gift_card_num.split(",");
      gcArray[0] = gcArray[0].substr(0, 15);
      gc_num_length = gcArray[0].length;
      gcLastFour = gcArray[0].substr(gc_num_length - 4, gc_num_length);

      gcScrapedLength = gc_applied_info.length;

      for (var x = 0; x < gcScrapedLength; x++) {
        if (gcLastFour == gc_applied_info[x][1]) {
          gc_amount_used = gc_applied_info[x][0];
        }
      }

      dataToSend = JSON.stringify({
        gift_cards: [
          {
            card_number: gcRaw,
            amount: gc_amount_used,
            supplier_order_number: order_number,
          },
        ],
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log("GiftCard info successfully sent to WebFactional!");
        },
      });
    }

    if (request.infoGrabbed !== true) {
      // do nothing
    } else {
      gc_applied_info = request.gc_applied_info;
      gc_total = request.gc_total;
      order_total = request.order_total;
      order_number = request.order_number;

      sendToWebF_Targ_GCD();
    }
  }

  if (supplier == "G") {
    console.log("Message from Content Script to Popup received.");

    function sendToWebF_BassPro_SST() {
      dataToSend = JSON.stringify({
        supplier_site_total: order_total,
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log(
            "Supplier site total successfully sent to WebFactional! Requesting GiftCard..."
          );

          genFirstGC();
        },
      });
    }

    if (request.totalGrabbed !== true) {
      // do nothing
    } else {
      order_total = request.order_total;
      sendToWebF_BassPro_SST();
    }

    function sendToWebF_Targ_GCD() {
      // gcArray = gift_card_num.split(",");
      // gcArray[0] = gcArray[0].substr(0, 15);
      // gc_num_length = gcArray[0].length;
      // gcLastFour = gcArray[0].substr(gc_num_length - 4, gc_num_length);

      // gcScrapedLength = gc_applied_info.length;

      // for (var x = 0; x < gcScrapedLength; x++) {
      //   if (gcLastFour == gc_applied_info[x][1]) {
      //     gc_amount_used = gc_applied_info[x][0];
      //   }
      // }

      dataToSend = JSON.stringify({
        gift_cards: [
          {
            card_number: gcRaw,
            amount: gc_amount_used,
            supplier_order_number: order_number,
          },
        ],
      });
      console.log(dataToSend);
      $.ajax({
        url: "http://admin.stlpro.com/products/getdsforchrome/update_ds_info/",
        data: dataToSend,
        dataType: "json",
        contentType: "application/json",
        type: "POST",
        success: function () {
          console.log("GiftCard info successfully sent to WebFactional!");
        },
      });
    }

    if (request.infoGrabbed !== true) {
      // do nothing
    } else {
      gc_applied_info = request.gc_applied_info;
      gc_total = request.gc_total;
      order_total = request.order_total;
      order_number = request.order_number;
      sendToWebF_Targ_GCD();
    }
  }
});
