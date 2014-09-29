/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The controller for the WordFrequencies.
http://trifacta.github.io/vega/
*/
Ext.define('WordSeer.controller.WordFrequenciesController', {
	extend: 'Ext.app.Controller',
	views: [
		'widget.WordFrequenciesWidget',
		'visualize.wordfrequencies.WordFrequencies',
	],
	init:function() {
//		console.log('Word Frequencies Controller Initialized');
		this.control({
			'word-frequencies': {
				'search': this.requestWordFrequenciesData,
			},
			'word-frequencies  checkbox[name=stacked]': {
				'change': this.change,
			},
			'word-frequencies  checkbox[name=normalized]': {
				'change': this.changeNormalized,
			},
			'word-frequencies  checkbox[name=labels]': {
				'change': this.toggleLabels,
			},
			'word-frequencies checkbox[action=hide-show-chart]': {
				'change': this.hideShowChart,
			},
			'word-frequencies  combobox': {
				'change': this.changeTopN,
			}
		});
	},

	/** Fetches WordFrequencies data from the server in response to a search request.
	When the server returns the data, calls the draw code.

	@param {WordSeer.model.FormValues} formValues a
	{@link WordSeer.controll.SeachController formValues} object.
	@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies}
	word_frequencies_panel The view into which the WordFrequencies should be
	rendered.
	*/
	requestWordFrequenciesData: function(formValues, word_frequencies_panel) {
		var values = formValues.serialize();
		Ext.Ajax.request({
		    url:'../../src/php/word-frequencies/bar-charts.php',
		    method:'GET',
		    disableCaching: false,
		    timeout: 900000,
		    params: Ext.apply({
		        metadata:formValues.metadata,
		        phrases: formValues.phrases,
		        user:getUsername(),
		        instance:getInstance(),
		    }, values),
		    scope:this,
		    success:function(response){
		        // reconfigure data for nv.d3
				var resp = Ext.decode(response.responseText),
		        	data = [],
					sentences = resp.counts[0].sentences,
					prop_names = [];

				d3.keys(sentences[0]).forEach(function(k){
					if (k.indexOf('__') >= 0) {
						var components = k.split('__');
						var type = components[0],
							name = components[1];
						prop_names.push(name);
						var prop = {
							'property': name,
							'type': type,
							'streams': [{
								'key': resp.counts[0].query.gov,
								'values': [],
							}],
						};
						var unique = {};
						sentences.forEach(function (sent) {
						  if (!unique[sent[k]]) {
						    prop.streams[0].values.push({
								"x": sent[k],
								"y": sentences.filter(function(s){
										return s[k] == sent[k];
									}).length,
								});
							unique[sent[k]] = true;
						  }
						});
						data.push(prop);
					}
				});

				word_frequencies_panel.data = data;
		        this.draw(data, word_frequencies_panel);
				word_frequencies_panel.fireEvent('rendered', word_frequencies_panel);
		    },
		    reset:function(response) {

		    },
		    failure: function(response) {

		    	console.log("request to bar-charts failed.");
		    }
		})
	},

	/** Draws a WordFrequencies.
	@param {Object} data The data structure containing a list of lists, where
	each list contains sentence records, each with complete metadata, that match
	each search in the {@link WordSeer.model.FormValues#search} values.
	frequencies.
	@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies} panel the
	view in which the wordfrequencies is currently being drawn.
	*/
	draw: function(data, panel){
		// size params
		var width = 375, height = 300,
			padding = {"top": 5, "bottom": 5, "left": 5, "right": 5},
			margin = {"top": 0, "bottom": 0, "left": 0, "right": 15};

		var canvas = d3.select(panel.getComponent('canvas').getEl().dom);
		var chart;

		data.forEach(function(x){
			var svg = canvas.append('div')
				.attr("class", "viz-container")
				.text(x.property)
					.append('div')
					.attr("class", "wordfreq")
						.append('svg')
						.attr("class", x.property)
						.datum(x.streams);

			var chart;
			nv.addGraph(function() {
			    chart = nv.models.multiBarChart()
			      .margin({bottom: 100})
			      .transitionDuration(300)
			      .delay(0)
			      .rotateLabels(45)
			      .groupSpacing(0.1)
				  .defaultState({"stacked": true})
				  .showLegend(false)
				  .showControls(false)
			      ;

			    chart.multibar
			      .hideable(false);

			    chart.reduceXTicks(false).staggerLabels(true);
				chart.yAxis
			        // .ticks
					.tickFormat(d3.format(',d'));

			    svg.call(chart);

			    nv.utils.windowResize(chart.update);

			    chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });

			    return chart;
			});

		});
	},

});
