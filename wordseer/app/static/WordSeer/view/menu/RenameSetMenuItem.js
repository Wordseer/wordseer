/**
A menuitem for renaming a set.
*/
Ext.define('WordSeer.view.menu.RenameSetMenuItem', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.rename-set-menuitem',
	config: {

		/**
		@cfg {WordSeer.store.DocumentSetListStore|WordSeer.store.SentenceSetListStore} store
		The store containing the set records.
		*/
		store: false,

		/**
		@cfg {WordSeer.model.SubsetModel} record The set being renamed.
		*/
		record: null,
	},
	initComponent: function() {
		if (this.record) {
			this.value = this.record.get('text');
		}
		this.callParent(arguments);
	}
});
