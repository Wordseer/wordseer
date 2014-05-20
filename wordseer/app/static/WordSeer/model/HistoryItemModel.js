/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents an item in the user's search history. New instances are
created in response to searches by the
{@link WordSeer.controller.HistoryController#newHistoryItem} method, which
is called by the {@link WordSeer.controller.SearchController} which listens and
responds to such actions.

@cfg {String} id An auto-generate unique identifier.

@cfg {WordSeer.model.FormValues} formValues The object representing the search
query.

@cfg {String} widget_xtype The xtype of the
{@link WordSeer.view.widget.Widget} in which the search was issued.

@cfg {Date} creation_timestamp The timestamp at which this search was issued.

@cfg {Date} last_viewed_timestamp The timestamp at which the
{@link WordSeer.view.windowing.viewport.LayoutPanel LayoutPanel} containing
this search was last active (i.e. clicked).

@cfg {Boolean} is_current Whether this history item is the most recent.

@cfg {String} layout_panel_id The ID of the
{@link WordSeer.view.windowing.viewport.LayoutPanel LayoutPanel} in which
this history item is currently being viewed. If the history item is not
currently visible, this is set to '', the empty string (see
{@link WordSeer.controller.HistoryController#hideHistoryItem}).

*/

Ext.define('WordSeer.model.HistoryItemModel', {
	extend: 'Ext.data.Model',
	fields: [
		{type: 'string', name: 'id'},
		{type: 'auto', name: 'formValues'},
		{type: 'string', name: 'widget_xtype'},
		{type: 'date', name:'creation_timestamp'},
		{type: 'date', name:'last_viewed_timestamp'},
		{type: 'boolean', name: 'is_current'},
		{type: 'string', name: 'layout_panel_id'},
	],
	associations: {
		type: 'hasOne',
		model: 'WordSeer.model.LayoutPanelModel',
		name: 'panel',
		foreignKey: 'layout_panel_id',
	}
})
