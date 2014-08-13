/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Manages adding and removing
{@link WordSeer.view.windowing.viewport.LayoutPanel}s to and from the
{@link WordSeer.view.windowing.viewport.Layout}.
*/
Ext.define('WordSeer.controller.WindowingController', {
	extend: 'Ext.app.Controller',
	requires: [
		'WordSeer.view.windowing.viewport.HboxLayout',
	],
	stores: [
		'HistoryItemStore',
		'LayoutStore',
	],
	models: [
		'HistoryItemModel',
		'LayoutModel',
		'LayoutPanelModel'
	],
	views: [
		'box.Overlay',
		'windowing.viewport.Viewport',
		'windowing.viewport.Layout',
		'windowing.viewport.LandingPage',
		'windowing.viewport.LayoutPanel',
		'windowing.viewport.TopBar',
		'menu.ResultListMenu'
	],
	init: function() {
//		console.log('Windowing Controller Loaded');
		this.control({
			'windowing-viewport': {
				afterrender: this.start,
			},
			'layout-panel' : {
				navButtonClicked: function(panel, type) {
//					console.log("Nav button of type " + type + " clicked");
					switch (type) {
						case 'close':
							this.closePanel(panel);
							break;
						default:
							break;
					}
				},
				//TODO: add the move drag and drop behavior.
				activate: this.layoutPanelActivated,
				switchWidgets: this.switchWidgets,
			},
			'widgets-menu > button': {
				click: this.launchWidgetFromWidgetsMenu
			},
			'sentence-list, document-grid': {
				select: this.showResultMenu,
				deselect: this.destroyResultMenu
			}
		});
	},

	land: function() {
		this.initialized = false;
		Ext.getCmp('windowing-viewport').down('layout').hide();
		var landing = Ext.getCmp('windowing-viewport').down('landing-page');
		if (landing) {
			landing.show();
		} else {
			Ext.getCmp('windowing-viewport').add({xtype:'landing-page'});
		}
//      remove any lingering panels
		var panels = Ext.getCmp("windowing-viewport").query("layout-panel");
		for (var i = 0; panels[i]; i++){
			panels[i].destroy();
		}

	},

	/** Creates a fresh layout and plays the empty history
	item (which gives the user an overview of the collection) in its current
	panel. Executed only once, when the page loads. Called by the
	{@link WordSeer.controller.UserController#signUserIn} method once the
	initial sign in has been completed.
	*/
	start: function() {
		var landing = Ext.getCmp('windowing-viewport').down('landing-page');
		if (landing) landing.hide();
		if (!Ext.getCmp('windowing-viewport').down('layout')) {
			this.initializeLayouts();
			var layout_model = Ext.getStore('LayoutStore').getCurrent();
			view = Ext.getCmp('windowing-viewport').addLayout(layout_model);
		} else {
			Ext.getCmp('windowing-viewport').down('layout').show();
		}
		$('.x-mask').remove();
	},

	/** Sets up the layouts that the application will use. By default, only
	sets up the {@link WordSeer.view.windowing.viewport.HboxLayout}.
	*/
	initializeLayouts: function() {
		if (!this.initialized) {
			// 1. The column layout. This is the default layout.
			var hbox_layout = Ext.create('WordSeer.model.LayoutModel', {
				id: 'single',
				name: 'Single View',
				viewport_view: 'WordSeer.view.windowing.viewport.HboxLayout',
				thumbnail_view: 'WordSeer.view.windowing.overview.HboxLayoutThumbnail',
				is_current: true,
			});
			// var panels = hbox_layout.panels();
			// panels.add({
			// 	id: "0",
			// 	layout_id: "0",
			// 	name: 'Main Panel'
			// })
			this.getStore('LayoutStore').add(hbox_layout);
			if (!this.getStore('LayoutStore').getCurrent()) {
				this.getStore('LayoutStore').setCurrent(hbox_layout);
			}
			this.initialized = true;
		}
	},

	/** Checks whether the {@link WordSeer.view.windowing.viewport.LayoutPanel}'s
	current {@link WordSeer.view.widget.Widget} matches the search being issued.
	If not, it replaces the widget with the one being searched with.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel The panel to
	refresh.
	*/
	refreshPanel: function(panel) {
		// console.time('refreshPanel');
		var panel_model = panel.getLayoutPanelModel();
		var history_item_id = panel_model.get('history_item_id');
		var history_item = Ext.getStore('HistoryItemStore')
			.getById(history_item_id);
		var formValues = WordSeer.model.FormValues.deserialize(
				history_item.get('formValues')).copy();
		var widget_xtype = history_item.get('widget_xtype');
		// Switch the widget if necessary
		if(!panel.down('widget') || panel.down('widget').xtype != widget_xtype) {
			var inner = panel.getComponent('inner');
			// die here if user has already hit back/fwd
			if (!inner){ return false; }
			inner.removeAll();
			inner.add({
				xtype: widget_xtype,
			});
		}
		var widget = panel.down('widget');
		if (widget) {
			// Push up the old formValues into the panel.
			widget.setHistoryItem(history_item);
			widget.setFormValues(formValues);
		}
		this.setWidgetCombobox(panel, widget_xtype);
		this.layoutPanelActivated(panel);

		// bring any floating windows to the front.
		var windows = Ext.ComponentQuery.query('window');
		try {
			windows.forEach(function(w) {w.toFront()});
		} catch (e) {};
		// console.timeEnd('refreshPanel');
	},

	/** Asks the current layout to add a panel to the layout.

	@param {String} direction The region for the new panel, to be passed into a
	{@link Ext.layout.container.Border Border Layout}, either 'east' or 'south'.

	@return {WordSeer.view.windowing.viewport.LayoutPanel} The newly added
		panel.
	*/
	addPanel: function(panel_id) {
		// console.time('addPanel');
		var current_layout = Ext.getStore('LayoutStore').getCurrent();
		var view = Ext.getCmp('windowing-viewport').getComponent(
			current_layout.get('id'));
		var panel =  view.addPanel(panel_id);
		this.layoutPanelActivated(panel);
		// console.timeEnd('addPanel');
		Ext.resumeLayouts();
		return panel;
	},

	/** Removes the given panel from the layout, and un-links the history item
	being viewed from the layout panel. Called by {#closePanel} when the
	user clicks the 'close' tool on a
	{@WordSeer.view.windowing.viewport.LayoutPanel}, or by
	{@link WordSeer.controller.HistoryController#hideHistoryItem} when the user
	unchecks a {@link WordSeer.view.history.HistoryList} item.

	@param panel the {WordSeer.view.windowing.viewport.LayoutPanel} instance to
		remove.
	*/
	removePanel: function(panel) {
		// console.time('removePanel');
		var view = panel.up('layout');
		view.removePanel(panel);
		// console.timeEnd('removePanel');
		this.layoutPanelActivated(view.getCurrentPanel());
		if (Ext.ComponentQuery.query('layout-panel').length === 0) {
			this.land();
		}
	},

	/** Responds to a click in a panel. Keeps track of the order in which panels
	were last active, sets the border of the clicked panel to show that it is
	the most recent.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} layout_panel The panel
	that was clicked.
	*/
	layoutPanelActivated:function(layout_panel) {
		if (layout_panel) {
			Ext.ComponentQuery.query('layout-panel').forEach(function(item){
				if (item.rendered) {
					var el = item.getEl();
					if (el) {
						el.removeCls("active");
					}
					if (item == layout_panel) {
						el.addCls("active");
					}
				} else {
					item.autoEl.cls = item.autoEl.cls.replace(/active/g, "")
					if (item == layout_panel)
						item.autoEl.cls += " active ";
				}
			})
			var history_item = Ext.getStore('HistoryItemStore').getById(
				layout_panel.getLayoutPanelModel().get('history_item_id'));
			if(history_item) {
				history_item.set(
				'last_viewed_timestamp', new Date().getTime());
			}
			var layout = layout_panel.up('layout');
			layout.panel_activation_order.remove(layout_panel.itemId);
			layout.panel_activation_order.unshift(layout_panel.itemId);
			// Change the default option in the universal search form to the
			// active panel's widget_xtype.
			if (!layout_panel.layoutPanelModel.get('history_item_id').length == 0
				&& history_item){
				var forms = Ext.ComponentQuery.query('universal-search-form');
				if (forms.length > 0) {
					forms[0].down('switch-widget-combobox').setValue(
						history_item.get('widget_xtype'));
				}
			}

		}
	},

	/** Alters the switch-widget combobox on the layout panel to reflect the
	current widget.
	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel The panel whose
	combobox to switch.
	@param {String} widget_xtype The new xtype.
	*/
	setWidgetCombobox: function(panel, widget_xtype) {
		var formValues = panel.getLayoutPanelModel().getFormValues();
		var blank = (formValues.phrases.length == 0 &&
			formValues.metadata.length == 0 &&
			formValues.document_id == "" && formValues.search.length == 0);
		var has_search = formValues.search.length > 0;
		var has_grammatical_search = (formValues.relation != "");
		var is_document = formValues.document_id != "";
		if (panel.rendered) {
			var el = panel.getEl().down('select.panel-header-widget-select')
			var option = el.down('option.switch-widget.document-viewer');
			if (is_document && !option) {
				el.appendChild({tag: 'option',
					value:'document-viewer-widget',
					html: 'Reader',
					cls:'switch-widget document-viewer'});
			} else if (!is_document && option) {
				option.remove();
			}
			$(el.dom).val(widget_xtype);
			options = panel.getEl().select('option.switch-widget');
			options.each(function(el){$(el.dom).removeAttr('disabled')});
			if (blank) {
				var el = panel.getEl().down('option[value=word-frequencies-widget]');
				if (el) el.set({disabled:'disabled'});
				el = panel.getEl().down('option[value=sentence-list-widget]');
				if (el) el.set({disabled:'disabled'});
			}
			if (!has_grammatical_search || !has_search) {
				el = panel.getEl().down('option[value=search-widget]');
				if (el) el.set({disabled:'disabled'});
			}
		} else {
			var options = panel.autoEl.children[0].children[4].children;
			if (is_document) {
				options.push({tag: 'option',
					value:'document-viewer-widget',
					cls:'switch-widget document-viewer'})
			}
			options.forEach(function(option) {
				if (option.value == widget_xtype) {
					option.selected = "selected";
				} else {
					delete option.selected;
				}
				delete option.disabled;
				if (blank) {
					if (option.value == 'word-frequencies-widget' ||
						option.value == 'sentence-list-widget') {
						option.disabled = 'true'
					}
				}
				if (!has_grammatical_search || !has_search) {
					if (option.value == 'search-widget') {
						option.disabled = true
					}
				}
			})
		}
	},


	/** Displays a {@link WordSeer.model.HistoryItemModel} within the given
	panel. Sets up {@link WordSeer.view.search.BreadCrumb}s corresponding
	to the {@link WordSeer.model.HistoryItemModel#formValues} and by calling
	{@link WordSeer.controller.BreadCrumbsController#setBreadCrumbsForFormValues}
	and then calls
	{@link WordSeer.controller.SearchController#assembleSearchParamsAndSearch}
	to do the search.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} layout_panel The panel
	in which to display the history item

	@param {WordSeer.model.LayoutPanelModel} layout_panel_model The model
	instance representing the state of the `layout_panel`.

	@param {String} history_item_id The ID of the history item to play -- which
	can be used to retrieve the history item using
		Ext.getStore('HistoryItemStore').getById(history_item_id);
	*/
	playHistoryItem: function(layout_panel, layout_panel_model, history_item_id) {
		layout_panel_model.set('history_item_id', history_item_id);
		this.refreshPanel(layout_panel);
		this.getController('HistoryController').selectHistoryItem(
			history_item_id);
		var history_item = Ext.getStore('HistoryItemStore')
			.getById(history_item_id);
		var formValues = WordSeer.model.FormValues.deserialize(
			history_item.get('formValues'));
		layout_panel.fireEvent('initSearch', layout_panel, formValues,
			history_item_id);
	},

	/** Adds a new panel to the layout and displays the
	{@link WordSeer.model.HistoryItemModel} with the given ID in that panel.
	Adds a new panel, and calls {@link #playHistoryItem} with the new panel and
	the given history item ID.

	@param {String} history_item_id The ID of the
	{@link WordSeer.model.HistoryItemModel} to display. The model is retrieved
	from the {@link WordSeer.store.HistoryItemStore} by this ID.

	@return {WordSeer.view.windowing.viewport.LayoutPanel} The new layout panel.
	*/
	playHistoryItemInNewPanel: function(history_item_id, panel_id) {
		var panel = this.addPanel(panel_id);
		Ext.defer(function(history_item_id, panel){
			var current_layout_model = Ext.getStore('LayoutStore').getCurrent();
			var history_item = Ext.getStore('HistoryItemStore')
				.getById(history_item_id);
			current_layout_model.addHistoryItemToPanel(history_item,
				panel.itemId);
			this.playHistoryItem(panel, panel.getLayoutPanelModel(),
				history_item_id);
		},
		1000,
		this,
		[history_item_id, panel]);
		return panel;
	},

	/** Adds a new panel to the layout and displays the
	{@link WordSeer.model.HistoryItemModel} with the given ID in that panel.
	Adds a new panel, and calls {@link #playHistoryItem} with the new panel and
	the given history item ID.

	@param {String} history_item_id The ID of the
	{@link WordSeer.model.HistoryItemModel} to display. The model is retrieved
	from the {@link WordSeer.store.HistoryItemStore} by this ID.

	@return {WordSeer.view.windowing.viewport.LayoutPanel} The new layout panel.
	*/
	playHistoryItemInPreviousPanel: function(history_item_id) {
		var current_layout_model = Ext.getStore('LayoutStore').getCurrent();
		var view = Ext.getCmp('windowing-viewport').getComponent(
			current_layout_model.get('id'));
		var previous_panel = view.getPreviousPanel();
		var current_panel = view.getCurrentPanel();
		if (previous_panel.itemId == current_panel.itemId) {
			previous_panel = this.addPanel();
		}
		Ext.defer(function(history_item_id, panel){
			var current_layout_model = Ext.getStore('LayoutStore').getCurrent();
			var history_item = Ext.getStore('HistoryItemStore')
				.getById(history_item_id);
			current_layout_model.addHistoryItemToPanel(history_item,
				panel.itemId);
			this.playHistoryItem(panel, panel.getLayoutPanelModel(),
				history_item_id);
		},
		1000,
		this,
		[history_item_id, previous_panel]);
	},

	/** Displays the {@link WordSeer.model.HistoryItemModel} with the given ID
	in the layout's current panel. Asks the layout for the correct panel
	(if there are no panels, cals {#addPanel} to create one), then calls
	{@link #playHistoryItem} with the new panel and the given history item ID.

	@param {String} history_item_id The ID of the
	{@link WordSeer.model.HistoryItemModel} to display. The model is retrieved
	from the {@link WordSeer.store.HistoryItemStore} by this ID.
	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel (optional) the
	panel in which to play the history item.
	*/
	playHistoryItemInCurrentPanel: function(history_item_id, panel) {
		var current_layout_model = Ext.getStore('LayoutStore').getCurrent();
		var current_panel = panel
		if (!panel) {
			var view = Ext.getCmp('windowing-viewport').getComponent(
				current_layout_model.get('id'));
			current_panel = view.getCurrentPanel();
			if (!current_panel) {
			current_panel = this.getController('WindowingController')
				.addPanel();
			}
		}
		var history_item = Ext.getStore('HistoryItemStore')
			.getById(history_item_id);
		current_layout_model.addHistoryItemToPanel(history_item,
			current_panel.itemId);
		this.playHistoryItem(current_panel, current_panel.getLayoutPanelModel(),
			history_item.get('id'));
	},

	/** Called when the 'close' nav button is clicked on a
	{@link WordSeer.view.windowing.viewport.LayoutPanel}. Triggers the deselect
	event on the {@link WordSeer.view.history.HistoryList} view for the
	{@link WordSeer.model.HistoryItemModel} belonging to the panel. This calls
	{@link WordSeer.controller.HistoryController#hideHistoryItem}.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel The layout panel
	to close.
	*/
	closePanel: function(panel){
		var history_item_id = panel.getLayoutPanelModel()
			.get('history_item_id');
		if (history_item_id !== '') {
			if (Ext.ComponentQuery.query('history-list').length > 0) {
				// If it's not an empty panel and is displaying a history item, then
				// deselect the history item.
				this.getController('HistoryController').deselectHistoryItem(
					history_item_id, true);
			} else {
				this.removePanel(panel);
			}
		} else {
			// If it's an empty panel that's not displaying a history item, just
			// remove it.
			this.removePanel(panel);
		}
	},

	/** Called when a menu button in the
	{@link WordSeer.view.desktop.topbar.WidgetsMenu} is clicked. Opens up the
	Widget corresponding to the clicked-on button's 'action' attribute.

	@param {Ext.button.Button} button The clicked-on menu button.
	*/
	launchWidgetFromWidgetsMenu: function(button) {
		this.start();
		var formValues = Ext.create('WordSeer.model.FormValues');
		formValues.widget_xtype =  button.action;
		var history_item = this.getController('HistoryController')
			.newHistoryItem(formValues);
		this.playHistoryItemInNewPanel(history_item.get('id'));
	},

	/** Called when the user uses the 'view as' combobox in the header
	of a {@link WordSeer.view.windowing.viewport.LayoutPanel} to change
	the widget displaying the search. Creates a new
	{@link WordSeer.model.HistoryItemModel} with all the same parameters as
	the existing search, but with a different
	{@link Wordseer.model.HistoryItemModel#widget_xtype}, and plays that history
	item in the same layout panel.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} layout_panel The panel
	whose combobox was changed.
	@param {String} new_xtype The xtype of the new widget selected.
	*/
	switchWidgets: function(layout_panel, new_xtype) {
		var layout_panel_model = layout_panel.getLayoutPanelModel();
		var old_history_item = Ext.getStore('HistoryItemStore').getById(
				layout_panel_model.get('history_item_id'));
		var old_xtype = old_history_item ? old_history_item.get('widget_xtype')
			: '';
		if (new_xtype != old_xtype) {
			var new_form_values = WordSeer.model.FormValues.deserialize(
				old_history_item.get('formValues'));
			new_form_values.widget_xtype = new_xtype;
			var new_history_item = this.getController('HistoryController')
				.newHistoryItem(new_form_values);
			this.playHistoryItemInCurrentPanel(new_history_item.get('id'),
				layout_panel);
		}
	},

	showResultMenu: function(view, record, selected) {
		if (record) {
			var id = record.get('id');
			var row_element = view.getEl().down('tr[record=' + id + ']');
			this.destroyResultMenu(view, record);
			view.getEl().select('tr.hovered').removeCls('hovered');
			var menu = Ext.create('WordSeer.view.menu.ResultListMenu', {
				type: view.xtype == 'sentence-list'? 'sentence' : 'document',
				sentenceId: view.xtype == 'sentence-list'? record.get('id'): false,
				documentId: view.xtype == 'sentence-list'? record.get('document_id')
				: record.get('id'),
			});
			$(row_element).addClass('hovered');
			menu.showBy(row_element, 'tl-bl?');
		}
	},

	destroyResultMenu: function(view, record, selected) {
		var candidates = Ext.ComponentQuery.query('result-list-menu');
		candidates.forEach(function(c) { c.close(10); });
	},



	dispatchUrlToken: function(token){
		if (token == 'home'){
			// show landing page
			this.land();

		} else if (/^panels:/.test(token)) {
			// make sure controller is ready to display windows
			if (!this.initialized) {
				this.start();
			}
			// parse the token
			var parts = token.split(":");
			var panel_itemids = [];
			var history_ids = [];

			for (var i = 1; parts[i]; i++) {
				var panel_parts = parts[i].split("_");
				panel_itemids.push(panel_parts[0]);
				history_ids.push(panel_parts[1]);
			}

			// get current panels
			var panels = Ext.getCmp("windowing-viewport").query("layout-panel");
			var active_panels = [];
			for (var i = 0; panels[i]; i++){
				active_panels.push(panels[i].itemId)
			}

			for (var i = 0; active_panels[i]; i++) {
				if (panel_itemids.indexOf(active_panels[i]) == -1) {
					// if panel isn't in token list, close it
					this.closePanel(panels[i]);
				} else if (history_ids[i] !=
						   Ext.getStore("HistoryItemStore")
						       .findRecord("layout_panel_id", active_panels[i])
							       .internalId
						  ) {
					// if there's a history change for a panel, update it
					this.playHistoryItemInCurrentPanel(history_ids[i], panels[i]);
				}
			}

			// if token isn't in window, play history item in new panel
			// with the requested id
			for (var i = 0; panel_itemids[i]; i++) {
				if (active_panels.indexOf(panel_itemids[i]) == -1) {
					this.playHistoryItemInNewPanel(history_ids[i],
						panel_itemids[i]);
				}
			}
		}
	},

});
