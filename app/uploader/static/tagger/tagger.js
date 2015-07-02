/* This file contains all the UI interactions for the XML tagger
 * @Author = Hassan Jannah
 */
$(document).ready(function() {
    console.log('ready');
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
    RENAME_FORM: {filename: 'rename_form.html'},
    COMBINE_FORM: {filename: 'combine_form.html'},
    INTRO: {filename: 'intro.html'},
    JSON_PREVIEW: {filename: 'json_preview.html'}
};

var buckets = {
    sentences: {id: 'sentence-bucket',
        header: 'Selected text nodes to analyze',
        help: 'Text nodes are nodes that contain the target text content of the analysis.'},
    properties: {id: 'property-bucket',
        header: 'Selected analysis properties',
        help: 'Properties are additional information that help perform multi-propertyal analysis on the text.'}};

var nodes;//the node model 
/**
 * Initiate tagger
 * @returns {undefined}
 */
function init_tagger()
{
//     
    loadRequestParams();
    nodes = new NodeModel();
    nodes.loadFromXMLURL(document_url, filename);
    loadTemplates();
    render();
    loadNodeTreeEvents();
    loadTooltips();
    loadOutputPreview();
    loadSubmitEvent();
    addRootNode();
    loadIntro();
}
/**
 * render inital UI elements
 * @returns {undefined}
 */
function render()
{
    renderContainers();
    renderBuckets();
    renderTreeNodes(nodes, '#tagger-node-preview .tagger-container-body');
    renderXMLPreview(nodes.attributes.xml, '#tagger-xml-preview .tagger-container-body');
//    $('.tagger-container').resizable();
}
/**
 * Load request params
 * @returns {undefined}
 */
function loadRequestParams()
{
    project_id = $('#project-id').val();
    document_id = $('#document-id').val();
    filename = $('#filename').val();
    document_url = $('#document-url').val();
    templates_url = $('#templates-url').val();
}
/**
 * Load events related to submitting the form (save file) eents will prevent the form from refreshing
 * @returns {undefined}
 */
function loadSubmitEvent()
{

    $('#tagger').submit(function() {
        return false;
    });
    $('#save-structure-button').on('click', function() {
        saveStructureFile();
        return false;
    });
}

/**
 * Load introduction dialogue
 * @returns {undefined}
 */
function loadIntro()
{
    $('#tagger-loading-box').hide();
    renderTemplate('#tagger-intro-box', TEMPLATES.INTRO);
    $('#tagger-intro-box').show()
            .on('click', function() {
                $(this).hide();
            });
    $('#show-intro').on('click', function() {
        $('#tagger-intro-box').show();
        return false;
    });


}

/************************
 *  SAVE STRUCTURE FILE *
 ************************/
/**
 * Save the structure file back to the project
 * @returns {undefined}
 */
function saveStructureFile()
{
//    alert('Saving structure file');
    var data = nodes.toActiveJSON(), token = $('#csrf_token').val();
    var url = S(window.location.href).chompRight('#').s + '/save/';
    console.log(url);
    //Submit ajax request to Flask to save file
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
            //if the save was successful, reirect to project main page
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

function previewStructureFile()
{
    var json = nodes.toActiveJSON();
    renderTemplate('#json-preview-box', TEMPLATES.JSON_PREVIEW, {json: JSON.stringify(json, undefined, 2)})
    $('#json-preview-box').show().on('click', function() {
        $(this).hide();
    });
    ;
    console.log(json);

    return false;
}
/**
 * Hide the save file response dialogue
 * @returns {undefined}
 */
function hideSaveFileResponse()
{
    $('#tagger-save-file-result').hide();
}
/**
 * Load all app templates locally (not render)
 * @returns {undefined}
 */
function loadTemplates()
{
    for (var template in TEMPLATES)
    {
        TEMPLATES[template]['url'] = templates_url + '/' + TEMPLATES[template].filename;
        TEMPLATES[template]['html'] = loadTemplate(TEMPLATES[template].url);
        TEMPLATES[template]['render'] = _.template(TEMPLATES[template]['html']);
    }
}
/**
 * Load a specific HTML template
 * @param {string} filename filename of the template
 * @returns {$@call;ajax.responseText}
 */
function loadTemplate(filename)
{
    var jqxhr = $.ajax({url: filename, async: false});
    return jqxhr.responseText;
}
/**
 * Load all tooltips associated with the tooltipster library 
 * @returns {undefined}
 */
function loadTooltips()
{
    try {
        $('.tagger-tooltip').tooltipster({contentAsHTML: true});
    }
    catch (err)
    {

    }
}
/*
 * Render a specific HTML template
 * @param {string} target target HTML element ID to render the template under
 * @param {Object} template template  from TEMPLATES
 * @param {Object} args arguments to pass to the templates
 * @param {boolean} replace whether to replace the existing contents of the target
 * @param {string} id the id to give the rendered template
 * @returns {undefined}
 */
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
/**
 * Remove a specific HTML element from its parent and refresh it
 * @param {string} target HTML ID
 * @returns {undefined}
 */
function removeNode(target) {

    var parent = $(target).parent();
    $(target).remove();
    parent.trigger(BODY_CHANGE_EVENT);
}
/**
 * REnder the initial containers
 * @returns {undefined}
 */
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

/**
 * Render the bucket (sentences and properties)
 * @returns {undefined}
 */
function renderBuckets() {
    $('#tagger-buckets-container .tagger-container-body').append('<table></table>');
    for (var bucket in buckets)
    {
        renderTemplate('#tagger-buckets-container .tagger-container-body table', TEMPLATES.BUCKET, buckets[bucket]);
    }
}
/**
 * Render the main tree nodes
 * @param {NodeModel} node root node
 * @param {string} target target HTML ID
 * @returns {undefined}
 */
function renderTreeNodes(node, target)
{
    renderNodes(node, TEMPLATES.TREE_NODE, target, 'tree');
}
/**
 * Render the tree nodes in the select node title dialogue
 * @param {NodeModel} node root node
 * @param {string} target target HTML ID
 * @returns {undefined}
 */
function renderTitleTreeNodes(node, target)
{
    renderNodes(node, TEMPLATES.TITLE_TREE_NODE, target, 'title');
}

/**
 * Recursively render node under a specific target
 * @param {NodeModel} node the node to render
 * @param {Object} template the template to use to render the nodes form TEMPLATES
 * @param {string} target HTML target ID
 * @param {string} target_prefix whether the target is a Tree node or a title tree node
 * @returns {undefined}
 */
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
/**
 * Recursively render the XML document preview
 * @param {XML} xml
 * @param {string} target HTML ID
 * @param {string} parent_id the ID of the current XML element's parent
 * @returns {undefined}
 */
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
            //render the children of this node directly under it
            renderXMLPreview(child, '.' + node_id + ':last .xml-preview-children:first', node_id);
        });
    }
}
/**
 * Add the root node to the property bucket by default
 * @returns {undefined}
 */
function addRootNode()
{
    var root_node = $('.node-tag-document');
    var root_id = root_node.attr('data-id');
    addElement(null, root_id, NODE_TYPES.PROPERTY, false);
}
/********************
 *      EVENTS      *
 ********************/
/**
 * Load node tree vents
 * @returns {undefined}
 */
function loadNodeTreeEvents()
{
    loadGenericNodeTreeEvents();
    //highlight the XML text when a node is clicked
    $('.node-tag').on('click', function() {
        var self = $(this), id = self.attr('data-id');
        enableHighlightNodes(id, false);
    });
    //text node added
    $('.node-tag-action-text').on('click', function()
    {
        processElement(this);

    });
    //property node added
    $('.node-tag-action-property').on('click', function()
    {
        processElement(this);

    });
}

/**
 * Load generic events associated with tree nodes
 * @returns {undefined}
 */
function loadGenericNodeTreeEvents()
{
    //Tree collapse events
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
    //Tree expand events
    $('.tagger-node .expand-node').unbind('click').on('click', function() {
        var self = $(this);
        self.parents('.tagger-node:first').children('.tagger-node-children:first').slideDown();
        self.hide();
        self.siblings('.collapse-node').show();
    });
}

/**
 * Add bucket tag events
 * @param {string} id node id
 * @returns {undefined}
 */
function addBucketTagEvents(id) {
    //highlight xml and other elements when hovering
    $('.bucket-body > .' + id).on('mouseover', function()
    {
        enableHighlightNodes(id, true);

    }).on('mouseout', function()
    {
        disableHighlightNodes(id);
    });
    //show rename dialogue when a property bucket node is clicked
    $('.bucket-body .bucket-tag-property.' + id).unbind('click').on('click', function()
    {
        var self = $(this), type = self.attr('data-type'), id = self.attr('data-id');
        showRenameDialogue(id);
    });
    //show combine text dialogue when a property bucket node is clicked
    $('.bucket-body .bucket-tag-sentence.' + id).unbind('click').on('click', function()
    {
        var self = $(this), type = self.attr('data-type'), id = self.attr('data-id');
        showCombineForm(id);
    });
    //removing a bucket node
    $('.bucket-tag-remove.' + id).on('click', function() {
        var myId = $(this).attr('data-id'), type = $(this).attr('data-node-type');
        removeElement(null, myId, type);
        disableHighlightNodes(myId);
    });
}
/*
 * Highlight all instances of specifc node id in XML preview, tree node, and output preview
 * @param {string} id node id to highlihgt
 * @param {boolean} highlightTreeNodes highlight tree nodes or not
 * @returns {undefined}
 */
function enableHighlightNodes(id, highlightTreeNodes)
{
    if (highlightTreeNodes) {
        $('#tagger-node-preview .' + id).addClass('highlighted-tag');
    }
    $('#tagger-output-preview .' + id).addClass('highlighted-tag');
    $('.xml-preview-node .highlighted-nodes').removeClass('highlighted-nodes');
    $('.xml-preview-node .' + id).addClass('highlighted-nodes');
    $('#tagger-xml-preview-container .tagger-container-body').scrollTop(0);
    var top = $('#tagger-xml-preview-container .' + id + ":first").offset().top - $('#tagger-xml-preview-container .tagger-container-body').position().top - 25;
    $('#tagger-xml-preview-container .tagger-container-body').scrollTop(top);
    var tid = nodes.map[id].attributes.titleId;
    if (tid !== '')
    {
        enableHighlightNodes(tid, highlightTreeNodes);
    }
}
/** 
 * disable highlights
 * @param {string} id node id
 * @returns {undefined}
 */
function disableHighlightNodes(id)
{
    $('#tagger-node-preview  .' + id).removeClass('highlighted-tag');
    $('#tagger-output-preview  .' + id).removeClass('highlighted-tag');
    if (nodes.map[id].attributes.titleId !== '')
        disableHighlightNodes(nodes.map[id].attributes.titleId);

}

/**
 * Process a tree node element (add or remove)
 * @param {HTML} el HTML element to process
 * @returns {undefined}
 */
function processElement(el)
{
    var tag = $(el), id = tag.attr('data-id'), nodeType = tag.attr('data-node-type'), active = nodes.map[id].attributes.isActive;

    if (active)
        removeElement(tag, id, nodeType);
    else
        addElement(tag, id, nodeType, true);
}
/**
 * Remvoe an element from buckets
 * @param {string} tag HTML tag
 * @param {string} id node id
 * @param {string} nodeType from NODE_TYPES
 * @returns {undefined}
 */
function removeElement(tag, id, nodeType)
{
    if (!tag)
        tag = $('.node-tag-action.' + id);
    if (nodeType === NODE_TYPES.TEXT)
        removeTextElement(id);
    else
        removePropertyElement(id);
    refreshNodeTreeView();
}

/**
 * Add and element to buckets
 * @param {string} tag HTML tag
 * @param {string} id node id
 * @param {string} nodeType from NODE_TYPES
 * @param {booelan} renameDialogue show the rename dialogue after adding
 * @param {boolean} preventRender prevent render the UI after adding
 * @returns {undefined}
 */
function addElement(tag, id, nodeType, renameDialogue, preventRender)
{
    var bucket = $('.bucket-tag-' + nodeType + '.' + id);
    if (bucket.length === 0)//check if bucket node already exists
    {
        if (!tag) {
            tag = $('.node-tag-action-' + nodeType + '.' + id);
            tag.attr('data-added-auto', 'true');
        }
        if (nodeType === NODE_TYPES.TEXT)
        {
            addTextElement(id);
        }
        else
        {
            addPropertyElement(id, renameDialogue, preventRender);
        }
        addBucketTagEvents(id);
    }
    else
    {
        console.log('tag alreeady exists ' + id);
    }
    refreshNodeTreeView();
}
/**
 * Add a node to the sentence bucket
 * @param {string} id node id
 * @returns {undefined}
 */
function addTextElement(id)
{
    removePropertyElement(id);
    var node = nodes.map[id];
    if (!node.attributes.isActive)
    {
        node.activate();
        node.setAsSentence(true);
        renderTemplate('#sentence-bucket .bucket-body', TEMPLATES.BUCKET_NODE, node);
        showCombineForm(id);

    } else {
        alert('node already added');
    }
}
/**
 * Add a node to the properties bucket
 * @param {string} id node id
 * @param {boolean} renameDialogue show the rename dialogue after adding
 * @param {boolean} preventRender prvent UI refresh after adding
 * @returns {undefined}
 */
function addPropertyElement(id, renameDialogue, preventRender)
{
    removeTextElement(id);
    var node = nodes.map[id];
    if (!node.attributes.isActive)
    {
        node.activate();
        node.setAsProperty(true);
        if (!preventRender)
            renderTemplate('#property-bucket .bucket-body', TEMPLATES.BUCKET_NODE, node);
    } else {
        alert('node already added');
    }

    if (renameDialogue || node.attributes.type === SUBUNIT_TAG)
        showRenameDialogue(id);
}
/**
 * Remvoe node form sentence bucket and deactivate it
 * @param {string} id node id
 * @returns {undefined}
 */
function removeTextElement(id)
{

    var node = nodes.map[id];
    node.deactivate();
    node.setAsSentence(false);
    removeNode('#sentence-bucket .bucket-body .' + id);
}
/**
 * Remvoe node form properties bucket and deactivate it
 * @param {string} id node id
 * @returns {undefined}
 */
function removePropertyElement(id)
{
    var node = nodes.map[id];
    node.deactivate();
    removeNode('#property-bucket .bucket-body .' + id);
    if (node.attributes.titleId !== '')
    {
        var titleNode = nodes.map[node.attributes.titleId];
        titleNode.deactivate();
    }
}
/**
 * Refresh the UI of a certain bucket node from node model
 * @param {string} id node id
 * @returns {undefined}
 */
function refreshElement(id) {

    var node = nodes.map[id], target = '.bucket-tag-group.' + id;
    renderTemplate(target, TEMPLATES.BUCKET_NODE, node, true, id);
    addBucketTagEvents(id);

}
/**
 * Refresh the UI of the node tree preview based on the active node model nodes. 
 * This will ensure proeper UI rendering instead of handling each event individually (add/remove)
 * @returns {undefined}
 */
function refreshNodeTreeView()
{
    $('.node-tag-action').removeClass('added-node');
    _.each(nodes.map, function(node)
    {
        var id = node.attributes.id, type = node.attributes.type,
                active = node.attributes.isActive;
        if (active)
        {
            if (node.attributes.isSentence)
                $('.node-tag-action-text.' + id).addClass('added-node');
            if (node.attributes.isProperty)
                $('.node-tag-action-property.' + id).addClass('added-node');
        }
    });
}
/****************************
 *      Rename dialogue     *
 ***************************/
/**
 * Show the rename/assign title dialogue
 * @param {string} id
 * @returns {undefined}
 */
function showRenameDialogue(id)
{
    hideRenameDialogue();
    var node = nodes.map[id];
    renderTemplate('#tagger-rename-dialogue', TEMPLATES.RENAME_FORM, node.attributes);
    if (node.attributes.type !== METADATA_TAG)
        renderTitleTreeNodes(node, '#rename-form #title-tree-nodes');
    $('#tagger-xml-preview .xml-preview-node:first').clone().appendTo('#title-tree-xml-preview');
    $('#title-tree-xml-preview .xml-preview-node').addClass('title-xml-preview-node').removeClass('xml-preview-node');
    $('#tagger-rename-dialogue').fadeIn();
    loadRenameDialogueEvents();
    if (node.attributes.titleId !== '')
    {
        $('.title-node-tag.' + node.attributes.titleId).trigger('click');
    }
}
/**
 * Load the rename dialogue events
 * @returns {undefined}
 */
function loadRenameDialogueEvents()
{
    loadGenericNodeTreeEvents();
    //tag click event to add as title, 
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
            //tag hover event to highlight XML
            .on('mouseover', function()
            {
                var self = $(this), id = self.attr('data-id');
                $('.title-xml-preview-node .highlighted-nodes').removeClass('highlighted-nodes');
                $('.title-xml-preview-node .' + id).addClass('highlighted-nodes');
                $('#title-tree-xml-preview').scrollTop(0);
                var top = $('#title-tree-xml-preview .' + id + ":first").offset().top - $('#title-tree-xml-preview').position().top - 160;
                $('#title-tree-xml-preview').scrollTop(top);
            });
    //clear form event
    $('#rename-form-clear-title').unbind('click').on('click', function()
    {
        $('#selected-property-title').val('').attr('data-id', '');
        $('.title-node-tag.highlighted-tag').removeClass('highlighted-tag');
    });
    //data type event
    $('#selected-property-data-type').dropdown();
    $('#selected-property-data-type-list li a').on('click', function() {
        var type = $(this).attr('data-type');
        $('#selected-property-data-type').attr('data-type', type).html(S(type).capitalize().s + ' <span class="caret">');
        if (type === DATA_TYPES.DATE) {
            $('#selected-property-date-format').show();
            $('#selected-property-date-format-help').show();
        }
        else
        {
            $('#selected-property-date-format').hide();
            $('#selected-property-date-format-help').hide();
        }
    });
}
/**
 * hide the rename dialogue
 * @param {boolean} remove remove the added node from the bucket after hiding
 * @param {string} id node id
 * @param {string} nodeType node type from NODE_TYPES
 * @returns {undefined}
 */
function hideRenameDialogue(remove, id, nodeType)
{
    $('#tagger-rename-dialogue').hide();
    $('#tagger-rename-dialogue').empty();
//    if (remove && id)
//    {
//        /* if (nodes.map[id].attributes.type !== DOCUMENT_TAG)
//         removeElement(null, id, nodeType);*/
//    }
}
/**
 * Save the outcome of the rename dialogue to the node model
 * @returns {undefined}
 */
function saveRenameDialogue()
{
    var id = $('#title-tree-node-target').val(),
            new_name = $('#selected-display-title').val(),
            new_target_id = $('#selected-property-title').attr('data-id'),
            data_type = $('#selected-property-data-type').attr('data-type'),
            date_format = $('#selected-property-date-format').val(),
            node = nodes.map[id];
    //rename node
    if (new_name.length > 0)
        node.rename(new_name);

    if (nodes.map[new_target_id])
    {
        //update node title and data type
        node.setTitleAsXPath(nodes.map[new_target_id].attributes.xpaths[0]);
        node.setTitleNode(new_target_id);

        nodes.map[new_target_id].setDataType(data_type);
        var tag;
//        refreshElement(id);
        addElement(tag, new_target_id, NODE_TYPES.PROPERTY, false, true);
    }
    else
    {
        //reset node title
        var tid = node.attributes.titleId;
        if (tid !== '')
        {
            node.resetTitleNode();
        }
    }
    node.setDataType(data_type);
//update date format for date dataType
    if (data_type === DATA_TYPES.DATE) {
        node.setDateFormat(date_format);
    }
    refreshElement(id);//refresh the node UI after updating the model
    hideRenameDialogue();
}

/****************************
 *      OUTPUT PREVIEW      *
 ****************************/
//default sample size
var sampleSize = DEFAULT_SAMPLE_SIZE, defaultIncrease = DEFAULT_SAMPLE_SIZE;
/**
 * Load the structure file output preview
 * @returns {undefined}
 */
function loadOutputPreview()
{
    //"DOMSubtreeModified"
    //whenever the buckets are changed, reload the output preview
    $('.bucket-body').unbind(BODY_CHANGE_EVENT).on(BODY_CHANGE_EVENT, function()
    {
        var data = nodes.getSample(sampleSize);
        $('#tagger-output-preview-container').empty();
        if (data.length > 0) {
            for (var i = 0, j = data.length; i < j; i++)
                renderTemplate('#tagger-output-preview-container', TEMPLATES.OUTPUT_PREVIEW, {data: data[i]});
        }
        else
        {
            renderTemplate('#tagger-output-preview-container', TEMPLATES.OUTPUT_PREVIEW, {data: []});
        }
    });
}
/**
 * Show more outputs by increasing the smaple size 
 * @returns {undefined}
 */
function showMoreOutput()
{
    sampleSize += defaultIncrease;
    $('.bucket-body').trigger(BODY_CHANGE_EVENT);

}
/**
 * Show less outputs by decreasing the smaple size 
 * @returns {undefined}
 */
function showLessOutput()
{
    sampleSize -= (sampleSize > defaultIncrease) ? defaultIncrease : 0;
    $('.bucket-body').trigger(BODY_CHANGE_EVENT);

}
/****************************
 *      COMBINE FORM         *
 ****************************/
/**
 * Show the text combine form
 * @param {string} id node id
 * @returns {undefined}
 */
function showCombineForm(id)
{
    hideCombineForm();
    var node = nodes.map[id];
    var sample1 = nodes.getTextSample(id, 5, false), sample2 = nodes.getTextSample(id, 5, true);
    renderTemplate("#tagger-combine-dialogue", TEMPLATES.COMBINE_FORM, {node: node, sample1: sample1, sample2: sample2});
    loadCombineFormEvents();
    $('#tagger-combine-dialogue').show();
}
/**
 * Hide the combine text form
 * @param {booelan} remove remove element after hiding
 * @param {string} id node id
 * @param {string} nodeType from NODE_TYPES
 * @returns {undefined}
 */
function hideCombineForm(remove, id, nodeType)
{
    $('#tagger-combine-dialogue').empty();
    $('#tagger-combine-dialogue').hide();
    if (remove && id)
    {
        removeElement(null, id, nodeType);
    }
}
/**
 * Load combine form events
 * @returns {undefined}
 */
function loadCombineFormEvents()
{
//Place holder for events

}
/**
 * Save the options selected in the combine form
 * @returns {undefined}
 */
function saveCombineForm()
{
    var id = $('#combine-form').attr('data-id'), node = nodes.map[id], combine = $('#select-text-display-modes>.active').attr('data-combine') === 'true';
    node.setCombine(combine);
    refreshElement(id);
    hideCombineForm();
}
/**
 * Show loading image
 * @returns {undefined}
 */
function showLoading() {
    $('#tagger-loading-box').show();
}
/**
 * Hide loading image
 * @returns {undefined}
 */
function hideLoading() {
    $('#tagger-loading-box').fadeOut(200);
}