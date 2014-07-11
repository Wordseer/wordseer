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
    TITLE_TREE_NODE: {filename: 'title_tree_node.html'},
    XML_PREVIEW: {filename: 'xml_preview.html'},
    OUTPUT_PREVIEW: {filename: 'output_preview.html'},
    RENAME_FORM: {filename: 'rename_form.html'}
};
var buckets = {
    sentences: {id: 'sentence-bucket',
        header: 'Selected text nodes to analyze',
        help: 'Text nodes are nodes that contain the target text content of the analysis.'},
    properties: {id: 'property-bucket',
        header: 'Selected analysis properties',
        help: 'Properties are additional information that help perform multi-propertyal analysis on the text.'}};
var NODE_TYPES = {TEXT: 'text', PROPERTY: 'property'};
var nodes;
function init_tagger()
{
    loadRequestParams();
    nodes = new NodeModel();
    nodes.loadFromXMLURL(document_url, filename);
//    console.log(nodes);
    loadTemplates();
    render();
    loadNodeTreeEvents();
    loadTooltips();
    loadOutputPreview();
    loadSubmit();
    addRootNode();
}
function test()
{
    var counter = 0;
    _.each(nodes.map, function(item)
    {
        item.attributes.dataType = 'text ' + counter++;
    });
}
function render()
{
    renderContainers();
    renderBuckets();
    renderTreeNodes(nodes, '#tagger-node-preview .tagger-container-body');
    renderXMLPreview(nodes.attributes.xml, '#tagger-xml-preview .tagger-container-body');
//    $('.tagger-container').resizable();
}
function loadRequestParams()
{
    project_id = $('#project-id').val();
    document_id = $('#document-id').val();
    filename = $('#filename').val();
    document_url = $('#document-url').val();
    templates_url = $('#templates-url').val();
}
function loadSubmit()
{
    $('#tagger').submit(function() {
        saveStructureFile();
        return false;
    });
}
function saveStructureFile()
{
//    alert('Saving structure file');
    var data = nodes.toActiveJSON(), token = $('#csrf_token').val();
    var url = window.location.href + '/save/';
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data)
        , dataType: 'json'
        , contentType: "application/json"
    }).done(function(msg) {
        alert("Data Saved: " + msg);

    }).error(function(msg) {
        var text = msg.responseText;
        console.log(text);
        var pieces = url.split('/'), temp = pieces.slice(0, pieces.length - 4), redirect_url = temp.join('/');
        if (text === 'ok')
        {

            window.location.replace(redirect_url);
            return false;
        }
        else {
            $('#tagger-save-file-response > .panel-body').html(msg.responseText);
            $('#tagger-save-file-result').show().on('click', function() {
                hideSaveFileResponse();
            });
        }
    });
}
function hideSaveFileResponse()
{
    $('#tagger-save-file-result').hide();
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

function loadTooltips()
{
    try {
        $('.tagger-tooltip').tooltipster({contentAsHTML: true});
    }
    catch (err)
    {

    }
}
function renderTemplate(target, template, args, replace, id)
{
    if (replace)
    {
        if ($(target).length > 0)
        {
            $(target).replaceWith(template.render(args));
        }
        else
        {
            $(target).append(template.render(args));
        }
    }
    else
    {
        $(target).append(template.render(args));
    }
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
    renderTemplate('#tagger-output-preview', TEMPLATES.CONTAINER,
            {id: 'tagger-output-preview-container', header: 'XML Preview',
                help: 'a preview of the source Output text and properties document'});
}


function renderBuckets() {
    $('#tagger-buckets-container .tagger-container-body').append('<table></table>');
    for (var bucket in buckets)
    {
        renderTemplate('#tagger-buckets-container .tagger-container-body table', TEMPLATES.BUCKET, buckets[bucket]);
    }
}
function renderTreeNodes(node, target)
{
    renderNodes(node, TEMPLATES.TREE_NODE, target, 'tree');
}
function renderTitleTreeNodes(node, target)
{
    renderNodes(node, TEMPLATES.TITLE_TREE_NODE, target, 'title');
}

function renderNodes(node, template, target, target_prefix)
{
    if (node) {
        var target_id = '#' + target_prefix + '-' + node.attributes.id + ' .tagger-node-children:first';
        renderTemplate(target, template, node.attributes);
        if (node.attributes.metadata && $.isArray(node.attributes.metadata))
            for (var meta in node.attributes.metadata)
            {
                renderNodes(node.attributes.metadata[meta], template, target_id, target_prefix);
            }
        if (node.attributes.units && $.isArray(node.attributes.units))
            for (var unit in node.attributes.units)
            {
                renderNodes(node.attributes.units[unit], template, target_id, target_prefix);
            }
    }
}

function renderXMLPreview(xml, target, parent_id)
{
    parent_id = (parent_id) ? parent_id : NODE_ID_PREFIX;
    var node_id = parent_id + S(xml.tagName).replaceAll('.', '_');
    xml['nodeId'] = node_id;
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

function addRootNode()
{
    var root_node = $('.node-tag-document');
    var root_id = root_node.attr('data-id');
    addElement(null, root_id, NODE_TYPES.PROPERTY, true);
}
/********************
 *      EVENTS      *
 ********************/
function loadNodeTreeEvents()
{
    loadGenericNodeTreeEvents();
    $('.node-tag').on('click', function() {
        var self = $(this), id = self.attr('data-id');
        $('.xml-preview-node .highlighted-nodes').removeClass('highlighted-nodes');
        $('.xml-preview-node .' + id).addClass('highlighted-nodes');
        $('#tagger-xml-preview-container .tagger-container-body').scrollTop(0);
        var top = $('#tagger-xml-preview-container .' + id + ":first").offset().top - $('#tagger-xml-preview-container .tagger-container-body').position().top - 25;
        $('#tagger-xml-preview-container .tagger-container-body').scrollTop(top);
    });
    $('.node-tag-action-text').on('click', function()
    {
        processElement(this);

    });
    $('.node-tag-action-property').on('click', function()
    {
        processElement(this);

    });
}
function loadGenericNodeTreeEvents()
{
    $('.tagger-node .collapse-node').unbind('click').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideUp();
        self.hide();
        self.siblings('.expand-node').show();
    }).unbind('mouseover').on('mouseover', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').addClass('highlighted-nodes');
    }).unbind('mouseout').on('mouseout', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').removeClass('highlighted-nodes');
    });
    $('.tagger-node .expand-node').unbind('click').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideDown();
        self.hide();
        self.siblings('.collapse-node').show();
    });
}

function addBucketTagEvents(id) {
    $('.bucket-body > .' + id).on('mouseover', function()
    {
        console.log('hovering over '+id)
        $('#tagger-node-preview .' + id).addClass('highlighted-tag');
        $('#tagger-output-preview .' + id).addClass('highlighted-tag');
    }).on('mouseout', function()
    {
        $('#tagger-node-preview  .' + id).removeClass('highlighted-tag');
        $('#tagger-output-preview  .' + id).removeClass('highlighted-tag');
    });
    $('.bucket-body .bucket-tag-property.' + id).on('click', function()
    {
        var self = $(this), type = self.attr('data-type');
        showRenameDialogue(id);
    });
}


function processElement(el)
{
    var tag = $(el), id = tag.attr('data-id'), nodeType = tag.attr('data-node-type');

    if (tag.hasClass('added-node'))
        removeElement(tag, id, nodeType);
    else
        addElement(tag, id, nodeType);
}
function removeElement(tag, id, nodeType)
{
    if (!tag)
        tag = $('.node-tag-action.' + id);
    tag.removeClass('added-node');
    if (nodeType === NODE_TYPES.TEXT)
        removeTextElement(id);
    else
        removePropertyElement(id);
}
function addElement(tag, id, nodeType, renameDialogue)
{
    var bucket = $('.bucket-tag-' + nodeType + '.' + id);
    if (bucket.length === 0)//check if bucket node already exists
    {
        if (!tag) {
            tag = $('.node-tag-action-' + nodeType + '.' + id);
            tag.attr('data-added-auto', 'true');
        }
        tag.toggleClass('added-node');
        tag.siblings('.added-node').removeClass('added-node');
        if (nodeType === NODE_TYPES.TEXT)
        {
            addTextElement(id);
        }
        else
        {
            addPropertyElement(id, renameDialogue);
        }
        addBucketTagEvents(id);
    }
    else
    {
        console.log('tag alreeady exists ' + id);
    }
}
function addTextElement(id)
{
    removePropertyElement(id);
    var node = nodes.map[id];
    if (!node.attributes.isActive)
    {
        node.activate();
        node.setAsSentence(true);
        renderTemplate('#sentence-bucket .bucket-body', TEMPLATES.BUCKET_NODE, node.attributes);
    } else {
        alert('node already added');
    }
}
function addPropertyElement(id, renameDialogue)
{
    removeTextElement(id);
    var node = nodes.map[id];
    if (!node.attributes.isActive)
    {
        node.activate();
        node.setAsProperty(true);
        renderTemplate('#property-bucket .bucket-body', TEMPLATES.BUCKET_NODE, node.attributes);
    } else {
        alert('node already added');
    }

    if (renameDialogue || node.attributes.type === SUBUNIT_TAG)
        showRenameDialogue(id);
}
function removeTextElement(id)
{
    var node = nodes.map[id];
    node.deactivate();
    node.setAsSentence(false);
    removeNode('#sentence-bucket .bucket-body .' + id);
}
function removePropertyElement(id)
{
    var node = nodes.map[id];
    node.deactivate();
    removeNode('#property-bucket .bucket-body .' + id);
}

function refreshElement(id) {

    var node = nodes.map[id], target = '.bucket-tag.' + id;
    renderTemplate(target, TEMPLATES.BUCKET_NODE, node.attributes, true, id);
    addBucketTagEvents(id);

}
/****************************
 *      Rename dialogue     *
 ***************************/
/**
 * 
 * @param {type} id
 * @returns {undefined}
 */
function showRenameDialogue(id)
{
    var node = nodes.map[id];
    renderTemplate('#tagger-rename-dialogue', TEMPLATES.RENAME_FORM, node.attributes);
    if (node.attributes.type !== METADATA_TAG)
        renderTitleTreeNodes(node, '#rename-form #title-tree-nodes');
//    renderXMLPreview(nodes.attributes.xml, '#title-tree-xml-preview', null, 'title-xml-preview-node');
    $('#tagger-xml-preview .xml-preview-node:first').clone().appendTo('#title-tree-xml-preview');
    $('#title-tree-xml-preview .xml-preview-node').addClass('title-xml-preview-node').removeClass('xml-preview-node');
    $('#tagger-rename-dialogue').fadeIn();
    loadRenameDialogueEvents();
    if (node.attributes.titleId !== '')
    {
//        console.log('has title ' + node.attributes.titleId);
        $('.title-node-tag.' + node.attributes.titleId).trigger('click');
    }
}
function loadRenameDialogueEvents()
{
    loadGenericNodeTreeEvents();
    $('.title-node-tag').unbind('click')
            .on('click', function()
            {
                var self = $(this), id = self.attr('data-id');
                $('#selected-property-title')
                        .attr('data-id', id)
                        .val(self.text());
                $('.title-node-tag').removeClass('highlighted-tag');
                self.addClass('highlighted-tag');

            })
            .on('mouseover', function()
            {
                var self = $(this), id = self.attr('data-id');
                $('.title-xml-preview-node .highlighted-nodes').removeClass('highlighted-nodes');
                $('.title-xml-preview-node .' + id).addClass('highlighted-nodes');
                $('#title-tree-xml-preview').scrollTop(0);
                var top = $('#title-tree-xml-preview .' + id + ":first").offset().top - $('#title-tree-xml-preview').position().top - 160;
                $('#title-tree-xml-preview').scrollTop(top);
            });

    $('#rename-form-clear-title').unbind('click').on('click', function()
    {
        $('#selected-property-title').val('').attr('data-id', '');
        $('.title-node-tag.highlighted-tag').removeClass('highlighted-tag');
    });

}
function hideRenameDialogue()
{
    $('#tagger-rename-dialogue').hide();
    $('#tagger-rename-dialogue').empty();
    loadRenameDialogueEvents();

}
function saveRenameDialogue()
{
    var id = $('#title-tree-node-target').val(),
            new_name = $('#selected-display-title').val(),
            new_target_id = $('#selected-property-title').attr('data-id'),
            node = nodes.map[id];
    if (new_name.length > 0)
        node.rename(new_name);
    if (nodes.map[new_target_id])
    {
        node.setTitleAsXPath(nodes.map[new_target_id].attributes.xpaths[0]);
        node.setTitleNode(new_target_id);
        var tag;
        addElement(tag, new_target_id, NODE_TYPES.PROPERTY, false);
    }
    refreshElement(id);
    hideRenameDialogue();
}

/****************************
 *      OUTPUT PREVIEW      *
 ****************************/
function loadOutputPreview()
{
    //"DOMSubtreeModified"
    $('.bucket-body').on(BODY_CHANGE_EVENT, function()
    {
        var data = nodes.getSample();
        $('#tagger-output-preview-container').empty();
        for (var i = 0, j = data.length; i < j; i++)
            renderTemplate('#tagger-output-preview-container', TEMPLATES.OUTPUT_PREVIEW, {data: data[i]});
    });
}


