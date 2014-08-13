/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents an item of metadata (a property-value pair, and a count for how
many times it occurs) within a given set of search results. Used by the
{@link WordSeer.store.MetadataListStore}, which backs the
{@link WordSeer.view.metadata.MeatadataComboBox}.
*/
Ext.define("WordSeer.model.MetadataModel", {
	extend: "Ext.data.Model",
	fields: [
		/**
		@cfg {String} text The displayed value of this property.
		*/
		{name: 'text', type: 'auto', defaultValue:''},

		/**
		@cfg {String} text The displayed value of this property.
		*/
		{name: 'displayName', type: 'string', defaultValue:''},


		/**
		@cfg {String} value The value of this property.
		*/
		{name: 'value', type: 'auto', defaultValue:''},

		/**
		@cfg {Array} range A two-element array of strings, the start and
		end of the selected range.
		*/
		{name: 'range', type: 'auto', defaultValue:[]},

		/**
		@cfg {Integer} count The number of sentences in which this metadata
		appears.
		*/
		{name: 'count', type:'int', defaultValue:0},

		/**
		@cfg {Integer} document_count The number of sentences in which this
		metadata appears.
		*/
		{name: 'document_count', type:'int', defaultValue:0},

		/**
		@cfg {String} propertyName The property-name of this metadata.
		*/
		{name: 'propertyName', type: 'string', defaultValue:''},

		/**
		@cfg {String} type The data type of this metadata.
		*/
		{name: 'type', type: 'string', defaultValue:'string'},
	]
});
