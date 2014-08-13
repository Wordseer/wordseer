/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.topbar.TopBar', {
    extend: 'Ext.toolbar.Toolbar', // TODO - make this a basic hbox panel...

    requires: [
        'Ext.button.Button',
        'Ext.resizer.Splitter',
        'Ext.menu.Menu',
        
        'WordSeer.view.search.UniversalSearchForm',
        'WordSeer.view.desktop.topbar.User',
    ],

    alias: 'widget.topbar',
    cls: 'ux-taskbar',
    initComponent: function () {
        var me = this;
        me.items = [
            {xtype:'universal-search-form',flex:1},
            '-',
            {xtype:'user-button'}
        ];

        me.callParent();
    },


});



