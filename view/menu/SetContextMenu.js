/** Shows options on a {@link WordSeer.view.collections.SetList} for adding a
new subset, opening the set in a new tab, renaming and other options.
*/
Ext.define('WordSeer.view.menu.SetContextMenu', {
	extend: 'WordSeer.view.menu.Menu',
	alias: 'widget.set-context-menu',
	requires: [
		'WordSeer.view.menu.NewSetMenuItem',
		'WordSeer.view.menu.RenameSetMenuItem'
	],
	config: {
		/**
		@cfg {WordSeer.model.SubsetModel} record The record representing the
		set.
		*/
		record: null,

		/**
		@cfg {WordSeer.model.DocumentSetStore|SentenceSetStore|PhraseSetStore} store
		The store backing the list next to which this menu appears.
		*/
		store: null,

		/**
		@cfg {WordSeer.view.collections.SetList} view The list of sets.
		*/
		view: null,
	},
	initComponent: function() {
		this.items = [
			{
				text: 'Filter',
				action: 'filter'
			},
			{
				text: 'View',
				action: 'open-set',
			},
			{
				text: 'Rename',
				menu: [
					{
						xtype: 'rename-set-menuitem',
						record: this.record,
						store: this.store
					}
				]
			},
			{
				text: 'New Subset',
				menu: [
					{
						xtype: 'new-set-menuitem',
						parent: this.record,
						store: this.store
					}
				]
			},
			{
				text: 'Delete',
				action: 'delete-set'
			}
		];
		this.callParent(arguments);
	}
});
