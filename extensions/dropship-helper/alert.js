function onOrdersLoaded() {
  function contains(selector, text) {
    var elements = document.querySelectorAll(selector);
    return Array.prototype.filter.call(elements, function (element) {
      return RegExp(text).test(element.textContent);
    });
  }
  // get the host we are communicating with
  var host = $("#dsaddress").data("host");
  var supplier = $("#supplierCode").text();
  if (supplier == "W") {
    var dbPrice = document.querySelector('[id*="for_button_"]').parentElement
      .parentElement.children[5].innerText;
  }

  if (document.querySelector('[id="proxyOnButton"]') !== null) {
    document.querySelector('[id="proxyOnButton"]').hidden = true;
    document.querySelector('[id="proxyNextButton"]').hidden = true;
    document.querySelector('[id="proxyOffButton"]').hidden = true;
  }

  sCell = document
    .querySelector("thead")
    .children[0].querySelectorAll('[class="slimcell"]');
  wCell = document
    .querySelector("thead")
    .children[0].querySelectorAll('[class="widecell"]');

  for (var i = 0; i < sCell.length; i++) {
    sCell[i].setAttribute("style", "font-size:12px");
    sCell[i].innerHTML = "<b>" + sCell[i].innerHTML + "</b>";
  }

  for (var i = 0; i < wCell.length; i++) {
    wCell[i].setAttribute("style", "font-size:12px");
    wCell[i].innerHTML = "<b>" + wCell[i].innerHTML + "</b>";
  }

  /* This `if` statement for #picked_credit_card can be removed
   * once the HTML is added to WebFactional that the below code
   * is modifying.
   */
  if ($("#picked_credit_card")[0] !== undefined) {
    var spanToInputTag = document
      .querySelector('[id="picked_credit_card"]')
      .outerHTML.replace("</span>", "");
    spanToInputTag = spanToInputTag.substr(30, 500);
    spanToInputTag =
      '<input id="picked_credit_card" type="hidden" value="' +
      spanToInputTag +
      '">';
    document.querySelector(
      '[id="picked_credit_card"]'
    ).outerHTML = spanToInputTag;
    /* The code below can probably stay. It simply creates the array
     * from the CC info, another variable shortens the CC number to
     * the last four digits and is then injected into the HTML.
     */
    var ccArray = $("#picked_credit_card")[0].value.split("|");
    var ccLastFour = ccArray[7].substr(ccArray[7].length - 4, 4);
    document.querySelector('[id="picked_credit_card"]').outerHTML =
      '<span id="display_cc">' +
      ccArray[0] +
      ", " +
      ccLastFour +
      "</span>" +
      document.querySelector('[id="picked_credit_card"]').outerHTML;
  }

  // If GC is to be used, move everything above DS Order Tables into separate <div> and create Previous GC table
  if (document.getElementById("picked_gift_cards") !== null) {
    if (document.getElementById("picked_email") !== null) {
      GE = document.getElementById("GeneratedEmail");
      GI = document.getElementById("GenerateIp");
      GCC = document.getElementById("GenerateCreditCard");
      GGC = document.getElementById("GenerateGiftCard");
      GI.remove();
      GCC.remove();
      GGC.remove();
      document.getElementById("GeneratedEmail").outerHTML =
        '<span id="AllGenerated" style="float:left;margin-right:65px">' +
        GE.outerHTML +
        GI.outerHTML +
        GCC.outerHTML +
        GGC.outerHTML +
        '</span><table style="width:140px"><thead><tr><td class="widecell"><span style="font-size:10px"><b>Previous GCs</b></span></td></tr></thead><tbody><tr><td class="widecell"><span id="usedGCs" style="font-size:10px"></span></td></tr></tbody></table>';
    }
    if (document.getElementById("picked_username") !== null) {
      GA = document.getElementById("GeneratedAccount");
      GI = document.getElementById("GenerateIp");
      GCC = document.getElementById("GenerateCreditCard");
      GGC = document.getElementById("GenerateGiftCard");
      GI.remove();
      GCC.remove();
      GGC.remove();
      document.getElementById("GeneratedAccount").outerHTML =
        '<span id="AllGenerated" style="float:left;margin-right:65px">' +
        GA.outerHTML +
        GI.outerHTML +
        GCC.outerHTML +
        GGC.outerHTML +
        '</span><table style="width:140px"><thead><tr><td class="widecell"><span style="font-size:10px"><b>Previous GCs</b></span></td></tr></thead><tbody><tr><td class="widecell"><span id="usedGCs" style="font-size:10px"></span></td></tr></tbody></table>';
    }
    if (document.getElementById("picked_gift_cards").innerHTML == "") {
      giftCardUseButton.outerHTML =
        giftCardUseButton.outerHTML +
        '<button id="giftCardGenButton">Generate Gift Card</button>';
      giftCardUseButton.hidden = true;
      giftCardNextButton.disabled = true;

      $("#giftCardGenButton").on("click", function () {
        chrome.tabs.executeScript(null, { file: "jquery.js" }, function () {});
        chrome.tabs.executeScript(
          null,
          { file: "contentscript.js" },
          function () {
            chrome.tabs.executeScript({
              code: 'getSupplierSiteTotal("' + supplier + '")',
            });
          }
        );
        giftCardUseButton.hidden = false;
        giftCardGenButton.hidden = true;
        giftCardNextButton.disabled = false;
      });
    } else {
      // do nothing
    }

    // Get next gift card in rotation
    function giftCardNext() {
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
              ).innerHTML = document.getElementById(
                "picked_gift_cards"
              ).innerText;
            } else {
              document.getElementById("usedGCs").innerHTML =
                document.getElementById("usedGCs").innerHTML +
                "\n" +
                document.getElementById("picked_gift_cards").innerText;
            }

            if (supplier !== "T") {
              document.getElementById("picked_gift_cards").innerText =
                data["gift_card"];
            } else {
              document.getElementById("picked_gift_cards").innerText =
                data["gift_card"].substr(0, 15) +
                data["gift_card"].substr(26, 9);
              gcRaw = data["gift_card"].substr(0, 26);
            }
          };
          req.send(null);
        }
      );
    }

    document
      .querySelector("#giftCardNextButton")
      .addEventListener("click", giftCardNext);
  }

  // if #picked_ip exists, turn its text to the variable pulledIP
  if ($("#picked_ip")[0] !== undefined) {
    pulledIP = $("#picked_ip")[0].innerHTML;
  }

  pulledPort = "80";
  // if #picked_port exists, turn its text to the variable pulledPort
  if ($("#picked_port")[0] !== undefined) {
    pulledPort = $("#picked_port")[0].innerHTML;
  }

  if ($("#ds_order_id")[0] !== undefined) {
    dsOrderNumber = $("#ds_order_id")[0].innerHTML;
  }

  // set button of last order to green
  $("#button_" + localStorage["lastOrderItemId"]).css(
    "background-color",
    "#AACCAA"
  );

  // create account button for Target
  /*
    if (supplier == 'T') {
        document.querySelector('button[id="fill-email"]').outerHTML = document.querySelector('button[id="fill-email"]').outerHTML + '<span> </span><button id="create-account">Create Account</button>';
        $('#create-account').on('click', function() {
            var email = $('#picked_email').text();
			var first_name = document.querySelector('[id*="for_button"]').innerText.split('|')[2];
			var last_name = document.querySelector('[id*="for_button"]').innerText.split('|')[3];
            chrome.tabs.executeScript(null, { file: "jquery.js" }, function() {});
            chrome.tabs.executeScript(null, { file: "contentscript.js" }, function() {
                chrome.tabs.executeScript({ code: 'createTargAcct("' + first_name + '", "' + last_name + '")'});
                chrome.tabs.executeScript({ code: 'callLoadEmail("' + email + '", "' + supplier + '")'});
            });
        });
    } else if (supplier == 'P') {
		document.querySelector('button[id="fill-email"]').outerHTML = document.querySelector('button[id="fill-email"]').outerHTML + '<span> </span><button id="fill-warehouse">Fill STLPRO Address</button>';
        $('#fill-warehouse').on('click', function() {
			var first_name = document.querySelector('[id*="for_button"]').innerText.split('|')[2];
			var last_name = document.querySelector('[id*="for_button"]').innerText.split('|')[3];
			randomPhone();
			var dsData = 'P|000000000|' + first_name + '|' + last_name + '|1380 S KINGSHIGHWAY BLVD||SAINT LOUIS|63110|' + randomPhoneNumber + '|MO|0';
            chrome.tabs.executeScript(null, { file: "jquery.js" }, function() {});
			chrome.tabs.executeScript(null, { file: "contentscript.js" }, function() {
				chrome.tabs.executeScript({ code: 'callLoadDSAddress("' + dsData + '")'});
			});
        });
    }
	*/

  if (
    document.getElementById("picked_gift_cards") !== null &&
    document.getElementById("picked_gift_cards").innerText.indexOf("|") !== -1
  ) {
    if (
      document.querySelector('[id="picked_gift_cards"]').innerText.split("|")
        .length == 1
    ) {
      // do nothing
    } else {
      allGCs = document
        .querySelector('[id="picked_gift_cards"]')
        .innerText.split("|");
      document.querySelector('[id="picked_gift_cards"]').innerText =
        allGCs[allGCs.length - 1];

      joiner = "";
      for (var i = 0; i < allGCs.length; i++) {
        if (i == allGCs.length - 1) {
          // do nothing
        } else {
          usedGCs.innerHTML = joiner += allGCs[i] + "\n";
        }
      }
    }
  }

  $(".dsbutton").click(function () {
    var dsData = $("#for_" + this.id).text();
    var orderItemId = this.id.replace("button_", "");
    console.log("id " + orderItemId);

    localStorage["lastOrderItemId"] = orderItemId;

    var lastOrderItemId = localStorage["lastOrderItemId"];
    console.log("last order" + lastOrderItemId);
    $("#button_" + orderItemId).css("background-color", "#AACCAA");

    try {
      $.post(
        host + "/products/logorderattempt/",
        { order_item_id: orderItemId },
        (data, status, xhr) => console.log(status + " " + xhr.responseText)
      );
    } catch (ex) {
      console.log(ex);
    }
    chrome.tabs.executeScript(null, { file: "jquery.js" }, function () {});
    chrome.tabs.executeScript(null, { file: "contentscript.js" }, function () {
      chrome.tabs.executeScript({
        code: 'callLoadDSAddress("' + dsData + '")',
      });
      chrome.tabs.executeScript({
        code: 'callLoadDSNumber("' + dsOrderNumber + '")',
      });
    });
    console.log("loaded content script in tab");
  });

  $("#fill-email").on("click", function () {
    var email = $("#picked_email").text();
    chrome.tabs.executeScript(null, { file: "jquery.js" }, function () {});
    chrome.tabs.executeScript(null, { file: "contentscript.js" }, function () {
      chrome.tabs.executeScript({
        code: 'callLoadEmail("' + email + '", "' + supplier + '")',
      });
    });
  });

  $("#fill-account").on("click", function () {
    var username = $("#picked_username").text();
    var password = $("#picked_password").text();
    chrome.tabs.executeScript(null, { file: "jquery.js" }, function () {});
    chrome.tabs.executeScript(null, { file: "contentscript.js" }, function () {
      chrome.tabs.executeScript({
        code:
          'callLoadAccount("' +
          username +
          '", "' +
          password +
          '", "' +
          supplier +
          '")',
      });
    });
  });

  $("#cardUseButton").on("click", function () {
    console.log("clciked");
    var card_info = document.querySelector('[id="picked_credit_card"]')
      .defaultValue;
    card_info = card_info.replace("\n", "");
    console.log(card_info);
    //        var card_info = document.querySelector('[id="picked_credit_card"]').innerText;

    chrome.tabs.executeScript(null, { file: "jquery.js" }, function () {});
    chrome.tabs.executeScript(null, { file: "contentscript.js" }, function () {
      chrome.tabs.executeScript({
        code: 'callLoadCardInfo("' + card_info + '", "' + supplier + '")',
      });
    });
  });

  $("#accountNextButton").on("click", function () {
    chrome.storage.sync.get(
      {
        host: "admin.stlpro.com",
      },
      function (items) {
        var url =
          "https://" + items.host + "/products/getdsforchrome/next/account/";
        var req = new XMLHttpRequest();
        req.open("GET", url, true);
        //set host to dom element
        req.onload = function (e) {
          var data = JSON.parse(e.target.responseText);
          console.log("Proxy data is ", data);
          if (supplier == "B") {
            document.getElementById("picked_username").innerText =
              data["username"];
            document.getElementById("picked_password").innerText =
              data["password"];
          }
          if (supplier === "P") {
            document.getElementById("picked_username").innerText =
              data["username"];
            document.getElementById("picked_password").innerText =
              data["password"];
          }
        };
        req.send(null);
      }
    );
  });

  $("#giftCardUseButton").on("click", function () {
    gift_card_num = document.querySelector('[id="picked_gift_cards"]')
      .innerText;
    gift_card_num = gift_card_num.replace("\n", "");

    if (supplier == "T") {
      gcBypassProxy();
    }
    chrome.tabs.executeScript(null, { file: "jquery.js" }, function () {});
    chrome.tabs.executeScript(null, { file: "contentscript.js" }, function () {
      chrome.tabs.executeScript({
        code:
          'callLoadGiftCardInfo("' + gift_card_num + '", "' + supplier + '")',
      });
      chrome.tabs.executeScript({
        code: 'getGiftCardInfo("' + supplier + '")',
      });
    });
  });

  if (document.querySelector("#cardNextButton") !== null) {
    document
      .querySelector("#cardNextButton")
      .addEventListener("click", cardNext);
  }

  function gcBypassProxy() {
    proxyOff();
    setTimeout(proxyOn, 1234);
  }
}

// parse json data from python
function JSONParse(data) {
  try {
    return JSON.parse(data.replace(/u'/g, "'").replace(/'/g, '"'));
  } catch (e) {
    console.log(e);
    return {};
  }
}

const shuffle = (str) =>
  [...str]
    .reduceRight(
      (res, _, __, arr) => [
        ...res,
        arr.splice(~~(Math.random() * arr.length), 1)[0],
      ],
      []
    )
    .join("");

var randomPhoneNumber;
function randomPhone() {
  var phRNG = Math.floor(Math.random() * 100 + 1);
  var phoneNumbers = [
    "2714289343",
    "4183965741",
    "3723304471",
    "6213179384",
    "3055074179",
    "3634414996",
    "3349292467",
    "5839912824",
    "3743217971",
    "8307754262",
    "6838001586",
    "6292809548",
    "4219283927",
    "3767840797",
    "7054057576",
    "6577074199",
    "6818830306",
    "4679139582",
    "7086022565",
    "3509460083",
    "5042196351",
    "4572881205",
    "6244394581",
    "3529806681",
    "6973479676",
    "7282514244",
    "6298851507",
    "8664738469",
    "5798932827",
    "8129388944",
    "5325410665",
    "5092876681",
    "2844449511",
    "8257884593",
    "6803126969",
    "6333080020",
    "5287132484",
    "2826764195",
    "3457509629",
    "9743051058",
    "5242294843",
    "3839845483",
    "6518059455",
    "8189886865",
    "7603490752",
    "9643610903",
    "7963342782",
    "6503309836",
    "3799434736",
    "4533198113",
    "7308649856",
    "9344595669",
    "9526841157",
    "3334244130",
    "4674289022",
    "2089983839",
    "2289178070",
    "3887079660",
    "4906336021",
    "6422961121",
    "8967833419",
    "7475647035",
    "9267234421",
    "5884385142",
    "9098924141",
    "6268041490",
    "7573613946",
    "6206735229",
    "2815856923",
    "3179534564",
    "5093119125",
    "4778074927",
    "8714387082",
    "8139384913",
    "3573948707",
    "9138280470",
    "5835441579",
    "8634105023",
    "9534911382",
    "8736446756",
    "2286936662",
    "4019650419",
    "8336575107",
    "4156026709",
    "7255746278",
    "9332875001",
    "5184202324",
    "2327735021",
    "9828244838",
    "6078163844",
    "2156618480",
    "2314050426",
    "8803679200",
    "4467778307",
    "5622100439",
    "7824518999",
    "5649131478",
    "8644517939",
    "8924958263",
    "2817333957",
  ];
  var shuffleLast4 = phoneNumbers[phRNG].substr(6, 10);
  var shuffleLast4 = shuffle(shuffleLast4);
  randomPhoneNumber = phoneNumbers[phRNG].substr(0, 6) + shuffleLast4;
}
