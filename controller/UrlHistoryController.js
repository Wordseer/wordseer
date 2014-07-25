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

        } else if (/^panels:/.test(token)) {
            // make sure controller is ready to display windows
            if (!this.getController('WindowingController').initialized) {
                this.getController('WindowingController').start();
            }
//          parse the token
            var parts = token.split(":");
            var panel_itemids = [];
            var history_ids = [];

            for (var i = 1; parts[i]; i++) {
                var panel_parts = parts[i].split("_");
                panel_itemids.push(panel_parts[0]);
                history_ids.push(panel_parts[1]);
            }

//          get current panels
            var panels = Ext.getCmp("windowing-viewport").query("layout-panel");
            var active_panels = [];
            for (var i = 0; panels[i]; i++){
                active_panels.push(panels[i].itemId)
            }

            // if panel isn't in token list, close it
            for (var i = 0; active_panels[i]; i++) {
                if (panel_itemids.indexOf(active_panels[i]) == -1) {
                    windowing.closeToolClicked(Ext.getCmp(active_panels[i]));
                }
            }

// if token isn't in window, play history item in new panel with the requested id
            for (var i = 0; panel_itemids[i]; i++) {
                if (active_panels.indexOf(panel_itemids[i]) == -1) {
                    windowing.playHistoryItemInNewPanel(history_ids[i],
                        panel_itemids[i]);
                }
            }
        }

    },

    newPanel: function(panel_itemid, history_item_id){
        var token = Ext.History.getToken();
        if (! /^panels:/.test(token)) {
            token = "panels:";
        }
        token += panel_itemid + "_" + history_item_id + ":";
        Ext.History.add(token);
    },
});
