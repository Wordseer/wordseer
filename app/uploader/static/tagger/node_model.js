/*
 * Node model object is a recursive data object to model an xml document in
 * wordseer compatible structure JSON file
 * @Author = Hassan Jannah
 */
var DOCUMENT_TAG = 'document', SUBUNIT_TAG = 'subunit', METADATA_TAG = 'metadata', SENTANCE_TAG = 'sentance', NODE_ID_PREFIX='tagger-id-';
var NodeModel = function() {
    var self = {}, xml, url, filename;
    var primaryKeys = ['id', 'tag', 'type', 'xpaths', 'name', 'active'],
            document_keys = ['filename', 'url', 'xml'],
            subunit_keys = ['structureName'],
            metadata_keys = ['attr', 'propertyName', 'displayName', 'dataType', 'nameIsDisplayed', 'valueIsDisplayed', 'isCategory'];
    self.attributes = {filename: '', url: '', xml: {}, id: '', tag: '', type: '', xpaths: [], name: '',
        units: [], metadata: [], children: [], sub_xpaths: [], attrs: {}, attr: '',
        sbelongsTo: '', isAttribute:false,
        isCategory: false, nameIsDisplayed: false, valueIsDisplayed: false, dataType: '',
        structureName: '', 'propertyName': '', displayName: '', root: false, sentance: false};
    self.init = function() {

    };
    self.loadFromXMLURL = function(xml_filepath)
    {
        var jqxhr = $.ajax({url: xml_filepath, async: false});
        xml = $.parseXML(jqxhr.responseText);
        url = xml_filepath;
        filename = xml_filepath.replace(/^.*[\\\/]/, '');
        self.createFromXML($(xml).children()[0]);
//        console.log(attributes);

    };
    self.createFromXML = function(inXML, path, id) {
        xml = inXML;
        path = (path) ? path : '/';
        id = (id) ? id : NODE_ID_PREFIX;
        self.attributes.root = (path === '/') ? true : false;
//        console.log(path);
//        console.log(xml);
        var children = $(xml).children(), attrs = xml.attributes;
        self.attributes.tag = $(xml).prop('tagName');
        self.attributes.id = id + self.attributes.tag;
        self.attributes.xpaths.push(path + self.attributes.tag + "/");
        self.attributes.structureName = self.attributes.tag;
        self.attributes.displayName = self.attributes.structureName;
        _.each(attrs, function(attr)
        {
            self.attributes.attrs[attr.nodeName] = attr.nodeValue;
            var node = new NodeModel();
            node.createAsAttribute(self.attributes.id, attr.nodeName, attr.nodeValue, self.attributes.xpaths);
            if (!_.contains(self.attributes.sub_xpaths, node.attributes.xpaths[0]))
            {
                self.attributes.sub_xpaths.push(node.attributes.xpaths[0]);
                self.attributes.metadata.push(node);
            }
        });
        if (self.attributes.root)
        {
            self.attributes.type = DOCUMENT_TAG;
            self.attributes.filename = filename;
            self.attributes.url = url;
            self.attributes.xml = xml;
        }
        if (children.length > 0)
        {
            if (!self.attributes.root)
                self.attributes.type = SUBUNIT_TAG;
            _.each(children, function(child) {
                var node = new NodeModel();
                node.createFromXML(child, self.attributes.xpaths[0], self.attributes.id);
                if (!_.contains(self.attributes.sub_xpaths, node.attributes.xpaths[0]))
                {
                    self.attributes.sub_xpaths.push(node.attributes.xpaths[0]);
                    self.attributes.children.push(node);
                    if (node.attributes.type === METADATA_TAG)
                        self.attributes.metadata.push(node);
                    else
                        self.attributes.units.push(node);
                }
            });
        }
        else {
            self.attributes.type = METADATA_TAG;
        }
    };
    self.createAsAttribute = function(id, name, value, xpaths)
    {
        self.attributes.id = id + 'attr' + name;
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
    self.toJSON = function() {
        var json = {};
        // put the primary keys in the json file
        _.each(primaryKeys, function(key) {
            if (self.attributes[key])
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
        if (self.attributes.units.length > 0)
        {
            json['units'] = [];
            _.each(self.attributes.units, function(unit) {
                json.units.push(unit.toJSON());
            });
        }
        //create metadata child objects
        if (self.attributes.metadata.length > 0)
        {
            json['metadata'] = [];
            _.each(self.attributes.metadata, function(unit) {
                json.metadata.push(unit.toJSON());
            });
        }
        /*
         if (self.attributes.children.length > 0)
         {
         json['children'] = [];
         _.each(self.attributes.children, function(child) {
         json.children.push(child.toJSON());
         });
         }*/
//        console.log(json);
        return json;
    };
    self.setDisplayName = function(name)
    {
        self.attributes.displayName = name;
    };
    self.hasChildren = function() {
        return self.attributes.children.length > 0;
    };
    return self;
};
function getNode(nodes, xpath)
{
    var node;
    for (var key in nodes)
    {
        var n = nodes[key];
        var sub_xpaths = n.attributs.sub_xpaths;
        if (_.contains(sub_xpaths, xpath))
        {
            node = getNode(n.attributes.units, xpath);
            if (!node)
                node = getNode(n.attributes.metadata, xpath);
        }
    }
    return node;
}