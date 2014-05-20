/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays the records in a store within a table
*/
Ext.define('WordSeer.view.treepanel.MultiTable', {
	extend: 'WordSeer.view.box.OptionsDataBox',
	requires: [
		'WordSeer.model.ColumnDefinition'
	],
	alias: 'widget.databox-multitable',
	config: {
		/**
		@cfg Array[WordSeer.model.ColumnDefinition/Object] columns An array of
		{@link WordSeer.model.ColumnDefinition} or config objects, one for each
		column.
		*/
		columns: [],

		/**
		@cfg {Number} height The height of this multitables's table.
		*/
		multitableHeight: 100,

		/**
		@cfg {Boolean} multiSelect Whether or not this multitable allows multiple
		rows to be selected.

		*/
		multiSelect: false,

		/**
		@cfg {Boolean} selectable Whether or not this multitable allows rows to be
		selected.

		*/
		selectable: true,

		/**
		@cfg {Ext.data.TreeStore} store The treestore from which the data
		in this multitable will be pulled.
		*/
		store: false

	},
	/**
	@property {Ext.util.MixedCollection} selected The selected records.
	*/
	selected: Ext.create('Ext.util.MixedCollection'),

	/**
	@property {Ext.util.MixedCollection} sorters An array of sort specifications
	that can be passed to the {@link Ext.data.Store#sorters Store sorters}.
	*/
	sorters: [],

	/**
	@property {Object} expandedNodes Maintains the expanded/collapsed
	status of nodes across store reloads.
	*/
	expandedNodes: {},

	/**
	Replaces the default databox body with a 'table' element add changes the
	body's CSS class to 'databox-table'
	@param {Object} cfg The configuration object
	*/
	constructor: function(cfg) {
		this.callParent(arguments);
		this.selected = Ext.create('Ext.util.MixedCollection');
		this.sorters = [];
		this.expandedNodes = {};
		// Instantiate column definition objects.
		if(this.columns) {
			this.columns = this.columns.map(function(c) {
				if (!(c instanceof WordSeer.model.ColumnDefinition)) {
					return Ext.create('WordSeer.model.ColumnDefinition', c);
				} else {
					return c;
				}
			});
		}

		this.addListener('datachanged', function(me, store) {
			me.populate();
		});
		this.addListener('headerClick', function(me, columnDefinition) {
			this.sort(me, columnDefinition);
		});
		this.addListener('toggle', function(me, element, record) {
			console.log(record);
		});
		this.autoEl.cls = 'multitable';
		var body = this.autoEl.children.filter(function(domHelper) {
			return domHelper.cls.indexOf('databox-body') != -1;
		})[0];
		body.tag = "ul";
		body.cls = "multitable";
		body.style = "height:" + this.tableHeight+";";
	},

	initComponent: function() {
		/**
		@event itemHover Fires when a row in the table is hovered over.
		@param {WordSeer.view.table.Table} me This component.
		@param {Ext.data.Model} record The record for the row that was hovered.
		@param {Ext.Element} The '<tr>' element representing the row.
		*/
		/**
		@event itemclick Fires when a row in the table is clicked.
		@param {WordSeer.view.table.Table} me This component.
		@param {Ext.data.Model} record The record for the row that was clicked.
		@param {Ext.Element} The '<tr>' element representing the row.
		*/

		/**
		@event select Fires when a row in the table is selected.
		@param {WordSeer.view.table.Table} me This component.
		@param {Ext.util.MixedCollection} selected The selected records.
		*/

		/**
		@event deselect Fires when a row in the table is deselected.
		@param {WordSeer.view.table.Table} me This component.
		@param {Ext.data.Model} record The record that was deselected.
		@param {Ext.util.MixedCollection} selected The selected records.
		*/
		/**
		@event headerClick Fires when the column header in the table is clicked.
		@param {WordSeer.view.table.Table} me This component.
		@param {WordSeer.model.ColumnDefinition} column The column definition for
		the column header that was clicked.
		@param {Ext.Element} The '<tr>' element representing the row.
		*/
		this.addEvents('itemHover', 'itemclick', 'select', 'deselect',
			'headerClick');
		this.callParent(arguments);
	},

	/**
	Redraws the table using the data in the store. Clears the current HTML of
	the body, re-draws the table header and body.
	*/
	populate: function() {
		var me = this;
		var body = this.getEl().down('ul.multitable');
		body.update('');
		var header = this.makeHeader();
		var top_level = this.getStore().getRootNode().childNodes.map(function(x){return x;});
		top_level.sort(function(a, b){
			a_text = a.get('text');
			b_text = b.get('text');
			return a_text > b_text? 1 : (a_text == b_text? 0 : -1);
		});
		top_level.forEach(function(node, index) {
			if (!node.get('id'))
				node.set('id', index.toString());
			if (me.filterFn(node))
				me.addTree(node, body, header);
		});
		this.addEventTriggers(body);
	},

	/**
	Returns the table element corresponding to a particular record.
	@override
	*/
	getElement: function(record) {
		return this.getEl().down('li[record=' + record.get('id') +']');
	},

	/**
	Makes an 'li' element to the supplied table element according to the column
	definitions.
	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	makeHeader: function() {
		var me = this;
		var cols = [];
		for (var i = 0; i < me.columns.length; i++) {
			var column = me.columns[i];
			var children = [
				{
					tag: 'span',
					cls: 'multitable-header-cell ' + column.headerCls,
					html: column.headerTitle,
					index: i,
				}
			];
			if (column.sortable) {
				var sortClass = 'unsorted';
				if (column.sortDirection == 'ASC') {
					sortClass = 'ascending';
				} else if (column.sortDirection ==  'DESC') {
					sortClass = 'descending';
				}
				children.push({
					tag: 'span',
					cls: 'table-header-sorter ' + sortClass
				});
			}
			var col = {
				tag: 'span',
				index: i,
				cls: 'multitable-header ' + column.headerCls,
				children: children
			};
			cols.push(col);
		}
		var header = {
			tag: 'li',
			cls: 'multitable-header',
			children: cols
		};
		return header;
	},

	/**
	Adds a 'li' element to the supplied ul element containing a sublist
	according to the data under the given node.
	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	addTree: function(node, body, header) {
		var me = this;
		if (!me.expandedNodes[node.get('text')]) {
			me.expandedNodes[node.get('text')] = false;
		}
		var renderers = me.columns.map(function(col) {
			return function (record) {
				return col.renderer(record, col.field);
			};
		});
		this_row_cells = [
			{
				tag: 'span',
				cls: 'action-button-toggle-expand action-button-toggle'
			},
			{
				tag: 'span',
				cls: 'multitable-cell metadata-category',
				html: node.get('text') + " (" + node.childNodes.length +")"
			}
		];
		this_row = {
			tag: 'span',
			cls: 'multitable-row multitable-level-1',
			children: this_row_cells
		};
		var child_rows = [header];
		node.childNodes.forEach(function(record, index) {
			if (typeof(record.get('id')) == 'undefined') {
				record.set('id', node.get('id')+"-"+index.toString());
			}
			var cells = renderers.map(function(renderer) {
				var cell = renderer(record);
				if (!cell.cls) {
					cell.cls = 'multitable-cell';
				} else {
					cell.cls += ' multitable-cell';
				}
				return cell;
			});
			child_rows.push({
				tag:'li',
				cls: 'multitable-row multitable-level-2',
				record: record.get('id'),
				children: cells
			});
		});
		var collapsedCls = me.expandedNodes[node.get('text')] ?
			'expanded' : 'collapsed';
		body.appendChild({
			tag: 'li',
			cls: 'multitable-level-1 ' + collapsedCls,
			record: node.get('id'),
			children: [
				this_row,
				{
					tag: 'ul',
					cls: 'multitable-level-2',
					children: child_rows
				}
			]
		});
	},


	/**
	Add event listeners to the table elements to listen for clicks and hovers
	and trigger the appropriate event on the component.
	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	addEventTriggers: function(body) {
		var me = this;

		// Add the headerClick event.
		var header_cells = body.select('.multitable-header-cell');
		header_cells.each(function(el) {
			var index = el.getAttribute('index');
			el.on('click', function(event, clicked_element, clicked_dom) {
				me.fireEvent('headerClick', me, me.columns[index], el, index);
			});
		});

		body.select('li.multitable-level-2').each(function(el) {
			var record_id = el.getAttribute('record');
			var record = me.getStore().getNodeById(record_id);

			// Add the itemHover event
			el.on('mouseover', function(event, hovered_element, hovered_dom) {
				me.fireEvent('itemHover', me, record);
			});

			// add the itemclick event
			el.on('click', function(event, clicked_element, clicked_dom) {
				if (me.selectable) {
					if (me.isSelected(record)) {
						me.deselect(record, false, this);
					} else {
						me.select(record, false, this);
					}
				}
				me.fireEvent('itemclick', me, record);
			});
		});

		body.select('.action-button-toggle').each(function(el) {
			var li = el.up('li.multitable-level-1');
			var record_id = li.getAttribute('record');
			var record = me.getStore().getNodeById(record_id);
			el.on('click', function(event) {
				if (!me.expandedNodes[record.get('text')]) {
					li.addCls('expanded');
					li.removeCls('collapsed');
				} else {
					li.removeCls('expanded');
					li.addCls('collapsed');
				}
				me.expandedNodes[record.get('text')] =
				!me.expandedNodes[record.get('text')];
				this.toggleCls('action-button-toggle-expand');
				this.toggleCls('action-button-toggle-contract');
			});
		});
	},

	/**
	Checks whether or not this particular record is selected;
	@param {Ext.data.Model} record The record to check.
	@return {Boolean} True if the record is selected. False otherwise.
	*/
	isSelected: function(record) {
		return this.selected.containsKey(record.get('id'));
	},

	/**
	Selects this record according to the selection model (allows multiple select)
	and modifies the DOM appropriately to reflect the selection.
	@param {Ext.data.Model} record The record to check.
	@param {Boolean} silent Whether or not to suppress the select event. True to
	suppress it, false to fire it.
	*/
	select: function(record, silent) {
		var me = this;
		var id = record.get('id');
		var el = me.getEl().down('li[record=' + id + ']');
		if (!me.selected.containsKey(id)) {
			if (!me.multiSelect) {
				me.selected.removeAll();
				me.getEl().select('li.selected').each(function(el) {
					if (el) el.removeCls('selected');
				});
			}
			me.selected.add(id, record);
			if (el) el.addCls('selected');
		}
		if (!silent) {
			me.fireEvent('select', me, record, me.selected);
		}
	},

	/**
	Deselects this record and modifies the DOM appropriately to reflect the
	selection.
	@param {Ext.data.Model} record The record to check.
	@param {Boolean} silent Whether or not to suppress the select event. True to
	suppress it, false to fire it.
	*/
	deselect: function(record, silent) {
		var me = this;
		me.selected.removeAtKey(record.get('id'));
		var id = record.get('id');
		var el = me.getEl().down('tr[record=' + id + ']');
		if (el) el.removeCls('selected');
		if (!silent) {
			me.fireEvent('deselect', me, record, me.selected);
		}
	},

	/**
	Sorts the data in the store according to the given sorters and re-draws the
	table.
	*/
	sort: function(view, column) {
		column.sortDirection = (column.sortDirection == "DESC" ? "ASC" : "DESC");
		// Remove any sorters that currently exist on this column.
		var new_sorters = view.sorters.filter(function(sorter) {
			return sorter.property != column.field;
		});
		var sorter = {
			direction: column.sortDirection,
			property: column.field,
		};
		if (column.sortFunction) {
			sorter.sortFn = column.sortFunction;
		}
		new_sorters.unshift(sorter);
		view.sorters = new_sorters;
		view.getStore().sort(view.sorters);
		view.populate();
	}
});
