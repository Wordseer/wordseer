/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Extends the {@link WordSeer.view.search.GrammaticalSearchForm} to include a
{@link WordSeer.view.windowing.viewport.WidgetSwitcherCombobox} for choosing
which {@link WordSeer.view.widget.Widget} to issue the search in.
*/
Ext.define('WordSeer.view.search.UniversalSearchForm',{
    extend:'WordSeer.view.search.GrammaticalSearchForm',
    alias: 'widget.universal-search-form',
    requires: [
        'WordSeer.view.windowing.viewport.SwitchWidgetComboBox',
        'WordSeer.view.visualize.columnvis.ColumnVisWidget',
        'WordSeer.view.visualize.wordtree.WordTreeWidget',
        'WordSeer.view.widget.SearchWidget',
    ],
    id: 'universal-search-form',
    initComponent: function() {
        this.callParent(arguments);
        this.insert(6, [
        {
            xtype:'switch-widget-combobox',
            flex:1,
        },
        ]
        )
    },
})
