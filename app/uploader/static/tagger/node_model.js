/*
 * Node model object is a recursive data object to model an xml document in
 * wordseer compatible structure JSON file
 * @Author = Hassan Jannah
 */
var DOCUMENT_TAG = 'document',
        SUBUNIT_TAG = 'subunit',
        METADATA_TAG = 'metadata',
        SENTENCE_TAG = 'sentence',
        NODE_ID_PREFIX = 'tagger-id-',
        TITLE_NODE_TAG = 'title'
        ;
var NODE_TYPES = {TEXT: 'text', PROPERTY: 'property'};
var DATA_TYPES = {'STRING': 'string', 'NUMBER': 'number', 'DATE': 'date'};
var DEFAULT_SAMPLE_SIZE = 10;
/**
 * Recursively created node model object
 * @returns {NodeModel.self}
 */
var NodeModel = function() {
    var self = {}, xml, xmlns, url, filename, xml_raw;
    //main keys to included in structure file for each node type. Primary is included for all
    var primaryKeys = ['id', 'tag', 'type', 'xpaths', 'name', 'isActive', 'dataType', 'dateFormat'],
            document_keys = ['structureName', 'titleXPaths', 'filename'],
            subunit_keys = ['structureName', 'titleXPaths', 'combine'],
            metadata_keys = ['attr', 'propertyName', 'displayName', 'dataType',
                'dateFormat', 'nameIsDisplayed', 'valueIsDisplayed',
                'isCategory']//main keys to included in structure file for document node types;
    self.attributes = {filename: '', url: '', xml: {}, id: '', paretnId: '', tag: '', type: '',
        xpaths: [], name: '', titleXpaths: [], titleId: '',
        units: [], metadata: [], children: [], sub_xpaths: [], attrs: {}, attr: '',
        belongsTo: '', isAttribute: false, isActive: false, combine: false, hasChildElements: function() {
            return self.hasChildElements();
        },
        isCategory: false, nameIsDisplayed: false, valueIsDisplayed: false, dataType: '', dateFormat: '',
        structureName: '', 'propertyName': '', displayName: '',
        isRoot: false, isSentence: false, isProperty: false, isTitle: false, nodeType: null};
    self.map = {};
    self.init = function() {

    };
    /*
     * Inital call to generate internal node model from XML
     * @param {string} xml_filepath full XML file path
     * @param {string} fn filename
     * @returns {undefined}
     */
    self.loadFromXMLURL = function(xml_filepath, fn)
    {
        var jqxhr = $.ajax({url: xml_filepath, async: false});
        xml_raw = jqxhr.responseXML;
        xml = $.parseXML(jqxhr.responseText);
        url = xml_filepath;
        filename = (fn) ? fn : xml_filepath.replace(/^.*[\\\/]/, '');
        self.attributes.filename = filename;
        self.createFromXML($(xml).children()[0]);
        //TODO: Fix slave narratives
    };
    /**
     * Recursive funciton to generate internal node model from XML
     * @param {XML} inXML raw XML data
     * @param {string} path recursively passed xpath
     * @param {string} id recursively passed id
     * @returns {undefined}
     */
    self.createFromXML = function(inXML, path, id)
    {
        xml = inXML;
        path = (path) ? path : '/';
        id = (id) ? id : NODE_ID_PREFIX;//for root node
        //setup basic attributes
        self.attributes.isRoot = (path === '/') ? true : false;
        if (!self.attributes.isRoot)
            self.attributes.parentId = id;
        var children = $(xml).children(), attrs = xml.attributes;
        self.attributes.tag = $(xml).prop('tagName');
        self.attributes.name = $(xml).prop('tagName');
        //To render XML as HTML and use JQuery, element tags must not contain '.'. All '.' are changed to '_'.
        self.attributes.id = id + S(self.attributes.tag).replace('.', '_').s;
        self.attributes.xpaths.push(((self.attributes.isRoot) ? "" : path) + "/" + self.attributes.tag);//setup initial XPath
        self.attributes.structureName = self.attributes.tag;
        self.attributes.displayName = self.attributes.structureName;
        self.attributes.dataType = DATA_TYPES.STRING;//default node type is String
        var paths = path.split('/');
        if (paths.length > 1)
            self.attributes.belongsTo = paths[paths.length - 2];
        //process node attributes
        _.each(attrs, function(attr)
        {
            self.attributes.attrs[attr.nodeName] = attr.nodeValue;
            if (attr.nodeName === 'xmlns')
            {
                xmlns = attr.nodeValue;
            }
            var node = new NodeModel();//create child node model
            node.createAsAttribute(self.attributes.id, attr.nodeName, attr.nodeValue, self.attributes.xpaths);
            //if this element tag was not processed before, process it. this will create a tree of uniqu structure elements
            if (!_.contains(self.attributes.sub_xpaths, node.attributes.xpaths[0]))
            {
                self.attributes.sub_xpaths.push(node.attributes.xpaths[0]);
                self.attributes.metadata.push(node);
                self.map[node.attributes.id] = node;
            }
        });
        //process child nodes
        //IF this child has child nodes
        if (children.length > 0)
        {
            if (!self.attributes.isRoot)
                self.attributes.type = SUBUNIT_TAG;
            //process each child
            _.each(children, function(child)
            {
                var node = new NodeModel();
                node.createFromXML(child, self.attributes.xpaths[0], self.attributes.id);
                if (!self.hasChild(node.attributes.id))//if element type is new
                {
                    self.addChild(node);
                }
                else//node type processed before: compare children to include any new children
                {
                    var myChild = self.map[node.attributes.id];
                    _.each(node.attributes.children, function(nodeChild)
                    {
                        if (!myChild.hasChild(nodeChild.attributes.id))
                        {
                            myChild.addChild(nodeChild);
                            _.each(node.map, function(item, key)
                            {
                                if (!self.map[key])
                                    self.map[key] = item;
                            });
                        }
                    });
                }
            });
        }
        //If this element has no child nodes but has attributes
        else if (attrs.length > 0)
        {
            self.attributes.type = SUBUNIT_TAG;
            self.attributes.xpaths[0] += '/text()';
        }
        //if this element is a leaf node with no attributes
        else {
            self.attributes.type = METADATA_TAG;
            self.attributes.xpaths[0] += '/text()';
        }
        if (self.attributes.isRoot)
        {
            self.attributes.type = DOCUMENT_TAG;
            self.attributes.filename = filename;
            self.attributes.url = url;
            self.attributes.xml = xml;
            self.map[self.attributes.id] = self;
        }
    };
    /*
     * Check if node has a direct child with id
     * @param {string} id
     * @returns {Boolean}
     */
    self.hasChild = function(id)
    {

        for (var child_id in self.attributes.children)
        {
            var child = self.attributes.children[child_id];
            if (child.attributes.id === id)
            {
                return true;
            }
        }
        return false;
    };
    /**
     * Add a child to this node (either unit or metadata based on node type)
     * @param {NodeModel} node
     * @returns {undefined}
     */
    self.addChild = function(node)
    {
        self.attributes.sub_xpaths.push(node.attributes.xpaths[0]);
//        if(!self.attributes.children)
        self.attributes.children.push(node);
        if (node.attributes.type === METADATA_TAG)
            self.attributes.metadata.push(node);
        else
            self.attributes.units.push(node);
        self.map[node.attributes.id] = node;
        _.each(node.map, function(item, key)
        {
            if (!self.map[key])
                self.map[key] = item;
        });
    };
    /**
     * If if this node has any unit or metadata childrent
     * @returns {Boolean}
     */
    self.hasChildElements = function()
    {
        if (self.attributes.units.length > 0)
            return true;
        var notAttrs = _.filter(self.attributes.metadata, function(item) {
            return !item.attributes.isAttribute;
        });
//        console.log(attrs);
        if (notAttrs.length > 0) {
            return true;
        }

        return false;
    };
    /**
     * Check if another node ID is a descendant of this node
     * @param {string} childId
     * @returns {Boolean}
     */
    self.hasDescendant = function(childId)
    {
        if (self.map[childId])
        {
//            console.log(self.attributes.id + ' has descendant ' + childId)
            return true;
        }
        else
            return false;
    };
    /**
     * Check if a another node is a sibling to this node in the XML
     * @param {string} siblingId
     * @returns {Boolean}
     */
    self.hasSibling = function(siblingId) {
//        console.log('is ' + siblingId + ' a sibling of ' + self.attributes.id + '?');
        if (self.map[siblingId]) {
            var result = self.map[siblingId].attributes.parentId === self.attributes.parentId;
            if (result)
                console.log(siblingId + ' is sibling to ' + self.attributes.id);
            return result;
        }
        return false;
    };
    /**
     * Create the node as an attribute of an XML node
     * @param {string} id
     * @param {string} name
     * @param {string} value
     * @param {string} xpaths
     * @returns {undefined}
     */
    self.createAsAttribute = function(id, name, value, xpaths)
    {
        self.attributes.id = id + 'attr' + name;
        self.attributes.tag = name;
        self.attributes.tag = name;
        self.attributes.type = METADATA_TAG;
        self.attributes.dataType = DATA_TYPES.STRING;
        self.attributes.attr = name;
        self.attributes.xpaths.push(xpaths + '/@' + name);//XPath for attributes
        self.attributes.displayName = name;
        self.attributes.isAttribute = true;
    };
    self.loadFromJSON = function(json) {

    };
    /**
     * Activate the node (include it in structure file)
     * @returns {undefined}
     */
    self.activate = function() {
        self.attributes.isActive = self.attributes.valueIsDisplayed = self.attributes.nameIsDisplayed = true;
    };
    /**
     * Deactivate the node and reset its values
     * @returns {undefined}
     */
    self.deactivate = function() {
        self.attributes.isActive = self.attributes.valueIsDisplayed
                = self.attributes.nameIsDisplayed = self.attributes.isSentence
                = self.attributes.isProperty = false;
        self.updateNodeType();
    };
    /**
     * Rename this node
     * @param {string} newName
     * @returns {undefined}
     */
    self.rename = function(newName) {
        var oldName = self.attributes.name + '';
        self.attributes.displayName = self.attributes.name = self.attributes.propertyName = newName;
    };
    /**
     * Change the display node of this node
     * @param {string} name
     * @returns {undefined}
     */
    self.setDisplayName = function(name)
    {
        self.attributes.displayName = name;
    };
    /**
     * Change the title of this node
     * @param {string} title
     * @returns {undefined}
     */
    self.setTitleAsText = function(title) {
        self.rename(title);
    };
    /**
     * Set the titleXPath of this node to another node's XPath
     * @param {string} titleXPath
     * @returns {undefined}
     */
    self.setTitleAsXPath = function(titleXPath) {
        self.attributes.titleXpaths = [titleXPath];
    };
    /**
     * Assign another node as a title for this node
     * @param {string} id of title node
     * @returns {undefined}
     */
    self.setTitleNode = function(id) {
        self.map[id].rename(TITLE_NODE_TAG);
        self.map[id].attributes.isTitle = true;
        self.attributes.titleId = id;
        self.attributes.titleXPaths = self.map[id].attributes.xpaths[0];
    };
    /**
     * Reset the tile node as empty
     * @returns {undefined}
     */
    self.resetTitleNode = function()
    {
        self.setTitleAsXPath('');
        var tid = self.attributes.titleId;
        self.map[tid].rename('');
        self.map[tid].attributes.isTitle = false;
        self.attributes.titleId = '';
        self.attributes.titleXPaths = '';

    };
    /**
     * set data type
     * @param {string} dataType from DATA_TYPES
     * @returns {undefined}
     */
    self.setDataType = function(dataType) {
        self.attributes.dataType = dataType;
    };
    /**
     * Set date format
     * @param {string} format D3 date format string
     * @returns {undefined}
     */
    self.setDateFormat = function(format) {
        self.attributes.dateFormat = format;
        if (self.attributes.titleId !== '')
            self.map[self.attributes.titleId].setDateFormat(format);
    };
    /*
     * Update the node type based on attributes
     * @returns {undefined}
     */
    self.updateNodeType = function() {
        if (self.attributes.isProperty)
            self.attributes.nodeType = NODE_TYPES.PROPERTY;
        else if (self.attributes.isSentence)
            self.attributes.nodeType = NODE_TYPES.TEXT;
        else
            self.attributes.nodeType = null;
    };
    /**
     * Set whether to combine text nodes or not
     * @param {boolean} enable enable combining text
     * @returns {undefined}
     */
    self.setCombine = function(enable) {
        self.attributes.combine = (enable) ? true : false;
    };
    /**
     * Check if nodes has children
     * @returns {Boolean}
     */
    self.hasChildren = function() {
        return self.attributes.children.length > 0;
    };
    /**
     * Set this node as a sentence node
     * @param {boolean} flag boolean
     * @returns {undefined}
     */
    self.setAsSentence = function(flag) {
        if (flag)
        {
            self.rename(SENTENCE_TAG);
            self.attributes.isSentence = true;
            self.attributes.isProperty = false;
            self.attributes.type = SUBUNIT_TAG;
            self.attributes.isCategory = false;
            if (!S(self.attributes.xpaths[0]).endsWith('/text()') && !self.attributes.isAttribute)
                self.attributes.xpaths[0] += '/text()';
        }
        else
        {
            self.rename('');
            self.attributes.isSentence = false;
        }
        self.updateNodeType();
    };
    /**
     * Set this node as a property node
     * @param {boolean} flag boolean
     * @returns {undefined}
     */
    self.setAsProperty = function(flag)
    {
        if (flag)
        {
            self.rename(self.attributes.tag);
            self.attributes.isSentence = false;
            self.attributes.isProperty = true;
            self.attributes.isCategory = true;
            if (S(self.attributes.xpaths[0]).endsWith('/text()'))
                self.attributes.xpaths[0] = S(self.attributes.xpaths[0]).chompRight('/text()').s;
        }
        else
        {
            self.rename('');
            self.attributes.isSentence = false;
        }
        self.updateNodeType();
    };
    /**
     * Retrieve a full structure file of all the nodes on the XML
     * @returns {NodeModel.self.toJSONAll.json|Window.attributes|self.attributes}
     */
    self.toJSONAll = function() {
        var json = {};
        // put the primary keys in the json file
        _.each(primaryKeys, function(key) {
            if (self.attributes[key])
                json[key] = self.attributes[key];
        });
        //put document attributes
        if (self.attributes.type === DOCUMENT_TAG)
            _.each(document_keys, function(key) {
                json[key] = self.attributes[key];
            });
        //put metadata attributes
        if (self.attributes.type === METADATA_TAG)
            _.each(metadata_keys, function(key) {
                json[key] = self.attributes[key];
            });
        //put subunit attributes
        if (self.attributes.type === SUBUNIT_TAG)
            _.each(subunit_keys, function(key) {
                json[key] = self.attributes[key];
            });
        //create subnit child objects
        json['children'] = [];
        if (self.attributes.metadata.length > 0)
        {
            json['metadata'] = [];
            _.each(self.attributes.metadata, function(unit) {
                json.metadata.push(unit.toJSONAll());
                json.children.push(unit.toJSONAll());
            });
        }
        if (self.attributes.units.length > 0)
        {
            json['units'] = [];
            _.each(self.attributes.units, function(unit) {
                json.units.push(unit.toJSONAll());
                json.children.push(unit.toJSONAll());
            });
        }
        //create metadata child objects
        if (json['children'].length === 0)
            delete json['children'];
        return json;
    };
    /**
     * Retrieve the wordseer valid structure file of selected nodes (active).
     * @returns {Array}
     */
    self.toActiveJSON = function() {
        var jsonIn = self.toJSONAll(), json;
        console.log(jsonIn);

        function cleanUp(node)
        {
            var out, tempMeta = [], tempUnits = [];
            _.each(node.children, function(child)
            {
                if (child.type === METADATA_TAG && child.isActive)
                    tempMeta.push(child);
                else if (child.type === SUBUNIT_TAG)
                {
                    var tempNode = cleanUp(child);
                    if ($.isArray(tempNode))
                    {
                        _.each(tempNode, function(tempNodeChild)
                        {
                            if (tempNodeChild.type === METADATA_TAG)
                                tempMeta.push(tempNodeChild);
                            else
                                tempUnits.push(tempNodeChild);
                        });
                    }
                    else
                    {
                        if (tempNode.type === METADATA_TAG)
                            tempMeta.push(tempNode);
                        else
                            tempUnits.push(tempNode);
                    }
                }
            });

            if (node.isActive)
            {
                node.metadata = tempMeta;
                node.units = tempUnits;
                if (node.units && node.units.length === 0)
                    delete node['units'];
                if (node.metadata && node.metadata.length === 0)
                    delete node['metadata'];
                if (node.attr && node.attr === '')
                    delete node['attr'];
                delete node['children'];
                delete node['isActive'];
                out = node;
            }
            else
            {
                out = [];
                out = $.merge(tempUnits, tempMeta);
            }

            return out;
        }

        json = cleanUp(jsonIn);
        console.log(json);
        return json;
    };
    /**
     * Get an XML sample based on the chosing structure file nodes
     * Must only be called from root node
     * @param {int|null} size
     * @returns {NodeModel.self.getSample.sample|Array}
     */
    self.getSample = function(size)
    {
        size = (size) ? size : DEFAULT_SAMPLE_SIZE;
        var sample = [];
        var map = self.map;

        map = _.filter(self.map, function(item) {
            return item.attributes.isActive;
        });
        var sentences = _.filter(map, function(item) {
            return item.attributes.isSentence;
        });
        var properties = _.filter(map, function(item) {
            return item.attributes.isProperty;
        });
        var sampleColumn = function() {
            return {id: '', help: '', name: '', value: '', xpath: ''};
        };

        _.each(sentences, function(node, key)
        {
            var outputItems = [], nodeId = node.attributes.id;
            for (var i = 1; i <= size; i++)
            {

                var outputItem = [], xpath = node.attributes.xpaths[0], combine = node.attributes.combine,
                        sentence = new sampleColumn();
                sentence.help = 'sentence';
                sentence.tag = node.attributes.tag;
                sentence.name = node.attributes.name;
//                sentence.value = getXPathNode(xml_raw, xmlns, xpath, i, null, null, node.attributes.isAttribute);
                sentence.value = getTextXPathNode(xml_raw, xmlns, xpath, i, null, combine);
                sentence.xpath = xpath;
                sentence.id = node.attributes.id;
                if (sentence.value !== null)
                {
                    outputItem.push(sentence);
                    _.each(properties, function(property)
                    {
                        var dim_col = new sampleColumn(), xpath2 = property.attributes.xpaths[0], xpath2Title, titleId = property.attributes.titleId, propertyId = property.attributes.id;
                        dim_col.help = 'property';
                        dim_col.tag = property.attributes.tag;
                        dim_col.name = property.attributes.name;
                        if (titleId === '') {

                            xpath2Title = xpath2;
                            titleId = property.attributes.id;

                        }
                        else
                            xpath2Title = self.map[titleId].attributes.xpaths[0];
                        if (combine)
                        {
                            dim_col.value = getTextXPathNode(xml_raw, xmlns, xpath, i, xpath2Title, combine);
                        } else
                        {
                            dim_col.value = getXPathNode(xml_raw, xmlns, xpath, i, xpath2Title, null);
                        }
                        dim_col.xpath = xpath2;
                        dim_col.id = property.attributes.id;
                        if (!property.attributes.isTitle)
                            outputItem.push(dim_col);
                    });
                    outputItems.push(outputItem);
                }
            }
            sample.push(outputItems);
        });
        return sample;
    };
    /**
     * Get a sample of normal or combined text from XML. 
     * Must only be called from root node
     * @param {string} id node id
     * @param {int} size size of the sample
     * @param {boolean} combine boolean to conbine text or not
     * @returns {Array|NodeModel.self.getTextSample.result}
     */
    self.getTextSample = function(id, size, combine)
    {
        size = (size) ? size : DEFAULT_SAMPLE_SIZE;
        var result = [], node = self.map[id];
        for (var i = 1; i <= size; i++)
        {
            var output = getTextXPathNode(xml_raw, xmlns, node.attributes.xpaths[0], i, null, combine);
            result.push(output);
        }
        return result;
    };
    return self;
};
/*
 * Retrieve normal or combined text node values from xml based on primary XPath
 * @param {XML} xml raw xml data
 * @param {string} xmlns 
 * @param {string} nodeXPath xpath of primary node to retrieve
 * @param {int} index item index of primary noe
 * @param {string} ancestorXPath xpath of the ancestor of the primary node
 * @param {boolean} combine boolean to combine text or not
 * @returns {getXPathNode.nodes|String}
 */
function getTextXPathNode(xml, xmlns, nodeXPath, index, ancestorXPath, combine)
{
    var output;
    if (combine)
    {
        /*
         to combine text, the last XPath node is removed from the XPath so that indeces are applied to the its parent. 
         The actual node xpath is then passed as a secondary XPath which will be appended later. 
         The output will be a concatenation of the list of retrieved XPath results.
         */
        var xpaths = nodeXPath.replace('/text()', '').split('/'),
                secondaryXPath = _.last(xpaths);
        xpaths = xpaths.slice(0, xpaths.length - 1);
        xpaths = xpaths.join('/');
        output = getXPathNode(xml, xmlns, xpaths, index, ancestorXPath, secondaryXPath);
    }
    else
    {
        output = getXPathNode(xml, xmlns, nodeXPath, index, ancestorXPath, null);
    }
    return output;
}

/**
 * Retrieve the XML value of an XPath expression
 * The xpath is evaluated as "(<nodeXPath>)[<index>]/<secondaryXPath>/ancestor::<ancestorXPath>
 * 
 * @param {XML} xml XML DOM
 * @param {string} xmlns XML Name space
 * @param {string} nodeXPath the xpath to the primary node to evaluate
 * @param {int} index (optional) retrieve a specific element from the primary node
 * @param {string} ancestorXPath retrieve the andestors of the specific primary node
 * @param {string} secondaryXPath a secondaryXPath for combined text
 * @returns {string} results
 */
function getXPathNode(xml, xmlns, nodeXPath, index, ancestorXPath, secondaryXPath)
{
    var result,
            xpathExpression = '(' + nodeXPath + ')',
            fullNodeXPath = (secondaryXPath) ? nodeXPath + '/' + secondaryXPath : nodeXPath,
            isChild = false;
    xpathExpression = (index) ? xpathExpression + '[' + index + ']' : xpathExpression;
    if (secondaryXPath)
    {
        xpathExpression += '/' + secondaryXPath;
    }
    if (ancestorXPath)
    {
//        console.log(ancestorXPath);
        var ancestorXPathShort = ancestorXPath.substring(1),
                ancestorList = ancestorXPath.substring(1).replace('/text()', '').split('/'),
                nodeList = nodeXPath.substring(1).replace('/text()', '').split('/');
        if (S(ancestorXPath).contains(fullNodeXPath))
        {
            isChild = true;
            xpathExpression += ancestorXPath.replace(nodeXPath);
        }
        else
        {
            for (var i = 1, j = ancestorList.length, k = nodeList.length; i < j && i < k; i++)
            {
                if (ancestorList[i] === nodeList[i])//Trees are diverging
                {
                    ancestorXPathShort = S(ancestorXPathShort).chompLeft(ancestorList[i - 1] + '/').s;
                }
            }
            xpathExpression += (ancestorXPathShort.length > 0) ? '/ancestor::' + S(ancestorXPathShort).chompRight('/').s : '';
        }
    }

//    console.log(xpathExpression);
    xmlns = (xmlns) ? xmlns : null;
    var xpe = new XPathEvaluator();
    var nsResolver = (function(element) {
        var nsResolver = element.ownerDocument.createNSResolver(element),
                defaultNamespace = element.getAttribute('xmlns');
        return function(prefix) {
            return nsResolver.lookupNamespaceURI(prefix) || defaultNamespace;
        };
    }(xml.documentElement));

    var nodes = xpe.evaluate(xpathExpression, xml, nsResolver, XPathResult.ANY_TYPE, null);
    result = '';
    var node = nodes.iterateNext();
    if (node === null)
        result = nodes;
    //concatenate ouptut values into a single string
    while (node)
    {
        if (node.childNodes && node.childNodes[0] && node.childNodes.length > 0)
        {
            result += ' ' + node.childNodes[0].nodeValue;
        }
        else
        {
            if (typeof (node) === 'object')
            {
                result += ' ' + $(node)[0].nodeValue;
            }
            else
                result += ' ' + node;
        }
        node = nodes.iterateNext();
    }
    if (typeof (result) === 'object')//if result is still null, return null
    {
        result = null;
    }
    return result;
}
