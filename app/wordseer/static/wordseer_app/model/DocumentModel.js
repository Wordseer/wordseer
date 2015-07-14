	/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a Document in WordSeer.

Each record has the following fields. In addition, any metadata attached
to documents are queried from the server and added as fields to this model
during initialization.

@cfg {boolean} has_text Whether or not this record includes the full text
of the document.

@cfg {Object} units The list of units that make up this documents, each with
their type, id, (and text if the type is 'sentence').

@cfg {Object} children An associative array of parent unit ID's to a
list of child ID's

@cfg {Object} metadata An associative array of unit ID's to an array of
name-value metadata fields.

@cfg {Number} matches Only filled in when there is a search query, the number
of matches within this document to a search query.
*/
Ext.define('WordSeer.model.DocumentModel', {
	extend: 'Ext.data.Model',
	statics: {
		/** Returns a list of fields that should not be used as columns in a
		table or list.For use by views that want to display an instance of this
		model in a list or table.
		@return An array of strings: the names of the fields that should not be
		used as columns.
		*/
		getBaseFieldNames: function() {
			return ['has_text', 'units', 'children', 'id', 'metadata',
			'matches', 'document_set'];
		}
	},
	proxy: {
		type:'ajax',
		noCache: false,
		reader: 'json',
		url: ws_project_path + project_id + "/document_contents/",
		extraParams: {
			include_text: 'false',
		}
	},
	fields: [
		{name: 'has_text', type: 'boolean', default: false},
		'units',
		'children',
		{name:'id', type:'int'},
		'metadata',
		{name:'matches', type:'int', sortType: 'asInt'},
		{name:'document_set', type:'string', defaultValue: ''},
	],
});
