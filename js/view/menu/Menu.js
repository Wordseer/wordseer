/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.menu.Menu',  {
	extend:'Ext.Container',
    alias:'widget.wordseer-menu',
    floating: true,
    constrain: true,
    shadow: false,
    config: {
        /**
        @cfg {Object[]/WordSeer.view.menu.MenuItem} The options in this menu.
        */
        items: [],

        /**
        @cfg {Boolean} modal Whether or not this is a modal overlay.
        */
        destroyOnClose: true,

        /**
        @cfg {WordSeer.view.menu.Menu} menu The parent menu of this menu
        */
        parent: null,

        /**
        @cfg {WordSeer.view.menu.MenuItem} menu The parent menu item of this menu
        */
        parentMenuItem: null
    },
    /**
    @property {WordSeer.view.menu.Menu} submenu The currently-displayed submenu.
    */
    submenu: false,

    /**
    @property {Timeout} closer The timeout that will close this
    menu and all submenus.
    */
    closer: false,

    autoEl: {
        tag: 'ul',
        cls: 'menu'
    },

    defaults: {
        xtype: 'wordseer-menuitem'
    },

    initComponent: function() {
        this.items.forEach(function(item, i) {
            item.tabindex = i;
        })
        this.addEvents(
            /**
            @event close Fired on this panel when the user clicks the close
            button.
            @param {WordSeer.view.box.Overlay} panel The overlay.
            */
            'close'
            );
        this.callParent(arguments);
        this.addListener('afterrender', function(me) {
            me.populate();
        });

    },

    /**
    Bind events to mouse enter and mouse leave.
    */
    populate: function() {
        var me = this;
        me.getEl().on('mouseleave', function() {
            me.close();
        });
        me.getEl().on('mouseenter', function() {
            me.activate();
        });
        if (me.items.items.length === 0) {
            me.close(10);
        }
    },

    close: function(time) {
        var me = this;
        var duration = 500;
        if (time) {
            duration = time;
        }
        this.closer = setTimeout(function() {
            if (me.destroyOnClose) {
                me.destroy();
            } else {
                me.hide();
            }
            if (me.parent && (!me.parent.isDestroyed || me.parent.isVisible()) ) {
                me.parent.close();
            }
            if (me.submenu && (!me.submenu.isDestroyed ||
                me.submenu.isVisible())) {
                me.submenu.close(duration);
            }
        }, duration);
    },

    activate: function() {
        window.clearTimeout(this.closer);
        if (this.parent) {
            this.parent.activate();
        }
    }
});
