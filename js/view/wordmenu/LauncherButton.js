/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} option that launches a
widget.
@cfg {String} widget The xtype of the {@link Wordseer.view.widget.Widget widget}
to launch.

@cfg {WordSeer.model.WordModel} The word menu's current item.
*/
Ext.define('WordSeer.view.wordmenu.LauncherButton', {
	extend: 'WordSeer.view.menu.MenuItem',
	alias: 'widget.launcherbutton',
	config: {
		/**
		@cfg {Object} widget An object containing the xtype of the widget that
		should be launched when the button is clicked.
		*/
		widget: false,

		/**
		@cfg {Ext.data.Model} current The object that is the basis for the new
		search.
		*/
		current: false,
	}
});
