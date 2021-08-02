
function Bruja() {
    
    this.template = {};
    
    this._index = 0;
    
    this.vars = {};
    
    this.eventHandlers = {
        clickLink: function(selector, event, value, delay) {
            setTimeout(function() {
                var link = $(selector);
                var target = link.attr("target");

                if($.trim(target).length > 0)
                {
                    window.open(link.attr("href"), target);
                }
                else
                {
                    window.location = link.attr("href");
                }

                
            }, delay);
        },
    };
        
    
}

Bruja.prototype = {
    loadScriptJSON : function(){},
    
    loadScript : function(template) {
        this.template = template;
    },
    
    runAction : function(selector, event, value, delay) {
        if(this.eventHandlers[event] != undefined) {
            this.eventHandlers[event](selector, event, value, delay);
        } else {
            
            setTimeout( function() {
                console.log(selector);
                $(selector).trigger(event, value);
            }, delay);
        }
        
        
    },
    
    runAll : function() {
        for(var i = 0; i < this.template.actions.length; i++) {
            var act = this.template.actions[i];
            this.runAction(act.selector, act.event, act.value, act.delay);
            //console.log(this.template.actions[i].event + " for " + this.template.actions[i].selector);
        }
    },
    
    runNext : function() {},
    
    
}

/*******************TESTING*******************************/
var ascr = { "name":"foo",
            "actions": [
                { "selector": "a#trigger-event-extraParameters", "event": "focus", "value":"", "delay":100 },
                { "selector": "span.category a:first", "event": "clickLink", "value":"", "delay":100 },
            ]};

var bruja = new Bruja();
bruja.loadScript(ascr);
bruja.runAll();
