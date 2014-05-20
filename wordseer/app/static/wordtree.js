/**********************************************************************
	wordtree.js
	Utilities for turning a list of sentences into a hierarchical Word Tree
	data structure of common words.
**********************************************************************/
if (typeof(wordtree) == 'undefined') {
	wordtree = {};
}


wordtree.makeWordTreeDataStructure = function(sentences, context, detail, direction){
	var tree = wordtree.makeTree(sentences, 1, detail, direction);
	var t = {children:tree, all_children:tree, key:context, count:sentences.length, expanded:true, selected:false}
    return t
}

/** Recursively makes a tree out of either a left or a right context
	@param context : a list of strings (sentences);
 **/
wordtree.makeTree = function(context, level, detail, orientation){	
	var tree = {};
	var first, sentence, max, collapsed, subtree, key ;
	max = 0;
	var keys = [];
	for(var i = 0; i < context.length; i++){
		sentence = context[i].sentence;
		if(sentence.length > 0){
			first = sentence[0];
			if(!first){
				sentence = sentence.slice(1);
				first = sentence[0]
			}
			if(first){
				first = first.toLowerCase();
				if(typeof(tree[first]) != 'object'){
					tree[first] = {key:first, after:[],depth:level, count:1, children:{}, ids:[]};
				}
				tree[first].after.push({id:context[i].id, sentence:sentence.slice(1)});
				tree[first].ids.push(context[i].id);
				tree[first].count += 1;
			} 
		}
	}
	var total =0;
	for(var key in tree){
		if(tree[key].count > max){
			max = tree[key].count;
		}
		keys.push(key);
		total += tree[key].count;	
	}
	for(var i = 0 ; i < keys.length; i++){
		key = keys[i];
		if(tree[key].count > (total*(100-detail)/100)){
			if(tree[key].after.length > 0){
				subtree = wordtree.makeTree(tree[key].after, level+1, detail, orientation);
				collapsed = wordtree.collapse(subtree, key, orientation);
				tmp = tree[key];
				delete tree[key];
				tree[collapsed.key] = {};
				tree[collapsed.key]["after"] = tmp["after"];
				tree[collapsed.key]["count"] = tmp["count"];
				tree[collapsed.key]["depth"] = tmp["depth"];
				tree[collapsed.key]["ids"] = tmp["ids"];
				tree[collapsed.key]["children"] = collapsed.children;
				tree[collapsed.key]["all_children"] = collapsed.children;
				tree[collapsed.key]["key"] = collapsed.key;
				tree[collapsed.key]["expanded"] = true;
				tree[collapsed.key]["selected"] = false;		
			}
		}else{
			delete tree[key];
		}
	}
	return wordtree.sort(tree);
}

wordtree.collapse = function(tree, key, orientation){
	if(tree.length == 1){
		for(k in tree){
			if(orientation == "right"){
				return wordtree.collapse(tree[k].children, key+" "+tree[k].key);
			}else if(orientation == "left"){
				return wordtree.collapse(tree[k].children, tree[k].key+" "+key);
			}
		}6
	}else{
		return {children:tree, "key":key}
	}
}

wordtree.sort = function(tree){
	var tmp = [];
	for(key in tree){
		tmp.push(tree[key]);
	}
	tmp.sort(wordtree.compareSubTrees);
	return tmp
}

wordtree.compareSubTrees = function(t1, t2){
	return t2.count - t1.count;
}