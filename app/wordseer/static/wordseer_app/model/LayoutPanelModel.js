/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.model.LayoutPanelModel', {
	extend: 'Ext.data.Model',
	requires: [
		'WordSeer.store.MetadataTreeStore',
	],
	fields: [
		{type: 'string', name: 'id'},
		{type: 'int', name: 'layout_id'},
		{type: 'string', name: 'name'},
		{type: 'string', name:'history_item_id', default:''},
		{type: 'auto', name: 'previous_history_items', default: []},
		{type: 'int', name: 'index_from_last', default:0},
	],

	constructor: function(cfg) {
		this.initConfig(cfg);
		Ext.apply(this, cfg);
		this.callParent(arguments);
		this.phrasesStore = Ext.create('WordSeer.store.PhrasesStore');
		this.metadataTreeStore = Ext.create('WordSeer.store.MetadataTreeStore');
		this.JStore = Ext.create('WordSeer.store.AssociatedWordsStore', {pos:'Adjectives'});
		this.VStore = Ext.create('WordSeer.store.AssociatedWordsStore', {pos:'Verbs'});
		this.NStore = Ext.create('WordSeer.store.AssociatedWordsStore', {pos:'Nouns'});
		this.topJ = Ext.create("WordSeer.store.FrequentWordsStore", {pos: "J"});
		this.topN = Ext.create("WordSeer.store.FrequentWordsStore", {pos: "N"});
		this.topV = Ext.create("WordSeer.store.FrequentWordsStore", {pos: "V"});
		this.metadataListStore = Ext.create('WordSeer.store.MetadataListStore');
		this.breadcrumbs = [];
	},

	config: {
		/**
		@cfg {WordSeer.store.PhrasesStore} phrasesStore The store for the
		list of phrases for this search.
		*/
		phrasesStore: false,

		/**
		@cfg {Object} stringFacetsStore The hierarchical metadata related to
		this slice.
		*/
		metadataTreeStore: false,

		JStore: false,
		VStore: false,
		NStore: false,

		topJ: false,
		topN: false,
		topV: false,

		/**
		@cfg {WordSeer.store.MetadataListStore} metadataListStore The metadata
		list store backing the metadata combobox.
		*/
		metadataListStore: false,

		breadcrumbs: []
	},

	addHistoryItem: function(history_item) {
		if (this.get('previous_history_items') === "") {
			this.set('previous_history_items', []);
		}
		var history_list_view = Ext.getCmp('historylist');
		if (this.get('history_item_id') !== '') {
			var old_history_item = Ext.getStore('HistoryItemStore').getById(
				this.get('history_item_id'));
			if (old_history_item) {
				old_history_item.set('layout_panel_id', "");
				if (history_list_view) {
					history_list_view.deselect(old_history_item,
						true);  // Pass in 'true' to suppress the deselect event.
				}
			}
		};
		this.set('history_item_id', history_item.get('id'));
		if (this.get('history_item_id') != '') {
			this.get('previous_history_items').push(
				this.get('history_item_id'));
		}
		this.set('index_from_last', 0);
		history_item.set('layout_panel_id', this.get('id'));
		Ext.getStore('LayoutStore').sync();
	},

	getFormValues: function() {
		var history_item = Ext.getStore('HistoryItemStore')
		.getById(this.get('history_item_id'));
		if (history_item) {
			return WordSeer.model.FormValues.deserialize(
				history_item.get('formValues'));
		} else {
			return Ext.create('WordSeer.model.FormValues');
		}
	},

	isSameSlice: function() {
		if (this.get('previous_history_items').length > 1) {
			var this_slice = this.getFormValues();
			var previous_id = this.get('previous_history_items')[
			this.get('previous_history_items').length - 2];
			if (previous_id) {
				return this_slice.sameSlice(Ext.getStore('HistoryItemStore')
					.getById(previous_id).get('formValues'));
			} else {
				return false;
			}
		} else {
			return false;
		}
	}
});
