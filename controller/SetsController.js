/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls the treeview panels that display and manage the user's collections
of documents, words, and sentences. The views that are controlled are:
*/
Ext.define('WordSeer.controller.SetsController', {
	extend: 'Ext.app.Controller',
	views: [
		'menu.Menu',
		'menu.NewSetMenuItem',
		'menu.RenameSetMenuItem',
		'menu.SetContextMenu',
		'collections.SetList',
		'document.DocumentGrid',
		'sentence.SentenceList',
	],
	models: [
		'SubsetModel',
	],
	stores: [
			'PhraseSetStore',
			'SentenceSetStore',
			'DocumentSetStore',
	],
	init: function() {
		Ext.getStore('DocumentSetStore').load({params:{user:getUsername()}});
		Ext.getStore('SentenceSetStore').load({params:{user:getUsername()}});
//		console.log('SetsController initialized');
		this.control({
			'layout-panel': {
				menuButtonClicked: function(panel, type, button) {
					if (type == 'sets') {
						this.showSetsOverlay(panel, button);
					}
				}
			},
			'sets-list': {
				deselect: this.toggleOptions,
				select: this.toggleOptions,
				itemMouseEnter: this.showSetContextMenu,
				itemMouseLeave: this.hideSetContextMenu,
				optionEvent: function(view, event, option, option_el) {

						if (option.option.action == 'new-set') {
							if (event == 'click') {
								this.showNewSetMenu(view, option, option_el);
							} else if (event == 'mouseleave') {
								this.hideNewSetMenu(view, option, option_el);
							}
					}
				}
			},
			// In the set context menu
			'set-context-menu > wordseer-menuitem[action="filter"]': {
				click: this.filterBySet
			},
			'set-context-menu > wordseer-menuitem[action="open-set"]': {
				click: function(menuitem) {
					this.openSet(menuitem.up('set-context-menu').record);
				}
			},
			'set-context-menu > wordseer-menuitem[action="delete-set"]': {
				click: this.deleteSet
			},
			'new-set-menuitem': {
				specialkey: this.newSet,
			},
			'rename-set-menuitem': {
				specialkey: this.renameSet,
			},

			// In the word menu:
			'create-and-add-menuitem': {
				specialkey: this.createAndAdd,
			},
			'set-menuitem[action="add"], set-menuitem[action="open"]': {
				click: this.addToSet
			},
			'set-menuitem[action="remove"]': {
				click: this.removeItems
			},

			// Other places
			'widget': {
				subsetTagClicked: this.subsetTagClicked,
			},
			'sentence-list, document-grid': {
				optionEvent: function(view, event, option, option_el) {
					if (event === 'click') {
						this.showAddRemoveMenu(view, option, option_el);
					} else if (event === 'mouseleave') {
						this.hideAddRemoveMenu(view, option, option_el);
					}
				},
				select: this.enableDisableSubsetOptions,
				deselect: this.enableDisableSubsetOptions
			},
			'windowing-viewport': {
				'setchanged': function() {
					var me = this;
					Ext.ComponentQuery.query('layout-panel').forEach(
						function(panel) {
							me.getController('MetadataController').getMetadata(
								panel.getLayoutPanelModel().getFormValues(), panel);
						});
				}
			},

		});
	},



	/** Disables the 'Delete Set' option on the
	{@link WordSeer.view.collections.SetList} if there isn't a set selected.
	@param {WordSeer.view.collections.SetList} view The view displaying the list
	of sets.
	*/
	toggleOptions: function(view) {
		var options = view.getEl().select(
			'span.databox-option > span.button');
		options.each(function(el) {
			var action = el.getAttribute('action');
			if (view.selected.getCount() === 0) {
				if (action == 'delete-set' || action == 'rename-set' ||
					action == 'open-set') {
					el.addCls('disabled');
				}
				if (action == 'new-set') {
					el.setHTML('New Set');
				}

			} else {
				if (action == 'delete-set' || action == 'rename-set' ||
					action == 'open-set') {
					el.removeCls('disabled');
				}
				if (action == 'new-set') {
					el.setHTML('New Subset');
				}
			}
		});
	},

	showSetContextMenu: function(view, record, row_element) {
		view.getEl().select('tr.hovered').removeCls('hovered');
		$(row_element).addClass('hovered');
		var menu = Ext.create('WordSeer.view.menu.SetContextMenu', {
			record: record,
			view: view,
			store: view.store
		});
		view.up('overlay').menuActive = menu;
		menu.showBy(row_element, 'tl-tr?');
	},

	hideSetContextMenu: function(view, record, row_element) {
		var candidates = Ext.ComponentQuery.query('set-context-menu');
		candidates.forEach(function(c) {
			c.close(10);
		});
	},

	/** Asks the server to delete the selected set by asking the store backing
	the {@link WordSeer.view.collections.SetList} calling
	{@link WordSeer.model.SubsetModel#delete} on each selected subset
	@param {WordSeer.view.menu.MenuItem} button The menuitem that was clicked.
	*/
	deleteSet: function(button) {
		var menu = button.up('set-context-menu');
		menu.record.delete(function(operation) {
			menu.store.load({params:{user:getUsername()}});
		}, this);
		if (menu.view.selected.length > 0 ){
			menu.view.selected.removeAll();
			this.toggleOptions(menuitem.view);
		}
	},

	/** Opens the given sentence or document collection in the appropriate view.
	@param {WordSeer.view.menu.MenuItem} button The menuitem that was clicked.
	*/
	openSet: function(record) {
		var formValues = Ext.create('WordSeer.model.FormValues');
		var metadata_record = Ext.create('WordSeer.model.MetadataModel', {
			text: record.get('text'),
			value: record.get('id'),
			propertyName: record.subsetType +"_set"
		});
		if (record.subsetType == "document") {
			formValues.widget_xtype = "document-browser-widget";
		} else if (record.subsetType == "sentence") {
			formValues.widget_xtype = "sentence-list-widget";
		} else {
			//formValues.widget_xtype = "sentence-list-widget";
			this.getController('PhraseSetsController').openPhraseSetWindow(
				record);
		}
		if (record.subsetType != 'phrase') {
			formValues.metadata.push(metadata_record);
			var history_item = this.getController('HistoryController')
				.newHistoryItem(formValues);
			this.getController('WindowingController').playHistoryItemInNewPanel(
				history_item.get('id'));
		}
	},

	/** Opens the given sentence or document collection in the appropriate view.
	@param {WordSeer.view.menu.MenuItem} button The menuitem that was clicked.
	*/
	filterBySet: function(menuitem) {
		var menu = menuitem.up('set-context-menu');
		var record = menu.record;
		var panel = menu.view.up('layout-panel');
		if (panel) {
			var formValues = panel.getLayoutPanelModel().getFormValues().copy();
			var metadata_record = Ext.create('WordSeer.model.MetadataModel', {
				text: record.get('text'),
				value: record.get('id'),
				propertyName: record.subsetType +"_set"
			});
			formValues.metadata.push(metadata_record);
			panel.fireEvent('searchParamsChanged', panel, formValues);
		}
	},


	/**
	Displays a drop-down menu of the currently-available collections, where
	clicking on a menu item will cause the selected items to be added to that
	collection.
	@param {WordSeer.view.table.Table} view The table containing the list of
	sentences or documents.
	@param {WordSeer.model.Option} option The clicked-on option.
	@param {Ext.Element} option_el The clicked-on element.

	*/
	showAddRemoveMenu: function(view, option, option_el) {
		var candidates = Ext.ComponentQuery.query('set-menu');
		if (candidates.length > 0) {
			this.hideAddRemoveMenu();
		} else {
			var selected_ids = [];
			view.selected.eachKey(function(id) {
				selected_ids.push(id+"");
			});
			if (selected_ids.length > 0) {
				var store = (view.xtype == 'sentence-list') ?
					Ext.getStore('SentenceSetStore')
					: Ext.getStore('DocumentSetStore');
				var menu = Ext.create('WordSeer.view.menu.SetMenu', {
					type: option_el.getAttribute('action'),
					store: store,
					ids: selected_ids
				});
				menu.showBy(option_el, 'tl-bl?');
			}
		}
	},

	/**
	Enables or disables the subset options depending on whether or not any
	sentences/documents are selected.
	*/
	enableDisableSubsetOptions: function(view, record, selected_items) {
		var options = view.getEl().select(
			'span.databox-option > span.button');
		if (selected_items.getCount() > 0) {
			options.each(function(el) {
				el.removeCls('disabled');
			});
		} else {
			options.each(function(el) {
				el.addCls('disabled');
			});
		}
	},

	/**
	Hides the Add/Remove menu when the user mouses out of the option.
	*/
	hideAddRemoveMenu: function() {
		var candidates = Ext.ComponentQuery.query('set-menu');
		if (candidates.length > 0) {
			candidates.forEach(function(c) {c.close(10);});
		}
	},


	/** Asks the server to create a new set by asking the store backing the
	{@link WordSeer.view.collections.SetList} (which is displaying
	the hierarchy of sets) to create a new item.
	@param {WordSeer.view.menu.NewSetMenuItem} The textfield containing the name
	of the new set.
	*/
	newSet: function(menuitem, event) {
		if (event.getKey() == event.ENTER) {
			var store = menuitem.getStore();
			var parent = menuitem.getParent();
			if (parent) {
				parent.newSet(function(operation) {
					store.load({params:{user:getUsername()}});
				}, this, menuitem.getValue());
			}
			menuitem.up('wordseer-menu').close(10);
		}
	},

	showNewSetMenu: function(view, option, option_el) {
		var menu = Ext.create('WordSeer.view.menu.Menu', {
			id: 'new-set-menu',
			items: [{
				xtype: 'new-set-menuitem',
				parent: view.getStore().getRootNode(),
				store: view.getStore()
			}]
		});
		view.up('overlay').menuActive = menu;
		menu.showBy(option_el, 'tl-bl?');
	},

	hideNewSetMenu: function() {
		var menu = Ext.getCmp('new-set-menu');
		if (menu) {
			menu.close(10);
		}
	},
	/** Called when the user edits the name of a set.
	@param {WordSeer.view.RenameSetMenuItem} menuitem The menuitem holding
	the new name of the set.
	*/
	renameSet: function(menuitem, event) {
		if (event.getKey() == event.ENTER) {
			var new_name = menuitem.getValue();
			var store = menuitem.getStore();
			menuitem.record.rename(new_name, function(){
				store.load({params:{user:getUsername()}});
				}, this);
			menuitem.up('wordseer-menu').close(10);
		}
	},


	/** Creates a new set and adds the menuitem's stored id's to the
	newly-created set.

	@param {WordSeer.view.menu.SetMenuItem} menuitem The new set.
	- {@link WordSeer.store.DocumentSetsStore} or
	{@link WordSeer.store.SentenceSetStore} store: the list of sets.
	- {Array} ids: A list of item ID's to add to the newly created set.
	*/
	createAndAdd: function(textfield, event) {
		if (event.getKey() == event.ENTER) {
			var store = textfield.getStore();
			store.getRootNode().newSet(function(operation){
				var data = Ext.decode(operation.response.responseText);
				var new_set_id = parseInt(data.id);
				WordSeer.model.SubsetModel.load(
					new_set_id, {
						scope: this,
						success: function(record){
							if (textfield.ids.length > 0) {
								record.addItems(textfield.ids, function(){
									textfield.store.load(
										{params:{user:getUsername()}});
									this.getController('MetadataController')
									.subsetsChanged();
								}, this);
							}
						}
					});
			}, this, textfield.getValue());
			textfield.up('wordseer-menu').close(10);
		}
	},

	/** Adds the menuitem's stored id's to the menuitem's stored set.

	@param {WordSeer.view.menu.SetMenuItem} menuitem A menu item with the additional properties
	- {@link WordSeer.model.SubsetModel} record: the set to which the
	ids should be added.
	- {Array} items: A list of item ID's to add to the newly created set.
	*/
	addToSet: function(menuitem) {
		menuitem.record.addItems(menuitem.items, function(){
			menuitem.getStore().load();
			this.getController('MetadataController').subsetsChanged();
		}, this);
	},

	/** Removes the menuitem's stored id's from the menuitem's stored set.

	@param {WordSeer.view.menu.SetMenuItem} menuitem A menu item with the additional properties
	- {@link WordSeer.model.SubsetModel} record: the set to which the
	ids should be added.
	- {Array} items: A list of item ID's to add to the newly created set.
	*/
	removeItems: function(menuitem) {
		menuitem.record.removeItems(menuitem.items, function(){
			menuitem.getStore().load();
			this.getController('MetadataController').subsetsChanged();
		}, this);
	},


	/** Triggered when the user clicks a
	{@link WordSeer.model.SubsetModel#makeSubsetTag}
	anywhere in the text.
	@param {Integer} id The ID of the subset.
	*/
	subsetTagClicked: function(id) {
		var record = "";
		var type = "";
		if (Ext.getStore("CollectionsStore").getById(id)) {
			record = Ext.getStore("CollectionsStore").getById(id);
			type = "document";
		} else if (Ext.getStore("SentenceSetStore").getById(id)) {
			record = Ext.getStore("SentenceSetStore").getById(id);
			type = "sentence";
		} if (Ext.getStore("PhraseSetStore").getById(id)) {
			record = Ext.getStore("PhraseSetStore").getById(id);
			type = "word";
		}
		if (type == "word") {
			this.getController('PhraseSetsController').openPhraseSetWindow(
				record.get('id'));
		} else {
			this.openSet(record);
		}
	},

	/**
	Shows the metadata filters overlay.
	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel The layout
	panel upon which to show the overlay.

	@param {HTMLElement} button The button under which to show this overlay like
	a menu.
	*/
	showSetsOverlay: function(panel, button) {
		if (!panel.getComponent('sets-overlay')) {
			var button_el = panel.getEl().down(
				'span.panel-header-menubutton.sets');
			var overlay = Ext.create('WordSeer.view.menu.MenuOverlay', {
				destroyOnClose: false,
				button: button_el,
				floatParent: panel,
				itemId: 'sets-overlay',
				width: 430,
				height: 450,
				items: [
					{
						xtype: 'sets-list',
						metadataStore: panel.getLayoutPanelModel()
							.getMetadataTreeStore(),
						type: 'phrase',
						store: Ext.getStore('PhraseSetStore'),
						title: 'Word/Phrase Sets',
						collapsed: true,
						columns: [
							{
								field: 'text',
								headerTitle: 'Set',
								headerCls: 'frequent-word-word',
								renderer: function(record, field) {
									return {
										tag: 'td',
										html: record.get(field),
										cls: 'frequent-word-word',
									};
								}
							},
							{
								field: 'phrases',
								headerTitle: 'Items',
								headerCls: 'frequent-word-count',
								renderer: function(record, field) {
									return {
										tag: 'td',
										html: record.get(field).length,
										cls: 'frequent-word-count',
									};
								}
							},
							{
								field: 'sentence_count',
								headerTitle: 'Sentences',
								headerCls: 'frequent-word-count',
								renderer: function(record, field, view) {
									var matched_sentence_count = view.getMatchedCount(
										record, 'count');
									return {
										tag: 'td',
										html: matched_sentence_count + "/" + record.get(field),
										cls: 'frequent-word-count',
									};
								}
							},
							{
								field: 'document_count',
								headerTitle: 'Documents',
								headerCls: 'frequent-word-count',
								renderer: function(record, field, view) {
									var matched_document_count = view.getMatchedCount(
										record, 'document_count');
									return {
										tag: 'td',
										html: matched_document_count + "/" + record.get(field),
										cls: 'frequent-word-count',
									};
								}
							}

						]
					},
					{
						xtype: 'sets-list',
						type: 'sentence',
						store: Ext.getStore('SentenceSetStore'),
						title: 'Sentence Sets',
						collapsed: true,
						metadataStore: panel.getLayoutPanelModel()
							.getMetadataTreeStore()
					},
					{
						xtype: 'sets-list',
						type: 'document',
						store: Ext.getStore('DocumentSetStore'),
						title: 'Document Sets',
						collapsed: true,
						metadataStore: panel.getLayoutPanelModel()
							.getMetadataTreeStore()
					}
				]
			});
			overlay.showBy(button_el);
			panel.add(overlay);
		}
	}

});
