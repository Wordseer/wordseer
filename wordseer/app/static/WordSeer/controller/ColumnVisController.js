/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The controller for the {@link WordSeer.view.visualize.columnvis.ColumnVis}
Column Visualization.
*/
Ext.define('WordSeer.controller.ColumnVisController', {
	extend: 'Ext.app.Controller',
	views: [
		'WordSeer.view.visualize.columnvis.ColumnVis',
	],
	init: function() {
        console.log('SentencePopup controller Initialized');
		this.control({
			'column-vis': {
				'search': this.requestColumnVisData,
				'draw': this.drawColumnVisData,
				'columnmouseover': this.columnMouseOver,
				'columnmouseout': this.columnMouseOut,
				'rectanglemouseover': this.rectangleMouseOver,
				'rectanglemouseout': this.rectangleMouseOut,
                'rectanglehoverintent': this.rectangleHoverIntent,
			}
		})
	},

	/** Requests data for the column visualization from the server at 
	../../src/php/strip-vis/get-sentences.php.
	@param {WordSeer.model.FormValues} formValues A 
	formValues object representing a search query.
	@param {WordSeer.view.visualize.columnvis.ColumnVis} view the column vis
	view into which the visualization should be drawn.
	*/
	requestColumnVisData: function(formValues, view){
        view.paper.clear();
        view.data = [] // reset, don't add;
        view.formValues = formValues;
        Ext.apply(view, formValues.serialize());
        view.search = formValues.search;
        var me = view;
        var i = 0;
        view.getEl().mask("loading");
        formValues.search.forEach(function(values){
            var index = i;
            var direction = 'ascending', sort = '';            
            Ext.Ajax.request({
                url:'../../src/php/strip-vis/get-sentences.php', 
                method:'GET',
                disableCaching: false,
                params:Ext.apply({
                    sort:sort,
                    direction:direction,
                    unit:'sentences',
                    collection:me.collection,
                    phrases: me.phrases,
                    metadata:me.metadata,
                    instance:getInstance(),
                    user:getUsername(),
                    query_id: formValues.query_id,
                }, values),
                scope:this,
                success:function(response){
                    view.getEl().unmask();
                    var documentInfo = Ext.decode(response.responseText);
                    view.data[index] = documentInfo;
                    if (index == formValues.search.length -1) {
                        view.draw(); 
                    }
                    view.getEl().unmask();
                },
                reset:function(response){
                    view.data = [];
                    view.draw();
                    view.getEl().unmask();
                }
            })
            i++;
        });
    },

    /** Called when the user mouses over a document column.
    @param {WordSeer.view.visualize.columnvis.ColumnVis} view The column
    visualization view.
    @param {RaphaelJS Rectangle} rect The rectangle representing a document that
    the user hovered over. 
    */
    columnMouseOver: function(view, rect) {
	    var narr = $(rect.node).attr("column");
	    var position = $(rect.node).closest("rect[column="+narr+"]").offset();
	    var popup = view.documentPopup;
	    var opacity =  
	    WordSeer.view.visualize.columnvis.ColumnVis.highlightFillOpacity;
	    popup.showAt([position.left+50, position.top]);
	    $(popup.getEl().dom).html(
	    	('<span class="title" document-id="'+narr+'">' + 
	    		$(rect.node).attr("title") + "</span>"));
	    $(rect.node).closest('rect[column="'+narr+'"]')
	        .css("fill-opacity", opacity);	
    },

    /** Called when the user mouses out of a document column.
    @param {WordSeer.view.visualize.columnvis.ColumnVis} view The column
    visualization view.
    @param {RaphaelJS Rectangle} rect The rectangle representing a document that
    the user hovered over. 
    */
    columnMouseOut: function(view, rect) {
	    view.documentPopup.hide();
	    var controller = this.getController('SentencePopupController');
        var sentencePopup = rect.vis.sentencePopup;
        controller.destroySentencePopupTimeOut = setTimeout(function(){
          controller.removePopup(sentencePopup);
        }, 1000);
	    var opacity = 
	    WordSeer.view.visualize.columnvis.ColumnVis.baseFillOpacity;
		if(rect.attr("fill") == $(rect.node).attr("c")){
			var narr = $(rect.node).attr("column");
			var i = $(rect.node).attr("index");
			$(rect.node).css("fill-opacity", opacity[i%2]);
		}
    },

    /** Called when the user mouses over a highlight rectangle. Calls 
    {@link #columnMouseOver} with the document column that represents the
    document in which this highlight occurs.

     @param {WordSeer.view.visualize.columnvis.ColumnVis} view The column
    visualization view.
    @param {RaphaelJS Rectangle} rect The rectangle representing a document that
    the user hovered over. 
    */
    rectangleMouseOver: function(view, rect) {
        var document_id = $(rect.node).attr("document");
        var document_rect = $(view.getEl().dom)
            .find('rect[column="'+document_id+'"]');
        this.columnMouseOver(view, {node:document_rect});
    },

    /** Called when the user mouses over a highlight rectangle. Shows a popup
    with the information about the document.
     @param {WordSeer.view.visualize.columnvis.ColumnVis} view The column
    visualization view.
    @param {RaphaelJS Rectangle} rect The rectangle representing a document that
    the user hovered over. 
    */
    rectangleMouseOut: function(view, rect) {
        rect.vis.documentPopup.hide();
        var controller = this.getController('SentencePopupController');
        var sentencePopup = rect.vis.sentencePopup;
        controller.destroySentencePopupTimeOut = setTimeout(function(){
          controller.removePopup(sentencePopup);
        }, 1000);
        var narr = $(rect.node).attr("document");
        var document_rect = $(view.getEl().dom)
            .find('rect[column="'+narr+'"]');
        var opacity = 
            WordSeer.view.visualize.columnvis.ColumnVis.baseFillOpacity;
        if(document_rect.attr("fill") == document_rect.attr("c")){
            var i = document_rect.attr("index");
            document_rect.css("fill-opacity", opacity[i%2]);
        }
    },

    /** Shows a {@link WordSeer.view.visualize.wordtree.SentencePopup}
    corresponding to the sentences that were hovered over.
    
    @param {WordSeer.view.visualize.columnvis.ColumnVis} view The column
    visualization view.
    @param {RaphaelJS Rectangle} rect The rectangle representing a highlight 
    that the user hovered over.
    @param {Number} index The index of the search term in the formValues object.
    @param {Event} event The hover event object that triggered this callback.
    */
    rectangleHoverIntent: function(view, rect, index, event) {
        var document_id = $(rect.node).attr("document");
        var document_rect = $(view.getEl().dom)
            .find('rect[column="'+document_id+'"]');
        this.columnMouseOver(view, {node:document_rect});
        var sentence_numbers = $(rect.node).attr("sentences");
        var color =  $(rect).attr("c");
        var params = Ext.apply({
          document:document_id,
          numbers: sentence_numbers,
          instance:getInstance(),
          user: getUsername(),
        }, view.search[index]);
        Ext.Ajax.request({
           url:'../../src/php/strip-vis/getsentence.php',
           method:'GET',
           disableCaching: false,
           params:params,
           scope:this,
           success:function(response){
               this.drawSentencePopup(response, rect, view, event);
           }
        })
    },

    /** Asks for data about highlight sentences from the server. Displays a 
    {@link WordSeer.view.visualize.wordtree.SentencePopup} for
    the sentences that match the hovered-over rectangle.

    @param {XMLHTTPResponse} response The data containing the information about
    the sentences matching the hovered-over highlight.
    @param {RaphaelJS Rectangle} rect The rectangle representing a highlight 
    that the user hovered over.
    @param {WordSeer.view.visualize.columnvis.ColumnVis} view The column
    visualization view.
    @param {Event} event The hover event object that triggered this callback.
    */
    drawSentencePopup:function(response, rect, view, event){
        var me = this;
        var sentences = Ext.decode(response.responseText);
        view.sentencePopup = Ext.create(
                    'WordSeer.view.visualize.wordtree.SentencePopup', 
                    {
                       sentences: sentences,
                    });
        view.sentencePopup.setPosition(event.pageX+20, 
           event.pageY+20);
        view.sentencePopup.show();
    },
})