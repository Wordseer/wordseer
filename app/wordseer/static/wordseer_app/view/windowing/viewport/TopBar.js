/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** WordSeer's top bar, containing the grammatical search form, the user sign in
-sign out buttons and the menu of widgets that can be opened up without any
search input.
*/
Ext.define('WordSeer.view.windowing.viewport.TopBar', {
	extend: 'Ext.toolbar.Toolbar', // TODO - make this a basic hbox panel...
    alias: 'widget.windowing-topbar',
    requires: [
        'WordSeer.view.desktop.topbar.WidgetsMenu',
        'WordSeer.view.search.UniversalSearchForm',
    ],
    items:[
        {xtype: 'widgets-menu', flex:1},
        '-',
        {xtype:'universal-search-form',flex:1},
        '-',
        {xtype:'user-button'},
    ],
})