/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.visualize.wordtree.WordTree', {
    extend:'Ext.Container',
    layout: 'fit',
    requires:[
        'Ext.tip.Tip',
    ],
    alias:'widget.word-tree',
    autoScroll: true,
    items:[
        {
            xtype:'component',
            itemId:'container',
            autoScroll: 'true',
        }
    ],
    initComponent:function(){
        this.w = 500,
        this.h = 3000,
        this.wordtreeID = (new Date()).getTime();
        /**
        @event search Fired when the user issues a search query or when the tree
        is loaded for the first time.
        @param {WordSeer.model.FormValues} formValues a
        formValues object representing a search query.
        @param {WordSeer.view.visualize.wordtree.WordTree} this WordTree view.
        */
        /**
        @event draw Fired when a request for data from the server
        returns successfully.
        @param {WordSeer.view.visualize.wordtree.WordTree} this WordTree view.
        @param {String} query The original query, the root of the tree.
        @param {Object} concordance An object containing 'left' and 'right' fields, which
        contain the list of left and right contexts in the tree.
        */
        /**
        @event nodeclick Fired when the user clicks on a node in the word tree.
        @param {SVGElement} node The svg element representing the node that was
        hovered over.
        @param {Object} d The object containing the data for the node that was
        clicked.
        @param {String} orientation Either 'left' or 'right', which tree we're
        drawing.
        @param {Object} root The root of this tree.
        @param {SVGElement} vis The svg canvas we're drawing into.
        @param {String} clickType either "click" or "dbclick".
        */
        /**
        @event nodedblclick Fired when the user double-clicks on a node in the
        word tree.
        @param {SVGElement} node The svg element representing the node that was
        hovered over.
        @param {Object} d The object containing the data for the node that was
        clicked.
        @param {String} orientation Either 'left' or 'right', which tree we're
        drawing.
        @param {Object} root The root of this tree.
        @param {SVGElement} vis The svg canvas we're drawing into.
        @param {String} clickType either "click" or "dbclick".
        */
        /**
        @event nodecontexmenu Fired when the user right-clicks on a node in the
        word tree.
        @param {SVGElement} node The svg element representing the node that was
        hovered over.
        @param {Object} d The object containing the data for the node that was
        clicked.
        @param {String} orientation Either 'left' or 'right', which tree we're
        drawing.
        @param {Object} root The root of this tree.
        @param {SVGElement} vis The svg canvas we're drawing into.
        @param {String} clickType either "click" or "dbclick".
        */
        /**
        @event nodemouseout Fired when the user's mouse leaves a node in the
        word tree.
        @param {SVGElement} node The svg element representing the node that was
        hovered over.
        @param {Object} d The object containing the data for the node that was
        clicked.
        @param {String} orientation Either 'left' or 'right', which tree we're
        drawing.
        @param {Object} root The root of this tree.
        @param {SVGElement} vis The svg canvas we're drawing into.
        @param {String} clickType either "click" or "dbclick".
        */
        /**
        @event nodemouseover Fired when the user mouses over a node in the word
        tree.
        @param {SVGElement} node The svg element representing the node that was
        hovered over.
        @param {Object} d The object containing the data for the node that was
        clicked.
        @param {String} orientation Either 'left' or 'right', which tree we're
        drawing.
        @param {Object} root The root of this tree.
        @param {SVGElement} vis The svg canvas we're drawing into.
        @param {String} clickType either "click" or "dbclick".
        */
        this.addEvents('search', 'draw','nodeclick','nodedblclick',
            'nodemouseover','nodemouseout', 'nodecontextmenu');
        this.callParent(arguments);
    },
    listeners:{
        afterrender:function(){
            this.container = this.getComponent('container').getEl().dom;
            $(this.container).addClass('word-tree-container');
            this.containerClass = 'word-tree-container-' + Ext.id(this, 'wordtree');
            $(this.container).addClass(this.containerClass);
             var me = this;
            $(this.container).bind('filter', function(event, selected_phrase,
                    main_phrase){
                 me.fireEvent('filter', me, selected_phrase, main_phrase);
             })
        },
        resize:function(me, width, height, oldWidth, oldHeight) {
            if (oldWidth > 0 && oldHeight > 0) {
                //center tree
                this.scrollBy(-9999999, 0, false);
                this.scrollBy(this.w*5.1-width/2, 0, false);
            }
        }
    },

    convertToHumanReadable: function(words){
        if(words.indexOf("|") == -1){
            return words;
        }else{
           var components = words.split("|");
           var rels = components[1];
           var humanLabel = rels+" todo ";
           return components[0]+" "+components[2];
        }
    },

})
