// Enable proxy 
if (window.location.href.indexOf('admin.stlpro.com/products/getdsorders/') > -1) {
	
	isGetOrders = true;
	
	ready(function () {
		asinTitl = contains('tr','Asin Title');
		
		if (isEmpty(asinTitl) == true) {
			// do nothing
		} else {
			asinTitl[0].innerHTML = contains('tr','Asin Title')[0].innerHTML.replace(/td/g,'th');
			
			contains('tr','Asin Title')[0].outerHTML = "<tr><td><td><td><td><td><td><td><a href=javascript:null; target=_blank>Open All Items</a><td><td><td><td><td><td><td><td><td><td><td><td><td>" + contains('tr','Asin Title')[0].outerHTML;
			
			if (document.getElementById('proxyIp') === null) {
				// do nothing
			} else {
				pulledIP_webF = document.getElementById('proxyIp').value;
				pulledPort_webF = document.getElementById('proxyPort').value;
			}
			
			document.getElementById('site-name').outerHTML = '<span style="float:left">' + document.getElementById('site-name').outerHTML + '</span>';
			
			document.getElementById('branding').outerHTML = document.getElementById('branding').outerHTML + '<span style="float:right;font-size:15px"><a id="chrome-ext" target="_blank" style="text-decoration:none" href="https://chrome.google.com/webstore/detail/stl-pro-dropship-helper/lfojkfpamgfacngbdcbdagbpdohmjace">Dropship Helper Version: ' + chrome.runtime.getManifest().version + '</a></span>'
			
			var ths = document.getElementsByTagName('th');
			var trs = document.getElementsByTagName('tr');
			supplierColumn = [];
			orderStatusColumn = [];
			itemNumCol = [];
			extraItemCol = [];

			for (var i = 0; i < ths.length; i++) {
				if (ths[i].innerHTML.indexOf('Supplier') !== -1) {
					if (ths[i].innerHTML == "Supplier Price") {
						// do nothing
					} else {
						var scId = i;
						break;
					}
				}
			}

			for (var i = 0; i < trs.length; i++) {
				supplierColumn.push(trs[i].children[scId]);
			}

			for (var i = 0; i < ths.length; i++) {
				if (ths[i].innerHTML.indexOf('Order Status') !== -1) {
					var oscId = i;
					break;
				}
			}

			for (var i = 0; i < trs.length; i++) {
				orderStatusColumn.push(trs[i].children[oscId]);
			}
			
			for (var i = 0; i < ths.length; i++) {
				if (ths[i].innerHTML.indexOf('Item #') !== -1) {
					if (ths[i].innerHTML == "Supplier Price") {
						// do nothing
					} else {
						var icId = i;
						break;
					}
				}
			}

			for (var i = 0; i < trs.length; i++) {
				itemNumCol.push(trs[i].children[icId]);
			}
			
			for (var i = 0; i < ths.length; i++) {
				if (ths[i].innerHTML.indexOf('Extra Item') !== -1) {
					var extraItemId = i;
					break;
				}
			}
			for (var i = 0; i < trs.length; i++) {
				extraItemCol.push(trs[i].children[extraItemId]);
			}

			extraItemCol = extraItemCol.splice(4, extraItemCol.length -1);
			itemNumCol = itemNumCol.splice(4, itemNumCol.length -1);
			supplierColumn = supplierColumn.splice(4, supplierColumn.length -1);
			orderStatusColumn = orderStatusColumn.splice(4, orderStatusColumn.length -1);
			extraItem = extraItemCol[extraItemCol.length-1].innerText;
			
			if (supplierColumn[0].innerText.indexOf('Walmart') > -1) {
				document.querySelectorAll('td')[5].innerHTML = '<a href="https://www.walmart.com/account/login?returnUrl=%2Fcart"; target=_blank>WALMART PREPROCESSED: Sign-in & Checkout</a>';
				document.querySelectorAll('td')[6].innerHTML = '<a href="https://www.walmart.com/account/signup?returnUrl=%2Flists%2Fcreate-events-registry%3Fr%3Dyes"; target=_blank>WALMART: Open Signup & Registry</a>';
			}
			
			function clickAllItems() {
				if (document.querySelectorAll('tbody')[1].querySelectorAll('tr').length == 1 && extraItem !== "") {
					for (var i = 0; i < itemNumCol.length; i++) {
						window.open(itemNumCol[i].querySelector('a').href);
						window.open(extraItemCol[i].querySelector('a').href);
						window.focus();
					}
				} else if (document.querySelectorAll('tbody')[1].querySelectorAll('tr').length > 1 && extraItem == "" || document.querySelectorAll('tbody')[1].querySelectorAll('tr').length == 1 && extraItem == "") {
					for (var i = 0; i < itemNumCol.length; i++) {
						window.open(itemNumCol[i].querySelector('a').href);
						window.focus();
					}
				}
			}
			
			contains('a','Open All Items')[0].addEventListener('click', clickAllItems);
			
//			for (var i = 0; i < supplierColumn.length; i++) {
//				supplierColumn[i] = supplierColumn[i].innerText;
//				orderStatusColumn[i] = orderStatusColumn[i].innerText;
//			}

			for (var i = 0; i < supplierColumn.length; i++) {
				orderStatusColumn[i] = orderStatusColumn[i].innerText;
				if (supplierColumn[i].innerText.indexOf('BestBuy') > -1) {
					supplierColumn[i] = "B";
				} else if (supplierColumn[i].innerText.indexOf('Target') > -1) {
					supplierColumn[i] = "T";
				} else if (supplierColumn[i].innerText.indexOf('Walmart') > -1) {
					supplierColumn[i] = "W";
				} else if (supplierColumn[i].innerText.indexOf('Kohls') > -1) {
					supplierColumn[i] = "H";
				}
			}
			
			function isSame(el, index, arr) {
				if (index === 0){
					return true;
				}
				else {
					return (el.answer === arr[index - 1].answer);
				}
			}
			
			if (supplierColumn.every(isSame) == true) {
				mixedSuppliers = false;
			}
			
			if (orderStatusColumn.every(isSame) == true) {
				allOrdersNew = true;
			}
			
			function checkAutoDS(callback) {
				if (document.querySelector('[id="autods_alert"]') !== null) {
					console.log("AutoDS Alert Found");
					document.querySelector('[class="info"]').outerHTML = document.querySelector('[class="info"]').outerHTML + '<li id="dsh_alert" class="info"><b>Dropship Helper: Confirmed AutoDS captured needed info. Proxy has been enabled.</b></li>'
					callback && callback();
				} else {
					setTimeout(checkAutoDS, 1000, callback);
				}
			}
			
			if (document.getElementsByClassName("info")[0].innerText == "All Order Items are updated successfully" || document.getElementsByClassName("info")[0].innerText == "All items are purchased") {
				chrome.runtime.sendMessage({
					newOrderStarted: false,
					isGetOrders: isGetOrders,
				});
			}
			
			checkAutoDS(function() {
				if (document.getElementsByClassName("info")[0].innerText !== "All Order Items are updated successfully") {
					chrome.runtime.sendMessage({
						newOrderStarted: true,
						isGetOrders: isGetOrders,
						orderSupplier: supplierColumn[0],
						proxyIP: pulledIP_webF,
						proxyPort: pulledPort_webF,
					});
				}
			});
		}
	});
}

function hasNumber(myString) {
  return /\d/.test(myString);
}

function textNodesUnder(el) {
    return walkNodeTree(el, {
        inspect: n => !['STYLE', 'SCRIPT'].includes(n.nodeName),
        collect: n => (n.nodeType === 3),
        //callback: n => console.log(n.nodeName, n),
    });
}

function walkNodeTree(root, options) {
    options = options || {};

    const inspect = options.inspect || (n => true),
          collect = options.collect || (n => true);
    const walker  = document.createTreeWalker(
        root,
        NodeFilter.SHOW_ALL,
        {
            acceptNode: function(node) {
                if(!inspect(node)) { return NodeFilter.FILTER_REJECT; }
                if(!collect(node)) { return NodeFilter.FILTER_SKIP; }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );

    const nodes = []; let n;
    while(n = walker.nextNode()) {
        options.callback && options.callback(n);
        nodes.push(n);
    }

    return nodes;
}

// Ready?
function ready(callback) {
	if (document.readyState != 'loading')
		callback();
	else if (document.addEventListener)
		document.addEventListener('DOMContentLoaded', callback);
	else
		document.attachEvent('onreadystatechange', function () {
			if (document.readyState == 'complete')
				callback();
		});
}
	

// Fill Text injection
fillText = (selector, value) => {
    document.querySelector(selector).select();
    document.execCommand('insertText', false, value);
}

// Check if array is empty
function isEmpty(obj) {
    for (var key in obj) {
        if (obj.hasOwnProperty(key))
        return false;
    }
        return true;
}

// Contains function
function contains(selector, text) {
    var elements = document.querySelectorAll(selector);
    return Array.prototype.filter.call(elements, function (element) {
        return RegExp(text).test(element.textContent);
    });
}

window.callLoadDSAddress = function(flds) {
    console.log("callLoadDSAddress");
    window.loadDSAddress = loadDSAddressKohls;
    var fld = flds.split("|");
    console.log("store is: " + flds);
    // Toys R Us, KMart, or Target
    if (fld[0] == 'U') {
        window.loadDSAddress = loadDSAddressTRU;
    } else if (fld[0] == 'K') {
        window.loadDSAddress = loadDSAddressKMart;
    } else if (fld[0] == 'T') {
        window.loadDSAddress = loadDSAddressTarget;
    } else if (fld[0] == 'S') {
        window.loadDSAddress = loadDSAddressSamsClub;
    } else if (fld[0] == 'W' || fld[0] == 'Y') {
        window.loadDSAddress = loadDSAddressWalMart;
    } else if (fld[0] == 'F') {
        window.loadDSAddress = loadDSAddressFisherPrice;
    } else if (fld[0] == 'P') {
        window.loadDSAddress = loadDSAddressHomeDepot;
    } else if (fld[0] == 'L') {
        window.loadDSAddress = loadDSAddressBuyBuyBaby;
    } else if (fld[0] == 'B') {
        window.loadDSAddress = loadDSAddressBestBuy;
    } else if (fld[0] == 'H') {
        window.loadDSAddress = loadDSAddressKohls;
    }

    // only use 5 digit zip code
    if (fld[7].length > 5) {
        fld[7] = fld[7].substring(0,5);
    }

    // keep numeric characters on phone, use default phone number if empty
    fld[8] = fld[8].replace(/\D/g,'');
    if (!fld[8]) {
        fld[8] = '3146981997';
    }

    fld[9] = getCorrectState(fld[9]);

    //TODO: make this an object to be passed
    loadDSAddress(fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8], fld[9], fld[10]);
}

window._v = function(value) {
    if (value !== "")
        return value;
    return "..";
}

window.createTargAcct = function(first_name, last_name) {
    if (document.querySelector('h1').innerText == "Create account" || document.querySelector('h2').innerText == "Create account") {
        var elem = document.getElementById("username");
        elem.dispatchEvent(new Event('input', {bubbles: true}));
        elem.dispatchEvent(new Event('blur'));
        document.getElementById('firstname').select();
        document.execCommand('insertText', false, first_name);
        document.getElementById('lastname').select();
        document.execCommand('insertText', false, last_name);
        document.getElementById('password').select();
        document.execCommand('insertText', false, 'forte1long');
        document.getElementById('createAccount').click();
    }
}

window.callLoadEmail = function(email, supplier) {
    var $ = function(sel) {
        return document.querySelector(sel);
    }
    if (supplier === 'U') {
        $('input[name=orderEmail]').value = email;
    }
    else if (supplier === 'W' || supplier === 'Y') {
		if (window.location.href.indexOf('create-events-registry') > -1 && window.location.href.indexOf('account/signup') > -1) {
			fillText('[id="email-su"]', email);
			fillText('[id="password-su"]', 'forte1');
			document.querySelector('[id="su-newsletter"]').click();
		} else if (window.location.href.indexOf('/account/login') > -1) {
			fillText('[id="email"]', email);
			fillText('[id="password"]', 'forte1');
		} else {
			try {
				document.querySelector('.SignIn-container input[type=email]').select();
				document.execCommand('insertText', false, email);
			}
			catch(err) {
				document.querySelector('input[name=email]').select();
				document.execCommand('insertText', false, email);
			}
		}
    }
    else if (supplier === 'P') {
		if (document.querySelector('[id="guestLoginValue"]') !== null) {
			document.querySelector('[id="guestLoginValue"]').select();
			document.execCommand('insertText', false, email);
		} else if (document.querySelector('[id="emailInput"]') !== null) {
			document.querySelector('[id="emailInput"]').select();
			document.execCommand('insertText', false, email);
		} else {
			document.querySelector('[name="guestEmail"]').select();
			document.execCommand('insertText', false, email);
		}
    }
    else if (supplier === 'T') {
        $('#username').value = email;
        var elem = document.getElementById("username");
        elem.dispatchEvent(new Event('input', {bubbles: true}));
        elem.dispatchEvent(new Event('blur'));
    }
    else if (supplier === 'K') {
        $('#guestEmail').value = email;
    }
    else if (supplier === 'L') {
        fillText('input[name=email]', email);
        fillText('input[name=emailConfirm]', email);
    }
    else if (supplier === 'B') {
        fillText = (selector, value) => {
            document.querySelector(selector).select();
            document.execCommand('insertText', false, value);
        }
        var selector = '[id="user.emailAddress"]';
        fillText(selector, email);
    }
    else if (supplier === 'H') {
        fillText = (selector, value) => {
            document.querySelector(selector).select();
            document.execCommand('insertText', false, value);
        }
		var selector1 = '[id="email"]';
        var selector2 = '[id="email-confirm"]';
        fillText(selector1, email);
		fillText(selector2, email);
    }
}


window.callLoadCardInfo = function(card_info, supplier) {
    
    var $ = function(sel) {
        return document.querySelector(sel);
    };
    if (supplier === 'P') {
        
        console.log(card_info);
        
        ccArray = card_info.split('|');
        ccExp = ccArray[9].split('/');
        
        fillText('[id="cardNumber"]', ccArray[7]);
        fillText('[id="cvv"]', ccArray[8]);
        document.querySelector('[id="ccMonth"]').querySelector('option[label^="' + ccExp[0] + '"]').selected = true;
        document.querySelector('[id="ccMonth"]').querySelector('option[label^="' + ccExp[0] + '"]').dispatchEvent(new Event('change'));
        document.querySelector('[id="ccMonth"]').dispatchEvent(new Event('change'));
        document.querySelector('[id="ccYear"]').querySelector('option[label^="' + ccExp[1] + '"]').selected = true;
        document.querySelector('[id="ccYear"]').querySelector('option[label^="' + ccExp[1] + '"]').dispatchEvent(new Event('change'));
        document.querySelector('[id="ccYear"]').dispatchEvent(new Event('change'));
        
        if (document.querySelector('input[name="emailCustomSubscribed"]') !== null) {
            if (document.querySelector('input[name="emailCustomSubscribed"]').checked == true) {
                document.querySelector('input[name="emailCustomSubscribed"]').click();
            }
        }
        
    }
};

window.callLoadGiftCardInfo = function(gift_card_num, supplier) {
    
    var $ = function(sel) {
        return document.querySelector(sel);
    };
    if (supplier == 'B') {
        
        console.log(gift_card_num);
        
        gcArray = gift_card_num.split(',');
		
		if (document.querySelector('[data-track="gift-promo-code-link"]') !== null) {
			function bbyApply() {
				document.querySelector('[class="gift-promo-cards__apply-btn btn btn-outline"]').click();
			}
			
			document.querySelector('[data-track="gift-promo-code-link"]').click();
			
			setTimeout(function () {
				bbyCode = document.getElementById("promotionCode");
				bbyPIN = document.getElementById("payment.giftCard.pin");
				
				fillText('[id="promotionCode"]', gcArray[0]);
				fillText('[id="payment.giftCard.pin"]', gcArray[1]);
				
				bbyCode.selected = true;
				bbyCode.dispatchEvent(new Event('change'));
				bbyPIN.selected = true;
				bbyPIN.dispatchEvent(new Event('change'));
				
				setTimeout(bbyApply, 100);
				
				console.log(gcArray);
			}, 1000);
		} else {
			if (document.querySelector('[class="gift-promo-cards"]') !== null) {
				if (document.querySelector('[id="promotionCode"]') !== null) {
					bbyCode = document.getElementById("promotionCode");
					fillText('[id="promotionCode"]', gcArray[0]);
				} else {
					bbyCode = document.getElementById("payment.giftCard.code");
					fillText('[id="payment.giftCard.code"]', gcArray[0]);
				}
			} else {
				bbyCode = document.getElementById("payment.giftCard.code");
				fillText('[id="payment.giftCard.code"]', gcArray[0]);
			}
			
			bbyPIN = document.getElementById("payment.giftCard.pin");
			fillText('[id="payment.giftCard.pin"]', gcArray[1]);

			bbyCode.selected = true;
			bbyCode.dispatchEvent(new Event('change'));
			bbyPIN.selected = true;
			bbyPIN.dispatchEvent(new Event('change'));
			
			setTimeout(function () {
				if (document.querySelector('[class="gift-promo-cards__apply-btn btn btn-outline"]') !== null) {
					document.querySelector('[class="gift-promo-cards__apply-btn btn btn-outline"]').click();
				} else {
					document.querySelector('[class="gift-cards__apply-btn btn btn-outline"]').click();
				}
			}, 100);
			
			console.log(gcArray);
		}
    }
	
	if (supplier == "H") {
		
		console.log(gift_card_num);
		
		gcArray = gift_card_num.split(',');
		
		fillText('[id="gift_card_number"]', gcArray[0]);
		fillText('[id="gift_card_pin_code"]', gcArray[1]);
		
		setTimeout(function() {document.querySelector('[class="applyGiftCard"]').click();}, 200);
		
	}
	
    if (supplier == 'P') {
        
        console.log(gift_card_num);
        
        gcArray = gift_card_num.split(',');
		
		if (document.querySelectorAll('[id="giftCardNumber"]').length == 0) {
			document.querySelector('[ng-click="toggleGiftCard()"]').click();
			setTimeout(function() { fillHDGC(); }, 789);
		} else {
			fillHDGC();
		}
        
		function fillHDGC() {
			if (document.getElementById('giftCardNumber').value !== '') {
				fillText('[id="giftCardNumber"]', '');
				fillText('[id="pin"]', '');
				fillText('[id="giftCardNumber"]', gcArray[0]);
				fillText('[id="pin"]', gcArray[1]);
			} else {
				fillText('[id="giftCardNumber"]', gcArray[0]);
				fillText('[id="pin"]', gcArray[1]);
			}
		}
    }
    
    if (supplier == 'T') {
        
        console.log(gift_card_num);
        
        gcArray = gift_card_num.split(',');
        
        if (document.querySelector('[id="giftCardNumberInput"]').value !== '') {
            fillText('[id="giftCardNumberInput"]', '');
            fillText('[id="giftCardAccessNumberInput"]', '');
            fillText('[id="giftCardNumberInput"]', gcArray[0]);
            fillText('[id="giftCardAccessNumberInput"]', gcArray[1]);
        } else {
            fillText('[id="giftCardNumberInput"]', gcArray[0]);
            fillText('[id="giftCardAccessNumberInput"]', gcArray[1]);
        }
    }
	
    if (supplier == 'K') {
        
        console.log(gift_card_num);
        
        gcArray = gift_card_num.split(',');
        
        if (document.querySelector('[id="giftCardNum"]').value !== '') {
            fillText('[id="giftCardNum"]', '');
            fillText('[id="giftCardPin"]', '');
            fillText('[id="giftCardNum"]', gcArray[0]);
            fillText('[id="giftCardPin"]', gcArray[1]);
			document.querySelector('[id="giftCardNum"]').select();
        } else {
            fillText('[id="giftCardNum"]', gcArray[0]);
            fillText('[id="giftCardPin"]', gcArray[1]);
			document.querySelector('[id="giftCardNum"]').select();
        }
		
		setTimeout(function() {contains('[class="shc-btn"]','Apply')[0].click();}, 200);
    }
};

window.getSupplierSiteTotal = function(supplier) {
    if (supplier == 'T') {
		order_total = contains('span[class="h-text-lg h-text-bold"]','Total')[0].parentElement.lastChild.innerText.replace(/[^0-9.]/g, "");

		// Pass info to popup.js
		chrome.runtime.sendMessage({
			totalGrabbed: true,
			order_total: order_total,
		});    
    }
	
    if (supplier == 'K') {
		order_total = document.querySelector('[ng-bind-html="ordersummary.totalDue | price:true"]').innerText.replace(/[^0-9.]/g, "");

		// Pass info to popup.js
		chrome.runtime.sendMessage({
			totalGrabbed: true,
			order_total: order_total,
		});    
    }
    
    if (supplier == 'P') {
		order_total = document.querySelectorAll('[ng-if="order.orderAmount"]')[1].querySelector('[class="price__format"]').parentElement;
		order_total = textNodesUnder(order_total)[1].textContent + '.' + textNodesUnder(order_total)[2].textContent;
		order_total = +order_total;
		console.log(order_total);

		// Pass info to popup.js
		chrome.runtime.sendMessage({
			totalGrabbed: true,
			order_total: order_total,
		});    
    }
	
    if (supplier === 'B') {
		order_summary = document.querySelectorAll('[class="order-summary-card__total-line"]');
		bby_subtotal = order_summary[0].lastChild.innerText.replace(/[^0-9.]/g, "");
		bby_shipping = order_summary[1].lastChild.innerText.replace(/[^0-9.]/g, "");
		bby_tax = order_summary[2].lastChild.innerText.replace(/[^0-9.]/g, "");
		order_total = +document.querySelector('[class="order-summary__total"]').innerText.replace(/[^0-9.]/g, '');
		order_total = Math.round(order_total * 100) / 100;
		
		// Pass info to popup.js
		chrome.runtime.sendMessage({
			totalGrabbed: true,
			order_total: order_total
		});
    }
	
    if (supplier === 'H') {
		order_total = document.getElementById('totalcharges').innerText.replace('$','');
		
		// Pass info to popup.js
		chrome.runtime.sendMessage({
			totalGrabbed: true,
			order_total: order_total
		});
    }
};
	

window.getGiftCardInfo = function(supplier) {
    if (supplier == 'T') {
        function targGC() {
            // Check that needed element exists before grabbing info
            function targ_DOMCheck() {
                target_gc_used = contains('span', 'applied from');
                if (isEmpty(target_gc_used) == true) {
                    // If element doesn't exist, try again
                    setTimeout(targ_DOMCheck, 100);
                } else {
                    if (document.getElementById('totalGCs') !== null && target_gc_used.length == +document.getElementById('totalGCs').innerText) {
                        // Button has been clicked again, wait for additional element and try again
                        setTimeout(targ_DOMCheck, 100);
                        return;
                    } else {
                        // Element exists, begin grabbing info
                        totalGCs = target_gc_used.length;
                        
                        if (document.getElementById('totalGCs') === null) {
                            var gcNum = document.createElement('div');
                            gcNum.id = "totalGCs";
                            gcNum.innerHTML = totalGCs;
                            document.head.appendChild(gcNum);
                        } else {
                            document.getElementById('totalGCs').innerHTML = totalGCs;
                        }

                        gc_applied_info = [];

                        for (var i = 0; i < totalGCs; i++) {
                            gc_applied_info[i] = target_gc_used[i].innerText.search('applied');
                            gc_applied_info[i] = target_gc_used[i].innerText.substr(1, gc_applied_info[i] - 2);
                            gc_last_four = target_gc_used[i].innerText.search('from');
                            gc_last_four = target_gc_used[i].innerText.substr(gc_last_four + 5, 8).replace(/\*/g,'');
                            gc_applied_info[i] = gc_applied_info[i] + '||' + gc_last_four;
                            gc_applied_info[i] = gc_applied_info[i].split('||');
                        }

                        //gc_total = contains('span[class="h-text-bs h-text-bold"]','Total giftcards')[0].parentElement.lastChild.innerText.replace('\n','').replace(/[^0-9.]/g, "");

                        // Pass info to popup.js
                        chrome.runtime.sendMessage({
                            infoGrabbed: true,
                            gc_applied_info: gc_applied_info,
                            gc_length: totalGCs
                        });
						if (document.querySelectorAll('[class="h-padding-a-tight h-margin-l-tiny h-text-bs h-display-inline-block h-text-black"]')[2].innerText == "3 of 6 | Order pickup info") {
//							setTimeout(ccTrick1, 1000);
						}
                    }
                }
            }
            targ_DOMCheck();
        }
        targGC();
    }

	if (supplier == 'P') {
		function hdGC() {
			// Check that needed element exists before grabbing info
			function hd_DOMCheck() {
				hd_gc_used = document.querySelectorAll('[ng-repeat="giftCard in user.giftCards"]');
				if (isEmpty(hd_gc_used) == true) {
					// If element doesn't exist, try again
					setTimeout(hd_DOMCheck, 100);
				} else {
					if (document.getElementById('totalGCs') !== null && hd_gc_used.length == +document.getElementById('totalGCs').innerText) {
						// Button has been clicked again, wait for additional element and try again
						setTimeout(hd_DOMCheck, 100);
						return;
					} else {
						// Element exists, begin grabbing info
						totalGCs = hd_gc_used.length;

						if (document.getElementById('totalGCs') === null) {
							var gcNum = document.createElement('div');
							gcNum.id = "totalGCs";
							gcNum.innerHTML = totalGCs;
							document.head.appendChild(gcNum);
						} else {
							document.getElementById('totalGCs').innerHTML = totalGCs;
						}
						
						// If the arrays for remaining balance and applied info doesn't exist, create them
						if (typeof prevHdRemaining == "undefined") {
							gc_applied_info = [];
							prevHdRemaining = [];
						}
						
						hdTotal = document.querySelectorAll('[ng-if="order.orderAmount"]')[1].querySelector('[class="price__format"]').parentElement;
						hdTotal = textNodesUnder(hdTotal)[1].textContent + '.' + textNodesUnder(hdTotal)[2].textContent;
						hdTotal = +hdTotal;
						
						// Grab info for first gift card
						if (isEmpty(prevHdRemaining) == true) {
							if (isEmpty(contains('[ng-if="!paymentCard.cardNumber && !paymentCard.profileOrderId"][class="alert-inline__message ng-scope"]', 'Please provide an additional')) == false) {
								hdRemaining = +contains('[ng-if="!paymentCard.cardNumber && !paymentCard.profileOrderId"][class="alert-inline__message ng-scope"]', 'Please provide an additional')[0].children[0].innerText.replace('$','');
								hdGcUsed = +hdTotal - +hdRemaining;
								prevHdRemaining[0] = hdRemaining;
								gc_applied_info[0] = hdGcUsed + '||' + hd_gc_used[0].innerText.replace('Remove','').replace('****','').replace('PIN: ',',').replace('	','').trim();
								gc_applied_info[0] = gc_applied_info[0].split('||');
							} else if (isEmpty(contains('[ng-if="!paymentCard.cardNumber && !paymentCard.profileOrderId"][class="alert-inline__message ng-scope"]', 'Please provide an additional')) == true) {
								hdGcUsed = +hdTotal;
								gc_applied_info[0] = hdGcUsed + '||' + hd_gc_used[0].innerText.replace('Remove','').replace('****','').replace('PIN: ',',').replace('	','').trim();
								gc_applied_info[0] = gc_applied_info[0].split('||');
							}
						// Grab info for any gift cards after the first one
						} else if (hdRemaining !== prevHdRemaining[totalGCs-1] && isEmpty(document.querySelectorAll('[ng-if="!paymentCard.cardNumber && !paymentCard.profileOrderId"][class="alert-inline__message ng-scope"]')) == false) {
							hdRemaining = +contains('[ng-if="!paymentCard.cardNumber && !paymentCard.profileOrderId"][class="alert-inline__message ng-scope"]', 'Please provide an additional')[0].children[0].innerText.replace('$','');
							hdGcUsed = Math.round((prevHdRemaining[totalGCs-2] - hdRemaining) * 100) / 100;
							prevHdRemaining[totalGCs-1] = hdRemaining;
							gc_applied_info[totalGCs-1] = hdGcUsed + '||' + hd_gc_used[totalGCs-1].innerText.replace('Remove','').replace('****','').replace('PIN: ',',').replace('	','').trim();
							gc_applied_info[totalGCs-1] = gc_applied_info[totalGCs-1].split('||');
						// Grab info for last gift card.
						} else if (isEmpty(document.querySelectorAll('[ng-show="!paymentCard.giftCardRemoved"][class="alert-inline__message"]')) == false) {
							hdGcUsed = prevHdRemaining[totalGCs-2];
							gc_applied_info[totalGCs-1] = hdGcUsed + '||' + hd_gc_used[totalGCs-1].innerText.replace('Remove','').replace('****','').replace('PIN: ',',').replace('	','').trim();
							gc_applied_info[totalGCs-1] = gc_applied_info[totalGCs-1].split('||');
						}

						// Pass info to popup.js
						chrome.runtime.sendMessage({
							infoGrabbed: true,
							gc_applied_info: gc_applied_info,
							gc_length: totalGCs
						});
					}
				}
			}
			hd_DOMCheck();
		}
		hdGC();
	}
    
    if (supplier === 'B') {
        // Gift card info grabber
        function bbyGC() {
            // Check that needed element exists before grabbing info
            function bby_DOMCheck() {
                bby_gc_used = document.querySelectorAll('[class="alternate-payment clearfix"]');
                if (isEmpty(bby_gc_used) == true) {
                    // If element doesn't exist, try again
                    setTimeout(bby_DOMCheck, 100);
                } else {
                    if (document.getElementById('totalGCs') !== null && bby_gc_used.length == +document.getElementById('totalGCs').innerText) {
                        // Button has been clicked again, wait for additional element and try again
                        setTimeout(bby_DOMCheck, 100);
                        return;
                    } else {
                        // Element exists, begin grabbing info
                        totalGCs = bby_gc_used.length;
                        
                        if (document.getElementById('totalGCs') === null) {
                            var gcNum = document.createElement('div');
                            gcNum.id = "totalGCs";
                            gcNum.innerHTML = totalGCs;
                            document.head.appendChild(gcNum);
                        } else {
                            document.getElementById('totalGCs').innerHTML = totalGCs;
                        }
                        
                        gc_applied_info = [];
						
                        for (var i = 0; i < totalGCs; i++) {
							if (document.querySelector('[id="GiftcardEmptyModal"]') !== null && i == totalGCs - 1) {
								console.log('Empty gift card found');
								gc_applied_info[i] = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').innerText.search('\n');
								gc_applied_info[i] = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').innerText.substr(1, gc_applied_info[i] - 1);
								gc_last_four = bby_gc_used[i].querySelector('[class="alternate-payment__details"]').innerText.replace(/[^0-9.]/g, "");
								gc_last_four = gc_last_four.substr(gc_last_four.length - 4, 4);
								gc_applied_info[i] = gc_applied_info[i] + '||' + gc_last_four;
								gc_applied_info[i] = gc_applied_info[i].split('||');
								
								if (i == totalGCs) {
									totalGCs = totalGCs - 1;
									gc_total_remaining = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').querySelector('[class="alternate-payment__subprice"]').innerText.search('left');
									gc_total_remaining = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').querySelector('[class="alternate-payment__subprice"]').innerText.substr(2, gc_total_remaining - 3);
									gc_applied_info[i][2] = gc_total_remaining;
								} else {
									totalGCs = totalGCs - 1;
									gc_applied_info[i][2] = '0.00';
								}
							} else {
								gc_applied_info[i] = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').innerText.search('\n');
								gc_applied_info[i] = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').innerText.substr(1, gc_applied_info[i] - 1);
								gc_last_four = bby_gc_used[i].querySelector('[class="alternate-payment__details"]').innerText.search('\n');
								gc_last_four = bby_gc_used[i].querySelector('[class="alternate-payment__details"]').innerText.substr(gc_last_four + 1, 8).replace(/[^0-9.]/g, "");
								gc_applied_info[i] = gc_applied_info[i] + '||' + gc_last_four;
								gc_applied_info[i] = gc_applied_info[i].split('||');
								
								if (i == totalGCs) {
									gc_total_remaining = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').querySelector('[class="alternate-payment__subprice"]').innerText.search('left');
									gc_total_remaining = bby_gc_used[i].querySelector('[class="alternate-payment__actions"]').querySelector('[class="alternate-payment__subprice"]').innerText.substr(2, gc_total_remaining - 3);
									gc_applied_info[i][2] = gc_total_remaining;
								} else {
									gc_applied_info[i][2] = '0.00';
								}
							}
                        }
                        
                        var text = "";
                        var totalSum = 0;
                        for (var i = 0; i < totalGCs; i++) {
                            gc_total = totalSum += +gc_applied_info[i][0];
                        }
                        gc_total = text += gc_total;
						
                        // Pass info to popup.js
                        chrome.runtime.sendMessage({
                            infoGrabbed: true,
                            gc_applied_info: gc_applied_info,
                            gc_total: gc_total,
                            gc_length: totalGCs,
                        });
                        
                    }
                }
            }
            bby_DOMCheck();
        }
        bbyGC();
    }
	
    if (supplier == 'H') {
        function kohlsGC() {
            // Check that needed element exists before grabbing info
            function kohls_DOMCheck() {
                kohls_gc_used = document.querySelectorAll('[class="card_number"]');
                if (isEmpty(kohls_gc_used) == true) {
                    // If element doesn't exist, try again
                    setTimeout(kohls_DOMCheck, 100);
                } else {
                    if (document.getElementById('totalGCs') !== null && kohls_gc_used.length == +document.getElementById('totalGCs').innerText) {
                        // Button has been clicked again, wait for additional element and try again
                        setTimeout(kohls_DOMCheck, 100);
                        return;
                    } else {
                        // Element exists, begin grabbing info
                        totalGCs = kohls_gc_used.length;
                        
                        if (document.getElementById('totalGCs') === null) {
                            var gcNum = document.createElement('div');
                            gcNum.id = "totalGCs";
                            gcNum.innerHTML = totalGCs;
                            document.head.appendChild(gcNum);
                        } else {
                            document.getElementById('totalGCs').innerHTML = totalGCs;
                        }

                        gc_applied_info = [];

                        for (var i = 0; i < totalGCs; i++) {
							if (document.querySelector('[id="amnt_applied_confirm"]').children[i].children[0].innerText.trim().indexOf('Gift Cardx') > -1) {
								gc_applied_info[i] = document.querySelector('[id="amnt_applied_confirm"]').children[i].children[1].innerText.trim().replace('$','');
							}
                            gc_last_four = document.querySelector('[id="amnt_applied_confirm"]').children[i].children[0].innerText.trim().split('Gift Cardx')[1];
                            gc_applied_info[i] = gc_applied_info[i] + '||' + gc_last_four;
                            gc_applied_info[i] = gc_applied_info[i].split('||');
                        }

                        //gc_total = contains('span[class="h-text-bs h-text-bold"]','Total giftcards')[0].parentElement.lastChild.innerText.replace('\n','').replace(/[^0-9.]/g, "");

                        // Pass info to popup.js
                        chrome.runtime.sendMessage({
                            infoGrabbed: true,
                            gc_applied_info: gc_applied_info,
                            gc_length: totalGCs
                        });
						if (document.querySelectorAll('[class="h-padding-a-tight h-margin-l-tiny h-text-bs h-display-inline-block h-text-black"]')[2].innerText == "3 of 6 | Order pickup info") {
//							setTimeout(ccTrick1, 1000);
						}
                    }
                }
            }
            kohls_DOMCheck();
        }
        kohlsGC();
    }
};


window.callLoadAccount = function(username, password, supplier) {
    var $ = function(sel) {
        return document.querySelector(sel);
    }

    if (supplier === 'W' || supplier === 'Y') {
        fillText = (selector, value) => {
            document.querySelector(selector).select();
            document.execCommand('insertText', false, value);
        }
        try {
            fillText('.SignIn-container input[type=email]', username);
            fillText('.SignIn-container input[type=password]', password);
        }
        catch(err) {
            fillText('input[name=email]', username);
            fillText('input[name=password]', password);
        }
    }
}

window.dsUSStates = function() {
    return [
        { name: 'ALABAMA', abbreviation: 'AL'},
        { name: 'ALASKA', abbreviation: 'AK'},
        { name: 'AMERICAN SAMOA', abbreviation: 'AS'},
        { name: 'ARIZONA', abbreviation: 'AZ'},
        { name: 'ARKANSAS', abbreviation: 'AR'},
        { name: 'CALIFORNIA', abbreviation: 'CA'},
        { name: 'COLORADO', abbreviation: 'CO'},
        { name: 'CONNECTICUT', abbreviation: 'CT'},
        { name: 'DELAWARE', abbreviation: 'DE'},
        { name: 'DISTRICT OF COLUMBIA', abbreviation: 'DC'},
        { name: 'FEDERATED STATES OF MICRONESIA', abbreviation: 'FM'},
        { name: 'FLORIDA', abbreviation: 'FL'},
        { name: 'GEORGIA', abbreviation: 'GA'},
        { name: 'GUAM', abbreviation: 'GU'},
        { name: 'HAWAII', abbreviation: 'HI'},
        { name: 'IDAHO', abbreviation: 'ID'},
        { name: 'ILLINOIS', abbreviation: 'IL'},
        { name: 'INDIANA', abbreviation: 'IN'},
        { name: 'IOWA', abbreviation: 'IA'},
        { name: 'KANSAS', abbreviation: 'KS'},
        { name: 'KENTUCKY', abbreviation: 'KY'},
        { name: 'LOUISIANA', abbreviation: 'LA'},
        { name: 'MAINE', abbreviation: 'ME'},
        { name: 'MARSHALL ISLANDS', abbreviation: 'MH'},
        { name: 'MARYLAND', abbreviation: 'MD'},
        { name: 'MASSACHUSETTS', abbreviation: 'MA'},
        { name: 'MICHIGAN', abbreviation: 'MI'},
        { name: 'MINNESOTA', abbreviation: 'MN'},
        { name: 'MISSISSIPPI', abbreviation: 'MS'},
        { name: 'MISSOURI', abbreviation: 'MO'},
        { name: 'MONTANA', abbreviation: 'MT'},
        { name: 'NEBRASKA', abbreviation: 'NE'},
        { name: 'NEVADA', abbreviation: 'NV'},
        { name: 'NEW HAMPSHIRE', abbreviation: 'NH'},
        { name: 'NEW JERSEY', abbreviation: 'NJ'},
        { name: 'NEW MEXICO', abbreviation: 'NM'},
        { name: 'NEW YORK', abbreviation: 'NY'},
        { name: 'NORTH CAROLINA', abbreviation: 'NC'},
        { name: 'NORTH DAKOTA', abbreviation: 'ND'},
        { name: 'NORTHERN MARIANA ISLANDS', abbreviation: 'MP'},
        { name: 'OHIO', abbreviation: 'OH'},
        { name: 'OKLAHOMA', abbreviation: 'OK'},
        { name: 'OREGON', abbreviation: 'OR'},
        { name: 'PALAU', abbreviation: 'PW'},
        { name: 'PENNSYLVANIA', abbreviation: 'PA'},
        { name: 'PUERTO RICO', abbreviation: 'PR'},
        { name: 'RHODE ISLAND', abbreviation: 'RI'},
        { name: 'SOUTH CAROLINA', abbreviation: 'SC'},
        { name: 'SOUTH DAKOTA', abbreviation: 'SD'},
        { name: 'TENNESSEE', abbreviation: 'TN'},
        { name: 'TEXAS', abbreviation: 'TX'},
        { name: 'UTAH', abbreviation: 'UT'},
        { name: 'VERMONT', abbreviation: 'VT'},
        { name: 'VIRGIN ISLANDS', abbreviation: 'VI'},
        { name: 'VIRGINIA', abbreviation: 'VA'},
        { name: 'WASHINGTON', abbreviation: 'WA'},
        { name: 'WEST VIRGINIA', abbreviation: 'WV'},
        { name: 'WISCONSIN', abbreviation: 'WI'},
        { name: 'WYOMING', abbreviation: 'WY' }
    ];
}

window.getCorrectState = function(state) {
    var usStates = dsUSStates();

    var stateMap = {};
    for(var i = 0; i < usStates.length; i++)
        stateMap[usStates[i].name] = usStates[i].abbreviation;

    state = state.replace('.','').toUpperCase();
    if(state.length > 2)
        state = stateMap[state];
    return state;
}

// TRU
window.loadDSAddressTRU = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    var $ = function(sel) {
        return document.querySelectorAll(sel);
    }

    // load the shipping address info
    NodeList.prototype.val = function(input) {
        for(var i = 0; i < this.length; i++) {
            if (this[i].value == "") {
                this[i].value = input;
            }
        }
    }

    fname = fname.replace(/-/g, "");
    lname = lname.replace(/-/g, "");

    // load the shipping address info
    $('input[name=nickname]').val(_v(lname));
    $('input[name=firstName]').val(_v(fname));
    $('input[name=lastName]').val(_v(lname));
    $('input[name=address1]').val(_v(add1));
    if(add2) {
        $('input[name=address2]').val(add2);
    }
    $('input[name=city]').val(_v(city));
    $('input[name=postalCode]').val(_v(zip));
    $('input[name=phoneNumber]').val(_v(phone));
    $('select[name=state]').val(_v(state));
    if (_v(phone) == '..') {
        $('input[name=phoneNumber]').val('3146981997');
    }
};

// KMart (jQuery is present on the page)
window.loadDSAddressKMart = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    var $ = function(sel) {
        return document.querySelector(sel);
    }

    HTMLInputElement.prototype.val = function(input) {
        this.value = input;
    }
    // load the shipping address info
    $("div.address-layer input[name=firstName]").val(_v(fname));
    $("div.address-layer input[name=lastName]").val(_v(lname));
    $("div.address-layer input[name=address1]").val(add1);
    $("input[name=phone1]").val(_v(phone.replace(/\D/g,'')));
    $("div.address-layer input[name=zipCode]").val(_v(zip));
    if ($("input[name=city]")) {
        $("input[name=city]").val(_v(city));
    }
    setTimeout(function() {
        var cityInput = $('#shipCitySelect');
        for(var i = 0; i < cityInput.childElementCount; i++) {
            if (cityInput[i].label == city.toUpperCase()) {
                cityInput.selectedIndex = i;
            }
        }
        var stateInput = $('#shipState');
        for(var i = 0; i < stateInput.childElementCount; i++) {
            if (stateInput[i].label == dsUSStates[state]) {
                stateInput.selectedIndex = i;
            }
        }
    }, 1000)
    // dispatch change event
    var event = new Event("change");
    var elem = document.getElementById("addressZipInput");
    elem.dispatchEvent(event);
    var selectors  = ["firstName", "lastName", "address1", "address2", "zipCode", "phone1"];
    for(var i = 0; i < selectors.length; i++) {
        var el = document.querySelector("div.address-layer input[name=" + selectors[i] + "]");
        el.dispatchEvent(event);
    }
};

// Target
window.loadDSAddressTarget = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
	
	if (window.location.href.indexOf('co-delivery') > -1 && document.querySelector('[data-test="line2-text"]').placeholder === undefined) {
		if (add2 !== '') {
			if (hasNumber(add1) == false) {
				add1 = [add2, add2 = add1][0];
			}
			document.querySelector('[data-test="line2-text"]').click();
		}
	}

    var full_name = fname + ' ' + lname;
	
	if (add2 !== '') {
		var selectors = [
			'fullName', 'line1', 'line2', 'zipCode', 'city', 'USPhone',
		];

		var values = [
			_v(full_name), _v(add1), _v(add2), _v(zip), _v(city), _v(phone)
		];
	} else {
		var selectors = [
			'fullName', 'line1', 'zipCode', 'city', 'USPhone',
		];

		var values = [
			_v(full_name), _v(add1), _v(zip), _v(city), _v(phone)
		];
	}
	
	
    for (var i = 0; i < selectors.length; i++) {
        var selector = 'input[name=' + selectors[i] + ']';
        var el;
        el = document.querySelector(selector);
        el.value = values[i];
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('blur'));
    }

    var el = document.querySelector('select[name=state]');
    el.value = state;
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('blur'));
};

// loadDSAddressSamsClub("Joe", "Boxer", "123 Elm", "apt B", "Miami", "20200", "900-555-9090", "FL");
window.loadDSAddressSamsClub = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    phone = phone || "";
    var $ = function(sel) {
        return document.querySelector(sel);
    }
    // load the shipping address info
    HTMLInputElement.prototype.val = function(input) {
        this.value = input;
    }

    $('#fName-add').val(_v(fname));
    $('#lName-add').val(_v(lname));
    $('#stAdd-add').val(_v(add1));
    $('#add2-add').val(add2);
    $('#zip-add').val(_v(zip));
    $('#city-add').val(_v(city));
    $('#full_phone_num-add').val(phone);
    $('#state-dropdown-add').val(_v(state));

    // These below lines do not work
    // $('#applyDefaultShippingGroup').prop('checked', false);
    // $('#states span').html(_v(state));

    document.getElementsByClassName('selected pull-left')[0].innerHTML = _v(state);
    document.getElementById("applyDefaultShippingGroup").checked = false;
    // document.getElementById("state-dropdown-add").value = _v(state);
};

// WalMart
// loadDSAddressWalMart('Joel', 'Smithy', '234 King St.', '', 'Zhantilly', '22033', '703-456-7890', 'Virginia')
window.loadDSAddressWalMart = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    // These two lines represent the most important change.  The initEvent()
    // call had me running in circles for ages until I started reading about
    // how ReactJS uses a Virtual DOM.  A comment somebody made on one of the
    // articles about React not responding to certain events clued me in that
    // the event needs to be told to propagate up through its parents.  Without
    // that addition to the event the form elements were not validating.
	
	if (window.location.href.indexOf('create-events-registry') > -1 && window.location.href.indexOf('account/signup') > -1) {
		fillText('[id="first-name-su"]', fname);
		fillText('[id="last-name-su"]', lname);
	} else if (window.location.href.indexOf('/lists/create-events-registry') > -1 || window.location.href.indexOf('/payment') > -1) {
		
		if (window.location.href.indexOf('/lists/create-events-registry') > -1) {
			// Choose date weeks out
			document.querySelector('button[class*="LNR-EventDate-Button"]').click();
			if (document.querySelector('[class*="dp-current"]').parentElement.nextElementSibling.nextElementSibling !== null) {
				document.querySelector('[class*="dp-current"]').parentElement.nextElementSibling.nextElementSibling.children[3].click();
			} else {
				document.querySelector('[class="dp-next-nav dp-nav-cell dp-cell"]').click();
				document.querySelectorAll('[class="dp-week dp-row"]')[2].children[3].click();
			}
			
			// Choose state part 1
			document.querySelector('[id="regstate"]').dispatchEvent(new Event('focus'));
			document.querySelector('[id="regstate"]').value = state;
			document.querySelector('[id="regstate"]').dispatchEvent(new Event('input', {bubbles: true}));
			document.querySelector('[id="regstate"]').dispatchEvent(new Event('change', {bubbles: true}));
			document.querySelector('[id="regstate"]').dispatchEvent(new Event('blur'));
		}
		
		fillText('[id="firstName"]', fname);
		fillText('[id="lastName"]', lname);
		fillText('[id="addressLineOne"]', add1);
		fillText('[id="addressLineTwo"]', add2);
		fillText('[id="city"]', city);
		fillText('[id="postalCode"]', zip);
		
		// Choose state part 1
		document.querySelector('[id="state"]').dispatchEvent(new Event('focus'));
		document.querySelector('[id="state"]').value = state;
		document.querySelector('[id="state"]').dispatchEvent(new Event('input', {bubbles: true}));
		document.querySelector('[id="state"]').dispatchEvent(new Event('change', {bubbles: true}));
		document.querySelector('[id="state"]').dispatchEvent(new Event('blur'));
		
		// The phone element on the registry page requires a special kind of input. For some
		// reason it does not work correctly to run it here, but injecting the phone number 
		// as a variable and then executing javascript on the page works.
		var gotPhone = 'var custPhone = "' + phone.replace(/-/g, '') + '"';
		var phoneTag = document.createElement("script");
		phoneTag.innerHTML = gotPhone;
		document.head.appendChild(phoneTag);
		
		window.location.href = `javascript:
		document.querySelector('[id="phone"]').dispatchEvent(new Event('focus'));
		document.querySelector('[id="phone"]').value = custPhone;
		document.querySelector('[id="phone"]').dispatchEvent(new Event('input', {bubbles: true}));
		document.querySelector('[id="phone"]').dispatchEvent(new Event('change', {bubbles: true}));
		document.querySelector('[id="phone"]').dispatchEvent(new Event('blur'));`
		
	} else {
		var e = new Event("Event");
		e.initEvent("input", true, true);

		// Most of these are the same.  The zipcode entry changed from ..ZipCode to
		// just ..Zip.
		var selectors = [
			"COAC2ShpAddrFirstName", "COAC2ShpAddrLastName", "COAC2ShpAddrAddress1",
			"COAC2ShpAddrAddress2", "COAC2ShpAddrCity", "COAC2ShpAddrZip",
			"COAC2ShpAddrPhone",
		];

		var values = [
			_v(fname), _v(lname), _v(add1), add2, _v(city), _v(zip),
			_v(phone.replace('-', '')),
		];

		var el;
		
		fillText('[id="firstName"]', fname);
		fillText('[id="lastName"]', lname);
		fillText('[id="addressLineOne"]', add1);
		fillText('[id="addressLineTwo"]', add2);

		// The next big change was that they switched from using the ID attribute to
		// using custom HTML5 attributes
		for (var i = 0; i < selectors.length; i++) {
			if (i > 3) {
				var selector = 'input[data-tl-id=' + selectors[i] + ']';
				el = document.querySelector(selector);
				if (el === null) {
					var selector = 'input[tealeafid=' + selectors[i] + ']';
					el = document.querySelector(selector);
				}
				el.value = values[i];
				el.dispatchEvent(e);
			}
		}

		el = document.querySelector('select[data-tl-id=COAC2ShpAddrState]');
		if (el === null) {
			el = document.querySelector('select[tealeafid=COAC2ShpAddrState]');
		}
		el.value = state;
		el.dispatchEvent(e);
		
		if (document.querySelector('[for="marketingEmailPref"]') !== null && document.querySelector('[for="marketingEmailPref"]').querySelector('[type="checkbox"]').checked) {
			document.querySelector('[for="marketingEmailPref"]').click();
		}
	}
	
};

// Fisher Price
window.loadDSAddressFisherPrice = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    // load the shipping address info
    jQuery('#firstName_').val(_v(fname));
    jQuery('#lastName_').val(_v(lname));
    jQuery('#address1_').val(_v(add1));
    jQuery('#address2_').val(add2);
    jQuery('#city_').val(city);
    jQuery('#zipCode_').val(_v(zip));
    jQuery('#state0_').val(_v(state));
};

// Home Depot
window.loadDSAddressHomeDepot = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    fname = fname.replace(/[\&\/\#\+\(\)\$\"\~\%\*\?\<\>]/g, "");
    lname = lname.replace(/[\&\/\#\+\(\)\$\"\~\%\*\?\<\>]/g, "");
    add1 = add1.replace(/[\&\/\#\+\(\)\$\"\~\%\*\?\<\>]/g, "");
    email_element = document.querySelectorAll('input[name=inputField]')[0];
	
    if (email_element.id == 'emailInput') {
        email_element.setAttribute('name', 'email');
    }
	
	if (document.querySelector('[ng-click="showAddApartment()"]') !== null) {
		if (add2 !== '') {
			if (hasNumber(add1) == false) {
				add1 = [add2, add2 = add1][0];
			}
			document.querySelector('[ng-click="showAddApartment()"]').click();
		}
	}
	
	if (add2 !== '') {
		var selectors = [
			"zip", "firstName", "lastName", "inputField", "line1", "street", "pickupLocation",
		];

		var values = [
			_v(zip), _v(fname), _v(lname), _v(phone), _v(add1), _v(add2), _v(city)
		];
		
		for (var i = 0; i < 6; i++) {
			var selector = 'input[name=' + selectors[i] + ']';
			var el;
			el = document.querySelector(selector);
			el.value = values[i];
			el.dispatchEvent(new Event('input'));
			if (i == 0) {
				el.dispatchEvent(new Event('blur'));
			}
		}	
	} else {
		var selectors = [
			"zip", "firstName", "lastName", "inputField", "line1", "pickupLocation",
		];

		var values = [
			_v(zip), _v(fname), _v(lname), _v(phone), _v(add1), _v(city)
		];
		
		for (var i = 0; i < 5; i++) {
			var selector = 'input[name=' + selectors[i] + ']';
			var el;
			el = document.querySelector(selector);
			el.value = values[i];
			el.dispatchEvent(new Event('input'));
			if (i == 0) {
				el.dispatchEvent(new Event('blur'));
			}
		}
		
	}
	
    setTimeout(function() {
        for (var i = 0; i < selectors.length; i++) {
            var selector = 'input[name=' + selectors[i] + ']';
            var el;
            el = document.querySelector(selector);
            if (i == 5 && add2 == '') {
                city = values[i].toUpperCase();
                selector = 'select[id=cityStateListSelector]';
                el = document.querySelector(selector);
                var selected_option = el.querySelector('option[selected=selected]');
                selected_option.removeAttribute('selected');

                var option = el.querySelector('option[value^="' + city + '"]');
                option.setAttribute('selected', 'selected');
                option.dispatchEvent(new Event('change'));
                el.value = option.value;
                el.dispatchEvent(new Event('change'));
            } else if (i == 6 && add2 !== '') {
                city = values[i].toUpperCase();
                selector = 'select[id=cityStateListSelector]';
                el = document.querySelector(selector);
                var selected_option = el.querySelector('option[selected=selected]');
                selected_option.removeAttribute('selected');

                var option = el.querySelector('option[value^="' + city + '"]');
                option.setAttribute('selected', 'selected');
                option.dispatchEvent(new Event('change'));
                el.value = option.value;
                el.dispatchEvent(new Event('change'));
			}
            el.dispatchEvent(new Event('blur'));
        }
    }, 2000);
};

// Best Buy
window.loadDSAddressBestBuy = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
	
	if (add2 !== '') {
		if (hasNumber(add1) == false) {
			add1 = [add2, add2 = add1][0];
		}
		var selectors = [
			"zipcode", "firstName", "lastName", "mainAddy", "optAddy", "city", "state", "phone",
		];

		var values = [
			_v(zip), _v(fname), _v(lname), _v(add1), _v(add2), _v(city), _v(state), _v(phone),
		];
	} else {
		var selectors = [
			"zipcode", "firstName", "lastName", "mainAddy", "city", "state", "phone",
		];

		var values = [
			_v(zip), _v(fname), _v(lname), _v(add1), _v(city), _v(state), _v(phone),
		];
	}

    // Previous method of filling forms with a Virtal DOM do not work with
    // newer versions of ReactJS. However, this method of dirty injection
    // works, and does not require firing an event other than for the state
    // dropdown menu.
    if (window.location.href.indexOf('fulfillment') > -1) {
        fillText = (selector, value) => {
            document.querySelector(selector).select();
            document.execCommand('insertText', false, value);
        }


        function hideAddySuggest() {
            if (document.querySelector('[class="autocomplete__toggle"]') !== null) {
                document.querySelector('[class="autocomplete__toggle"]').click();
                document.querySelector('[class="autocomplete__toggle"]').outerHTML = '';
            } else {
                console.log('Suggestions for Addresses Hidden');
            }
        }


        // Due to every textarea appearing on one page, as each form is filled,
        // the element id is changed. This does not affect the checkout process
        // as the submission appears to be more reliant on the className used.
		if (add2 !== '') {			
			for (var i = 0; i < selectors.length; i++) {
				var selector = '[id*=' + selectors[i] + ']';
				var el;
				el = document.querySelector(selector);
				if (i == 0) {
					fillText(selector, values[i]);
					el.setAttribute('id','zcodeFilled');
				}
				if (i == 1) {
					fillText(selector, values[i]);
					el.setAttribute('id','fnameFilled');
				}
				if (i == 2) {
					fillText(selector, values[i]);
					el.setAttribute('id','lnameFilled');
				}
				if (i == 3) {
					optAddyLength = document.querySelectorAll('[id*=".street2"]').length;
					addyLength = document.querySelectorAll('[id*=".street"]').length;
					for (var j = 0; j < optAddyLength; j++) {
						document.querySelector('[id*=".street2"]').setAttribute('id', 'optAddy' + j);
					}
					for (var j = 0; j < optAddyLength; j++) {
						document.querySelector('[id*=".street"]').setAttribute('id', 'mainAddy' + j);
					}
					fillText(selector, values[i]);
					document.querySelector('input[id*=mainAddy]').id = document.querySelector('input[id*=mainAddy]').id.replace('mainAddy','addyFilled');
					setTimeout(hideAddySuggest, 700);
				}
				if (i == 4) {
					fillText(selector, values[i]);
					document.querySelector('input[id*=optAddy]').id = document.querySelector('input[id*=optAddy]').id.replace('optAddy','optFilled');
				}
				if (i == 5) {
					fillText(selector, values[i]);
					el.setAttribute('id','citFilled');
				}
				if (i == 6) {
					el.querySelector('option[value=' + values[i] + ']').selected = true;
					el.dispatchEvent(new Event('input', {bubbles: true}));
					el.dispatchEvent(new Event('change', {bubbles: true}));
					el.dispatchEvent(new Event('blur'));
					el.setAttribute('id','statFilled');
				}
				if (i == 7) {
					fillText(selector, values[i]);
					el.setAttribute('id','foneFilled');
				}
			}
		} else {
			for (var i = 0; i < selectors.length; i++) {
					var selector = '[id*=' + selectors[i] + ']';
					var el;
					el = document.querySelector(selector);
					if (i == 0) {
						fillText(selector, values[i]);
						el.setAttribute('id','zcodeFilled');
					}
					if (i == 1) {
						fillText(selector, values[i]);
						el.setAttribute('id','fnameFilled');
					}
					if (i == 2) {
						fillText(selector, values[i]);
						el.setAttribute('id','lnameFilled');
					}
					if (i == 3) {
						optAddyLength = document.querySelectorAll('[id*=".street2"]').length;
						addyLength = document.querySelectorAll('[id*=".street"]').length;
						for (var j = 0; j < optAddyLength; j++) {
							document.querySelector('[id*=".street2"]').setAttribute('id', 'optAddy' + j);
						}
						for (var j = 0; j < optAddyLength; j++) {
							document.querySelector('[id*=".street"]').setAttribute('id', 'mainAddy' + j);
						}
						fillText(selector, values[i]);
						document.querySelector('input[id*=mainAddy]').id = document.querySelector('input[id*=mainAddy]').id.replace('mainAddy','addyFilled');
						setTimeout(hideAddySuggest, 700);
					}
					if (i == 4) {
						fillText(selector, values[i]);
						el.setAttribute('id','citFilled');
					}
					if (i == 5) {
						el.querySelector('option[value=' + values[i] + ']').selected = true;
						el.dispatchEvent(new Event('input', {bubbles: true}));
						el.dispatchEvent(new Event('change', {bubbles: true}));
						el.dispatchEvent(new Event('blur'));
						el.setAttribute('id','statFilled');
					}
					if (i == 6) {
						fillText(selector, values[i]);
						el.setAttribute('id','foneFilled');
					}
				}
			}
    }

    // Order lookup page
    if (window.location.href.indexOf('guestorderlookup') > -1) {
        document.querySelector('[name="lastName"]').select();
        document.execCommand('insertText', false, values[2]);
        document.querySelector('[name="phoneNumber"]').select();
        document.execCommand('insertText', false, values[6]);
    }
};

// Buy Buy Baby
window.loadDSAddressBuyBuyBaby = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    var selectors = [
        "zipUS", "checkoutfirstName", "checkoutlastName", "address1", "address2", "cityName", "stateName", "basePhoneFull",
    ];

    var values = [
        _v(zip), _v(fname), _v(lname), _v(add1), _v(add2), _v(city), _v(state), _v(phone),
    ];

    fillText = (selector, value) => {
        document.querySelector(selector).select();
        document.execCommand('insertText', false, value);
    }

    if (window.location.href.indexOf('buybuybaby') > -1 && window.location.href.indexOf('checkout/billing') > -1) {
        var selector = '[name=' + selectors[7] + ']';
        var el;
        el = document.querySelector(selector);
        fillText(selector, values[7]);
    } else {
        for (var i = 0; i < selectors.length - 1; i++) {
            var selector = '[name=' + selectors[i] + ']';
            var el;
            el = document.querySelector(selector);
            if (i < 6) {
                fillText(selector, values[i]);
            }
            if (i == 4 && address2.value == '..') {
                fillText(selector, '')
            }
            if (i == 6) {
                el.querySelector('option[value=' + values[i] + ']').selected = true;
                el.dispatchEvent(new Event('change', {bubbles: true}));
                el.dispatchEvent(new Event('blur'));
            }
        }
    }
};

// Kohls
window.loadDSAddressKohls = function(fname, lname, add1, add2, city, zip, phone, state, buttonIndex) {
    var selectors = [
        "postalCode", "firstName", "lastName", "addr1", "addr2", "city", "state", "phoneNumber",
    ];

    var values = [
        _v(zip), _v(fname), _v(lname), _v(add1), _v(add2), _v(city), _v(state), _v(phone),
    ];

    fillText = (selector, value) => {
        document.querySelector(selector).select();
        document.execCommand('insertText', false, value);
    }
	
	fillText('[name="phoneNumber"]', phone);

  for (var i = 0; i < selectors.length - 1; i++) {
		var selector = '[name=' + selectors[i] + ']';
		var el;
		el = document.querySelector(selector);
		if (i < 6 || i == 7) {
			fillText(selector, values[i]);
		}
		if (i == 4 && document.querySelector('[name="addr2"]').value == '..') {
			fillText(selector, '')
		}
		if (i == 6) {
			el.querySelector('option[value=' + values[i] + ']').selected = true;
			el.dispatchEvent(new Event('change', {bubbles: true}));
			el.dispatchEvent(new Event('blur'));
		}
	}
};