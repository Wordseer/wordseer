/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls the issuing of search queries and the assembling of search
parameters from the {@link WordSeer.view.search.GrammaticalSearchForm}.
*/
Ext.define('WordSeer.controller.SearchController', {
	extend: 'Ext.app.Controller',
	requires: [
		'WordSeer.store.DocumentSetListStore',
		'WordSeer.store.GrammaticalRelationsStore',
	],
	views: [
		'widget.Widget',
		'search.UniversalSearchForm',
		'search.GrammaticalSearchForm',
		'search.DocumentSetsComboBox',
		'search.PhraseSetComboBox',
	],
	stores: [
		'GrammaticalRelationsStore',
		'DocumentSetListStore',
		'SentenceSetListStore',
		'HistoryItemStore',
		'LayoutStore',
	],
	models: [
		'HistoryItemModel',
		'LayoutModel',
		'FormValues',
	],
	/**
	@property {Boolean} server_side_caching Whether or not we're using server-side
	query caching to avoid doing duplicate work for each sub-part of a widget
	(i.e. avoiding duplicate filter actions for each word list, the phrases list
	and the metadata pane, and the main widget content).
	*/
	server_side_caching: true,

	init: function() {
//		console.log("Initialized search controller");
		Ext.Ajax.request({
			url:'../../src/php/document/get-metadata-fields.php',
			method:'GET',
			disableCaching: false,
			params:{
				instance:getInstance(),
				unit: 'sentence'
			},
			scope:this,
			success:function(response){
				var data = Ext.decode(response.responseText);
				var newFields = [
					{name:'sentence', type: 'auto'},
					{name: 'id', type:'int'},
					{name: 'document_id', type: 'int'},
					{name: 'sentence_set', type: 'string', defaultValue:"", hidden: true},
				];
				for (var i = 0; i < data.length; i++) {
					newFields.push({
						text: data[i].nameToDisplay,
						name: data[i].propertyName,
						type: data[i].type == 'number'? 'float': 'auto',
						sortType: data[i].type == 'number'? 'asFloat': '',
						hidden: data[i].valueIsDisplayed === 0,
					});
				}
				WordSeer.model.SentenceSearchResultModel.setFields(newFields);
			}
		});
		this.control({
			'layout-panel': {
				initSearch: this.initSearch,
				searchParamsChanged: this.searchParamsChanged,
			},
			'landing-page tag-list': {
				tagClicked: this.tagClicked,
			},
			'widget' : {
				searchWith: this.searchWith,
			},
			'button[action=search]': {
				click: this.searchButton,
			},
			'grammaticalrelationscombobox': {
				select: this.updateFormSubmittable,
			},
			'autosuggest-textfield': {
				specialkey: this.SearchBoxKeypress,
				change: this.SearchBoxChange,
			},
			'stringfacet > treepanel': {
				itemclick: this.metadataFilterChanged,
			},
		});
	},

	/**
	The user has clicked on a tag in the landing page. Create a new search based
	on that tag.
	*/
	tagClicked: function(tag_list_overview, record) {
		if (!this.getController('WindowingController').initialized) {
			this.getController('WindowingController').start();
		}

		var formValues = Ext.create('WordSeer.model.FormValues');
		formValues.widget_xtype = 'sentence-list-widget';
		if (record instanceof WordSeer.model.PhraseModel ||
			record instanceof WordSeer.model.WordModel) {
			// will be different property if single word or phrase
			var gov = record.data.word ? record.data.word : record.data.sequence;

			var values = {
				"gov": gov,
				"govtype": "word",
				"dep": "",
				"deptype": "word",
				"relation": "",
			};
			Ext.apply(formValues, values);
			formValues.search.push(values);
		} else if (record instanceof WordSeer.model.MetadataModel ){
			formValues.metadata.push(record);
		}
		var history_item = this.getController('HistoryController')
			.newHistoryItem(formValues);
		this.getController('WindowingController')
			.playHistoryItemInNewPanel(history_item.get('id'));
	},

	/** The user has clicked the search button on the
	{@link WordSeer.view.search.GrammaticalSearchForm GrammaticalSearchForm}.
	Reads the form values and issues a search to the current
	{@link WordSeer.view.windowing.viewport.LayoutPanel LayoutPanel}.

	@param {Ext.button.Button} button The button that was clicked.
	*/
	searchButton: function(button) {
		if (!this.getController('WindowingController').initialized) {
			this.getController('WindowingController').start();
		}
		// Get the form values.
		var form = button.up('form');
		var values = form.getValues();

		var formValues = Ext.create('WordSeer.model.FormValues');
		Ext.apply(formValues, values);
		Ext.apply(formValues, {
			widget_xtype: values.widget_xtype,
		});
		// Add any autocompleted metadata values
		var autosuggest = form.down('phrases-autosuggest');
		var was_metadata_search = false;
		if (autosuggest.record) {
			if (autosuggest.record.get('class') == 'metadata') {
				was_metadata_search = true;
				var record = Ext.create('WordSeer.model.MetadataModel', {
				    text: autosuggest.record.get('value'),
				    value: autosuggest.record.get('value'),
				    propertyName: autosuggest.record.get('property_name')
				});
				formValues.metadata.push(record);
			}
		}
		// close the autosuggest menu
		Ext.ComponentQuery.query("autosuggest-menu")[0].hide();

		var target = values.target;
		if (target == 'new') {
			// Make a new history item from the values.
			if (!was_metadata_search) {
				formValues.search = [values];
			}
			var history_item = this.getController('HistoryController')
				.newHistoryItem(formValues);
			this.getController('WindowingController')
				.playHistoryItemInNewPanel(history_item.get('id'));
		} else {
			// Get the current panel of the layout
			var layout_model = Ext.getStore('LayoutStore').getCurrent();
			var view = Ext.getCmp(layout_model.get('id'));
			if (!view) {
				view = Ext.getCmp('windowing-viewport').addLayout(layout_model);
			}
			var current_panel = view.getCurrentPanel();
			if (!current_panel) {
				current_panel = this.getController('WindowingController')
					.addPanel();
			} else {
				old_history_item = Ext.getStore('HistoryItemStore').getById(
					current_panel.getLayoutPanelModel().get('history_item_id'));
				if (old_history_item) {
					old_form_values = WordSeer.model.FormValues.deserialize(
						old_history_item.get('formValues'));
					formValues = old_form_values.copy();
					Ext.apply(formValues, values);
				}
			}
			if ((formValues.widget_xtype == 'column-vis-widget'
				|| formValues.widget_xtype == 'word-frequencies-widget')) {
				formValues.search.push(values);
			} else {
				if (was_metadata_search) {
					formValues.search = [values];
				}
			}
			// Make a new history item from the values.
			var history_item = this.getController('HistoryController')
				.newHistoryItem(formValues);
			this.getController('WindowingController').playHistoryItemInCurrentPanel(
				history_item.get('id'),
				current_panel);
		}
		return false;
	},

	/** Adds a breadcrumb representing a search to the given panel's
	{@link WordSeer.view.widget.Widget Widget} and then calls
	{@link #assembleSearchParamsAndSearch}.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} current_panel The
	panel in which the search should be performed.

	*/
	addNewSearch: function(current_panel) {
		var widget = current_panel.down('widget');
		var formValues = WordSeer.model.FormValues.deserialize(
			widget.getHistoryItem().get('formValues'));
		this.search(widget, formValues);
	},

	/** Responds to a click on a
	{@link WordSeer.view.wordmenu.GrammaticalSearchOption} within a
	{@link WordSeer.view.wordmenu.WordMenu}. Issues a search 'corresponding to'
	a word, grammatical relationship, word set, or something similar.

	The function assembles a set of {@link WordSeer.model.FormValues} objects
	corresponding to the
	{@link WordSeer.view.wordmenu.WordMenu#current current wordmenu word},
	then creates a new history item by calling
	{@link WordSeer.controller.HistoryController#newHistoryItem}, and then calls
	{@link #addNewSearch}.
	*/
	searchWith:function(widget_info, item){
		var values = Ext.create('WordSeer.model.FormValues');
		values.widget_xtype = widget_info.widget_xtype;
		var okToSearch = false;
		if (item.class == 'metadata'){
			console.log('metadata searchwith')
			values.metadata = item.metadata;

			var history_item = this.getController('HistoryController')
				.newHistoryItem(values);
			history_item.set('widget_xtype', widget_info.widget_xtype);
			this.getController('WindowingController')
				.playHistoryItemInNewPanel(history_item.get('id'));
		} else if(item.getClass() == 'word'){
			values.gov = item.get('word');
			okToSearch = true;
		}
		else if(item.getClass() == 'grammatical'){
			if(item.get('gov')){
				values.gov = item.get('gov');
				values.govtype = item.get('govtype');
			}
			if(item.get('dep')){
				values.dep = item.get('dep')
				values.deptype = item.get('deptype')
			}
			if(item.get('relation')){
				values.relation = item.get('relation')
			}
			okToSearch = true
		}
		else if (item.getClass() == 'phrase-set'){
			values.gov = item.get('id');
			values.govtype = 'phrase-set';
			okToSearch = true;
		}


		// TODO: implement searchWith for phrases.
		if(okToSearch){
			values.search = [{
				gov: values.gov,
				dep: values.dep,
				relation: values.relation,
				govtype: values.govtype,
				deptype: values.deptype,
			}];
			var history_item = this.getController('HistoryController')
				.newHistoryItem(values);
			history_item.set('widget_xtype', widget_info.widget_xtype);
			this.getController('WindowingController')
				.playHistoryItemInNewPanel(history_item.get('id'));
		}
	},

	/** Responds to a browse action or any other change in search parameters
	within a panel. Adds a new history item and calls
	{@link #assembleSearchParamsAndSearch}

	@param {WordSeer.model.FormValues} formValues the new formValues
	*/
	searchParamsChanged: function(panel, formValues) {
		formValues.widget_xtype =
		panel.getLayoutPanelModel().getFormValues().widget_xtype;
		var history_item = this.getController('HistoryController')
			.newHistoryItem(formValues);
		this.getController('WindowingController').playHistoryItemInCurrentPanel(
			history_item.get('id'), panel);
	},

	/** Fires the `search` event with the new formValues on each child component
	in the widget. Also informs the {@link WordSeer.view. metadata
	components and the phrases list so they can update their values. Updates
	the widget's current history item to contain the complete set of parameters
	for the search record.

	@param {WordSeer.view.windowing.viewport.LayoutPanel} The panel on which the
	new search is being issued.

	@param {WordSeer.model.FormValues} formValues The {@link #} FormValues object containing the
	new search parameters.
	*/
	initSearch: function(panel, formValues) {
		formValues.query_id = this.current_query_id;
		panel.formValues = formValues;
		var widget = panel.down('widget');
		if (widget) widget.setFormValues(formValues);
		if (APP.getSearchableWidgets().indexOf(formValues.widget_xtype) >= 0) {
			if(formValues) {
				var form = Ext.getCmp('universal-search-form');
				if (form) {
					form.getForm().setValues(formValues);
				}
				if (panel.getLayoutPanelModel().isSameSlice()) {
					// If it's not a new slice, we don't need a new query ID.
					// We can just reuse the old one.
					if (widget)
						this.relaySearchToWidgetComponents(widget, formValues);
				} else {
					// If it's a new slice, we're going to need a new query ID.
					var parameters = formValues.serialize();
					parameters.user = getUsername();
					parameters.instance = getInstance();
					// clear the previous query ID from the cache.
					Ext.Ajax.request({
						method: 'GET',
						url: '../../src/php/caching/caching.php',
						timeout: 90000000,
						params: {
							user: getUsername(),
							instance: getInstance(),
							query_id: this.current_query_id,
							clear: 'true',
						}
					});
					Ext.Ajax.request({
						method: 'GET',
						url: '../../src/php/caching/caching.php',
						timeout: 90000000,
						params: parameters,
						disableCaching: false,
						scope: this,
						success: function(response) {
							if (response) {
								var data = Ext.decode(response.responseText);
								var ok = data.ok;
								if (ok) {
									var query_id = data.query_id;
									this.current_query_id = query_id;
									formValues.query_id = query_id;
									panel.formValues.query_id = query_id;
									var widget = panel.down("widget");
									// die here if user has already hit back/fwd
									if (!widget) {return false;}
									widget.formValues.query_id = query_id;
								}
								panel.fireEvent('newSlice', panel, formValues);
								this.relaySearchToWidgetComponents(widget,
									formValues);
							}
						}
					})
				}
			}
		}
	},

	/** Relays the search event to the various components of a given widget.
	@param {WordSeer.view.widget.Widget} The widget on which the new search
	is being issued.

	@param {WordSeer.model.FormValues} formValues The {@link #} FormValues object containing the
	new search parameters.
	*/
	relaySearchToWidgetComponents: function(widget, formValues){
		widget.items.each(function(item) {
			item.fireEvent('search', formValues, item);
		})
	},

	// Grammatical search form controls.
	updateFormSubmittable: function(combobox, newValue, oldValue, options){
		if(newValue == ""){
			combobox
			.up('form')
			.down('textfield[name="dep"]').hide();
		} else {
			combobox
			.up('form')
			.down('textfield[name="dep"]').show();
		}
		this.checkIfSubmittable(combobox.up('form'));
	},

	checkIfSubmittable: function(form, record){
		var values = form.getForm().getValues();
		if (record) {
			return true
		} else if((values.gov && (values.gov.length > 0
			|| values.govtype != 'word'))
			|| (values.dep && values.dep.length > 0)
			|| values.relation != ""){
			form.down('button').enable();
			return true;
		} else {
			form.down('button').disable();
			return false;
		}
	},

	/** Checks whether the enter key was pressed. If so, submits the form if
	it's submittable.
	@param {WordSeer.view.autosuggest.AutoSuggestTextField} searchbox The field in which the user
	is typing.
	@param {Ext.EventObject} e The keypress event.
	*/
	SearchBoxKeypress:function(searchbox, event){
		if (event.getKey() == event.ENTER) {
			this.typeIsWord = true;
			this.SearchBoxChange(searchbox);
			var submittable = this.checkIfSubmittable(searchbox.up('form'),
				searchbox.record);
			if (submittable) {
				this.searchButton(
					searchbox.up('form').down('button[action=search]'));
			}
		} else {
			searchbox.typeIsWord = true;
			this.checkIfSubmittable(searchbox.up('form'));
		}
		return true;
	},

	SearchBoxChange:function(searchbox, newValue, oldValue, options){
		var field = searchbox.getName()+"type";
		if(!searchbox.getRecord() || searchbox.getRecord().get('class') === "phrase") {
			searchbox.up('form').down('textfield[name="'+field+'"]')
				.setValue('word');
		} else if (searchbox.getRecord().get('class') === "phrase-set") {
			searchbox.up('form').down('textfield[name="'+field+'"]')
				.setValue('phrase-set');
		}

		this.checkIfSubmittable(searchbox.up('form'), searchbox.record);
	},

});
