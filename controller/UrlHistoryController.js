/** controls dispatch of url history tokens to/from the windowing controller
url history relies on the query history in localstorage (see HistoryItem )
to record windowing state in the URL hash.

This enables standard browser back/forward actions but does not make URLs
shareable or truly persistent, since query history is not reliably or centrally
stored.

How it works:
- Listens for events indicating new searches or widget selections, updates URLs
accordingly (reflects app state rather than controlling it)
- Listens for URL changes (eg, from back/forward buttons) and hands them off to
the WindowingController for dispatching (keep windowing logic out of this controller)
*/
Ext.define('WordSeer.controller.UrlHistoryController', {
    extend: 'Ext.app.Controller',
    // flag for internal URL manipulation vs back/fwd clicks
    IGNORE_CHANGE: false,

    views: [
        'windowing.viewport.LayoutPanel'
    ],

    // listen for layout events and add them to url
    init: function(){
        this.control({
            'layout-panel': {
                navButtonClicked: this.navButton,
                newSlice: this.newSlice
            }

        });
    },

    // TODO: update this so it doesn't call windowing functions directly
    dispatch: function(token){
        if (this.IGNORE_CHANGE) { return; }

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
            // TODO: panel splitters are left hanging around after return home

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

            // if token isn't in window, play history item in new panel
            // with the requested id
            for (var i = 0; panel_itemids[i]; i++) {
                if (active_panels.indexOf(panel_itemids[i]) == -1) {
                    windowing.playHistoryItemInNewPanel(history_ids[i],
                        panel_itemids[i]);
                }
            }
        }

    },


    navButton: function(panel, buttonClicked){
        this.IGNORE_CHANGE = true;
        switch (buttonClicked){
            case 'close':
                var id = panel.itemId;
                this.removePanel(id);
                break;
            default:
                break;
        }
        this.IGNORE_CHANGE = false;
    },

    newSlice: function(panel, formValues){
        this.IGNORE_CHANGE = true;
        // get associated HistoryItem
        var history_item_id = Ext.getStore("HistoryItemStore")
            .findRecord("layout_panel_id", panel.itemId)
                .internalId;
        var new_search = panel.itemId + "_" + history_item_id;
        var token = Ext.History.getToken();
        if (! /^panels:/.test(token)) {
            token = "panels:" + new_search;
        } else {
            token = token.split(":");
            for (var i=0; i<token.length; i++){
                if (token[i].indexOf(panel.itemId) != -1) {
                    token.splice(i, 1, new_search);
                } else if (i == token.length - 1 ) {
                    // add to end
                    token.push(new_search);
                }
            }
            token = token.join(":");
        }
        Ext.History.add(token);
        this.IGNORE_CHANGE = false;
    },

    newPanel: function(panel_itemid, history_item_id){
        var token = Ext.History.getToken();
        if (! /^panels:/.test(token)) {
            token = "panels:";
        }
        token += panel_itemid + "_" + history_item_id + ":";
        Ext.History.add(token);
    },

    removePanel: function(id){
        var token = Ext.History.getToken();
        token = token.split(":");
        for (var i=0; i<token.length; i++){
            if (token[i].indexOf(id) != -1) {
                token.splice(i, 1);
            }
        }
        if (token.length == 1) {
            // no more tabs open
            token = "home";
        } else {
            token = token.join(":");
        }

        Ext.History.add(token);
    }
});
