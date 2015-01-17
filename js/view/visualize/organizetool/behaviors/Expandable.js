/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.behaviors.Expandable', {

    alternateClassName: ['Expandable'],
     
    statics: {     
 
           /* 
             This behavior allows resizing of groups by *dragging* the dark box 
             in the lower-right hand corner of the group. It is really a special
             case drag behavior. Dependant on the size of the group.
           */ 
           
        getExpandBehavior:function(minh, defh, minw, defw, svg){
            var expand = d3.behavior.drag()
                .on("dragstart", expandstart)
                .on("drag", expandmove)
                .on("dragend", expandend);
               
              //if this is the first drag, then "yes". otherwise, "no"     
            var expfirst = "yes";
            
              //to save the mouse position between expandmove calls
            var expandx = 0;
            var expandy = 0;
                
              //called when mouse is clicked and held down as if to drag
            function expandstart(d, i) {
                 expfirst = "yes";
                 return;
            }   
            
              //called when mouse is held down and moved
            function expandmove(d, i) {
            
                var group = this.id;
                
                  //the previous mouse position
                var befx = expandx;
                var befy = expandy;
                
                  //the current mouse position
                expandx = d3.event.x;
                expandy = d3.event.y;
                
                  //how much the mouse position has changed
                var dx = (expandx - befx);
                var dy = (expandy - befy);
                
                  //if this is the first call, don't update
                if( expfirst === "yes") {
                    expfirst = "no";
                    return;
                }
                
                  //if this is not the first call, update the position 
                  //with changed x and y values (dx and dy)
                else {
                    expandtick(dx, dy, group);
                }
            }

              //called on a mouse up from a drag
            function expandend(d, i) {

                CollisionHandling.handleCollisions(this, svg);
            }
            
              //update the movement (called from expandmove)
            function expandtick(dx, dy, group) { 
                
                var mygroup = svg.selectAll("#" + group);
                  
                          //get the container 
                var container = mygroup.select( function(d) {
                  if(this.getAttribute("use") === "container") { return this; }
                  else { return null; }
                });
                
                containerEl = D3Helper.getElFromSel(container);
                
                  //minimum width and height check         
                var newHeight = parseInt(containerEl.getAttribute("height")) + dy;
                var newWidth = parseInt(containerEl.getAttribute("width")) + (dx * 2);  
                
                var isMinHeight = false;
                var isMinWidth = false;
                
                if( newHeight < minh ) {
                    newHeight = minh;
                    isMinHeight = true;
                }
                
                if ( newWidth < minw ) {
                    newWidth = minw;
                    isMinWidth = true;
                }
                
                  //get the expand box (the dark box from lower right)
                mygroup.select( function() {
                  if(this.getAttribute("use") === "expand") {
                      return this;
                  }
                  else {
                      return null;
                  }
                  
                })
                     //move the expand box by dx and dy
                  .attr("transform", function(d) {
                       
                      if (this.getAttribute("transform") !== null) {
                          var move_x = D3Helper.getTransformX(this);
                          var move_y = D3Helper.getTransformY(this) + dy;
                          
                          if (isMinHeight) {
                              move_y = D3Helper.getTransformY(containerEl) - defh + minh;
                          }                              

                          return "translate(" + move_x + "," + move_y + ")";
                      }
                  })
                      .attr("x", function(d) {
                          return (D3Helper.getWidth("group", containerEl) / 2 ) - (this.getAttribute("width") / 2)
                      });
                
                    //change the container's height and width (resize it) according to the mouse's movement
                  container.attr("height", function(d) {
                      return newHeight;
                  })
                  .attr("width", function(d) {
                      return newWidth;
                  });
                  
                  container = D3Helper.getElFromSel(container);
                  
                  //get the text
                mygroup.select( function() {
                  if(this.getAttribute("use") === "text") {
                      return this;
                  }
                  else {
                      return null;
                  }
                  
                })
                
                    //center the text horozontally
                  .attr("x", function(d) {
                      return parseInt(container.getAttribute("width")) / 2;
                  });
            }

            return expand;
        }
    }
})
