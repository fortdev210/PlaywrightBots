chrome.proxy.onProxyError.addListener(function (details) {
  console.log(details.error);
  proxyOff();

  setTimeout(function () {
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

          setTimeout(proxyOn, 300);
        };
        req.send(null);
      }
    );
  }, 350);
});
