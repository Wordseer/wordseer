/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Stores all the parameters of an action in WordSeer: search query parameters,
which {@link WordSeer.view.widget.Widget} was opened, which document or sentence
it was. FormValues objects are stored in
{@link WordSeer.model.HistoryItemModel}s, which also store the time of the
action and whether or not the results are currently being displayed.
*/
Ext.define('WordSeer.model.FormValues', {
	/**
	@property {String} widget_xtype The xtype of the
	{@link WordSeer.view.widget.Widget} in which this search should be performed.
	*/
	widget_xtype: '',

	/**
	@property {Number} query_id The ID of this query, for use by server-side
	caches.
	*/
	query_id: '',

	/**
	@property {Boolean} separate_sub_searches Whether or not each search in the
	list of searches is to be assigned a separate query ID. Useful for
	visualizations such as the WordFrequencies view that can be used to compare
	the results of multiple searches. In this case, the main query_id will
	represent the results that match ALL the searches.
	*/
	separate_sub_searches: false,

	/**
	@property {String|Integer} gov The gov part of the search query. Blank is
	unspecified and will match all govs in a grammatical search. If the
	query is not a grammatical search, and is just a keyword search,
	this field is the search string. If the {@link #govtype} is 'phrase-set',
	then this field is the ID of the word set.
	*/
	gov: '',

	/**
	@property{String|Integer} dep: The dep part of the search query. Blank is unspecified
	and will match all deps in a grammatical search. Is an integer when
	{@link #deptype} is phrase-set, the ID of the word set.
	*/
	dep: '',

	/**
	@property {String} govtype: either "word" or "phrase-set", the type of the
	gov search query.
	*/
	govtype: 'word',

	/**
	@property {String} govtype: either "word" or "phrase-set", the type of the
	dep search query.
	*/
	deptype: 'word',

	/**
	@property {Integer} relation: the ID of the
	{@link WordSeer.store.GrammaticalRelationsStore grammatical relation}.
	*/
	relation:"",

	/**
	@property {Boolean} all_word_forms  Whether to match all the word forms of
	the words in the search query, or just the exact one that the user typed in.
	*/
	all_word_forms: 'off',

	/**
	@property {Array[formValues]} search: The set of searches already
	performed in this widget. (See
	{@link WordSeer.view.visualize.columnvis.ColumnVis}) for an example of a
	widget where multiple search queries are used.
	*/
	search:[],

	/**
	@property {Array[Metadata]} metadata: The metadata filters
	applied to the search.
	*/
	metadata:[],

	/**
	@property {WordSeer.model.DocumentSetsModel} collection The collection within
	which to search (defaults to 'all').
	*/
	collection: 'all',

	/**
	@property {Array[WordSeer.model.PhraseModel | WordSeer.model.WordModel]} phrases
	The words and phrases that are acting as filters.
	*/
	phrases: [],

	/**
	@property {Number} timing  A debug parameter. Set to 0 by default.
	Setting this to 1 will produce debut output (with timing statements)
	on the server side.
	*/
	timing: 0,

	/** @property {Number} document_id (Optional, except if used as input to the
	{@link WordSeer.view.document.DocumentViewer}). The ID of the document to
	view.
	*/
	document_id: "",

	/**
	@property {Number} sentence_id (Optional, except if used as input to the
	{@link WordSeer.view.document.DocumentViewer}). The ID of the sentence
	to zoom in on.
	*/
	sentence_id: "",

	/** Sets the fields for a new {@link WordSeer.model.FormValues} object.
	*/
	constructor: function(config) {
		this.initConfig(config);
		this.gov = "";
		this.dep = "";
		this.govtype = "word";
		this.deptype = "word";
		this.relation = "";
		this.widget_xtype = "";
		this.all_word_forms = "off";
		this.query_id = "";
		this.search = [];
		this.phrases = [];
		this.metadata = [];
		this.collection = "all";
		this.document_id = "";
		this.sentence_id = "";
		this.timing = 0;
		this.separate_sub_searches = true;
		Ext.apply(this, config);
		this.callParent(arguments);
	},

	statics: {
		/** Outputs a breadcrumb-like representation of a serialized
		FormValues object.
		@param {Object} serialized_values The result of calling {@link #serialize}
		on a {@link WordSeer.model.FormValues} object.
		*/
		toHtml: function(serialized_values, separator) {
			var terms = [];

			var grammaticalRelationsStore = Ext.getStore('GrammaticalRelationsStore');

			// The document ID if there was one.
			try {
				if (serialized_values.document_id != null && serialized_values.document_id != "") {
					var document = Ext.getStore('DocumentStore').getById(
					    parseInt(serialized_values.document_id));
					terms.push ('<span class="breadcrumb"> document: '
						+ document.get('title') + "</span>");
				}
			} catch (error) {
				console.log(error);
			}
			// The search terms.
			var me = this;
			try {
				if (serialized_values.hasOwnProperty('search')
					&& serialized_values.search.length > 0) {
					var searches = Ext.decode(serialized_values.search);
					searches.forEach(function(search) {
						var term = "<span class='search breadcrumb'>";
						if (search.all_word_forms) {
							term += "[all word forms of] ";
						}
						if (search.govtype != 'phrase-set') {
							term += search.gov
						} else {
							term += Ext.getStore('PhraseSetStore').getById(search.gov)
								.get('text');
						}
						if (search.relation != "") {
							var relation = grammaticalRelationsStore.getById(
								search.relation);
							if(relation){
								term += " <span class='relation'>"
								+ relation.get('name') +"</span> ";
							}
						}
						if (search.deptype != 'phrase-set') {
							term += search.dep
						} else {
							term += Ext.getStore('PhraseSetStore').getById(search.dep)
								.get('word')
						}
						term += "</span>"
						terms.push(term);
					})
				}
			} catch (error) {
				console.log(error);
			}
			// The phrase terms
			try {
				if (serialized_values.phrases && serialized_values.phrases.length > 0){
				var phrases = Ext.decode(serialized_values.phrases);
					if (phrases) {
						phrases.forEach(function(phrase) {
							var components = phrase.split("_")
						    var text = components[2];
						    terms.push("<span class='breadcrumb'>\"" + text + "\"</span>");
						})
					}
				}
			} catch (error) {
				console.log(error);
			}
			// The metadata terms
			try {
				if (serialized_values.metadata && serialized_values.metadata.length > 0){
					var metadata = Ext.decode(serialized_values.metadata);
					var properties = keys(metadata);
					for (var i = 0; i < properties.length; i++) {
						var identifier = properties[i];
						var components = identifier.split("_");
						var type = components[0];
						var property = components.slice(1).join("_");
						var metadata_serialized_values = metadata[identifier];
						metadata_serialized_values.forEach(function(val) {
							if (type != "string") {
								value = value[0] +" -- "+value[1];
							} else {
								var components = val.split("__");
								var value = components[0];
							}
							terms.push("<span class='breadcrumb'>" + property
								+ ": " + value + "</span>");
						});
					}
				}
			} catch (error) {
				console.log(error);
			}
			// The collection terms
			try {
				if (serialized_values.collection) {
					if (serialized_values.collection != 'all') {
						var id = parseInt(serialized_values.collection);
						var collection = null;
						if (Ext.getStore('DocumentSetStore').getById(id)) {
							collection = Ext.getStore('DocumentSetStore')
								.getById(id);
						} else if (Ext.getStore('SentenceSetStore')
							.getById(id)) {
							collection = Ext.getStore(
								'SentenceSetStore').getById(id);
						} else if (Ext.getStore('PhraseSetStore')
							.getById(id)) {
							collection = Ext.getStore(
								'PhraseSetStore').getById(id);
						}
						if (collection != null) {
							terms.push ('<span class="breadcrumb">within: '
								+ collection.get('text') + "</span>");
						}
					}
				}
			} catch (error) {
				console.log(error);
			}
			if (!separator) {
				separator = " ";
			}
			return terms.join(separator);
		},


		/** Returns a formValues object from a serialized JSON string.
		@param {Object} serialized A serialized FormValues object, such as the one
		produced by the {@link #serialize} function.
		@return {WordSeer.model.FormValues} a FormValues object.
		*/
		deserialize: function(serialized) {
			if (typeof(serialized) != "object") {
				return Ext.create('WordSeer.model.FormValues');
			} else {
				var formValues = Ext.create('WordSeer.model.FormValues');
				Ext.apply(formValues, serialized);
				formValues.search = Ext.decode(serialized.search);
				var collection = null;
				var id = parseInt(serialized.collection);
				// if (Ext.getStore('DocumentSetStore').getById(id)) {
				// 	collection = Ext.getStore('DocumentSetStore')
				// 		.getById(id);
				// } else if (Ext.getStore('SentenceSetStore')
				// 	.getById(id)) {
				// 	collection = Ext.getStore(
				// 		'SentenceSetStore').getById(id);
				// } else if (Ext.getStore('PhraseSetStore')
				// 	.getById(id)) {
				// 	collection = Ext.getStore(
				// 		'PhraseSetStore').getById(id);
				// }

				formValues.collection = (serialized.collection == 'all'
					|| (collection == null)) ? 'all' : collection;

				formValues.widget_xtype = serialized.widget_xtype;

				formValues.phrases = [];
				var phrases = Ext.decode(serialized.phrases);
				for (var i = 0; i < phrases.length; i++) {
					var components = phrases[i].split("_");
					var model =  (components[0] == 'word')? WordSeer.model.WordModel :
						WordSeer.model.PhraseModel;
					formValues.phrases.push(new model({
						class: components[0],
						id: components[1],
						sequence: components[2],
						word: components[2],
					}));
				}

				formValues.metadata = [];
				var metadata = Ext.decode(serialized.metadata);
				var identifiers = keys(metadata);
				for (var i = 0; i < identifiers.length; i++) {
					var identifier = identifiers[i].split("_");
					var type = identifier[0];
					var propertyName = identifier.slice(1).join("_");
					var field = (type == "string") ? "text" : "range";
					for (var j = 0; j < metadata[identifiers[i]].length; j++){
						var record = Ext.create('WordSeer.model.MetadataModel', {
							propertyName: propertyName,
							type: type,
						})
						var values = metadata[identifiers[i]][j];
						if (type != "string") {
							record.set(field, values)
						} else {
							values = values.split("__");
							record.set(field, values[0]);
							if (values.length > 0){
								record.set("value", values[1]);
							}
						}
						formValues.metadata.push(record);
					}
				}
				return formValues;
			}
		},
	},

	/** Returns a copy of the search query represented by this object in a
	format suitable for sending to the server and for storing in local history.
	@return {Object} The serialized version of this formValues object.
	*/
	serialize: function() {
		var formValues = {
			gov: this.gov,
			dep: this.dep,
			relation: this.relation,
			govtype: this.govtype,
			deptype: this.deptype,
			all_word_forms: this.all_word_forms,
			collection: (this.collection == 'all' ? 'all' :
				this.collection.get('id')),
			document_id: this.document_id,
			sentence_id: this.sentence_id,
			search: JSON.stringify(this.search),
			widget_xtype: this.widget_xtype,
			query_id: this.query_id,
			separate_sub_searches: this.separate_sub_searches
		};
		var phrases = [];
		for (var i = 0; i < this.phrases.length; i++) {
			var sequence = (this.phrases[i].get('class') == "word") ?
				this.phrases[i].get('word') : this.phrases[i].get('sequence');
			phrases.push(this.phrases[i].get('class') + '_'
				+ this.phrases[i].get('id') + "_"
				+ sequence);
		}
		formValues.phrases = JSON.stringify(phrases);

		var metadata = {};
		for (var i = 0; i < this.metadata.length; i++) {
			var record = this.metadata[i];
			var identifier = (record.get('type') + "_"
				+ record.get('propertyName'));
			if (typeof(metadata[identifier]) ==  "undefined") {
				metadata[identifier] = []
			}
			if (record.get('type') == "string") {
				metadata[identifier].push(record.get('text')+"__"+record.get('value'));
			} else {
				metadata[identifier].push(record.get('range'));
			}
		}
		formValues.metadata = JSON.stringify(metadata);
		return formValues;
	},

	/** Returns an independent copy of this FormValues object.
	@return {WordSeer.model.FormValues} A new formValues object that has the
	same field query values as this one. Modifying the retured object has no
	effect on this one.
	*/
	copy: function() {
		var string = JSON.stringify(this.serialize());
		var decoded = Ext.decode(string);
		var formValues = WordSeer.model.FormValues.deserialize(decoded);
		return formValues;
	},

	/** Outputs a breadcrumb-like representation of a serialized
	FormValues object.
	@param {Object} serialized_values The result of calling {@link #serialize}
	on a {@link WordSeer.model.FormValues} object.
	*/
	toText: function(separator) {
		var terms = [];
		if (!this.grammaticalRelationsStore) {
			this.grammaticalRelationsStore = Ext.getStore('GrammaticalRelationsStore');
		}
		// The document ID if there was one.
		try {
			if (this.document_id != null && this.document_id != "") {
				var document = Ext.getStore('DocumentStore').getById(
				    parseInt(this.document_id));
				terms.push ('document: '
					+ document.get('title'));
			}
		} catch (error) {
			console.log(error);
		}
		// The search terms.
		var me = this;
		try {
			this.search.forEach(function(search) {
				var term = "";
				if (search.all_word_forms) {
					term += "[all word forms of] ";
				}
				if (search.govtype != 'phrase-set') {
					term += search.gov
				} else {
					term += Ext.getStore('PhraseSetStore').getById(search.gov)
						.get('text');
				}
				if (search.relation != "") {
					var relation = me.grammaticalRelationsStore.getById(
						search.relation);
					if(relation){
						term += " " + relation.get('name');
					}
				}
				if (search.deptype != 'phrase-set') {
					term += search.dep
				} else {
					term += Ext.getStore('PhraseSetStore').getById(search.dep)
						.get('word')
				}
				terms.push(term);
			})
		} catch (error) {
			console.log(error);
		}
		// The phrase terms
		try {
			if (this.phrases) {
				this.phrases.forEach(function(phrase) {
					var components = phrase.get('id').split("_")
				    var text = components[2];
				    terms.push(text);
				})
			}
		} catch (error) {
			console.log(error);
		}
		// The metadata terms
		try {
			for (var i = 0; i < this.metadata.length; i++) {
				var record = this.metadata[i];
				var property = record.get('propertyName');
				var value = record.get('value');
				var type = record.get('type');
				if (type != "string") {
					value = "(" + value[0] +" -- "+value[1] +")";
				} else {
					value = value.split("__")[0];
				}
				terms.push(property
					+ "=" + value );
			}
		} catch (error) {
			console.log(error);
		}
		// The collection terms
		try {
			if (this.collection) {
				if (this.collection != 'all') {
						terms.push ('within: '
							+ collection.get('text'));

				}
			}
		} catch (error) {
			console.log(error);
		}
		if (!separator) {
			separator = " ";
		}
		return terms.join(separator);
	},

	/**
	Checks whether the given formValues object represents the same slice of
	data as this one.
	@param {Object/WordSeer.model.FormValues} other_form_values The serialized
	 other form values.
	@return {Boolean} True if the two formValues represent the same slice.
	*/
	sameSlice: function(other_serialized_form_values) {
		var serialized = this.serialize();
		serialized.widget_xtype = other_serialized_form_values.widget_xtype;
		serialized.query_id = other_serialized_form_values.query_id;
		return JSON.stringify(serialized) ==
		JSON.stringify(other_serialized_form_values);
	}
})
