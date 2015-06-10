Ext.define('WordSeer.store.AssociatedWordsStore', {
	extend: 'Ext.data.Store',
	requires: [
		'WordSeer.model.AssociatedWordModel'
	],
	autoDestroy: true,
	config: {
		/**
		@cfg {String} pos The part of speech of this list of frequent words.
		*/
		pos: 'Nouns'
	},
	model: 'WordSeer.model.AssociatedWordModel',
	constructor: function(config) {
		this.callParent(arguments);

		// configure proxy based on POS from config
		if (config) {
			var pos = config.pos;
		} else {
			var pos = this.config.pos;
		}
		
		this.proxy = new Ext.data.proxy.Ajax({
			noCache: false,
			timeout: 9000000,
			model: 'WordSeer.model.AssociatedWordModel',
			url: ws_api_path + ws_project_path + project_id + '/associated_words',
			reader: {
				type: 'json',
				root: 'Words'
			}
		})
	}
});
