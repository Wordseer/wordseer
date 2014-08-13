/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Stores all the parameters that define a {@link WordSeer.view.table.Table} column
*/
Ext.define('WordSeer.model.ColumnDefinition', {
	/**
	@property {String} headerTitle The title of this column.
	*/
	headerTitle: '',

	/**
	@property {String} headerCls A CSS class to apply to the header cell for this
	column.

	*/
	headerCls: 'databox-table-head',

	/**
	@property {String} field The field name within the record from which this data
	is extracted.
	*/
	field: null,

	/**
	@property {Function} renderer A function that generates the
	{@link Ext.DomHelper} specification for a table cell (tag: 'td' is always
	enforced).

	@param {Ext.data.Model} record The record being rendered
	@param {String} field The field name to render
	*/
	renderer: function(record, field) {
		return {
			tag: 'td',
			html: record.get(field).toString()
		};
	},

	/**
	@property {Array[Function]} listenerBinders  A list of function that bind listeners to
	events on the cell or within its contents.

	@param {Ext.Element} el The element representing the table cell
	@param {WordSeer.view.table.Table} table The table component to which this
	table belongs.
	*/
	listenerBinders: [],

	/**
	@property {Function} sortFunction A sorter for comparing two cell values. Leave
	null to use the default comparators for that data type.

	*/
	sortFunction: null,

	/**
	@property {Boolean} sortable Whether this column is sortable.

	*/
	sortable: true,

	/**
	@property {String} sortDirection the direction in which this field is currently
	sorted. Options are 'ASC' or 'DESC' or false, which indicates that this
	field is currently not sorted.

	*/
	sortDirection: false,


	/**
	@property {String} cls If not specified by the {@link #renderer), the CSS
	classes to apply to the table cell.

	*/
	cls: 'table-cell',

	/**
	@property {Boolean} hidden Whether or not this column is hidden.
	*/
	hidden: false,


	constructor: function(cfg) {
		this.initConfig(cfg);
		Ext.apply(this, cfg);
		this.callParent(arguments);
	}
});
