/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls various actions around exporting data
*/
Ext.define('WordSeer.controller.DataExportController', {
	extend: 'Ext.app.Controller',
	views: [
		'export.ExportableTable',
	],
	init: function() {
		console.log("Initialized data export controller");
		this.control({
			'tool[action=export-metadata]': {
				'click': this.exportMetadata,
			},
			'tool[action=export-svg]': {
				'click': this.exportSvg,
			},
			'exportable-grid-panel': {
				actionButtonClicked: function(table, type, button) {
					if (type == 'save') {
						this.exportTable(table, button);
					}
				}
			}
		});
	},

	/** Replaces the tool with a link to a downloadable file containing the
	data from all the visible columns in the table.
	@param {WordSeer.view.export.ExportableTable} table The table containing the
	data to export.
	@param {Ext.Element} button The clicked-on tool.
	*/
	exportTable: function (table, button) {
		var file_contents = "";
		if (table) {
			file_contents = table.generateFileContents("\t");
		}
		var link_href = "data:application/octet-stream," +
			escape(file_contents);
		var table_name = table.title;

		if (table.fileTitle) {
			table_name = table.fileTitle;
		}
		var context = "";
		var widget = table.up('widget');
		if (widget) {
			var formValues = widget.getFormValues();
			var text = formValues.toText();
			if (text.length > 0) {
				context = " for " + text;
			}
		}
		var download_name = getInstance() +" "+ table_name + context + ".tsv";
		var download_html = " <a class='download' download=\"" + download_name +
			"\" href=\"" + link_href +"\">tsv</a>";
		var dh = Ext.DomHelper;
		download_link = {
			tag: 'a',
			href: link_href,
			cls: 'download',
			download: download_name,
			html: 'Download'
		};
		dh.insertAfter(button, download_link);
		button.destroy();
	},

	/** Replaces the tool with a link to a downloadable file containing the
	data from all the visible columns in the table.
	@param {Ext.panel.Tool} The clicked-on tool.
	*/
	exportMetadata: function (tool) {
		var treepanel = tool.up('panel').down('treepanel');
		var header = tool.up();
		var file_contents = "";
		if (treepanel) {
			file_contents = treepanel.generateFileContents("\t");
		}
		var link_href = "data:application/octet-stream,"
			+ escape(file_contents);
		var table_name = 'Metadata';
		var context = "";
		var widget = treepanel.up('widget');
		if (widget) {
			var formValues = widget.getFormValues();
			var text = formValues.toText();
			if (text.length > 0) {
				context = " for " + text;
			}
		}
		var download_name = getInstance() +" "+ table_name + context + ".tsv";
		var download_html = " <a class='download' download=\"" + download_name +
			 "\" href=\"" + link_href +"\">tsv</a>";
		tool.hide();
		header.add({
			xtype: 'box',
			itemId:'download',
			html: download_html,
		});
	},

	/** Extracts the contents of an svg image rendered in the browser into an
	svg file's contents.
	@param {HTMLElement} svg The svg DOM node.
	@return {String} file_contents The contents of the SVG file.
	*/
	svgToSvgUrl: function(svg) {
		var svg = $(svg).parent().html();
		var b64 = Base64.encode(svg);
		return "data:image/svg+xml;base64,\n"+b64;
	},

	/** Extracts the contents of an svg image rendered in the browser into an
	png file contents.
	@param {HTMLElement} svg The svg DOM node.
	@return {String} file_contents The contents of the PNG file.
	*/
	svgToPNGUrl: function(svg) {
		$("body").append('<div style="display:none" id="tmp">' +
			'<canvas id="canvas"></canvas><div id="svg"></div></div>');
		$("#svg").append($(svg).clone());
		$("#canvas").attr("width", $(svg).attr("width"));
		$("#canvas").attr("height", $(svg).attr("height"));
		var canvas = $("#canvas").get(0);
		canvg('canvas', $("#svg").html());
		$("#tmp").remove();
		return canvas.toDataURL("image/png");
	},

	/** Replaces the tool with a link to a downloadable SVG and .jpg files
	for all the SVG elements within this layout panel.
	@param {Ext.panel.Tool} The clicked-on tool.
	*/
	exportSvg: function (tool) {
		var layout_panel = tool.up('layout-panel');
		var header = layout_panel.header;
		var widget = layout_panel.down('widget');
		var combobox = header.down('switch-widget-combobox');
		var title = "Image"
		if (combobox) {
			title = combobox.getRawValue();
		}
		context = "";
		if (widget) {
			var formValues = widget.getFormValues();
			var text = formValues.toText();
			if (text.length > 0) {
				context = " for " + text;
			}
			var index = 0;
			var me = this;
			widget.items.each(function(item) {
				var dom = item.getEl();
				if (dom) {
					dom = item.getEl().dom;
					var svgs = $(dom).find('svg');
					for (var i = 0; i < svgs.length; i++) {
						var svg = svgs[i];
						index ++;
						num = "";
						if (index > 1) {
							num = " "+index;
						}
						var png_href = me.svgToPNGUrl(svg);
						//var svg_href = me.svgToSvgUrl(svg);
						var download_name = getInstance() +" "+ title + context + num;
						//var download_html = " <a download=\"" + download_name +".svg" + "\" href=\"" +
						// 	svg_href +"\">.svg " + num +"</a>";
						// header.add({
						// 	xtype: 'box',
						// 	action:'download',
						// 	html: download_html,
						// });
						download_html = " <a class='download' download=\"" + download_name +".png" + "\" href=\"" +
							png_href +"\">" + num +".png</a>";
						var box = header.getComponent("png-"+index);
						if (box) {
							$(box.getEl().dom).fadeOut();
							header.remove(box);
						}
						Ext.defer(function(header, download_html, index) {
							var box = header.getComponent("png-"+index);
							if (box) {
								header.remove(box);
							}
							header.add({
								xtype: 'box',
								action:'download',
								itemId: "png-"+index,
								html: download_html,
							});
						}, 500, this, [header, download_html, index]);
					}
				}
			})
		}
		//tool.hide();
	}

})
