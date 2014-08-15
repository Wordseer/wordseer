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
        var key = tag.attr('metaname');
        var value = tag.children('.value').text();
        var key_display = tag.children('.key').text();
        var tag_display = key_display + " = " + value;

        me.items = [
            {
                xtype: 'wordseer-menuitem',
                text: 'filter by "' + tag_display + '"',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'sort by "' + key_display + '" (asc)',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'sort by "' + key_display + '" (desc)',
            },
            {
                xtype: 'wordseer-menuitem',
                text: 'search for "' + tag_display + '" (in new tab)',
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
