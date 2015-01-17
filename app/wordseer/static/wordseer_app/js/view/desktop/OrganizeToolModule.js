/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.OrganizeToolModule', {
    extend: 'WordSeer.view.desktop.Module',
    requires: [
        'WordSeer.view.visualize.organizetool.behaviors.Dragable',
        'WordSeer.view.visualize.organizetool.behaviors.Panable',
        'WordSeer.view.visualize.organizetool.behaviors.Expandable',
        'WordSeer.view.visualize.organizetool.behaviors.Layering',
        'WordSeer.view.visualize.organizetool.behaviors.Text',
        'WordSeer.view.visualize.organizetool.behaviors.CollisionHandling',
        'WordSeer.view.visualize.organizetool.helpers.D3Helper',
        'WordSeer.view.visualize.organizetool.helpers.GroupHierarchy',
        'WordSeer.view.visualize.organizetool.objects.Document',
        'WordSeer.view.visualize.organizetool.objects.SentenceOT',
        'WordSeer.view.visualize.organizetool.objects.WordOT',
        'WordSeer.view.visualize.organizetool.objects.Group',
        'WordSeer.view.visualize.organizetool.objects.Annotation',
        'WordSeer.view.visualize.organizetool.OrganizeTool',
        'WordSeer.view.visualize.organizetool.MenuOT',
        'WordSeer.view.visualize.organizetool.Color',
        'WordSeer.view.visualize.organizetool.objects.SetOT',
        'WordSeer.view.visualize.organizetool.ShapeOT'
    ],
    id:'organize-tool',
    text:'Organize Tool',
    alias: 'widget.organizetool.organize-tool',
    title: 'Organize Tool',
    
    initComponent: function() {
        

        this.callParent(arguments);  

    },
    
    createWindow:function() {
    
        OrganizeTool.getInstance();
    
    }
    
})