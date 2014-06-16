/**
A menuitem for adding an item to a new set.
*/
Ext.define('WordSeer.view.menu.CreateAndAddMenuItem', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.create-and-add-menuitem',
	value: 'New set',
	config: {

		/**
		@cfg {WordSeer.store.DocumentSetListStore|WordSeer.store.SentenceSetListStore} store
		The store containing the set records.
		*/
		store: false,

		/**
		@cfg {Array[Number]} item The identifier of the item that was
		clicked to produce this menu. In the case of documents and sentences,
		this is the sentence or document ID, in the case of words or phrases, it
		is the word or phrase;
		*/
		ids: '',
	}
});
