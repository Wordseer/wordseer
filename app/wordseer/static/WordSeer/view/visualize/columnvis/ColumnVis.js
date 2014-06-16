/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The main view that contains the Column Visualization. Uses the RaphaelJS
visualization library.
*/
Ext.define('WordSeer.view.visualize.columnvis.ColumnVis', {
    extend:'Ext.panel.Panel',
    requires:[
        'Ext.tip.Tip',
        'WordSeer.view.sentence.Sentence',
    ],
    alias:'widget.column-vis',
    config:{
        width:500,
        height:300,
    },
    title:'Column Visualization',
    items:[
        {xtype:'component', itemId:'container'}
    ],
    statics:{
        heatMapColors: d3.scale.category10(),
        baseFillOpacity: [0.3, 0.4],
        highlightFillOpacity: 0.5,
        minBlockWidth:3,
        minBlockHeight:5,
        maxBlockWidth:16,
        sentencesPerBlock:1,
        paragraphsPerBlock:2,
    },
    constructor:function(config){
      this.initConfig(config);
      this.callParent(arguments);
    },
    initComponent: function(){
        this.launcher = Ext.create('WordSeer.view.desktop.ColumnVisModule');
        this.data = [];
        this.processors = [];
        this.search = [];
        this._register = {};
        this.unit = 'sentences';
        this.documentPopup = Ext.create('Ext.tip.Tip', {
            html:'<span class=title>This is a title</span><br><span class="date">1929</span>',
            width:300,
            height: 'auto',
        });
        this.sentencePopup = Ext.create('Ext.panel.Panel',{
            width:500,
            autoScroll:true,
            floating:true,
        })
        this.addEvents('search', 'draw', 'columnmouseover','columnmouseout',
        'rectanglemouseover', 'rectanglemouseout', 'rectanglehoverintent');
        this.callParent(arguments);
    },
    listeners:{
        afterrender:function(){
            this.container = this.getComponent('container').getEl().dom;
            this.paper = Raphael(this.container, this.getWidth(), this.getHeight());
        },
        resize:function(panel, width, height, oldWidth, oldHeight){
            this.paper.setSize(width-20, height-20);
            this.draw();
        }
    },
    getQueryFromForm: function(gov, dep, relation){
        var query = null;
        if(relation == 2){
            query = gov.toString().replace(/,/, " ");
            this.queryIsGrammatical = "off";
        }else{
            query = gov+"|"+relation+"|"+dep;
            this.queryIsGrammatical = "on";
        }
        return query;
    },

    draw:function(){
        this.processors.forEach(function(processor) {
            clearInterval(processor);
        })
        this.processors = [];
        this.paper.clear();
        this.currentHeatMapColor = 0;
    	this.overlapRegister = {};
    	for(var i = 0; i < this.search.length; i++){
            if (i < this.data.length) {
                this.drawData(this.data[i], this.self.heatMapColors(this.currentHeatMapColor), i, this.data.length);
                this.currentHeatMapColor = (this.currentHeatMapColor + 1)%10;                
            }
    	}
    },

    drawData:function(data,currentColor, entryNumber, numEntries ){
        var overlay = (entryNumber > 0); /* only draw alternating grey columns the first time around*/
    	var documentInfo = [];
    	var sentences = [];
    	var rect = {};
    	var x = 0;
    	var y = 0;
    	var intensity = 0;
    	var sents = "";
    	var columns = this.paper.set();
    	var glow = 2;
    	var blockWidth = (this.getWidth()-20)/(data.length*numEntries);
    	blockWidth = Math.max(blockWidth, this.self.minBlockWidth);
    	blockWidth = Math.min(blockWidth, this.self.maxBlockWidth);
    	heatMapWidth = Math.max(data.length*numEntries*blockWidth, 800);
    	mainBlockWidth = blockWidth*numEntries;
    	var entry_x = blockWidth*entryNumber;
    	var maxLength = 0;
    	for(var i = 0; i < data.length; i++){
    	    data[i]['count'] = parseInt(data[i]['count']);
    		if(data[i]['count']> maxLength){
    		    maxLength = data[i]['count'];
    		}
    	}
    	//adaptable-height blocks
    	var perBlock = this.self.sentencesPerBlock;
    	//alert(perBlock);
    	if(this.unit == "paragraphs"){
    		perBlock = this.self.paragraphsPerBlock;
    	}
    	var heatMapHeight = this.getHeight()-20;
    	this.paper.setSize(heatMapWidth, heatMapHeight);
    	var smallest = perBlock*heatMapHeight/maxLength;
    	if(smallest < this.self.minBlockHeight){
    		perBlock = Math.round(this.self.minBlockHeight*maxLength/heatMapHeight);
    	}
    	var i = 0;
    	var limit = data.length;
    	var busy = false;
    	var vis = this;
    	if(data.length > 0){
    	    this.getEl().mask("drawing");
        	var processor = setInterval(function(){
                if(!busy){
                    busy = true;
                    documentInfo = data[i];
                    vis.drawDocument(documentInfo, perBlock, blockWidth, vis.self.blockHeight, vis.overlapRegister, x, mainBlockWidth, heatMapHeight, i, entry_x, currentColor, glow, overlay, entryNumber);
                	x += mainBlockWidth;
            		entry_x += mainBlockWidth;
                    i++;
                    if(i == limit){
                        clearInterval(processor);
                        vis.getEl().unmask();
                    }
                    busy = false;
                }else{
                    $("#debug").append("<br>Busy: "+processor);
                }
            }, 10);
            this.processors.push(processor);
        }else{
            vis.getEl().unmask();
        }       
    },

    drawDocument:function(documentInfo, perBlock, blockWidth, blockHeight, overlapRegister, x, mainBlockWidth, heatMapHeight, i, entry_x, currentColor, glow, overlay, entryNumber){
        var paper = this.paper;
        var baseFillOpacity = this.self.baseFillOpacity;
        var highlightFillOpacity = this.self.highlightFillOpacity;
        var words  = "";	
        y = 0;
        document = paper.set();
    	sentences = documentInfo['sentences'];
    	if(!sentences){
    	    sentences = [];
    	}
    	numBlocks = parseInt(parseInt(documentInfo['count'])/perBlock);
    	blockHeight = heatMapHeight/numBlocks;
    	if(!overlapRegister[i]) overlapRegister[i] = {};
    	if(!overlay){
    		rect = paper.rect(x, 0, mainBlockWidth, heatMapHeight);
    		$(rect.node).attr("column", documentInfo['document']);
    		$(rect.node).attr("index", i);
    		rect.attr("fill", "black");
    		rect.attr("stroke", "none");
    		rect.attr("fill-opacity", baseFillOpacity[i%2]);
    		$(rect.node).attr("c", "black");
    		$(rect.node).attr("fill", "black");
    		$(rect.node).attr("stroke", "#777");
    		$(rect.node).attr("title", documentInfo['title']);
    		$(rect.node).attr("date", documentInfo['date']);
    		rect.vis = this;
    		rect.hover(function(event){
                this.vis.fireEvent('columnmouseover', this.vis, this);
    		},
    		function(event){
    		     this.vis.fireEvent('columnmouseout', this.vis, this);
    		})	
    	}
    	for(var j = 1; j <= numBlocks; j++){
    	    if(!overlapRegister[i][j]) overlapRegister[i][j] = [];
    		if(sentences.length > 0 && (sentences[0].number/documentInfo['count'])*numBlocks < j){
    		    // Create a new rectangle.   		    
    			rect = paper.rect(entry_x, y, blockWidth, blockHeight);
    			rect.vis = this;
    			// Associate metadata with the newly-created rectangle.
    			$(rect.node).attr("document", documentInfo['document']);
    			$(rect.node).attr("title", documentInfo['title']);
    			$(rect.node).attr("date", documentInfo['date']);
    			$(rect.node).attr("start", sentences[0].number);
    			$(rect.node).attr("end", sentences[sentences.length-1]);
    			//$(rect.node).attr("words", words);
    			$(rect.node).attr("unit", sentences[0].id);
    			// register so that overlaps and interactivity
    			// can be computed
    			this.register(sentences[0].id, rect, "heatmap");
    			overlapRegister[i][j].push(rect);
    			// collect all the matching sentences within this block
    			sents = "";
    			intensity = 0;
    			while(sentences.length > 0 && (parseInt(sentences[0].number)/documentInfo['count'])*numBlocks < j){
    				intensity += 1;
    				sents += sentences[0].number+" ";
    				sentences = sentences.slice(1, sentences.length);
    			}
    			$(rect.node).attr("sentences", sents);
    			//set block appearance -- color, opacity, outline
    			intensity = Math.min(5, intensity*2)/5; // not used
    			$(rect.node).attr("c", currentColor);
    			//record the original color elsewhere too
    			$(rect.node).attr("unoverlapped_c", currentColor); 
    			rect.attr("fill-opacity", 1); // used to be intensity, not 1
    			$(rect.node).attr("stroke", "#333");
    			rect.attr("cursor", "pointer")
    			// check for overlap and color appropriately
    			rect.attr("fill", currentColor);
    			if(overlapRegister[i][j].length > 1){
    		        for(var k = 0; k < overlapRegister[i][j].length; k++){
    		             var rect = overlapRegister[i][j][k];
    		             var color = $(rect.node).attr("unoverlapped_c");
    		             var newColor = changeColorLightness(color, 50);			             
    		             rect.attr("fill", newColor);
    		             rect.attr("c", newColor);
    		        }
    		    }
    			// Fire events on the ColumnVis view whenever the highlight
                // rectangle is moused over, moused out, or hovered over for more
                // than a few seconds (hoverintent).
    			rect.vis = this;
    			rect.node.vis = this;
    			$(rect.node).data('vis', this);
    			rect.hover(function(event){
                    this.vis.fireEvent("rectanglemouseover", this.vis, this);
    			},
    			function(event){
    			    this.vis.fireEvent('rectanglemouseout', this.vis, this);
    			});
    			$(rect.node).hoverIntent(function(event){
    			   this.vis.fireEvent('rectanglehoverintent', rect.vis, 
                    rect, 
                    entryNumber, event);
    			}, function(){})
    		}
    		y += blockHeight;
    	}
    },
    /*************************************************************
    Interactivity between the heat map and the concordance
    *************************************************************/

    /** register objects as belonging to a particular heat map item **/
    register: function(id, object, type){
    	if(this._register[id] == null){
    		this._register[id] = {heatmap:new Array(), wordtree:new Array()};
    	}
    	this._register[id][type].push(object);
    },
    getRegistered:function(id, type){
    	return this._register[id][type];
    }
})