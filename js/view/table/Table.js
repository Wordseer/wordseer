/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays the records in a store within a table
*/
Ext.define('WordSeer.view.table.Table', {
	extend: 'WordSeer.view.box.OptionsDataBox',
	requires: [
		'WordSeer.model.ColumnDefinition'
	],
	alias: 'widget.databox-table',
	config: {
		/**
		@cfg Array[WordSeer.model.ColumnDefinition/Object] columns An array of
		{@link WordSeer.model.ColumnDefinition} or config objects, one for each
		column.
		*/
		columns: [],

		/**
		@cfg {Number} height The height of this table's table.
		*/
		tableHeight: 100,

		/**
		@cfg {Boolean} checkboxes Whether or not this table had a left-hand-side
		checkbox column for selecting records.

		*/
		checkboxes: false,

		/**
		@cfg {Boolean} multiSelect Whether or not this table allows multiple
		rows to be selected.

		*/
		multiSelect: false,

		/**
		@cfg {Boolean} selectable Whether or not this table allows rows to be
		selected.

		*/
		selectable: true,

		/**
		@cfg {Boolean} onlyCheckboxSelect Whether or not the only way to select
		rows is to use the checkboxes. If this is false, clicking anywhere in a
		row will select the row, if this is true, only clicking on the checkbox
		will select the row.
		*/
		onlyCheckboxSelect: false,

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
	Replaces the default databox body with a 'table' element add changes the
	body's CSS class to 'databox-table'
	@param {Object} cfg The configuration object
	*/
	constructor: function(cfg) {
		this.callParent(arguments);
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

		this.addListener('boxready', function(me) {
			var body = this.getEl().down('table.table');
			//$(body.dom).resizableColumns();
		});
		this.addListener('datachanged', function(me, store) {
			me.populate();
		});
		this.addListener('headerClick', function(me, columnDefinition,
			header_element) {
			this.sort(me, columnDefinition, header_element);
		});
		this.autoEl.cls = 'table';
		var body = this.autoEl.children.filter(function(domHelper) {
			return domHelper.cls == 'databox-body';
		})[0];
		body.tag = "table";
		body.cls += " table";
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
		me.selected.removeAll();
		var body = this.getEl().down('table.table');
		body.update('');
		this.addHeader(body);
		this.addBody(body);
		this.addEventTriggers(body);
	},

	/**
	@override
	*/
	getElement: function(record) {
		return this.getEl().down('tr[record=' + record.get('id') +']');
	},

	/**
	Adds a 'thead' element to the supplied table element according to the column
	definitions.
	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	addHeader: function(body) {
		var me = this;
		var cols = [];

		if (me.checkboxes) {
			cols.push({
				tag: 'th',
				cls: 'table-head table-select-all',
				children: [
					{
						tag: 'input',
						type: 'checkbox',
						cls: 'table-select-all'
					}
				]
			});
		}

		for (var i = 0; i < me.columns.length; i++) {
			var column = me.columns[i];
			if (!column.hidden) {
				var children = [
					{
						tag: 'span',
						cls: column.headerCls,
						html: column.headerTitle
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
					tag: 'th',
					index: i,
					cls: column.headerCls,
					children: children
				};
				cols.push(col);
			}
		}
		var header = {
			tag: 'thead',
			children: [
				{
					tag: 'tr',
					children: cols
				}
			]
		};
		body.appendChild(header);
	},

	/**
	Adds a 'tbody' element to the supplied table element containing rows
	according to the data in the {@link #store}.
	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	addBody: function(body) {
		var me = this;
		var is_visible = function(x){return !x.hidden;};
		var renderers = me.columns.filter(is_visible).map(
			function(col) {
			return function (record, index) {
				return col.renderer(record, col.field, me);
			};
		});

		if (me.checkboxes) {
			renderers = [
			function(record, index) {
				return {
					tag:'td',
					record: record.get('id'),
					children: [
						{
							tag: 'input',
							type: 'checkbox',
							cls: 'checkbox'
						}
					]
				};
			}].concat(renderers);
		}

		var rows = [];
		me.getStore().each(function(record, index) {
			if (typeof(record.get('id')) == 'undefined') {
				record.set('id', index+"");
			}
			var cells = renderers.map(function(renderer) {
				return renderer(record, index);
			});
			rows.push({
				tag:'tr',
				record: record.get('id'),
				children: cells
			});
		});
		body.appendChild({
			tag: 'tbody',
			cls: 'databox-table-body',
			children: rows
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
		var header_cells = body.select('th');
		header_cells.each(function(el) {
			var index = el.getAttribute('index');
			// The select-all checkbox.
			el.on('click', function(event, clicked_element, clicked_dom) {
				if (clicked_element.getAttribute('type') === 'checkbox' &&
					index === null) {
					// select all or none.
					if (clicked_element.checked) {
						me.getStore().each(function(record) {
							me.select(record, true);
						});
						me.fireEvent('select', me, undefined, me.selected);
					} else {
						me.getStore().each(function(record) {
							me.deselect(record, true);
						});
						me.fireEvent('deselect', me, undefined, me.selected);
					}
				} else {
					me.fireEvent('headerClick', me, me.columns[index], el,
						index);
				}
			});
		});

		body.select('table').each(function(el) {
			el.on('mouseleave', function(event) {
				el.select('tr.hovered').each(function(tr) {
					$(tr).removeClass('hovered');
				});
			});
		});

		body.select('tbody tr').each(function(el) {
			var record_id = el.getAttribute('record');
			var record = me.getStore().getById(record_id);
			if (!record) {
				record = me.getStore().getById(parseInt(record_id));
			}
			// Add the itemHover event
			el.on('mouseenter', function(event, hovered_element) {
				tr = $(hovered_element).closest('tr')[0];
				me.fireEvent('itemMouseEnter', me, record, tr);
			});
			// Add the itemHover event
			el.on('mouseleave', function(event, hovered_element) {
				tr = $(hovered_element).closest('tr')[0];
				me.fireEvent('itemMouseLeave', me, record, tr);
			});

			// add the itemclick event
			el.on('click', function(event, clicked_element, clicked_dom) {
				tr = $(clicked_element).closest('tr')[0];
				if (me.selectable) {
					var click_is_valid_select = true;
					if (me.checkboxes && me.onlyCheckboxSelect &&
						clicked_element.getAttribute('type') != 'checkbox') {
						click_is_valid_select = false;
					}
					if (click_is_valid_select) {
						if (me.isSelected(record)) {
							me.deselect(record, false, this);
						} else {
							me.select(record, false, this);
						}
					}
				}
				me.fireEvent('itemClick', me, record, tr);
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
		var el = me.getEl().down('tr[record=' + id + ']');
		if (!me.selected.containsKey(id)) {
			if (!me.multiSelect) {
				me.selected.removeAll();
				me.getEl().select('tr.selected').each(function(el) {
					if (el) {
						el.removeCls('selected');
						if (me.checkboxes) {
							$(el.down('input[type=checkbox]').dom).prop('checked', false);
						}
					}

				});
			}
			me.selected.add(id, record);
			if (me.checkboxes) {
				$(el.down('input[type=checkbox]').dom).prop('checked', true);
			}
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
		if (me.checkboxes) {
			$(el.down('input[type=checkbox]').dom).prop('checked', false);
		}
		if (!silent) {
			me.fireEvent('deselect', me, record, me.selected);
		}
	},

	/**
	Sorts the data in the store according to the given sorters and re-draws the
	table.

	@param {WordSeer.view.table.Table} view This table.
	@param {WordSeer.model.ColumnDefinition} column The column definition of
	the clicked-on column header
	@param {Ext.Element} header_element The header element that was clicked.
	*/
	sort: function(view, column, header_element) {
		icon = header_element.down('span.table-header-sorter');
		if (column.sortDirection === "DESC") {
			icon.removeCls('descending');
			icon.addCls('ascending');
			column.sortDirection = "ASC";
		} else if (column.sortDirection === "ASC") {
			icon.removeCls('ascending');
			icon.addCls('unsorted');
			column.sortDirection = "UNSORTED";
		} else if (column.sortDirection === "UNSORTED" || !column.sortDirection) {
			icon.removeCls('ascending');
			icon.addCls('descending');
			column.sortDirection = "DESC";
		}

		// Remove any sorters that currently exist on this column.
		var new_sorters = view.sorters.filter(function(sorter) {
			return sorter.property != column.field;
		});
		if (column.sortDirection !== "UNSORTED") {
			var sorter = {
				direction: column.sortDirection,
				property: column.field,
			};
			if (column.sortFunction) {
				sorter.sortFn = column.sortFunction;
			}
			new_sorters.push(sorter);
		}
		view.sorters = new_sorters;
		view.getStore().sort(view.sorters);
		view.populate();
	}
});
