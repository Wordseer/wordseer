/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls clicks and searches on the following metadata-related views:
    - {@link WordSeer.view.metadata.MetadataPane#search}: `search` event.
    - {@link WordSeer.view.metadata.facet.StringFacets}: a `click` event on
    an item in a treepanel.
    - {@link WordSeer.view.metadata.facet.RangeFacet}: events on the slider.
*/
Ext.define('WordSeer.controller.MetadataController', {
	extend: 'Ext.app.Controller',
	views: [
        'metadata.MetadataPane',
        'metadata.MetadataComboBox',
        'metadata.facet.StringFacets',
        'metadata.facet.RangeFacet',
        'metadata.RangeFacets',
        'treepanel.Treepanel'
	],
    stores: [
        'MetadataTreeStore',
    ],
    requires: [
        'Ext.data.TreeStore',
    ],
	init: function() {
		this.control({
            'windowing-viewport': {
                setchanged: this.subsetsChanged,
            },
            'layout-panel' :{
                newSlice: this.respondToSearch,
                menuButtonClicked: function(panel, type, button) {
                    if (type == 'filters') {
                        this.showMetadataOverlay(panel, button);
                    }
                }
            },
			'stringfacets' : {
				select: this.stringFacetitemclicked,
			},
            'rangefacet': {
                filter: this.rangeFacetFiltered,
            },
            'metadata-combobox': {
                'select': this.metadataComboBoxSelected
            },
            'metadata > panel[itemId=ranges]': {
                    expand: this.rangeFacetExpanded,
            },
            'metadata > header > checkbox': { // show language features
                change: function(checkbox) {
                    checkbox.up('metadata').drawMetadata();
                    checkbox.up('metadata').expand();
                }
            },
            'subsetslist': {
                'subsetschanged': this.subsetsChanged
            }
		});
	},

    /** The user has clicked on the range facets pane, making the facet visible.
    Renders the graph if not already rendered.
    @param {WordSeer.view.metadata.facet.RangeFacet} range_view The expanded
    view.
    */
    rangeFacetExpanded: function(ranges) {
        ranges.query('rangefacet').forEach(function(item) {
            item.draw();
        });
    },

    /** The user has filtered a range display. Adds a new metadata value
    to the {@link WordSeer.model.formValues} corresponding to the filter item
    and informs the
    {@link WordSeer.controller.SearchController#searchParamsChanged
    SearchController} that the search parameters have changed.

    @param {WordSeer.view.metadata.facet.RangeFacet} range_view The filtered
    view.
    @param {String} range_start The start of the filter range.
    @param {String} range_end The end of the filter range.
    */
    rangeFacetFiltered: function(range_view, range_start, range_end) {
        var record = Ext.create('WordSeer.model.MetadataModel', {
            range: [range_start, range_end],
            propertyName: range_view.getInfo().get('propertyName'),
            type: range_view.getType(),
            count: range_view.getTotal()
        });
        var panel = range_view.up('layout-panel');
        if (panel) {
            var widget = panel.down('widget');
            var formValues = panel.formValues.copy();
            formValues.metadata.push(record);
            widget.setFormValues(formValues);
            this.getController('SearchController').searchParamsChanged(panel,
                formValues);
        } else if (range_view.up('landing-page')) {
            this.getController('WindowingController').start();
            var formValues = Ext.create('WordSeer.model.FormValues');
            formValues.widget_xtype = 'word-tree-widget';
            formValues.metadata.push(record);
            var history_item = this.getController('HistoryController')
                .newHistoryItem(formValues);
            this.getController('WindowingController')
                .playHistoryItemInNewPanel(history_item.get('id'));
        }
    },

    /** The user has clicked on an item in the metadata-categories display.
    Adds a new metadata value corresponding to the clicked item and informs the
    {@link WordSeer.controller.SearchController#searchParamsChanged
    SearchController} that the search parameters have changed.

    @param {Ext.tree.Panel} treepanel The treepanel display.
    */
    stringFacetitemclicked: function(treepanel, record) {
        var panel = treepanel.up('layout-panel');
        var widget = panel.down('widget');
        var formValues = panel.getLayoutPanelModel().getFormValues().copy();
        var record_copy = Ext.create('WordSeer.model.MetadataModel', {
            text: record.get('text'),
            value: record.get('value'),
            count: record.get('count'),
            document_count: record.get('document_count'),
            propertyName: record.get('propertyName')
        });
        formValues.metadata.push(record_copy);
        widget.setFormValues(formValues);
        this.getController('SearchController').searchParamsChanged(panel,
            formValues);
    },

    /** Get and store the metadata corresponding to the user's search query
    from `src/php/grammaticalsearch/get-search-results.php`.

    @param {WordSeer.model.FormValues} formValues a formValues object
    representing a search query.

    @param {WordSeer.view.windowing.viewport.LayoutPanel} panel The panel to
    which the metadata belongs.
    */
    getMetadata:function(formValues, panel){
        var params = Ext.apply({
            instance:getInstance(),
            user:getUsername(),
            onlyMetadata:"true"
        }, formValues.serialize());
        panel.getLayoutPanelModel().getMetadataTreeStore().getProxy()
            .extraParams = params;
        panel.getLayoutPanelModel().getMetadataTreeStore().load();
        panel.getLayoutPanelModel().getMetadataListStore().getProxy()
            .extraParams = params;
        panel.getLayoutPanelModel().getMetadataListStore().load();
    },

    /** Responds to a search query by calling the {@link #getMetadata} function
    if the pane's search parameters are different from the old ones if the
    new search query is a different slice.
    @param {WordSeer.view.windowing.viewport.LayoutPanel} panel The panel
    to which the metadata belongs.
    @param {WordSeer.model.FormValues} formValues a formValues object
    representing the search query.
    */
    respondToSearch: function(panel, formValues) {
        if (!panel.formValues) panel.formValues = formValues;
        if (!panel.getLayoutPanelModel().isSameSlice()) {
            Ext.apply(formValues, formValues.search[0]);
            panel.getLayoutPanelModel().getMetadataListStore().load(
                {params:formValues.serialize()});
            this.getMetadata(formValues, panel);
            console.log('Loading metadata');
        }
    },

    /** The user has selected a value from the drop-down metadata combobox. Adds
    the selected item to the widget's metadata formValues and calls the
    {@link WordSeer.controller.SearchController#searchParamsChanged} handler.

    @param {WordSeer.view.metadata.MetadataComboBox} combobox The combobox the
    user selected.
    @param {Array[WordSeer.model.MetadataModel]} A list of
    {@link WordSeer.model.MetadataModel}s that are the selection.
    */
    metadataComboBoxSelected: function(combobox, selection) {
        var widget = combobox.up('widget');
        var formValues = widget.getFormValues().copy();
        for (var i = 0; i < selection.length; i++) {
            var record = selection[i];
            formValues.metadata.push(record);
        }
        widget.setFormValues(formValues);
        this.getController('SearchController').searchParamsChanged(widget);
        combobox.setValue("");
    },

    /** The subsets have changed, which means we need to reload all the metadata
    panes with fresh data from the server. Calls {@link #getMetadata} for
    each metadata pane.
    */
    subsetsChanged: function() {
        var panes = Ext.ComponentQuery.query('metadata-pane');
        var me = this;
        panes.forEach(function(pane) {
            var widget = pane.up('widget');
            if (widget) {
                formValues = widget.formValues;
                if (formValues) {
                    me.getMetadata(formValues, pane);
                }
            }
        });
        Ext.ComponentQuery.query('sets-overview').forEach(function(c){
            c.store.load();
        });
    },

    /**
    Shows the metadata filters overlay.
    @param {WordSeer.view.windowing.viewport.LayoutPanel} panel The layout
    panel upon which to show the overlay.

    @param {HTMLElement} button The button under which to show this overlay like
    a menu.
    */
    showMetadataOverlay: function(panel, button) {
        if (!panel.getComponent('metadata-overlay')) {
            var button_el = panel.getEl().down(
                'span.panel-header-menubutton.filters');
            var overlay = Ext.create('WordSeer.view.menu.MenuOverlay', {
                destroyOnClose: false,
                button: button_el,
                floatParent: panel,
                itemId: 'metadata-overlay',
                width: 360,
                height: 600,
                maxHeight: 700,
                items: [{
                        xtype: 'stringfacets',
                        filterFn: function(record) {
                            return record.get('type') == "string" &&
                            record.get('propertyName').indexOf('_set') == -1;
                        },
                        store:panel.getLayoutPanelModel()
                            .getMetadataTreeStore(),
                    },
                    {
                        xtype: 'rangefacets',
                        store: panel.getLayoutPanelModel()
                            .getMetadataTreeStore()
                    }
                ]
            });
            overlay.showBy(button_el);
            panel.add(overlay);
        }
    }
});
