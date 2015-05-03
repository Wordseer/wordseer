Ext.define('WordSeer.model.AssociatedWordModel', {
	extend: 'Ext.data.Model',
	fields: [
		{name:'id', type: 'int'},
		{name:'word', type: 'string'},
		{name:'pos', type: 'string'},
		{name:'count', type: 'auto', default: 0},
		{name:'doc_count', type: 'auto', default: 0},
		{name:'score_sentences', type: 'float', default:0.0}
	],
});
