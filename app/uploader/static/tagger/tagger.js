/* 
 * @Author = Hassan Jannah
 */


$(document).ready(function() {
    init_tagger();
});
var project_id, document_id, document_url, filename, kwargs, templates_url;
var BODY_CHANGE_EVENT = 'bodyChange';
var TEMPLATES = {
    CONTAINER: {filename: 'container.html'},
    BUCKET: {filename: 'bucket.html'},
    BUCKET_NODE: {filename: 'bucket_node.html'},
    TREE_NODE: {filename: 'tree_node.html'},
    XML_PREVIEW: {filename: 'xml_preview.html'},
    OUTPUT_PREVIEW: {filename: 'output_preview.html'}
};
var buckets = {
    sentences: {id: 'sentence-bucket',
        header: 'Selected text nodes to analyze',
        help: 'Text nodes are nodes that contain the target text content of the analysis.'},
    dimensions: {id: 'dimension-bucket',
        header: 'Selected analysis dimensions',
        help: 'Dimensions are additional information that help perform multi-dimensional analysis on the text.'}};

var nodes;
function init_tagger() {
    loadRequestParams();
    nodes = new NodeModel();
    nodes.loadFromXMLURL(document_url);
    console.log(nodes);
    loadTemplates();
    render();
    loadNodeTreeEvents();
    loadTooltips();
    loadOutputPreview();

//    test();
//    console.log(JSON.stringify(nodes.toJSON()));
}
function test()
{
    var counter = 0;
    _.each(nodes.map, function(item)
    {
        item.attributes.dataType = 'text ' + counter++;
    });
    console.log(nodes);
}
function render() {
    renderContainers();
    renderBuckets();
    renderNodes(nodes, '#tagger-node-preview .tagger-container-body');
//    console.log(nodes.attributes.xml);
    renderXMLPreview(nodes.attributes.xml, '#tagger-xml-preview .tagger-container-body');
}
function loadRequestParams() {
    project_id = $('#project-id').val();
    document_id = $('#document-id').val();
    filename = $('#filename').val();
    document_url = $('#document-url').val();
    templates_url = $('#templates-url').val();
}

function saveStructureFile()
{

}

function loadTemplates()
{
    for (var template in TEMPLATES)
    {
        TEMPLATES[template]['url'] = templates_url + '/' + TEMPLATES[template].filename;
        TEMPLATES[template]['html'] = loadTemplate(TEMPLATES[template].url);
//        console.log(TEMPLATES[template]);
        TEMPLATES[template]['render'] = _.template(TEMPLATES[template]['html']);
    }
}
function loadTemplate(filename)
{
    var jqxhr = $.ajax({url: filename, async: false});
    return jqxhr.responseText;
}

function loadTooltips()
{
    try {
        $('.tagger-tooltip').tooltipster({contentAsHTML: true});
    }
    catch (err)
    {

    }
}
function renderTemplate(target, template, args)
{
    $(target).append(template.render(args));
    $(target).trigger(BODY_CHANGE_EVENT);
}
function removeNode(target) {

    var parent = $(target).parent();
    $(target).remove();
    parent.trigger(BODY_CHANGE_EVENT);
}
function renderContainers()
{
    renderTemplate('#tagger-buckets', TEMPLATES.CONTAINER,
            {id: 'tagger-buckets-container', header: 'Map your document',
                help: ''});
    renderTemplate('#tagger-node-preview', TEMPLATES.CONTAINER,
            {id: 'tagger-node-preview-container', header: 'Document Map',
                help: 'An abstract tree view of the document structure'});
    renderTemplate('#tagger-xml-preview', TEMPLATES.CONTAINER,
            {id: 'tagger-xml-preview-container', header: 'XML Preview',
                help: 'a preview of the source XML document'});
}


function renderBuckets() {
    for (var bucket in buckets)
    {
        renderTemplate('#tagger-buckets-container .tagger-container-body', TEMPLATES.BUCKET, buckets[bucket]);
    }
}

function renderNodes(node, target)
{
    if (node) {
        renderTemplate(target, TEMPLATES.TREE_NODE, node.attributes);
        if (node.attributes.metadata && $.isArray(node.attributes.metadata))
            for (var meta in node.attributes.metadata)
            {
                renderNodes(node.attributes.metadata[meta], '#' + node.attributes.id + ' .tagger-node-children:first');
            }
        if (node.attributes.units && $.isArray(node.attributes.units))
            for (var unit in node.attributes.units)
            {
                renderNodes(node.attributes.units[unit], '#' + node.attributes.id + ' .tagger-node-children:first');
            }

    }
//    }
}

function renderXMLPreview(xml, target, parent_id)
{
    parent_id = (parent_id) ? parent_id : NODE_ID_PREFIX;
    var node_id = parent_id + xml.tagName;
    xml['nodeId'] = node_id;
//    console.log(xml);
    renderTemplate(target, TEMPLATES.XML_PREVIEW, xml);
    var children = $(xml).children();
    if (children.length > 0)
    {
        _.each(children, function(child)
        {
            renderXMLPreview(child, '.' + node_id + ':last .xml-preview-children:first', node_id);
        });
    }
}


/********************
 *      EVENTS      *
 ********************/
function loadNodeTreeEvents()
{
    $('.tagger-node .collapse-node').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideUp();
        self.hide();
        self.siblings('.expand-node').show();
    }).on('mouseover', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').addClass('highlighted-nodes');
    }).on('mouseout', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').removeClass('highlighted-nodes');
    });
    $('.tagger-node .expand-node').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideDown();
        self.hide();
        self.siblings('.collapse-node').show();
    });
    $('.node-tag').on('click', function() {
        var self = $(this), id = self.attr('data-id'), isAttribute = parseInt(self.attr('data-isattribute'));
        $('.xml-preview-node .highlighted-nodes').removeClass('highlighted-nodes');
        $('.xml-preview-node .' + id).addClass('highlighted-nodes');
//        console.log(id);
        var top = $('#tagger-xml-preview-container .' + id + ":first").offset().top - $('#tagger-xml-preview-container .tagger-container-body').position().top - 25;
//        console.log(top);
        $('#tagger-xml-preview-container .tagger-container-body').scrollTop(top);
    });
    $('.node-tag-action-text').on('click', function()
    {
        var self = $(this);
        var id = self.attr('data-id');
        if (self.hasClass('added-node'))
        {
            //elemeent already added, remove it
            self.removeClass('added-node');
            removeTextElement(id);
        }
        else
        {
            self.addClass('added-node');
            self.siblings('.added-node').removeClass('added-node');
            removeDimensionElement(id);
            addTextElement(id);
            addBucketTagHighlightEvent(id);
        }

//        $('.bucket-body').trigger('change');
    });
    $('.node-tag-action-dimension').on('click', function()
    {
        var self = $(this);
        var id = self.attr('data-id');
        if (self.hasClass('added-node'))
        {
            //elemeent already added, remove it
            self.removeClass('added-node');
            removeDimensionElement(id);
        }
        else
        {
            self.addClass('added-node');
            self.siblings('.added-node').removeClass('added-node');
            removeTextElement(id);
            addDimensionElement(id);
            addBucketTagHighlightEvent(id);
        }
//        $('.bucket-body').trigger('change');

    });
}



function addTextElement(id)
{
    var node = nodes.map[id];
//    console.log(node);
    if (!node.attributes.isActive)
    {

        node.activate();
        node.setAsSentence(true);
        renderTemplate('#sentence-bucket .bucket-body', TEMPLATES.BUCKET_NODE, node.attributes);
//        console.log(nodes);
    } else {
        alert('node already added');
    }
//    node.rename(SENTENCE_TAG);

}
function addDimensionElement(id)
{
    var node = nodes.map[id];
    if (!node.attributes.isActive)
    {
        node.activate();
        node.setAsDimension(true);
        renderTemplate('#dimension-bucket .bucket-body', TEMPLATES.BUCKET_NODE, node.attributes);
//        console.log(nodes);
    } else {
        alert('node already added');
    }
}
function removeTextElement(id)
{
    var node = nodes.map[id];
    node.deactivate();
    node.setAsSentence(false);
    removeNode('#sentence-bucket > .bucket-body .' + id);
}
function removeDimensionElement(id)
{
    var node = nodes.map[id];
//    console.log(id);
    node.deactivate();
    removeNode('#dimension-bucket > .bucket-body .' + id);
}

function addBucketTagHighlightEvent(id) {
    $('.bucket-body .' + id).on('mouseover', function() {
        $('#' + id + ' > .node-tag').addClass('highlighted-tag');
    })
            .on('mouseout', function() {
                $('#' + id + ' > .node-tag').removeClass('highlighted-tag');
            });
}

function loadOutputPreview()
{
    //"DOMSubtreeModified"
    $('.bucket-body').on(BODY_CHANGE_EVENT, function() {
//        console.log('body changed');
        var data = nodes.getSample();
        $('#tagger-output-preview').empty();
        renderTemplate('#tagger-output-preview', TEMPLATES.OUTPUT_PREVIEW, {data:data});


    });

}