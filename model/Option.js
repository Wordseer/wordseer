/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Stores all the parameters that define a {@link WordSeer.view.table.Table} column
*/
Ext.define('WordSeer.model.Option', {
	/**
	@property {String} label The label of this option.
	*/
	label: '',

	/**
	@property {DomHelper} option The DOMHelper spec for the actual option

	*/
	option: {
		tag: 'input',
		type: 'checkbox',
		cls: 'option',
	},

	/**
	@property {Object}[] listeners A list of {event: fn:} objects, where the function
	gets the following params:
		@param {WordSeer.view.box.OptionsDataBox} view The component owning
		the options.
		@param {Ext.Element} el THe clicked-on element.
	*/
	listeners: [],
	constructor: function(cfg) {
		this.initConfig(cfg);
		Ext.apply(this, cfg);
		if (!this.option.id) {
			this.option.id = Ext.id();
		}
		this.callParent(arguments);
	}
});
