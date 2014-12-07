/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Useful functions and global variables.
*/

var APP;
var phrase_set_LIST_STORE;
var phrase_set_STORE;
var COLLECTIONS_STORE;
var COLLECTIONS_LIST_STORE;
var SENTENCE_COLLECTIONS_STORE;
var SENTENCE_COLLECTIONS_LIST_STORE;
// colorbrewer Set3
var COLOR_SCALE = ["#8dd3c7","#fb8072","#b3de69","#bebada","#ffffb3","#80b1d3","#fdb462","#fccde5"];
var SUBSETS_COLOR_SCALE = d3.scale.category20();
var timing = 0;


/** checks if an array <a> contains an object <obj>**/
function contains(arr, obj) {
	if (typeof(arr) == typeof([])) {
		var i = arr.length;
		while (i--) {
			if (arr[i] == obj) {
				return true;
			}
		}
	}
	return false;
}

/** gets the keys of an object **/
function keys(obj)
{
    var keys = [];
    for (var key in obj)
    {
        if (obj.hasOwnProperty(key))
            keys.push(key);
    }
    return keys
}

/** gets all the tags **/
function getAllTags(){
	$.getJSON("src/php/listalltags.php",{}, function(data){
		allTags = data.tags;
		$(".tags.autocomplete").autocomplete({source:allTags});
		$("select.tag.select").html("");
		$("select.tag.select").append('<option name="filter" value="all">(all documents)</option>');
		for(var i = 0; i < data.tags.length; i++){
			$("select.tag.select").append('<option name="tag" value="'+data.tags[i]+'">'+data.tags[i]+'</option>');
		}
		if($.url.param("filter") && $.url.param("filter") == "tag" && contains(data.tags, $.url.param("tag"))){
		    $('select.tag').val($.url.param("tag"));
		}
		else{
			$('select.tag').val("all");
		}
	})
}

/** gets all the collections **/
function getAllCollections(){
    data = {};
    if(isSignedIn()){
        data['user'] = getUsername();
    }
	$.getJSON("src/php/listallcollections.php", data, function(data){
		allCollections = data.collections;
		$("select.collection.select").html("");
		$("select.collection.select").append('<option name="filter" value="all">(all documents)</option>');
		for(var i = 0; i < data.collections.length; i++){
			$("select.collection.select").append('<option name="collection" value="'+data.collections[i]+'">'+data.collections[i]+'</option>');
		}
		if($.url.param("collection")){
		    $('select.collection').val($.url.param("collection"));
	    }
		else{
			$('select.collection').val("all");
		}
	})
}

/** removes whitespace from the start and end of a string**/
String.prototype.trim = function () {
	return this.replace(/^\s*/, "").replace(/\s*$/, "");
}

/** appends a list of elements to the end of an array**/
Array.prototype.append = function(elements){
	for(var i = 0; i < elements.length; i++ ){
		this.push(elements[i]);
	}
	return this;
}


/** Lightens and darken colors
**/
function changeColorLightness(col,amt) {
    var usePound = false;
    if(col[0] == "#"){
        col = col.slice(1);
        usePound = true;
    }
    var num = parseInt(col,16);
    var r = (num >> 16) + amt;
    if(r > 255) r = 255;
    else if (r < 0) r = 0;
    var b = ((num >> 8) & 0x00FF) + amt;
    if ( b > 255 ) b = 255;
    else if  (b < 0) b = 0;
    var g = (num & 0x0000FF) + amt;
    if(g > 255) g = 255;
    else if (g < 0 ) g = 0;
    return (usePound?"#":"") + (g | (b << 8) | (r << 16)).toString(16);
}

Array.prototype.remove = function(s){
    for(i=0;i < this.length; i++){
        if(s==this[i]) this.splice(i, 1);
    }
}

/** checks if an array <a> contains an object <obj>**/
Array.prototype.contains = function(obj) {
	var i = this.length;
	while (i--) {
		if (this[i] === obj) {
			return true;
		}
	}
	return false;
}

/* calculates spacing between words based on the presence of punctuation*/
function spaceBetweenWords(word1, word2){
    if (word1 && word2) {
    	var prev = word1.substring(word1.length-1);
    	var next = word2.substring(0, 1);
    	var alphabet = "abcdefghijklmnopqrstuvwxyz&1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    	var no_space_before=".!,``)?;:%\"'";
    	var no_space_after='\'"``(';
    	var contractions = "n't";
    	if (next=="."){
    	    return "";
    	}
    	if (contractions.indexOf(word2) >= 0) {
    		return '';
    	} else if(no_space_before.indexOf(next) >= 0){
    		return '';
    	}else if(no_space_after.indexOf(prev) >= 0){
    		return '';
    	}else{
    		return ' ';
    	}
	} else {
	    return " ";
	}
}

/* accesses session storage to find out what the username is*/
function getUsername(){
    return sessionStorage["username"];
}

/* removes the field "username" from session storage */
function signUserOut(){
	sessionStorage.removeItem("username");
}

/* accesses session storage to set a username*/
function setUsername(name){
    if (typeof(sessionStorage) == 'undefined' ) {
		alert('Your browser does not support this feature, try upgrading.');
	}
	else{
		sessionStorage["username"] =  name;
	}
}

/* accesses session storage to find out what the instance is*/
function getInstance(){
    return sessionStorage.getItem('INSTANCE');
}

function setInstance(name) {
	sessionStorage.setItem('INSTANCE', name);
}

/* checks if an element is visible */
function isScrolledIntoView(elem, container) {
    var docViewTop = $(container).scrollTop();
    var docViewBottom = docViewTop + $(container).height()*0.5;
    var elemTop = $(elem).position().top;
    var elemBottom = elemTop + $(elem).height();
    return ((elemTop <= docViewTop) &&  (elemBottom >= docViewBottom));
}

/* Namespace declaration */
function setupWordSeer() {
	if (typeof(wordseer) == "undefined") {
		wordseer = {}
	}
}

/* continuous cycle through color palette */
function colorLoop(index) {
	index++;
	if (index >= COLOR_SCALE.length) {
		return 0;
	} else {
		return index;
	}
}

/* make a string safe to use as css class name */
function makeClassName(text) {
	return text.toLowerCase().replace(' ', '_');
}

/* convert a date format string from PHP strftime to moment.js tokens */
function momentFormat(fstring){
	var key, value, mFormat = fstring;
	var replacements = {
		'%a': 'ddd',
		'%A': 'dddd',
		'%b': 'MMM',
		'%B': 'MMMM',
		'%d': 'DD',
		'%H': 'HH',
		'%I': 'hh',
		'%j': 'DDDD',
		'%m': 'MM',
		'%M': 'mm',
		'%p': 'A',
		'%S': 'ss',
		'%Z': 'z',
		'%w': 'd',
		'%y': 'YY',
		'%Y': 'YYYY',
		'%%': '%'
	};

	for (key in replacements) {
		value = replacements[key];
		mFormat = mFormat.replace(key, value);
	}
	return mFormat;
}
