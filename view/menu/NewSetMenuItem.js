/**
A menuitem for creating a new empty set.
*/
Ext.define('WordSeer.view.menu.NewSetMenuItem', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.new-set-menuitem',
	value: 'New set',
	config: {

		/**
		@cfg {WordSeer.store.DocumentSetListStore|WordSeer.store.SentenceSetListStore} store
		The store containing the set records.
		*/
		store: false,

		/**
		@cfg {WordSeer.model.SubsetModel} parent The parent set of this set.
		*/
		parent: null,
	}
});
