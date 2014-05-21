/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The controller for the WordTree.
*/
Ext.define('WordSeer.controller.WordTreeController', {
	extend: 'Ext.app.Controller',
	views: [
		'visualize.wordtree.WordTree',
		'visualize.wordtree.SentencePopup',
	],
	init:function() {
		console.log('WordTree Controller Initialized');
		this.control({
			'word-tree': {
				// 'filter': function(view, selected_phrase, main_phrase) {
				// 	var widget = view.up('widget');
				// 	var breadcrumbs = widget.getComponent('breadcrumbs');
				// 	var formValues = this.getController('SearchController')
				// 		.assembleSearchParams(widget);
				// 	if (formValues.search.length == 0) {
				// 		breadcrumbs.addSearchBreadCrumb({
				// 			gov: main_phrase
				// 		})
				// 	}
				// 	breadcrumbs.addPhraseBreadCrumb(
				// 		Ext.create('WordSeer.model.PhraseModel', {
				// 			sequence: selected_phrase
				// 	}));
				// 	widget.fireEvent('searchParamsChanged', widget);
				// },
				'search': this.requestWordTreeData,
				'draw': this.makeWordTree,
				'nodeclick': this.wordTreeNodeClick,
				'nodedblclick': this.wordTreeNodeClick,
				'nodemouseover': this.wordTreeNodeMouseOver,
				'nodemouseout': this.wordTreeNodeMouseOut,
			}
		});
	},

	/** Fetches WordTree data from the server in response to a search request.
	When the server returns the data, calls the draw code.

	@param {WordSeer.model.FormValues} formValues a
	{@link WordSeer.controll.SeachController formValues} object.
	@param {WordSeer.view.visualize.wordtree.WordTree} word_tree_panel The view
	into which the WordTree should be rendered.
	*/
	requestWordTreeData: function(formValues, word_tree_panel) {
		Ext.Ajax.request({
		url:'../../src/php/wordtree/get-tree.php',
		method:'GET',
		disableCaching: false,
		timeout: 9000000,
		params: Ext.apply({
			collection:word_tree_panel.collection,
			metadata:formValues.metadata,
			phrases: formValues.phrases,
			user:getUsername(),
			instance:getInstance(),
		}, formValues.serialize()),
		scope:word_tree_panel,
		success:function(response){
		    var data  = Ext.decode(response.responseText);
		    this.fireEvent('draw', this, data.query, data.concordance);
		},
		failure: function(response) {
			console.log("request to get-tree failed.");
		}
		})
	},

	/** Computes the hierarchical word tree data structure from the given data
	then calls {@link #drawWordTree}. Uses the wordtree Javascript library in
	lib/wordtree.js

	@param {WordSeer.view.visualize.wordtree.WordTree} the WordTree view into
	which to render the tree.
	@param {String} query The root query, the root of the tree.
	@param {Object} concordance An object with 'left' and 'right' fields, which
	contain a list of sentence fragments that occurred to the left and right of
	the search query.
	*/
	makeWordTree:function(panel, query, concordance){
	    var detail = 100;
	    var rightTree = wordtree.makeWordTreeDataStructure(concordance['rights'],
	    	query, detail, "right");
		var leftTree = wordtree.makeWordTreeDataStructure(concordance['lefts'], "",
			detail, "left");
	    var w = panel.w,
	    canvasWidth = w*10,
	    h = panel.h;
	    var m = [20, 120, 20, canvasWidth/2];

	    // Get ready to draw the word tree by emptying this container and adding
	    // a new empty SVG container.
	    $('.'+panel.containerClass).html("");
	    var svg =  d3.select("."+panel.containerClass).append("svg:svg")
	           .attr("width", canvasWidth)
	           .attr("height", h)
	    var vis = svg.append("svg:g")
	    		.style("fill", "white")
	           .attr("transform", "translate(" + m[3] + "," + m[0] + ")");
		vis.panel = panel;

		// Calculate the dimensions of this Word Tree depending on the container
		// width and height, and the number of total branches.
		vis.m =m;
		vis.svg = svg;
		vis.w = w - vis.m[1] - vis.m[3];
	    vis.h = h - vis.m[0] - vis.m[2];
	    vis.maxVisibleBranches = Math.max(leftTree.children.length,
	    	rightTree.children.length);

	    vis.leftData = leftTree;
	    vis.rightData = rightTree;
		vis.maxWordTreeNodeID = 0;

		vis.container = $(panel.container);
		vis.wordtreeID = panel.wordtreeID;

		this.drawTree(leftTree, "left", vis, w, h, panel) // lib/wordtree-d3.js
		this.drawTree(rightTree,"right", vis, w, h, panel)	// lib/wordtree-d3.js
	},

	/** Draws a WordTree.
	@param {Object} data The hierarchical data structure containing the word
	tree. Each node (including the root) has the following fields:
		- {Number} x0, y0, x, y Positions
		- {Number} count The number of sentences under this node.
		- {Number} id The identifier of this node.
		- {Boolean} isRoot Whether or not this node is the root.
 		- {Number} depth The depth of this node.
		- {Array} ids The node ids of this node.
		- {Array} children The list of visible children of this node.
		- {Array} all_chilren The list of children of htis node
		- {Array} hidden_chilren a list of hidden children of this node.
		- {String} key The word or word sequence at this node.
		- {Boolean} expanded Whether or not this node is visible
		- {Boolean} selected Whether or not this node was selected for expansion
		by the user.
	@param {String} orientation "left" or "right", the side of the tree
	currently being drawn
	@param {WordSeer.view.visualize.wordtree.WordTree} the view in which the
	wordtree is currently being drawn.
	*/
	drawTree: function(data, orientation, vis, width, height){
		root = data;
		root.isRoot = true;
		if(orientation == "left"){
		  vis.leftData = root
		}else{
		  vis.rightData = root
		}
		vis.selectedIDs = [];
		vis.selectedNodeIDs = {left:[], right:[]};
		vis.selectedNodes = {left: [], right: []};
		// Initialize the display to show only one level of nodes.
		var me = this;
		root.children.forEach(function(child){
			me.toggleAll(child, me) // turn off all children of children
		});

		// A function that calculates the total height of the tree, depending
		// on the number of visible branches.
		vis.treeHeight = function(){
		    var vis = this;
		    var treeHeight = 20*vis.maxVisibleBranches;
		     var svgHeight = Math.max(treeHeight+vis.m[0], 100);
		     vis.svg.attr("height", svgHeight);
		     vis.h = svgHeight;
		    return treeHeight
		}

		// Initalize the tree layout algorithm from the D3 visualization library.
	    var me = this;
	    vis.tree_layout = d3.layout.tree()
	        .size([vis.treeHeight(), vis.w])
	        .sort(function(a, b){
	            return b.count - a.count;
	        })
	        .separation(function(a, b){
	            return me.fontSize(a)+me.fontSize(b)/2
	        });

	    vis.diagonal = d3.svg.diagonal()
	        .projection(function(d) {return [d.y, d.x]; });
		this.updateWordTreeNode(root, orientation, root, vis);
	},

	/** Calculates the font size of a node based on how many sentences are below it.
	@param {Object} d The node whose font size to calculate.
	*/
	fontSize: function(d){
	    if(d.isRoot){
	        return 40
	    }else{
	        return Math.min(35, 2*Math.sqrt(d.count)+7)
	    }
	},

	/** Calculates the width of a node.
	@param {Object} d The node whose width to calculate.
	*/
	width: function(d){
	    return this.fontSize(d) * d.key.length * 0.7
	},

	/** Called after any change to the word tree or when it's first rendered.
	Recursively moves nodes to their positions, and shows and hides them
	depending on whether they are expanded or not.
	@param {Object} source The parent node.
	@param {String} orientation Either 'left' or 'right' -- which tree we're
	drawing.
	@param {Object} root The root of this tree
	@param {SVGElement} vis The SVG element that is being drawn into.
 	*/
	updateWordTreeNode: function(source, orientation, root, vis) {
	    var diagonal = vis.diagonal;
	    var sign = (orientation == "left")?-1:1;
	    var duration = d3.event && d3.event.altKey ? 5000 : 500;

	    // Compute the new tree layout. Calculate the number of visible nodes
	    // and place the root at the center.
	    root.x0 = Math.min(vis.treeHeight()/2, 150);
	    root.y0 = 0;

		// Hierarchially compute new x and y values for each node in the tree
		// using the D3 visualization library.
		vis.tree_layout.size([vis.treeHeight(), vis.w]);
	    var nodes = vis.tree_layout.nodes(root);


	    // Normalize for the length of the longest strings, and
	    // move the root to the top of its child tree instead of
	    // the center.
	    this.calculateDepths(root, vis, sign);

	    // Correct positions for left-right orientation
	    if(orientation == "left"){
	      nodes.forEach(function(d){
	          d.y = -d.y;
	          if(d.isRoot){
	              vis.leftData = d
	          }
	        })
	    }else{
	      nodes.forEach(function(d){
	          if(!d.isRoot){
	              d.y = d.y-50;
	          }else{
	              vis.rightData = d;
	          }
	        })
	    }
	    // Update the visualization to reflect the new node positions.
	    var node = vis.selectAll("g.node"+"."+orientation)
	      .data(nodes, function(d) {
	      	  // If the nodes don't have ID's assign them id's.
	          return d.id || (d.id = ++vis.maxWordTreeNodeID);
	      });

	    // Start any newly-appearing nodes at the parent's previous position.
	    var nodeEnter = node.enter().append("svg:g")
	      .attr("class", "node "+orientation)
	      .attr("transform", function(d) {
	          return "translate(" + source.y0 + "," + source.x0 + ")";
	        })
	      .on("click", function(d){
	      		vis.event = d3.event;
	      		vis.panel.fireEvent('nodeclick',
	      			this, d,orientation, root, vis, "click");
	      })
	      .on("contextmenu", function(d){
	      		d3.event.preventDefault();
	      		vis.panel.fireEvent('nodecontextmenu',
	      			this, d,orientation, root, vis, "contextmenu");
	      })
	      .on("dblclick", function(d){
	          vis.panel.fireEvent('nodedblclick',
	           d, orientation, root, vis, "dblclick");
	      })
	      .on("mouseover", function(d){
	      		vis.panel.fireEvent('nodemouseover',
	      			this, d, orientation, root, vis, "mouseover");
	      })
	      .on("mouseout", function(d){
	          vis.panel.fireEvent('nodemouseout',
	          	this, d, orientation, root, vis, "mouseout");
	      });

	    var padding = 5;
	    var getNodeClasses = function(d) {
	        var childrenState = d.all_children.length > 0? 'tree':'leaf'
	        var filteredState = "";
	        if(vis.selectedNodeIDs[orientation].contains(d.id)){
	            filteredState = " selected";
	        }
	        var sentenceIDs = "";
	        if (d.ids) {
	           for (var i = 0; i < d.ids.length; i++) {
	              sentenceIDs += " wordtree-"+vis.wordtreeID+"-sentence-"+d.ids[i]; //TODO add wordtree id 2012-07-23 11:45 GMT-7
	           }
	        }
	        var classes = childrenState + filteredState + sentenceIDs;
	        return classes;
	    }
	    var controller = this;

	    nodeEnter.append("svg:text")
	      .attr("x", function(d) {
	          if(d.isRoot){
	              return 0
	          }else{
	             return orientation == "left"? -padding/2:padding/2;
	          }
	        })
	      .attr("fill", "black")
	      .attr("dy", ".35em")
	      .attr("id", function(d){return "text-"+d.id+"-wordtree-"+vis.wordtreeID})
	      .attr("text-anchor",function(d){
	              return orientation=="left"?"end":"start"
	      })
	      .attr("class", getNodeClasses)
	      .text(function(d) { return d.key; })
	      .style("fill-opacity", 1e-6)
	      .attr("font-size", this.fontSize);

	    // Transition nodes to their new position.
	    var nodeUpdate = node.transition()
	      .duration(duration)
	      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
	    nodeUpdate.select("text")
	        .attr("class", getNodeClasses)
	      .style("fill-opacity", 1);

	    // Transition exiting nodes to the parent's new position.
	    var nodeExit = node.exit().transition()
	      .duration(duration)
	      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
	      .remove();
	    nodeExit.select("text")
	      .style("fill-opacity", 1e-6);

	    // Update the links between nodes.
	    var link = vis.selectAll("path.link."+orientation)
	      .data(vis.tree_layout.links(nodes), function(d) { return d.target.id; });

	    // Enter any new links at the parent's previous position.
	    link.enter().insert("svg:path", "g")
	      .attr("class", "link "+orientation)
	      .attr("fill", "none")
	      .attr("stroke", "#D17519")
	      .attr("stroke-width", "0.5px")
	      .attr("d", function(d) {
	        var bbox = d3.select("#text-"+source.id+"-wordtree-"+vis.wordtreeID)[0][0].getBBox();
	        var o = {x: source.x0, y: source.y0+((padding+bbox.width)*sign)};
	        return vis.diagonal({source: o, target: o});
	      })
	    .transition()
	      .duration(duration)
	      .attr("d", function(d){
	          var sourceBox = d3.select("#text-"+d.source.id+"-wordtree-"+vis.wordtreeID)[0][0].getBBox();
	          var s = {x: d.source.x, y: d.source.y+((padding+sourceBox.width)*sign)};
	          return vis.diagonal({source:s, target:d.target})
	      });

	    // Transition links to their new position.
	    link.transition()
	      .duration(duration)
	      .attr("d", function(d){
	            var sourceBox = d3.select("#text-"+d.source.id+"-wordtree-"+vis.wordtreeID)[0][0].getBBox();
	            var s = {x: d.source.x, y:d.source.y+((padding+sourceBox.width)*sign)};
	            return vis.diagonal({source:s, target:d.target})
	        });

	    // Transition exiting links to the parent's new position.
	    link.exit()
	    .transition()
	      .duration(duration)
	      .attr("d", function(d) {
	          var bbox = d3.select("#text-"+source.id+"-wordtree-"+vis.wordtreeID)[0][0].getBBox();
	          var o = {x: source.x0, y: source.y0-((padding+bbox.width)*sign)};
	          return vis.diagonal({source: o, target: o});
	      })
	      .remove();

	    // Stash the old positions for transition.
	    nodes.forEach(function(d) {
	    d.x0 = d.x;
	    d.y0 = d.y;
	    });

	    // Scroll the container of this word tree so that the root of the
	    // tree is in view.
    	vis.container.parent().scrollTo('51%', {duration:1, axis:'x'});
	},

	/** Recursively repositions the x-value of tree nodes starting at the given
	node, to avoid overlapping text by moving them all to avoid the longest
	string at each level. Also calls {@link #adjustHeight} to move the node to
	the top of its child tree.

	@param {Object} d The node to reposition.
	@param {SVGElement} The main SVG canvas element.
	@param {Number} sign The sign of the adjustment to x, either -1 or +1. -1
	if we're drawing the left tree, +1 if we're drawing the right tree.
	*/
	calculateDepths: function(d, vis, sign){
	    if(d.isRoot){
	        d.y = d.y0;
	        d.x = d.x0;
	        d.depth = 0;
	    }else{
	        if(d.parent.isRoot){
	            d.y = this.width(d.parent)+50;
	            d.depth = 1;
	        }else{
	            var maxWidth = -1;
	            var controller = this;
	            d.parent.parent.children.forEach(function(node){
	                var w = controller.width(node);
	                if(w > maxWidth && node.children.length > 0){
	                    maxWidth = w
	                }
	            })
	            maxWidth = Math.max(maxWidth, 50);
	            d.y = d.parent.y + maxWidth;
	            d.depth = d.parent.depth + 1;
	        }
	        this.adjustHeight(d);
	    }
	    d.hidden_children = [];
	    var controller = this;
	    d.children.forEach(function(d){
	    	controller.calculateDepths(d, vis, sign)
	    });
	},

	/** To improve readability, recursively adjusts the y value (height) of parent
	nodes to the tops of their child trees (from the centers, where the D3 algorithm)
	positions them.
	@param {Object} d The node at which to start repositioning.
	*/
	adjustHeight: function(d){
	    if(!d.isRoot){
	        var minX = d.x;
	        d.children.forEach(function(node){
	            if(!minX){
	                minX = node.x
	            }
	            if(node.x < minX){
	                minX = node.x
	            }
	        })
	        var newX = Math.min(minX+20, d.x);
	        if (newX != d.x){
	            d.x = newX;
	            this.adjustHeight(d.parent);
	        }
	    }
	},

	/** Called when a word tree node is clicked or double clicked.
	For clicking, if the node was already
	selected, this deselcts it, and vice versa. Clicking a node filters the word
	tree to show only the sentences that 'pass through' that node. This list
	of sentences is stored in the 'ids' attribute of each node.

	Double clicking a node makes a difference (from just clicking a node) when
	there are already some filters active. Double clicking resets the filter to \
	only filter take into account that node.

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
	wordTreeNodeClick: function(node, d, orientation, root, vis, clickType){
		// Calculate which nodes should be collapsed or expanded.

		// If it's the root node that was clicked, then reset the filters.
	    if(d.isRoot){
	      vis.selectedIDs = [];
	      vis.selectedNodeIDs = {left:[], right:[]};
	      vis.selectedNodes = {left: [], right: []};
	      vis.filterDepth = 0;
	      vis.filterOrienation = null;
	    }
	    // If it was a double click, or there are no active filters, first
	    // reset the filters and then add the ID's for that node as the
	    // selected ID's.
	    else if(vis.selectedIDs.length == 0 || clickType == "dblclick"){
	        vis.selectedIDs = d.ids;
	        vis.selectedNodeIDs = {left:[], right:[]};
	        vis.selectedNodes = {left: [], right: []};
	        vis.selectedNodeIDs[orientation] = [d.id];
	        vis.selectedNodes[orientation] = [d];
	        vis.filterDepth = d.depth;
	        vis.filterOrientation = orientation;
	        this.toggle(d);
	    }
	    // If there are active filters, restrict the active filters to the
	    // just the list of ID's passing through this node.
	    else{
	    	//
	        this.toggle(d);
	        if((d.depth > vis.filterDepth && orientation == vis.filterOrientation) || orientation != vis.filterOrientation){
	            // sub-filtering in progress
	            vis.filterDepth = d.depth;
	            vis.selectedNodeIDs[orientation].push(d.id)
	            vis.selectedNodes[orientation].push(d);
	            var intersection = []
	            d.ids.forEach(function(id){
	                if(vis.selectedIDs.contains(id)){
	                    intersection.push(id)
	                }
	            })
	            vis.selectedIDs = intersection;
	            vis.filterOrientation = orientation;
	        }else if(d.depth < vis.filterDepth && orientation == vis.filterOrientation){
	            // backtracking up the tree
	            vis.selectedIDs = d.ids;
	            vis.selectedNodeIDs = {left:[], right:[]};
	            vis.selectedNodeIDs[orientation] = [d.id];
	            vis.selectedNodes[orientation] = [d.id];
	            vis.filterDepth = d.depth;
	            vis.filterOrientation = orientation;
	        }

	    }

	    // Apply the filter to the other tree, so nodes in the sentences that
	    // should be hidden or shown because of new filters can be hidden
	    // or shown as well.
	    var otherRoot = (orientation == "right")? vis.leftData:vis.rightData;
	    var otherOrientation = orientation == "right" ? "left" : "right";
	    vis.leftVisibleBranches = 0;
	    vis.rightVisibleBranches = 0;
	    this.showSentences(vis.selectedIDs, root, vis, orientation)
	    this.showSentences(vis.selectedIDs, otherRoot, vis, otherOrientation);

	    // Re-display the nodes.
	    vis.maxVisibleBranches = Math.max(vis.leftVisibleBranches, vis.rightVisibleBranches);
	    this.updateWordTreeNode(d, orientation, root, vis);
	    this.updateWordTreeNode(otherRoot, otherOrientation, otherRoot, vis);

	    // Compute the selected phrase.
	    var selected_phrase = "";
	    var main_phrase = "";
	    for (var i = vis.selectedNodes.left.length-1; i >= 0; i--) {
	      selected_phrase += vis.selectedNodes.left[i].key +" ";
	    }
	    if (vis.leftData.key.length > 0) {
	      selected_phrase += vis.leftData.key +" ";
	      main_phrase += vis.leftData.key +" ";
	    }
	    if (vis.rightData.key.length > 0) {
	      selected_phrase += vis.rightData.key + " ";
	      main_phrase += vis.rightData.key + " ";
	    }
	    for (var i = 0; i < vis.selectedNodes.right.length; i++) {
	      selected_phrase += vis.selectedNodes.right[i].key +" ";
	    }

	    // Inform the container that a filter has taken place.
	    $(vis.container).trigger('filter', [selected_phrase.trim(),
	        main_phrase.trim()]);
	},

	/** Show or hide the immediate children of the given node. If they are
	visible, hide them. If they are not visible, show them.
	@param {Object} d The node whose children should be hidden.
	*/
	toggle: function(d) {
	  if (d.children.length > 0) {
	      this.hideChildren(d);
	  } else {
	      this.showChildren(d);
	  }
	},

	/** Recursively show or hide all the descendants of the given node.
	If they are visible, hide them. If they are not visible, show them.
	@param {Object} d The node whose children should be hidden.
	*/
	toggleAll: function(d, controller) {
	  if (d.children) {
	    d.children.forEach(function(child){
	    	controller.toggleAll(child, controller)
	    });
	    controller.toggle(d);
	  }
	},

	/** Hide the children of the given node.
	@param {Object} d The node whose children should be hidden.
	*/
	hideChildren: function(d) {
	    d.hidden_children = d.all_children;
	    d.children = []
	},

	/** Show the children of the given node.
	@param {Object} d The node whose children should be hidden.
	*/
	showChildren: function(d){
	   d.children = d.all_children;
	   d.hidden_children = [];
	},

	/** Recursively hide or show a nodes upto a certain depth depending on how many
	sentences there are in this tree
	@param {Array[Number]} The list of visible sentence IDs.
	*/
	showSentences: function(ids, tree, vis, thisOrientation){
	    // fanOut is the depth to which to show nodes.
	    var fanOut = (ids.length < 50)? 10 :
	    (ids.length < 100)? 3:
	    (ids.length < 200)? 3 : 1;
	    // If there are sentences in this filter, recursively travel the
	    // tree and mark nodes visible if they span one of these sentences.
	    if(ids.length > 0){
	        tree.children = [];
	        var controller = this;
	        tree.all_children.forEach(function(t){
	            t.selected = false;
	            ids.forEach(function(id){
	                if(t.ids.contains(id)){
	                    t.selected = true;
	                }
	            })
	            if(t.selected){
	            // Show the nodes of this tree upto a certain depth
	                var show = false;
	                if(thisOrientation == vis.filterOrientation){
	                    if(t.depth <= vis.filterDepth + fanOut ){
	                        show = true
	                    }
	                }else{
	                    if(t.depth <= fanOut){
	                        show = true
	                    }
	                }
	                if(show){
	                    if(thisOrientation == "left"){
	                        vis.leftVisibleBranches += 1;
	                    }else{
	                        vis.rightVisibleBranches += 1;
	                    }
	                    controller.showSentences(ids, t, vis, thisOrientation);
	                    tree.children.push(t);
	                }
	            }
	        })
	    }
	    // If there are no selected sentences (i.e. there is no active filter)
	    // reset the tree nodes' visibility to their original state.
	    else{
	        // Show the children of the root
	        if(tree.isRoot){
	            this.showChildren(tree);
	            var controller = this;
	            tree.children.forEach(function(child){
	            	controller.hideChildren(child);
	            })
	            if(thisOrientation == "left"){
	                vis.leftVisibleBranches = tree.children.length;
	            }else{
	                vis.rightVisibleBranches = tree.children.length;
	            }
	        }
	    }
	},

	/** When the user hovers over a node, shows contextual information. If the
	node is not a leaf, it shows a popup with the number of sentences under
	the node. If the node is a leaf, it highlights all the nodes corresponding
	to the sentence, and shows a sentence popup.

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
	wordTreeNodeMouseOver: function(node, d, orientation, root, vis, eventName){
	    // Do nothing if the root is hovered over.
	    if(!d.isRoot){
	    	// If the hovered node is not a leaf, show a popup with the number.
		   	if(d.all_children.length > 1){
		   		// Remove the previous popups.
		        this.getController('SentencePopupController')
		        	.removePopup(vis.popup);
		        if (vis.number_popup) {
		        	vis.number_popup.remove();
		        }
		        vis.number_popup = d3.select(node).append("svg:text")
		          .attr("x", -15*(orientation=="left"?-1:1))
		          .attr("y", -10)
		          .attr("id", "number-popup")
		          .text("("+d.ids.length+")")
		          .attr("font-size", 10)
		          .attr("class", "number-popup");
		    }
		    // If the hovered node is a leaf, ask the server for details
		    // about the sentence, and highlight the nodes corresponding to
		    // this sentence.
		    else {
		    	// Get the sentence ID of the leaf -- since it's a leaf, there's
		    	// only one ID.
		        var id = d.ids[0];

		        // Highlight the nodes corresponding to this sentence by adding
		        // a CSS class to those SVG elements.
		        var nodes = $( ('*[class~="wordtree-' +
		        	vis.wordtreeID +'-sentence-'+id+'"]'));
		        for (var i = 0; i < nodes.length; i++) {
		            var old_class = $('#'+nodes[i].id).attr("class");
		            $('#'+nodes[i].id).attr("old-classes", old_class);
		            $('#'+nodes[i].id).attr("class",
		            	old_class+" wordtree-highlight-sentence");
		        }

		        // Only ask for a popup after 0.5 seconds, so that passing
		        // mouseovers don't cause popups to appear.
		        vis.event = d3.event;
		        var controller = this;
		        vis.mouseoverTimeout = setTimeout(function(){
		          controller.getMetadataForSentenceNode(node, id, orientation, vis)
		        }, 100);
		    }
		}
	},

	/** Requests details about the hovered-over sentence from the server.
	The server responds with a JSON object containing the following fields:
		- {String} sentence: The full sentence.
		- {String} title: The title of the document to which the sentence
		belongs.
		- {Object} metadata: Objects with name: and value: fields for metadata
		belonging to this sentence.
	@param {SVGElement} node: The svg element displaying the node that was
	hovered over.
	@param {Number} sentenceID The ID of the sentence about which to request
	information.
	@param {String} orientation 'left' or 'right' -- the side of the tree
	that we're drawing.
	#@param {SVGElement} vis The SVGElement in which the word tree is being
	drawn.
	*/
	getMetadataForSentenceNode: function(node, sentenceID, orientation, vis){
	    Ext.Ajax.request({
	        url:'../../src/php/strip-vis/getsentence.php',
	        method:'GET',
	        disableCaching: false,
	        params:{
	            id:sentenceID,
	            wordtree:'true',
	            instance:getInstance(),
	            user:getUsername(),
	        },
	        scope:this,
	        success:function(response){
	            var data = Ext.decode(response.responseText);
	            var sentence = {};
	            sentence.words = data.words;
	            sentence.sentenceID = data.sentence_id;
	            sentence.documentID = data.document_id;
	            sentence.metadata = data.metadata;
	            if (vis.number_popup) {
		            vis.number_popup.remove();
	            }
           		this.getController('SentencePopupController')
            		.removePopup(vis.popup);
	            vis.popup = Ext.create(
	            	'WordSeer.view.visualize.wordtree.SentencePopup',
	            	{
	                   sentences: [sentence],
	            	});
	            vis.popup.show();
	            vis.popup.setPosition(vis.event.pageX+20,
	                vis.event.pageY+20);
	        }
	    })
	},

	/** Called when the user mouses away from a node.
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
	wordTreeNodeMouseOut: function(node, d, orientation, root, vis, eventName){
	    clearTimeout(vis.mouseoverTimeout); //cancel queued popup
	    if (vis.popup) {
	    	var popup = vis.popup;
	    	var number_popup = vis.number_popup;
		    var controller = this.getController('SentencePopupController');
		    controller.destroySentencePopupTimeOut = setTimeout(function(){
		      controller.removePopup(popup);
		      if (number_popup){
			      number_popup.remove();
		      }
		    }, 1000);
		}
	    // Remove the highlight that was applied to the nodes when the user
	    // hovered over them, by restoring the old CSS class which we stored in
	    // the 'old-classes' attribute.
	    var nodes = $('*[class~="wordtree-highlight-sentence"]');
	    for (var i = 0; i < nodes.length; i++) {
	        $('#'+nodes[i].id).attr("class", $('#'+nodes[i].id).attr("old-classes"));
	        $('#'+nodes[i].id).attr("old-classes", "");
	    }
	},
})
