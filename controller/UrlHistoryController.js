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
//          parse the token
            var parts = token.split(":");
            var panel_ids = [];
            var history_ids = [];

            for (var i = 1; parts[i]; i++) {
                var panel_parts = parts[i].split("_");
                panel_ids.push(panel_parts[0]);
                history_ids.push(panel_parts[1]);
            }

//          get current panels
            var panels = Ext.getCmp("windowing-viewport").query("layout-panel");
            var active_panels = [];
            for (var i = 0; panels[i]; i++){
                active_panels.push(panels[i].id)
            }
            console.log(active_panels)

// if panel isn't in token list, close it
            for (var i = 0; active_panels[i]; i++) {
                if (panel_ids.indexOf(active_panels[i]) == -1) {
                    windowing.closeToolClicked(Ext.getCmp(active_panels[i]));
                }
            }

// if token isn't in window, play history item in new panel with the requested id
            for (var i = 0; panel_ids[i]; i++) {
                if (active_panels.indexOf(panel_ids[i]) == -1) {
                    windowing.playHistoryItemInNewPanel(history_ids[i], panel_ids[i]);
                }
            }
        }

    },

    newPanel: function(panel_id, history_item_id){
        var token = Ext.History.getToken();
        if (! /^panels:/.test(token)) {
            token = "panels:";
        }
        token += panel_id + "_" + history_item_id + ":"
        Ext.History.add(token);
    },
});
