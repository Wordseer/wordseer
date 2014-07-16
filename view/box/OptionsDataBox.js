/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the list of words of a given part of speech that most frequently
appear in sentences matching the main search. This view gets displayed in the
{@link WordSeer.view.widget.Widget} along with the list of frequent phrases.
*/
Ext.define('WordSeer.view.box.OptionsDataBox', {
	requires: [
		'WordSeer.model.Option'
	],
	extend: 'WordSeer.view.box.DataBox',
	alias: 'widget.options-table',
	config: {
		/**
		@cfg {WordSeer.model.Option}[] options
		A list of optional components that trigger optionClicked events on this
		component.
		*/
		options: null,
	},
	constructor: function(cfg) {
		this.initConfig(cfg);
		if (this.options) {
			this.options = this.options.map(function(cfg) {
				if (!(cfg instanceof WordSeer.model.Option)) {
					return Ext.create('WordSeer.model.Option', cfg);
				} else {
					return cfg;
				}
			});
		}
		this.callParent(arguments);
		if (this.options) {
			var options = this.options.map(function(option) {
				return {
					tag: 'span',
					cls: 'databox-option',
					children: [
						{
							tag: 'span',
							cls: 'databox-option-label',
							html: option.label
						},
						option.option
					]
				};
			});
			// Add the DOMHelpers for the options to the autoEl after the
			// header.
			cfg.autoEl.children[0].children.push({
				tag: 'div',
				cls: 'databox-options',
				children: options
			});
		}
	},

	initComponent: function() {
		/**
		@event optionEvent
		@param {WordSeer.view.box.OptionsDataBox} view The component
		to which the option belongs.
		@param {String} eventName The event name
		@param {WordSeer.model.Option} option The Option that was acted upon
		@param {Ext.Element} option_el The Ext.Element representing this option
		on the page.
		*/
		this.addEvents('optionEvent');
		this.callParent(arguments);
	},

	finish: function() {
		var me = this;
		if (me.options) {
			me.options.forEach(function(option) {
				var option_el = me.getEl().down('#'+option.option.id);
				option.listeners.forEach(function(listener) {
					option_el.on(listener.event,
						function(event, el, dom) {
							if (listener.fn) {
								listener.fn(me, el);
							}
							me.fireEvent('optionEvent', me, listener.event,
								option, el);
						});
				});
			});
		}
		me.getEl().select('span.checkbox').each(function(el){
			el.on('click', function(event, clicked_el) {
				this.toggleCls('checked');
			});
		});
		this.callParent(arguments);
	}
});
