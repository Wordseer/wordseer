/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
WordSeer.collections.subsets.SubsetsBBar

A toolbar intended for use underneath a subsets TreePanel

Displays buttons for adding, deleting, duplicating and subsetting
subsets.

Used as a bottom toolbar by the following Treepanels:
    - WordSeer.view.collections.DocumentSetList
    - WordSeer.collections.words.PhraseSetList
**/
Ext.define('WordSeer.view.collections.subsets.SubsetsBBar',{
    extend:'Ext.toolbar.Toolbar',
    alias:'widget.subsets-toolbar',
    items:[
        {
            text:'Refresh',
            action:'refresh',
        },
        {
            text:'New',
            action:'new-set',
        },
        {
            text:'Subset',
            action:'new-subset',
            disabled: true,
        },
        {
            text:'Delete',
            action: 'delete-set',
            disabled: true,
        },
    ],
})
