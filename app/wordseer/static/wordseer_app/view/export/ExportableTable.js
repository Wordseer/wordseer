/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A base class that provides data export functionality for a number of
different table types in WordSeer.
When clicked, the 'save' button transforms into a link to a downloadable
Tab-Separated Values (TSV) file. The TSV contains data from all the visible
columns.
*/
Ext.define('WordSeer.view.export.ExportableTable', {
	extend: 'WordSeer.view.table.Table',
	alias: 'widget.exportable-grid-panel',
	tools: [
		'save'
	],
	config: {
		/**
		@cfg {String} fileTitle The title of the file
		*/
		fileTitle: null
	},

	/** Checks which the visible columns are, then constructs a CSV of them.

	@return {String} file_contents The contents of the file.
	*/
	generateFileContents: function() {
		var file_contents = [];
		var columns = this.columns;
		if (columns) {
			var visible_indexes = [];
			var headers = [];
			for (var i = 0; i < columns.length; i++) {
				var column = columns[i];
				if (!column.hidden) {
					visible_indexes.push(column.field);
					headers.push(column.headerTitle);
				}
			}
			
			// Add a header line.
			file_contents.push(headers);
			
			// Add a line for each record.
			var store = this.getStore();
			if (store) {
				store.each(function(record) {
					var values = [];
					for (var i = 0; i < visible_indexes.length; i++) {
						var value = record.get(visible_indexes[i]);
						if (typeof(value) == "object") {
							value = value.text;
						}
						if (typeof(value) == "string") {
							value = '"' + value.replace(/\s+/g, " ") + '"';
						}
						values.push(value);
					}
					file_contents.push(values);
				});
			}
			return d3.csv.format(file_contents);
		}
	}
});
