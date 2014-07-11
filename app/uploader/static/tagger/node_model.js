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
var NodeModel = function() {
    var self = {}, xml, xmlns, url, filename, xml_raw;
    var primaryKeys = ['id', 'tag', 'type', 'xpaths', 'name', 'isActive'],
            document_keys = ['titleXPaths', 'filename'],
            subunit_keys = ['structureName', 'titleXPaths'],
            metadata_keys = ['attr', 'propertyName', 'displayName', 'dataType', 'nameIsDisplayed', 'valueIsDisplayed', 'isCategory'];
    self.attributes = {filename: '', url: '', xml: {}, id: '', tag: '', type: '',
        xpaths: [], name: '', titleXpaths: [], titleId: '',
        units: [], metadata: [], children: [], sub_xpaths: [], attrs: {}, attr: '',
        belongsTo: '', isAttribute: false, isActive: false,
        isCategory: false, nameIsDisplayed: false, valueIsDisplayed: false, dataType: '',
        structureName: '', 'propertyName': '', displayName: '',
        isRoot: false, isSentence: false, isProperty: false, isTitle: false};
    self.map = {};
    self.init = function() {

    };
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
    self.createFromXML = function(inXML, path, id) {
        xml = inXML;
        path = (path) ? path : '/';
        id = (id) ? id : NODE_ID_PREFIX;
        self.attributes.isRoot = (path === '/') ? true : false;
        var children = $(xml).children(), attrs = xml.attributes;
        self.attributes.tag = $(xml).prop('tagName');
        self.attributes.name = $(xml).prop('tagName');
        self.attributes.id = id + S(self.attributes.tag).replace('.', '_').s;
        self.attributes.xpaths.push(path + self.attributes.tag + "/");
        self.attributes.structureName = self.attributes.tag;
        self.attributes.displayName = self.attributes.structureName;
        var paths = path.split('/');
//console.log(paths);
        if (paths.length > 1)
            self.attributes.belongsTo = paths[paths.length - 2];
        _.each(attrs, function(attr)
        {
            self.attributes.attrs[attr.nodeName] = attr.nodeValue;
            if (attr.nodeName === 'xmlns')
            {
//console.log('xmlns namespace detected ' + attr.nodeValue);
//console.log(attr.nodeValue);
                xmlns = attr.nodeValue;
            }
            var node = new NodeModel();
            node.createAsAttribute(self.attributes.id, attr.nodeName, attr.nodeValue, self.attributes.xpaths);
            if (!_.contains(self.attributes.sub_xpaths, node.attributes.xpaths[0]))
            {
                self.attributes.sub_xpaths.push(node.attributes.xpaths[0]);
                self.attributes.metadata.push(node);
                self.map[node.attributes.id] = node;
            }
        });

        if (children.length > 0)
        {
            if (!self.attributes.isRoot)
                self.attributes.type = SUBUNIT_TAG;
            _.each(children, function(child)
            {
                var node = new NodeModel();
                node.createFromXML(child, self.attributes.xpaths[0], self.attributes.id);
//console.log(self.attributes.sub_xpaths);
                if (!self.map[node.attributes.id])
                {
                    self.attributes.sub_xpaths.push(node.attributes.xpaths[0]);
                    self.attributes.children.push(node);
//console.log(node.attributes.id);
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
                }
            });
        }
        else {
            self.attributes.type = METADATA_TAG;
            self.attributes.xpaths[0] += 'text()';
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
    self.createAsAttribute = function(id, name, value, xpaths)
    {
        self.attributes.id = id + 'attr' + name;
        self.attributes.tag = name;
        self.attributes.tag = name;
        self.attributes.type = METADATA_TAG;
        self.attributes.dataType = "string";
        self.attributes.attr = name;
        self.attributes.xpaths.push(xpaths + '@' + name);
        self.attributes.displayName = name;
        self.attributes.isAttribute = true;
    };
    self.loadFromJSON = function(json) {

    };
    self.activate = function() {
        self.attributes.isActive = self.attributes.valueIsDisplayed = self.attributes.nameIsDisplayed = true;
    };
    self.deactivate = function() {
        self.attributes.isActive = self.attributes.valueIsDisplayed
                = self.attributes.nameIsDisplayed = self.attributes.isSentence
                = self.attributes.isProperty = false;
    };
    self.rename = function(newName) {
        var oldName = self.attributes.name + '';
        self.attributes.displayName = self.attributes.name = self.attributes.propertyName = newName;
//console.log('renaming '+oldName +' to ' +self.attributes.name);

    };
    self.setDisplayName = function(name)
    {
        self.attributes.displayName = name;
    };
    self.setTitleAsText = function(title) {
        self.rename(title);
    };
    self.setTitleAsXPath = function(titleXPath) {
        self.attributes.titleXpaths = [titleXPath];
    };
    self.setTitleNode = function(id) {
        self.map[id].rename(TITLE_NODE_TAG);
        self.map[id].attributes.isTitle = true;
        self.attributes.titleId = id;
        self.attributes.titleXPaths = self.map[id].attributes.xpaths[0];
    };
    self.hasChildren = function() {
        return self.attributes.children.length > 0;
    };
    self.setAsSentence = function(flag) {
        if (flag)
        {
            self.rename(SENTENCE_TAG);
            self.attributes.isSentence = true;
            self.attributes.isProperty = false;
            self.attributes.type = SUBUNIT_TAG;
            self.attributes.isCategory = false;
//console.log(self.attributes.xpaths[0]);
            if (!S(self.attributes.xpaths[0]).endsWith('text()') && !self.attributes.isAttribute)
                self.attributes.xpaths[0] += 'text()';
//console.log(self.attributes.xpaths[0]);
        }
        else
        {
            self.rename('');
            self.attributes.isSentence = false;
        }
    };
    self.setAsProperty = function(flag)
    {
        if (flag)
        {
            self.rename(self.attributes.tag);
            self.attributes.isSentence = false;
            self.attributes.isProperty = true;
//self.attributes.type = METADATA_TAG;
            self.attributes.isCategory = true;

            if (S(self.attributes.xpaths[0]).endsWith('text()'))
                self.attributes.xpaths[0] = S(self.attributes.xpaths[0]).chompRight('text()').s;
//console.log(self.attributes.xpaths[0]);
        }
        else
        {
            self.rename('');
            self.attributes.isSentence = false;
        }
    };
    self.toJSONAll = function(activeOnly) {
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
                json.metadata.push(unit.toJSONAll(activeOnly));
                json.children.push(unit.toJSONAll(activeOnly));
            });
        }
        if (self.attributes.units.length > 0)
        {
            json['units'] = [];
            _.each(self.attributes.units, function(unit) {
//                var children = unit
//                if (self.attributes.isActive || !activeOnly)//if activeOnly, only process active nodes
                json.units.push(unit.toJSONAll(activeOnly));
                json.children.push(unit.toJSONAll(activeOnly));
                /*  else
                 {
                 _.each(unit.attributes.units, function(sub_unit){
                 
                 })
                 
                 }*/
            });
        }
        //create metadata child objects

        /*  if (self.attributes.isRoot)
         json['WORDSEER_CONFIG'] = self;*/
        if (json['children'].length === 0)
            delete json['children'];
        return json;
    };
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
    self.getSample = function(size)
    {
        size = (size) ? size : 10;
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
//console.log(map);
//console.log(self);
        var sampleColumn = function() {
            return {id: '', help: '', name: '', value: '', xpath: ''};
        };
//console.log(xml_raw);

        _.each(sentences, function(node, key)
        {
            var outputItems = [];
            for (var i = 1; i <= size; i++)
            {

                var outputItem = [];
                var xpath = node.attributes.xpaths[0],
                        sentence = new sampleColumn();
                sentence.help = 'sentence';
                sentence.tag = node.attributes.tag;
                sentence.name = node.attributes.name;
                sentence.value = getXPathNode(xml_raw, xmlns, xpath, i, null, node.attributes.isAttribute);
                sentence.xpath = xpath;
                sentence.id = node.attributes.id;
                if (sentence.value !== null)
                {
                    outputItem.push(sentence);
                    _.each(properties, function(property)
                    {
                        var dim_col = new sampleColumn(), xpath2 = property.attributes.xpaths[0], xpath2Title;
                        dim_col.help = 'property';
                        dim_col.tag = property.attributes.tag;
                        dim_col.name = property.attributes.name;
                        if (property.attributes.titleId === '')
                            xpath2Title = xpath2;
                        else
                            xpath2Title = self.map[property.attributes.titleId].attributes.xpaths[0];
                        dim_col.value = getXPathNode(xml_raw, xmlns, xpath, i, xpath2Title, property.attributes.isAttribute);
                        //console.log(typeof (dim_col.value));
                        dim_col.xpath = xpath2;
                        dim_col.id = property.attributes.id;
                        if (!property.attributes.isTitle)
                            outputItem.push(dim_col);
                    });
                    outputItems.push(outputItem);
                }
            }
            sample.push(outputItems);
//console.log(node);
        });


//console.log(sample);
        return sample;
    };
    return self;
};

/**
 * 
 * @param {type} xml XML DOM
 * @param {type} nodeXPath the xpath to the primary node to evaluate
 * @param {type} index (optional) retrieve a specific element from the primary node
 * @param {type} ancestorXPath retrieve the andestors of the specific primary node
 * @returns {unresolved} results
 */
function getXPathNode(xml, xmlns, nodeXPath, index, ancestorXPath, isAttribute)
{
    var result,
            xpathExpression = '(' + nodeXPath + ')',
            isChild = false, secondaryXPath = '';
    xpathExpression = (index) ? xpathExpression + '[' + index + ']' : xpathExpression;
    if (ancestorXPath)
    {
        var ancestorXPathShort = ancestorXPath.substring(1),
                ancestorList = ancestorXPath.substring(1).replace('/text()', '').split('/'),
                nodeList = nodeXPath.substring(1).replace('/text()', '').split('/');
        if (S(ancestorXPath).contains(nodeXPath))
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
    result = nodes;
    var node = nodes.iterateNext();

    if (node === null)
    {
        //TODO: FIx Slave narratives
        //console.log('null detected');
        node = nodes.iterateNext();
    }
    if (node)
    {
        if (node.childNodes && node.childNodes[0] && node.childNodes.length > 0)
        {
            result = node.childNodes[0].nodeValue;
        }
        else
        {
            if (typeof (node) == 'object')
            {
                result = $(node)[0].nodeValue;
            }
            else
                result = node;
        }
        return result;
    }
    else
    {
        return null;
    }
}