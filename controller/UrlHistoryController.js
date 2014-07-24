/** controls dispatch of url history tokens to/from the windowing controller
*/
Ext.define('WordSeer.controller.UrlHistoryController', {
    extend: 'Ext.app.Controller',

    dispatch: function(token){
        var windowing = this.getController('WindowingController');
        
        if (token == 'usersignin') {
//             initial sign-in
            Ext.create('Ext.container.Viewport', {
                layout: 'fit',
                items:{
                        xtype: 'usersignin',
                }
            });
        } else if (token == 'home'){
//             show landing page
            windowing.land();
            
        } else if (/^tabs:/.test(token)) {
//          parse the token
            var parts = token.split(":");
            var tab_ids = [];
            var history_ids = [];
            
            for (var i = 1; parts[i]; i++) {
                var tab_parts = parts[i].split("_");
                tab_ids.push(tab_parts[0]);
                history_ids.push(tab_parts[1]);
            }
            
//          get current tabs
            var tabs = Ext.getCmp("windowing-viewport").query("layout-panel");
            var active_tabs = [];
            for (var i = 0; tabs[i]; i++){
                active_tabs.push(tabs[i].id)
            }
            console.log(active_tabs)

// if tab isn't in token list, close it 
            for (var i = 0; active_tabs[i]; i++) {
                if (tab_ids.indexOf(active_tabs[i]) == -1) {
                    windowing.closeToolClicked(Ext.getCmp(active_tabs[i]));
                }
            }

// if token isn't in window, play history item in new tab with the requested id
            for (var i = 0; tab_ids[i]; i++) {
                if (active_tabs.indexOf(tab_ids[i]) == -1) {
                    windowing.playHistoryItemInNewPanel(history_ids[i], tab_ids[i]);
                }
            }            
        }
        
    },
    
    newTab: function(tab_id, history_item_id){
        var token = Ext.History.getToken();
        if (! /^tabs:/.test(token)) {
            token = "tabs:";
        }
        token += tab_id + "_" + history_item_id + ":"
        Ext.History.add(token);
    },
    
    updateTabToken: function(action, tab_id, history_id){
//      action should be "add", "remove", "update"
        var token = Ext.History.getToken();
        
        switch (action){
            case "add":
//                 token = token + tab_id + ":" + history_id = ";";
//                 Ext.History.add(token);
                break;
        }
        
    }
});

