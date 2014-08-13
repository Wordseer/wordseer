Ext.define('WordSeer.view.menu.MenuItem', {
	extend: 'Ext.Component',
	alias: 'widget.wordseer-menuitem',

	config: {
		/**
		@cfg {String} text The inner HTML of the menu item
		*/
		text: '',

		tabindex:0,

		/**
		@cfg {String} iconCls (Optional) the class of the icon that should
		accompany this item.
		*/
		iconCls: false,

		/**
		@cfg {String} action A label for this menu item
		*/
		action: '',

		/**
		@cfg {Object[]/WordSeer.view.menu.MenuItem[]} The submenu
		*/
		menu: [],
	},
	maxWidth: 200,
	constructor: function(cfg) {
		this.initConfig(cfg);
		var me = this;
		cfg.id = Ext.id(me, 'menuitem');
		var children = [ {
			tag: 'span',
			cls: 'menuitem-text',
			html: me.text
		}];
		if (me.menu.length > 0) {
			children.push({
				tag: 'span',
				cls: 'sub-menu-icon'
			});
		}
		if (me.iconCls) {
			children.unshift({
				tag: 'span',
				cls: me.iconCls + " menu-icon"
			});
		}

		cfg.autoEl = {
			tag: 'li',
			cls: 'menuitem',
			tabindex: this.tabindex,
			children: children
		};
		this.initConfig(cfg);
		this.callParent(arguments);
	},

	initComponent: function() {
		var me = this;
		this.addEvents('click', 'highlight');
		this.callParent(arguments);
		this.addListener('afterrender', function(me) {
			me.populate();
		});
	},

	populate: function() {
		var me = this;
		me.getEl().on('click', function(event) {
			me.fireEvent('click', me, event);
			me.up('wordseer-menu').close(10);
		});

		me.getEl().on('keydown', function(event) {
			me.fireEvent('keypress', me, event);
			if (event.getKey() == event.DOWN) {
				if (me.next()) {
					me.next().highlight();
				}
			} else if (event.getKey() == event.UP) {
				if(me.prev()) {
					me.prev().highlight();
				}
			} else if (event.getKey() == event.ENTER) {
				me.fireEvent('click', me, event);
			}
		});

		me.getEl().on('mouseover', function(event) {
			var parent = me.up('wordseer-menu');
			parent.activate();
		});
		me.getEl().on('mouseenter', function(event) {
			var parent = me.up('wordseer-menu');
			if (parent.submenu && parent.submenu.close) {
				parent.submenu.destroy(); // close it instantly
			}
			me.highlight();
			parent.activate();
			var menu = null;
			if (me.menu instanceof Array && me.menu.length > 0) {
				menu = Ext.create('WordSeer.view.menu.Menu', {
					items: me.menu,
					parent: parent,
					parentMenuItem: me,
					floatParent: parent,
				});
			} else if (me.menu instanceof Object && me.menu.xtype) {
				me.menu.parent = parent;
				me.menu.floatParent = parent;
				me.menu.parentMenuItem = me;
				menu = Ext.widget(me.menu.xtype, me.menu);
			}
			if (menu) {
				menu.showBy(me, 'tl-tr?');
				parent.submenu = menu;
			}
		});

	},

	highlight: function() {
		var me = this;
		me.up().getEl().select('.hovered').removeCls('hovered');
		$(me.up().getEl().dom).find('[tabindex=1]').attr('tabindex', false);
		me.getEl().addCls('hovered');
		me.getEl().focus();
		me.focus();
		me.fireEvent('highlight', me);
	}
});
