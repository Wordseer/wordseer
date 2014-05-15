/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.objects.Group', {

    alternateClassName: ['Group'],
     
    statics: {         
        id_count: 1,
        
          //default height and width
        def_height: 150,
        def_width: 250,
        
          //expand rectangle height and width
        exp_h: 7,
        exp_w: 30,
    
        createGroup:function(dataset, svg, drag, expand) {

            dataset.push( this.id_count );
            
            var x = this.id_count;
            this.id_count++; 
             
              //need to figure out where to insert the group...this could get complicated later            
            var selector = "*[layer=\"1\"]";
            
            if(svg.selectAll(selector).empty()) {
                selector = "*[layer=\"0\"]";
            }
            
            var group = svg.insert("rect", selector)
                .style("stroke", "#443322")
                .style("fill", "#F1F1C1")
                .attr("oldfill", "#F1F1C1")
                .attr("id", "group" + x + "")
                .attr("class", "foreground")
                .attr("type", "group")
                .attr("layer", 2)
                .attr("use", "container")
                .attr("shape", "right")
                .attr("parent", "none")
                .attr("z", x)
                .attr("rx", 0)
                .attr("ry", 0)
                .attr("height", Group.def_height)
                .attr("width", Group.def_width)
                .attr("transform", "translate(0,0)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(drag);
  
            svg.insert("rect", selector)
                .style("stroke", "#5F4F3F")
                .style("fill", "#5F4F3F")
                .attr("id", "group" + x + "")
                .attr("class", "foreground")
                .attr("type", "group")
                .attr("layer", 2)
                .attr("use", "expand")
                .attr("z", (x - 0.1))
                .attr("x", (Group.def_width / 2) - (Group.exp_w / 2) )
                .attr("y", Group.def_height )
                .attr("height", Group.exp_h)
                .attr("width", Group.exp_w)
                .attr("transform", "translate(0,0)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(expand);
                
            svg.insert("text", selector)
                .attr("id", "group" + x + "")
                .attr("class", "foreground")
                .attr("type", "group")
                .attr("layer", 2)
                .attr("use", "text")
                .attr("z", (x + 0.5))
                //XOFFSET YOFFSET
                .attr("x", 100 + 25)
                .attr("y", 50 - 35)
                .attr("text-anchor", "middle")
                .attr("transform", "translate(0,0)")
                .text("group " + x)
                .call(function(d) { Text.makeEditable(this, false); })
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                //.call(drag);
      
            var group = svg.selectAll("#group" + x + "")
                .select(function(d) {
                
                    if(this.getAttribute("use") === "container" && this.getAttribute("type") === "group") {
                        return this;
                    }
                    else {
                        return null;
                    }

                 });
                 
            group = D3Helper.getElFromSel(group);
      
            var newGroup = svg.selectAll("#group" + x + "").transition()
                .duration(150)
                .attr("transform", function(d) {
                    var window = D3Helper.getElFromSel(svg).parentNode;
                    var height = D3Helper.getStyle(window, "height");
                    height = D3Helper.getIntFromPx(height);
                    return "translate(" + 10 + "," + (height - (parseInt(group.getAttribute("height")) + 15) ) + ")";
                });
                


            OrganizeTool.getInstance().updateShape(1, group.getAttribute("shape"));
                 
        },
 
        removeGroup:function(el, dataset, svg) {
            var x = dataset[dataset.length - 1];
      
      
            svg.selectAll("*[parent=\"" + el.id + "\"]")
                .attr("parent", el.getAttribute("parent"));
      
            svg.selectAll("#" + el.id)
                .remove();
            
            dataset.pop();
            

        },
        
          //this isn't finished, we need to do something about the parents ideally.
        removeAll:function(el) {
            var ot = OrganizeTool.getInstance();
            var canvas = ot.canvas;
            
            var children = canvas.selectAll(".foreground").select(function(d) {
                if(GroupHierarchy.isDescendant(this, el, canvas) ) {
                    return this;
                }
                else {
                    return null;
                }
            });
            
            children.each(function(d) {
                ot.removeElement(this);
            });
        
            ot.removeElement(el);
            

        }
    
    }
    
})