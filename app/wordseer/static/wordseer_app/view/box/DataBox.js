/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
A small data panel intended to display data from a store, with a headerFreq and some
action buttons, but no navigation buttons.
*/
Ext.define('WordSeer.view.box.DataBox',  {
	extend: 'Ext.Component',
	alias: 'widget.databox',
	config: {
		/**
		@cfg {String} title The title of this panel
		*/
		title: '',

		/**
		@cfg {String} headerCls The CSS class to be applied to the header div.

		*/
		headerCls: 'databox-header',

		/**
		@cfg {Boolean} hideHeader A value of 'true' will result in a DataBox
		without a header div.

		*/
		hideHeader: false,

		/**
		@cfg {Array[String]} tools The buttons to add to the header
		*/
		tools: [],

		/**
		@cfg {Ext.data.Store} store The store holding the data that this view
		displays.
		*/
		store: null,

		/**
		@cfg {Boolean} collapsible Whether or not this databox is collapsible
		via a button in the header.

		*/
		collapsible: false,


		/**
		@cfg {Boolean} collapsed Whether or not this databox is collapsed (if
		it is collapsible)

		*/
		collapsed: false
	},
	/**
	Creates the inner HTML of this component.
	@param {Object} cfg Configuration -- the config parameters for this
	component.
	*/
	constructor: function(cfg) {
		this.initConfig(cfg);
		cfg.id = Ext.id(this, 'databox');
		cfg.autoEl = {
			tag: 'div',
			cls: 'databox',
			children:[
				{
					tag: 'div',
					cls: this.headerCls,
					children: [
						{
							tag: 'div',
							cls: 'databox-head',
							children: [
								{
									tag: 'span',
									cls: ('action-button-toggle-contract ' +
											'action-button-toggle')
								},
								{
									tag: 'h2',
									cls: this.headerCls,
									html: this.title
								}
							]
						}
					]
				},
				{
					tag: 'div',
					cls: 'databox-body',
					children: []
				}
			]
		};
		if (cfg.hideHeader) {
			// remove the header element
			cfg.autoEl.children.splice(0, 1);
		} else if (!this.collapsible) {
			cfg.autoEl.children[0].children[0].children.splice(0, 1);
		}
		this.callParent(arguments);
		this.addListener('afterrender',  function(me) {
			me.finish();
		});
		this.addListener('datachanged', function(me, store) {
			me.populate();
		});
		if (!cfg.hideHeader) {
			this.appendToolsToDomHelperSpec(this.autoEl.children[0].children[0].children,
				this.tools, this.id);
		}
	},

	initComponent: function() {
		/**
		@event actionButtonClicked Fires whenever an action button is clicked.
		@param {WordSeer.view.box.DataBox} The box owning the action button.
		@param {String} type The type of button that was clicked. Currently
		either 'save', 'see more', or 'save-picture'.
		*/

		/**
		@event datachanged Fires when the data in the store changes.
		@param {WordSeer.view.box.DataBox} The box owning the action button.
		@param {Ext.data.Store} store The store that was refreshed
		*/

		/**
		@event update
		@param {WordSeer.view.box.DataBox} The box owning the action button.
		@param {Ext.data.Store} store The store containing the model that was
		refreshed.
		@param {Ext.data.Model} record The record that was changed.
		*/
		this.addEvents('actionButtonClicked', 'datachanged', 'update');

		var me = this;
		if (typeof(this.store) == 'string') {
			this.store = Ext.getStore(this.store);
		}
		if(!this.store) {
			this.store = Ext.create('Ext.data.Store', {fields:[]});
		}
		this.store.on('datachanged', function(store) {
			me.fireEvent('datachanged', me, store);
		});
		this.store.on('load', function(store) {
			me.fireEvent('datachanged', me, store);
		});
		this.store.on('update', function(store, record) {
			me.fireEvent('update', me, store, record);
		});
		this.callParent(arguments);
	},

	/**
	Adds the given buttons to the DOM helper specification provided and
	configures them to trigger the actionButtonClicked event on the component
	with the given ID.
	@param {Object} The DOMHelperSpec to which to append the tool definitions.
	@param Array[String] tools The list of tool types to add.
	@param {String} idToTrigger The ID of the component on which to trigger the
	actionButtonClicked event.
	*/
	appendToolsToDomHelperSpec: function(spec, tools, idToTrigger) {
		for (var i = 0; i < tools.length; i++) {
			spec.push({
				tag: 'a',
				type: tools[i],
				cls: 'action-button action-button-' + tools[i]
			});
		}
	},

	finish: function() {
		var me = this;
		me.getEl().select('.action-button').each(function(element) {
			element.on('click', function(event, clicked_el, clicked_dom) {
				me.fireEvent('actionButtonClicked', me,
					clicked_el.getAttribute('type'), this);
			});
		});
		me.getEl().select('.action-button-toggle').each(function(el) {
			el.on('click', function(event) {
				me.toggleBody();
			});
		});
		me.populate();
		if (me.collapsed) {
			me.toggleBody();
			me.collapsed = true;
		}
	},

	populate: function() {},

	/**
	Returns the element representing the given record.
	@param {Ext.data.Model} record The record.
	@return {Ext.Element} The element representing this record.
	*/
	getElement: function(record) {
		return this.getEl().down('[record=' + record.get('id') + ']');
	},

	toggleBody: function() {
		var me = this;
		var body = me.getEl().select('.databox-body').elements[0];
		$(body).toggle();
		var options = me.getEl().select('.databox-options').elements[0];
		$(options).toggle();
		me.getEl().select('.action-button-toggle').each(function(el) {
			this.toggleCls('action-button-toggle-expand');
			this.toggleCls('action-button-toggle-contract');
		});
		me.collapsed = !me.collapsed;
	},

	resetTitle: function(title) {
		var me = this;
		if (me.getEl()) {
	        $(me.getEl().dom).find('h2.databox-header').html(title);
		}
	}
});
