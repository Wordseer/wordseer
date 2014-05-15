/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A base that provides data export functionality for treepanel types in
 WordSeer. Adds a header button that, when clicked,
transforms into a link to a downloadable Tab-Separated Values (TSV) file.
The TSV contains data from all the visible columns.
*/
Ext.define('WordSeer.view.export.ExportableTreePanel', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.exportable-tree-panel',

	config: {
		/**
		@cfg {String} fileTitle The title of the file
		*/
		fileTitle: null
	},

	/** Checks which the visible columns are, then iterates through the records
	in the Store adding a line of separator-delimited values for each record.

	@param {String} separator The delimiter by which to separate values for each
	field.
	@param {Boolean} no_headers Whether or not to include a first line that
	names the columns.

	@return {String} file_contents The contents of the file.
	*/
	generateFileContents: function(separator, no_headers) {
		var file_contents = new goog.string.StringBuffer();
		if (!separator) {
			separator = "\t";
		}
		var columns = this.columns;
		if (columns) {
			var visible_indexes = [];
			var headers = [];
			for (var i = 0; i < columns.length; i++) {
				var column = columns[i];
				if (column.isVisible()) {
					visible_indexes.push(column.dataIndex);
					headers.push(column.text);
				}
			}
			if (!no_headers) {
				// Add a header line.
				file_contents.append(headers.join(separator) + "\n");
			}
			// Add a line for each record.
			var store = this.getStore();
			if (store) {
				if (store.getRootNode) {
					store.getRootNode().cascadeBy(function(record) {
						if (!record.isLeaf()) {
							file_contents.append("\n\n");
						}
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
						file_contents.append(values.join(separator) + "\n");

					})
				}
			}
			return file_contents.toString();
		}
	}
})
