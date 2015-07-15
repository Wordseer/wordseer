Ext.define('WordSeer.view.sentence.SentenceMixins', {
	makeWordsClickable: function(html, elId){
		// given the sentence HTML, adds an onClick handler to each word
		return html.replace(/class='word'/g,
            function(match) {
                cls = "word ";
                // *********************************
                // TODO: this highlighting code doesn't work
                // sentence.gov_index is undefined
                // *********************************
                // if (sentence.gov_index.contains(i.toString())) {
                //     // cls += "gov-highlight ";
                //     cls += ' search-highlight';
                // }
                // if (sentence.dep_index == i) {
                //     // cls += "dep-highlight ";
                //     cls += ' search-highlight';
                // }
                i += 1;
                return (' onclick="Ext.getCmp(\'' +
                    elId +'\').fireEvent(\'wordclicked\', this, ' +
                    'Ext.getCmp(\'' + elId +'\'));"' +
               "container-id='" +elId+"' class='" + cls + "'");
            });
	}
});