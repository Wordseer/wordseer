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
    // flags for internal URL manipulation vs back/fwd clicks
    IGNORE_CHANGE: false,
    IGNORE_EVENTS: false,

    views: [
        'windowing.viewport.LayoutPanel',
        'windowing.viewport.LandingPage',
    ],

    // listen for layout events and add them to url
    init: function(){
        this.control({
            'layout-panel': {
                navButtonClicked: this.navButton,
                initSearch: this.initSearch,
                switchWidgets: this.switchWidget,
            },
            'landing-page': {
                render: this.landingPage,
            }

        });
    },

    // TODO: update this so it doesn't call windowing functions directly
    dispatch: function(token){
        if (this.IGNORE_CHANGE) { return; }

        this.IGNORE_EVENTS = true;
        this.getController('WindowingController').dispatchUrlToken(token);
        this.IGNORE_EVENTS = false;
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

    initSearch: function(panel, formValues){
        if (this.IGNORE_EVENTS) { return; }

        this.IGNORE_CHANGE = true;
        this.addOrUpdatePanel(panel);
        this.IGNORE_CHANGE = false;
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
    },

    landingPage: function(){
        this.IGNORE_CHANGE = true;
        Ext.History.add("home");
        this.IGNORE_CHANGE = false;
    },

    switchWidget: function(panel, widget_xtype){
        this.IGNORE_CHANGE = true;
        this.addOrUpdatePanel(panel);
        this.IGNORE_CHANGE = false;
    },

    addOrUpdatePanel: function(panel){
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
    },

});
