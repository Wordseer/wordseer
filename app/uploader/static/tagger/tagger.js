/* 
 * @Author = Hassan Jannah
 */


$(document).ready(function() {
    init_tagger();
});
var project_id, document_id, document_url, filename, kwargs, templates_url;
var TEMPLATES = {
    CONTAINER: {filename: 'container.html'},
    BUCKET: {filename: 'bucket.html'},
    TREE_NODE: {filename: 'tree_node.html'}
};
var buckets = {
    sentences: {id: 'sentance-bucket',
        header: 'Select text nodes to analyze',
        help: 'Text nodes are nodes that contain the target text content of the analysis.'},
    dimensions: {id: 'dimension-bucket',
        header: 'Select addtional dimensions',
        help: 'Dimensions are additional information that help perform multi-dimensional analysis on the text.'}};

var nodes;
function init_tagger() {
    loadRequestParams();
    nodes = new NodeModel();
    nodes.loadFromXMLURL(document_url);
    loadTemplates();
    render();
    loadNodeTreeEvents();

    loadTooltips();

    test();
//    console.log(JSON.stringify(nodes.toJSON()));
}
function test() {

}
function render() {
    renderContainers();
    loadBuckets();
    renderNodes(nodes, '#tagger-node-preview .tagger-container-body');
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
        TEMPLATES[template]['render'] = _.template(TEMPLATES[template]['html']);
    }
}
function loadTemplate(filename)
{
    var jqxhr = $.ajax({url: filename, async: false});
    return jqxhr.responseText;
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
function renderTemplate(target, template, args)
{
    $(target).append(template.render(args));
}


function loadBuckets() {
    for (var bucket in buckets)
    {
        renderBucket('#tagger-buckets-container .tagger-container-body', buckets[bucket]);
    }
}

function renderBucket(target, bucket)
{
    renderTemplate(target, TEMPLATES.BUCKET, bucket);
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


function loadTooltips()
{
    try {
        $('.tagger-tooltip').tooltipster({contentAsHTML: true});
    }
    catch (err)
    {

    }
}

function loadNodeTreeEvents()
{
    $('.tagger-node .collapse-node').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideUp();
        self.hide();
        self.siblings('.expand-node').show();
    }).on('mouseover', function(){
         var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').addClass('highlighted-nodes');
    }).on('mouseout', function(){
         var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').removeClass('highlighted-nodes');
    });
    $('.tagger-node .expand-node').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideDown();
        self.hide();
        self.siblings('.collapse-node').show();
    });
}