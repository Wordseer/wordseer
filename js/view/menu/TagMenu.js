/** A menu that appears next to metadata tags with options to
sort, filter, and search with the metadata item. Controlled by
the {@WordSeer.controller.TagMenuController TagMenuController}.

# TODO: Menu Options

**/
Ext.define('WordSeer.view.menu.TagMenu', {
    extend:'WordSeer.view.menu.Menu',
    alias:'widget.tagmenu',
    requires: [],
    width: 210,
    config: {
        /**
        @cfg {WordSeer.view.Word | HTMLElement} shownBy The item on the page
        next to which the menu should appear.
        */
        shownBy:null,

        /**
        @cfg {Ext.Component} view The actual component or container to which the
        {@link #shownBy} belongs.
        */
        view: null,

    },
    initComponent: function(){
        var me = this;
        var tag = $(me.shownBy);
        // retrieve metadata details
        me.key = tag.attr('metaname');
        me.value = tag.children('.value').text();
        me.key_display = me.key;
        me.tag_display = me.key_display + " = " + String(me.value).trim();

        me.items = [
            {
                xtype: 'wordseer-menuitem',
                text: 'filter by "' + me.tag_display + '"',
                action: 'filter',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'sort by "' + me.key_display + '" (asc)',
                action: 'sort',
                direction: 'ASC',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'sort by "' + me.key_display + '" (desc)',
                action: 'sort',
                direction: 'DESC',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'stop sorting by "' + me.key_display + '"',
                action: 'removesort',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'reset to collection order',
                action: 'resetsort',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'search for "' + me.tag_display + '" (in new tab)',
                action: 'search',
            },

        ];

        this.callParent(arguments);
    },

    close: function(time) {
        if (this.getShownBy().resetClass === undefined) {
            $(this.getShownBy()).removeClass('active');
        } else {
            this.getShownBy().resetClass();
        }
        this.callParent(arguments);
    }
});
