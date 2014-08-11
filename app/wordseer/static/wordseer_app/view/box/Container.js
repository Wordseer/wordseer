/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.box.Container',  {
	extend:'Ext.Container',
    alias:'widget.wordseer-container',
    config: {
        /**
        @cfg {String} title The title of this panel
        */
        title: false,
    },

    constructor: function(cfg) {
        this.initConfig(cfg);
        this.id = Ext.id(this, 'overlay');
        this.autoEl = {
            tag: 'div',
            cls: 'overlay',
            children: [
            ]
        };
        if (this.title) {
            this.autoEl.children.splice(0, 0, {
                tag: 'span',
                cls: 'overlay-title',
                html: this.title
            });
        }
        this.callParent(arguments);
    },

    initComponent: function() {
        this.callParent(arguments);
    },

});
