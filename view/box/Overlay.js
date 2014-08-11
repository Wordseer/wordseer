/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.box.Overlay',  {
	extend:'Ext.Container',
    alias:'widget.overlay',
    floating: true,
    cls: 'inner',
    config: {
        /**
        @cfg {Boolean} modal Whether or not this is a modal overlay.
        */
        modal: false,

        /**
        @cfg {String} title The title of this panel
        */
        title: false,

        /**
        @cfg {Boolean} modal Whether or not this is a modal overlay.
        */
        destroyOnClose: true,
    },
    layout: 'fit',
    /**
    @property {Boolean} menuActive Whether or not there's a menu active over this
    overlay -- so that it doesn't automatically close when the mouse "leaves" to
    mouse over this overlay.
    */
    menuActive: false,
    constructor: function(cfg) {
        this.initConfig(cfg);
        this.id = Ext.id(this, 'overlay');
        this.autoEl = {
            tag: 'div',
            cls: 'overlay',
            children: [
                {
                    tag: 'span',
                    cls: 'nav-button nav-button-close',
                },
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

    populate: function() {
        var me = this;
        me.getEl().down('.nav-button-close').on('click',
            function(event, clicked_el, clicked_dom) {
                if (me.destroyOnClose) {
                    me.destroy();
                } else {
                    me.hide();
                }
        });
    },

    close: function() {
        var me = this;
        if (!me.pinned && (!me.menuActive || me.menuActive.isDestroyed)) {
            if (me.destroyOnClose) {
                me.destroy();
            } else {
                me.hide();
            }
        }
    }
});
