/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.App', {
    extend: 'Ext.ux.desktop.App',
    alias: 'widget.app',
    requires: [
        'Ext.ux.desktop.ShortcutModel',

        'WordSeer.view.desktop.DocumentViewerModule',
        'WordSeer.view.desktop.DocumentBrowserModule',
        'WordSeer.view.desktop.PhraseSetsModule',
        'WordSeer.view.desktop.BarChartModule',
        'WordSeer.view.desktop.ColumnVisModule',
        'WordSeer.view.desktop.WordTreeModule',
        'WordSeer.view.desktop.OrganizeToolModule',
        'WordSeer.view.desktop.SentenceListModule',
        //'WordSeer.view.desktop.UniversalVisualizationModule',
        'WordSeer.view.desktop.SearchModule',

        'WordSeer.view.desktop.appbar.AppBarButton',
        // stores:
        'WordSeer.store.DocumentSetsStore',
        'MyDesktop.Settings'
    ],
    listeners:{
        /* The user has clicked on the browse documents icon */
        browse:function(){
            var module = this.getModule('document-browser');
            module.createWindow();
        },
     },
    init: function() {
        // custom logic before getXYZ methods get called...
        Ext.tip.QuickTipManager.init();
        this.callParent();
        this.addEvents('search', 'browse');
        // now ready...
        // create the collections set store:
        COLLECTIONS_STORE = new WordSeer.store.DocumentSetsStore();
        SENTENCE_COLLECTIONS_STORE = new WordSeer.store.SentenceSetStore();
    },
    // get the modules that launch windows
    getModules : function(){

        return [
            new WordSeer.view.desktop.SearchModule(),
            new WordSeer.view.desktop.ColumnVisModule(),
            //new WordSeer.view.desktop.BarChartModule(),
            new WordSeer.view.desktop.WordTreeModule(),
            new WordSeer.view.desktop.DocumentBrowserModule(),
            //new WordSeer.view.desktop.SentenceListModule(),

            new WordSeer.view.desktop.PhraseSetsModule(),
            new WordSeer.view.desktop.DocumentViewerModule(),

            // Combination modules: search + bar chat, and all visualizations.
            //new WordSeer.view.desktop.UniversalVisualizationModule(),
            //new WordSeer.view.desktop.OrganizeToolModule(),
        ];
    },
    // get the items that are going to be in the dock
    getApps:function(){
        var apps = [
            {module:'document-browser', text:'Documents'},
            {module:'phrase-sets', text:'Word Sets'},
            //{module:'organize-tool', text:'Canvas'}
        ];
        for(var i = 0; i < apps.length; i++){
            apps[i].xtype = 'appbar-button';
        };
        return apps;
    },
    getDesktopConfig: function () {
        var me = this, ret = me.callParent();

        return Ext.apply(ret, {

            contextMenuItems: [
                { text: 'Change Settings', handler: me.onSettings, scope: me }
            ],

            shortcuts: Ext.create('Ext.data.Store', {
                model: 'Ext.ux.desktop.ShortcutModel',
                data: []
            }),
            cls:'wordseer-desktop',
            bodyCls:'wordseer-desktop-body',
            wallpaper: '../wallpapers/Wood-Sencha.jpg',
            wallpaperStretch: false
        });
    },
    getAppBarConfig: function(){
        return {
            xtype:'toolbar',
            vertical:true,
            cls:'wordseer-appbar',
            floating:true,
            border:0,
            shadow:false,
            layout: {
                type:'vbox',
                padding:'5',
                pack:'center',
                align:'center',
            },
                width: '46',
                height: '100',
            items: this.getApps(),
        }
    },
    onLogout: function () {
        Ext.Msg.confirm('Logout', 'Are you sure you want to logout?');
    },
    onSettings: function () {
        var dlg = new MyDesktop.Settings({
            desktop: this.desktop
        });
        dlg.show();
    },
});


