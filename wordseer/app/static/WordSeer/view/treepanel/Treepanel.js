/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays the records in a store within a TreeStore, except with table columns.
*/
Ext.define('WordSeer.view.treepanel.Treepanel',  {
	extend: 'WordSeer.view.table.Table',
	alias: 'widget.treepanel',

	initComponent: function() {
		/**
		@event itemToggle Fires when an item is expanded or collapsed
		@param {WordSeer.view.table.Table} me This component.
		@param {Ext.util.MixedCollection} selected The selected records.
		*/

		this.addEvents('itemToggle');
		this.callParent(arguments);
	},

	/**
	Adds a 'tbody' element to the supplied table element containing rows
	according to the data in the {@link #store}.
	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	addBody: function(body) {
		var me = this;
		var i = 0;
		me.getStore().getRootNode().cascadeBy(function(record) {
			if (typeof(record.get('id')) == 'undefined') {
				record.set('id', i+"");
			}
			i++;
		});

		var renderers = me.columns.map(function(col) {
			return function (record) {
				return col.renderer(record, col.field, me);
			};
		});
		if (me.checkboxes) {
			renderers = [
			function(record) {
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
		make_row = function(node, level, parent_ids) {
			var cells = renderers.map(function(renderer) {
					var cell = renderer(node);
					cell.cls += " content";
					return cell;
				});
			rows.push({
				tag:'tr',
				level: level,
				parents: parent_ids,
				record: node.get('id'),
				children: cells
			});
			if (!node.isLeaf()) {
				node.childNodes.forEach(function(child) {
					make_row(child, level + 1, parent_ids +" " +node.get('id'));
				});
			}
		};
		me.getStore().getRootNode().childNodes.forEach(function(node){
			make_row(node, 0, "");
		});
		body.appendChild({
			tag: 'tbody',
			cls: 'databox-table-body',
			children: rows
		});
	},

	/**
	Add event listeners to the treepanel elements to listen for expand/collapse
	events. The remaining events (select, hover, etc.) are covered by the parent
	{@link WordSeer.view.table.Table#addEventTriggers} function.

	@param {Ext.Element} body The '<table>' element to which to add the data.
	*/
	addEventTriggers: function(body) {
		this.callParent(arguments);
	}
});
