/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** [DEPRECATED]Contains buttons that open up
{@link WordSeer.view.widget.Widget Widgets} that don't need a search input.
These Widgets are:
- {@link WordSeer.view.widget.DocumentBrowserWidget},
- {@link WordSeer.view.widget.SentenceListWidget},
- {@link WordSeer.view.widget.PhraseSetsWidget}
- {@link WordSeer.view.visualize.wordtree.WordTreeWidget}

Clicks on menu buttons are controlled by the Windowing Controller's
{@link WordSeer.controller.WindowingController#launchWidgetFromWidgetsMenu}
method.
*/
Ext.define('WordSeer.view.desktop.topbar.WidgetsMenu',{
	extend: 'Ext.toolbar.Toolbar',
	alias: 'widget.widgets-menu',
	items: [
	{
		xtype: 'button',
		href: ws_project_path,
		hrefTarget: "_self",
		html: '&laquo;Return to Project List'
	}
	]

})
