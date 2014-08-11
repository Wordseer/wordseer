/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.helpers.GroupHierarchy', {

    /*
            GroupHierarchy
        The functions in this class deal with the child-to-parent
        relationship between groups and the objects that are 
        positioned within the group.
    */

    alternateClassName: ['GroupHierarchy'],
     
    statics: {  
    
          //recursion to access all children of an object and move them by dx and dy.
        moveAllChildren:function(parent, dx, dy, svg) {
        
            if ( parent !== null) {
                var children = svg.selectAll("*[parent=\"" + parent.id + "\"]");
                
                children.each(function(d) {
                    svg.selectAll("#" + this.id)                 
                        .attr("transform", function(d) {
                        
                            if(this.tagName === "foreignObject" || this.tagName === "TEXTAREA") {
                                D3Helper.transformXByCoord(this, dx);
                                D3Helper.transformYByCoord(this, dy);
                                return "";
                            }
                        
                            return "translate(" + (D3Helper.getTransformX(this) + dx) + "," + (D3Helper.getTransformY(this) + dy) + ")";
                    });
                    
                    GroupHierarchy.moveAllChildren(this, dx, dy, svg);
                });
            }
            

        },
        
          //check if descendant in the group parent, or if descendant is in a group who descends from parent.
        isDescendant:function(descendant, parent, svg) {

            if ( descendant.getAttribute("parent") === parent.id ) {
                return true;
            }        
        
            while( descendant.getAttribute("parent") !== "none" && descendant.getAttribute("parent") !== null) {
            
                descendant = svg.selectAll("#" + descendant.getAttribute("parent") ).select(function(d) {
                    if ( descendant.getAttribute("use") === "container" ) {
                        return this;
                    }
                    
                    else {
                        return null;
                    }
                });

                descendant = D3Helper.getElFromSel(descendant);
            
                if(descendant.getAttribute("parent") === parent.id) {
                    return true;
                }
            }
            
            return false;
        }
    
    }
    
})
    

//Notes

    /* this function is a template for doing anything to all descendants of a group.
    
    function findAllChildren(parent, svg) {
        var children = svg.selectAll("*[parent=\"" + parent.id + "\"]")
        
        if (!children.empty()) {
            children.each(function(d) {
                //here is where we do anything we want to do to all children
                findAllChildren(this);
            });
        }
        
        else {
            return;
        }
    }
    */
