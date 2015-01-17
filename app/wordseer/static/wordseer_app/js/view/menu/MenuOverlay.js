/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** An overlay created by the top buttons in a layout panel.
*/
Ext.define('WordSeer.view.menu.MenuOverlay',  {
	extend:'WordSeer.view.box.Overlay',
    alias:'widget.menuoverlay',
    config: {
        /**
        @cfg {Ext.Element} button The button element to anchor to.
        */
        button: false,
        /**
        @cfg {Boolean} pinned Whether this element should stay visible after
        the mouse leaves it.
        */
        pinned: false,
    },
    draggable: {
        delegate: 'div.databox-head'
    },
    //resizable: true,
    layout: 'fit',
    destroyOnClose: false,
    constructor: function(cfg) {
        var wrapped = [
            {
                xtype: 'container',
                items: cfg.items,
                layout: cfg.layout,
                autoScroll: true,
            }
        ];
        cfg.items = wrapped;
        cfg.layout = 'fit';
        this.initConfig(cfg);
        this.callParent(arguments);
        this.autoEl.children.push({
            tag: 'div',
            cls: 'overlay-render-target',
            children: [],
        });
        this.pinned = false;
    },

    initComponent: function() {
        var layout = this.getLayout();
        layout.getRenderTarget = function() {
            var target = this.owner.el.down('div.overlay-render-target');
            this.innerCt = target;
            this.outerCt = this.owner;
            return target;
        };
        this.callParent(arguments);
        var me = this;
        if (me.button) {
            me.button.on('move', function() {
                me.showBy(me.button);
            });
            me.button.on('click', function() {
                if (me.isVisible()) {
                    me.hide();
                } else {
                    me.show();
                }
            });
        }
    },

    populate: function() {
        var me = this;
        me.getEl().down('.nav-button-close')
        .removeCls('nav-button-close')
        .addCls('nav-button-pinned')
        .addCls('disabled');
        me.getEl().down('.nav-button-pinned').on('click', function(event, el) {
            me.pinned = !me.pinned;
            if (me.pinned) {
                this.removeCls('nav-button-pinned');
                this.addCls('nav-button-close');
                this.removeCls('disabled');
            } else {
                this.addCls('disabled');
                this.removeCls('nav-button-close');
                this.addCls('nav-button-pinned');
            }
        });
        me.getEl().on('mouseleave', function(event) {
            me.close();
        });
        me.showBy(me.button);
    },
});
