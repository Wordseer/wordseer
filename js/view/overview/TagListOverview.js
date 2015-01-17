/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays a list of tags with optional numbers beside the tags.
*/
Ext.define('WordSeer.view.overview.TagListOverview',  {
	extend: 'WordSeer.view.box.OptionsDataBox',
	alias: 'widget.tag-list',
	config: {
		/**
		@cfg {String} tagField The name of the field in the record holding the
		tag's name.
		*/
		tagField: null,

		/**
		@cfg {Array[String]} countFields The name of the fields in the record
		that hold the counts.
		*/
		numberFields: [],

		/**
		@cfg {Function} filterFn a function to apply to the store to decide
		which nodes to display.
		*/
		filterFn: function(x){return x;},

		maxLength: 20,
	},
	/**
	Replaces the default databox body with a 'ul' element add changes the
	body's CSS class to 'tag-list-body'.
	@param {Object} cfg A configuration object
	*/
	constructor: function(cfg) {
		this.callParent(arguments);
		this.autoEl.cls = 'tag-list';
		var body = this.autoEl.children[1]; // The 'div.databox-body DomMHelper';
		body.tag = 'ul';
		body.cls = "tag-list-body";
	},

	initComponent: function() {
		/**
		@event tagClicked Fires when a tag in the list is clicked.
		@param {WordSeer.view.overview.TagListOverview} me This component.
		@param {Ext.data.Model} record The record for the tag that was clicked.
		@param {Ext.Element} The '<li>' element representing the tag.
		*/
		this.addEvents('tagClicked');
		this.callParent(arguments);
	},

	listeners: {
		datachanged: function(me, store) {
			me.populate();
		},
		tagClicked: function(me, record) {
			//console.log(record.get(me.tagField));
		},
		actionButtonClicked: function(me, type) {
			//console.log('Action button of type ' + type + ' clicked.');
		}
	},

	/**
	@override
	*/
	getElement: function(record) {
		return this.getEl().down('li[record=' + record.get('id') +']');
	},

	/**
	Redraws the tag list using the data in the store. Clears the current HTML
	of the body 'ul' and adds an 'li' for each item in the store.
	*/
	populate: function() {
		this.callParent();
		var me = this;
		var body = this.getEl().down('ul.tag-list-body');
		body.update('');
		var tags = [];
		me.getStore().each(function(record, index) {
			if (me.filterFn(record) && tags.length < me.maxLength) {
				if (typeof(record.get('id')) == 'undefined') {
					record.set('id', index.toString());
				}
				var tagName = record.get(me.tagField);
				var values = me.numberFields.map(function(fieldName) {
					return record.get(fieldName);
				});
				var children = [];
				if (tagName) {
					children.push({
						tag: 'span',
						cls: 'tag-list-name',
						html: tagName
					});
				}
				var tag = {
					tag: 'li',
					cls: 'tag-list',
					record: record.get('id'),
					children: children
				};
				for (var i = 0; i < values.length; i ++) {
					if (typeof(values[i]) != 'undefined') {
						tag.children.push({
							tag: 'span',
							cls: 'tag-list-number',
							html: '(' + values[i] + ')'
						});
					}
				}
				tags.push(tag);
			}
		});
		body.appendChild(tags);
		body.select('li.tag-list').each(function(el) {
			var record_id = el.getAttribute('record');
			el.on('click', function(event, clicked_element, clicked_dom) {
				me.fireEvent('tagClicked', me,
					me.getStore().getById(record_id), clicked_element);
			});
		});
	}
});
