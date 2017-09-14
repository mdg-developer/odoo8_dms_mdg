openerp.org_chart = function(instance){

    var QWeb = instance.web.qweb;
    var _t = instance.web._t,
        _lt = instance.web._lt;

    instance.web.client_actions.add('org_chart.company_employee','instance.org_chart.company_employee');
    instance.org_chart.company_employee = instance.Widget.extend({
        template: 'org_chart',

        init:function(data){
            this._super(data);
        },

        start: function(){
            var self = this
            var emp_child = []
            var orgdiagram = null;
            var counter = 0;
            var m_timer = null;
            var fromValue = null;
            var fromChart = null;
            var toValue = null;
            var toChart = null;
            var items = {};
            self.dept_dataset = new instance.web.DataSetSearch(self, 'hr.department', {}, []);

            $(document).ready(function () {
                jQuery.ajaxSetup({
                    cache: false
                });
                ResizePlaceholder();
                orgdiagram = SetupWidget(jQuery(".contentpanel"), "contentpanel");
            });

            function SetupWidget(element, name) {
                var result;
                var options = new primitives.orgdiagram.Config();
                var itemsToAdd = [];
                var dept_ids = []

                self.dept_dataset.call('employee_dept',[[]]).done(function(callbacks){
                    var options = new primitives.orgdiagram.Config();
                    _.each(callbacks[0],function(employee){
                        var employee_id = employee.emp_id
                        var employee_name = employee.emp_name
                        var employee_parent = parseInt(employee.parent)
                        var employee_email = employee.emp_email
                        var employee_job_title = employee.emp_job_title
                        var employee_data = {
                            'id': employee_id,
                            'title':employee_name,
                            'parent':employee_parent,
                            "itemTitleColor": "green",
                            "email":employee_email ? employee_email : "",
                             childrenPlacementType: primitives.common.ChildrenPlacementType.Vertical,
                             hasSelectorCheckbox :primitives.common.Enabled.False,
                            'image':window.location.origin + '/web/binary/image?model=hr.employee&field=image_medium&id='+employee_id,
                            'description': employee_job_title ? employee_job_title : "",
                        }
                        itemsToAdd.push(employee_data)
                        items[employee_data.id] = employee_data
                    })

                    _.each(callbacks[1],function(department){
                        var emp_id = department.dept_employee_id;
                        var dept_id;
                        var dept_name = department.dept_name;
                        var dept_parent_id ;
                        var dept_employee_id = department.dept_employee_id;
                        var dept_employee_name = department.dept_employee_name;
                        var dept_employee_email = department.dept_employee_email;
                        var dept_employee_job_title = department.dept_employee_job_title;

                        if(department.dept_id.split("_")[1] != 'False' ){
                            dept_id = department.dept_id
                        }else{
                            dept_id = null
                        }
                        if(department.dept_parent_id.split("_")[1] !='False' ){
                            dept_parent_id = department.dept_parent_id
                        }else{
                            dept_parent_id = null
                        }
                        var department_data = {
                            'id': dept_id,
                            'title':dept_name,
                            'parent':dept_parent_id,
                            'image':'org_chart/static/src/img/dept.gif',
                             hasSelectorCheckbox :primitives.common.Enabled.True,
                            "itemTitleColor": "red",
                            'description': "",
                        }
                        dept_ids.push(dept_id)
                        var employee = {}
                        if (dept_employee_id){
                            employee = {
                               'id': dept_employee_id, 
                               'title':dept_employee_name,
                               'parent':dept_id,
                               'description':dept_employee_job_title,
                               "itemTitleColor": "green",
                               "email":dept_employee_email ? dept_employee_email :"",
                               childrenPlacementType: primitives.common.ChildrenPlacementType.Vertical,
                               hasSelectorCheckbox :primitives.common.Enabled.False,
                               'image':window.location.origin + '/web/binary/image?model=hr.employee&field=image_medium&id='+dept_employee_id
                            }
                            itemsToAdd.push(employee)
                            items[employee.id] = employee
                        }
                        itemsToAdd.push(department_data)
                        items[department_data.id] = department_data
                    })

                    options.items = itemsToAdd;
                    options.cursorItem = 0;
                    options.selectedItems = dept_ids
                    options.pageFitMode = primitives.common.PageFitMode.pageHeight;
                    options.orientationType = primitives.common.OrientationType.Top;
                    options.horizontalAlignmentType = primitives.common.HorizontalAlignmentType.Center;
                    options.visibility = primitives.common.Visibility.Dot;
                    options.selectionPathMode =primitives.orgdiagram.SelectionPathMode.None,
                    options.items = itemsToAdd;
                    options.normalLevelShift = 20;
                    options.dotLevelShift = 10;
                    options.lineLevelShift = 10;
                    options.normalItemsInterval = 20;
                    options.dotItemsInterval = 10;
                    options.lineItemsInterval = 25;
                    options.templates = [getContactTemplate()];
                    options.defaultTemplateName = "contactTemplate";
                    options.onItemRender = (name == "contentpanel")?  onOrgDiagramTemplateRender : onOrgDiagramTemplateRender;

                    /* chart uses mouse drag to pan items, disable it in order to avoid conflict with drag & drop */
                    options.enablePanning = false;

                    result = element.orgDiagram(options);
                    element.droppable({
                        greedy: true,
                        drop: function (event, ui) {
                                    /* Check drop event cancelation flag
                                     * This fixes following issues:
                                     * 1. The same event can be received again by updated chart
                                     * so you changed hierarchy, updated chart and at the same drop position absolutly 
                                     * irrelevant item receives again drop event, so in order to avoid this use primitives.common.stopPropagation
                                     * 2. This particlular example has nested drop zones, in order to 
                                     * suppress drop event processing by nested droppable and its parent we have to set "greedy" to false,
                                     * but it does not work.
                                     * In this example items can be droped to other items (except immidiate children in order to avoid looping)
                                     * and to any free space in order to make them rooted.
                                     * So we need to cancel drop  event in order to avoid double reparenting operation.
                                     */
                            if (!event.cancelBubble) {
                                toValue = null;
                                toChart = name;
                                Reparent(fromChart, fromValue, toChart, toValue);
                                primitives.common.stopPropagation(event);
                            }
                        }
                    });
                    return result;
                });
            }

            function getContactTemplate() {
                var result = new primitives.orgdiagram.TemplateConfig();
                    result.name = "contactTemplate";
                    result.itemSize = new primitives.common.Size(200, 100);
                    result.minimizedItemSize = new primitives.common.Size(4, 4);
                    result.highlightPadding = new primitives.common.Thickness(2, 2, 2, 2);
                    var itemTemplate = jQuery(
                            '<div class="bp-item bp-corner-all bt-item-frame" style="border-width: 1px; width: 95px; height: 99px;  left: 922.5px; position: absolute; padding: 0px; margin: 0px; visibility: inherit;">'
                                + '<div name="titleBackground" class="bp-item bp-corner-all bp-title-frame" style="top: 2px; left: 2px; width: 216px; height: 20px;">'
                                + '<div name="title" class="bp-item bp-title" style="top: 3px; left: 6px; width: 208px; height: 18px;">'
                                + '</div>'
                          + '</div>'
                          + '<div class="bp-item bp-photo-frame" style="top: 26px; left: 2px; width: 50px; height: 60px;">'
                          + '<img name="photo" style="height: 60px; width:50px;" />'
                          + '</div>'
                          + '<div name="description" class="bp-item" style="top: 62px; left: 56px; width: 162px; height: 36px; font-size: 12px;"></div>'
                          + '<div class="bp-item" style="top: 44px; left: 56px; width: 162px; height: 18px; font-size: 12px;"><a name="email" href="" target="_top"></a></div>'
                          + '</div>'
                    ).css({
                        width: result.itemSize.width + "px",
                        height: result.itemSize.height + "px"
                    }).addClass("bp-item bp-corner-all bt-item-frame");
                    result.itemTemplate = itemTemplate.wrap('<div>').parent().html();
                return result;
            }

            function onOrgDiagramTemplateRender(event, data) {
                switch (data.renderingMode) {
                    case primitives.common.RenderingMode.Create:
                        data.element.draggable({
                            revert: "invalid",
                            containment: ".contentpanel",
                            scroll: true,
                            appendTo: ".oe_application",
                            helper: function(){
                                $copy = $(this).clone();
                                return $copy;
                            },
                            cursor: "move",
                            "zIndex": 10,
                            delay: 30,
                            distance: 10,
                            start: function (event, ui) {
                                fromValue = jQuery(this).attr("data-value");
                                fromChart = "contentpanel";
                            },
                            drag: function( event, ui ) {
                                
                                // Keep the left edge of the element
                                // at least 100 pixels from the container
                                ui.position.left = Math.min( ui.position.left,$(".contentpanel").width()-200 );
                                ui.position.top = Math.min( ui.position.top,$(".contentpanel").height()-50);
                              },
                        });
                        data.element.droppable({
                            /* this option is supposed to suppress event propogation from nested droppable to its parent
                             *  but it does not work*/
                            greedy: true,
                            drop: function (event, ui) {
                                if (!event.cancelBubble) {
                                    console.log("Drop accepted!");
                                    toValue = jQuery(this).attr("data-value");
                                    toChart = "contentpanel";
                                    Reparent(fromChart, fromValue, toChart, toValue);
                                    primitives.common.stopPropagation(event);
                                } else {
                                    console.log("Drop ignored!");
                                }
                            },
                            over: function (event, ui) {
                                toValue = jQuery(this).attr("data-value");
                                toChart = "contentpanel";
                                $(".openerp_webclient_container").animate({
                                    scrollTop:  event.target.offsetTop,
                                    scrollLeft :event.target.offsetLeft - 400
                                });
                                jQuery(this).attr("data-value")      /* this is needed in order to update highlighted item in chart, 
                                 * so this creates consistent mouse over feed back */

                                jQuery(".contentpanel").orgDiagram({ "highlightItem": toValue });
                                jQuery(".contentpanel").orgDiagram("update", primitives.common.UpdateMode.PositonHighlight);
                            },
                            accept: function (draggable) {
                                /* be carefull with this event it is called for every available droppable including invisible items on every drag start event.
                                 * don't varify parent child relationship between draggable & droppable here it is too expensive.*/
                                return (jQuery(this).css("visibility") == "visible");
                            }
                        });
                    /* Initialize widgets here */
                    break;
                    case primitives.common.RenderingMode.Update:
                        /* Update widgets here */
                        break;
                }
                var itemConfig = data.context;
                /* Set item id as custom data attribute here */
                data.element.attr("data-value", itemConfig.id);
                RenderField(data, itemConfig);
            }

            function Reparent(fromChart, value, toChart, toParent) {
                /* following verification needed in order to avoid conflict with jQuery Layout widget */
                if (fromChart != null && value != null && toChart != null) {
                    console.log("Reparent fromChart:" + fromChart + ", value:" + value + ", toChart:" + toChart + ", toParent:" + toParent);
                    var item = items[value];
                    var fromItems = jQuery("#" + fromChart).orgDiagram("option", "items");
                    var toItems = jQuery("#" + toChart).orgDiagram("option", "items");
                    if (toParent != null) {
                        var toParentItem = items[toParent];
                        var to_id;

                        this.org_dataset = new instance.web.DataSetSearch(this, 'hr.department', {}, []);
                        if(typeof toParentItem.id == "number"){
                            to_id = parseInt(toParentItem.id);
                        }else{
                            to_id = parseInt(toParentItem.id.split('_')[1])
                        }

                        this.org_dataset.read_slice(['id', 'manager_id'],{'domain': [['id', '=',to_id ]]}).then(function(table_records){
                            if(typeof item.id == "string" && typeof toParentItem.id == "number"){
                                alert("Not Possible")
                                return false
                            }else if(typeof item.id == "string" || (typeof item.id == "number" && typeof toParentItem.id == "number")){
                                if (!isParentOf(item, toParentItem)) {
                                    var children = getChildrenForParent(item);
                                    children.push(item);
                                    for (var index = 0; index < children.length; index++) {
                                        var child = children[index];
                                        fromItems.splice(primitives.common.indexOf(fromItems, child), 1);
                                        toItems.push(child);
                                    }
                                    item.parent = toParent;
                                }
                                jQuery(".contentpanel").orgDiagram("update", primitives.common.UpdateMode.Recreate);
                            }else if(table_records[0].manager_id){
                                alert("Manager Already Exists..")
                                return false
                            }else{
                                if (!isParentOf(item, toParentItem)) {
                                    var children = getChildrenForParent(item);
                                    children.push(item);
                                    for (var index = 0; index < children.length; index++) {
                                        var child = children[index];
                                        fromItems.splice(primitives.common.indexOf(fromItems, child), 1);
                                        toItems.push(child);
                                    }
                                    item.parent = toParent;
                                }
                                jQuery(".contentpanel").orgDiagram("update", primitives.common.UpdateMode.Recreate);
                            }
                        });
                    }
                }
            }

            function getChildrenForParent(parentItem) {
                var children = {};
                for(var id in items) {
                    var item = items[id];
                    if (children[item.parent] == null) {
                        children[item.parent] = [];
                    }
                    children[item.parent].push(id);
                }
                var newChildren = children[parentItem.id];
                var result = [];
                if (newChildren != null) {
                    while (newChildren.length > 0) {
                        var tempChildren = [];
                        for(var index = 0; index < newChildren.length; index++) {
                            var item = items[newChildren[index]];
                            result.push(item);
                            if (children[item.id] != null) {
                                tempChildren = tempChildren.concat(children[item.id]);
                            }
                        }
                        newChildren = tempChildren;
                    }
                }
                return result;
            }

            function isParentOf(parentItem, childItem) {
                var self = this;
                self.org_dataset = new instance.web.DataSetSearch(self, 'hr.department', {}, []);
                self.org_emp_dataset = new instance.web.DataSetSearch(self, 'hr.employee', {}, []);
                //dtod
                if (typeof parentItem.id == "string" && typeof childItem.id == "string"){
                    self.org_dataset.write(parseInt(parentItem.id.split("_")[1]),{'parent_id':parseInt(childItem.id.split("_")[1])}); 
                }
                //etod
                if(typeof parentItem.id == "number" && typeof childItem.id == "string"){
                    var parentItem_parent = parentItem.parent
                    var parentItem_id = parentItem.id
                    self.org_dataset.write(parseInt(childItem.id.split("_")[1]),{'manager_id':parseInt(parentItem.id)}).done(function(){
                        if(typeof parentItem_parent == "number"){
                            self.org_emp_dataset.write(parentItem_id,{'parent_id':false});
                        }else{
                            self.org_dataset.write(parseInt(parentItem_parent.split("_")[1]),{'manager_id':false});
                        }
                    });
                }
                //etoe
                if(typeof parentItem.id == "number" && typeof childItem.id == "number"){
                    var parentItem_parent = parentItem.parent
                    self.org_emp_dataset.write(parseInt(parentItem.id),{'parent_id':parseInt(childItem.id)}).done(function(){
                        if(typeof parentItem_parent == "string" ){
                            self.org_dataset.write(parseInt(parentItem_parent.split("_")[1]),{'manager_id':false});
                        }
                    });
                    //this.org_emp_dataset.write(parseInt(childItem.id),{'parent_id':false});
                }
                var result = false,
                    index,
                    len,
                    itemConfig;
                if (parentItem.id == childItem.id) {
                    result = true;
                } else {
                    while (childItem.parent != null) {
                       childItem = items[childItem.parent];
                       if (childItem.id == parentItem.id) {
                           result = true;
                           break;
                       }
                    }
                }
                return result;
            };

            function RenderField(data, itemConfig) {
                if (data.templateName == "contactTemplate") {
                    data.element.find("[name=photo]").attr({ "src": itemConfig.image, "alt": itemConfig.title });
                    data.element.find("[name=titleBackground]").css({ "background": itemConfig.itemTitleColor });
                    data.element.find("[name=email]").attr({ "href": ("mailto:" + itemConfig.email + "?Subject=Hello%20again") });
                    var fields = ["title", "description", "phone", "email"];
                    for (var index = 0; index < fields.length; index++) {
                        var field = fields[index];
                        var element = data.element.find("[name=" + field + "]");
                        if (element.text() != itemConfig[field]) {
                            element.text(itemConfig[field]);
                        }
                    }
                }
            }

            $(window).resize(function(){
                ResizePlaceholder()
            })

            function ResizePlaceholder() {
                var panel = jQuery("window");
                var panelSize = new primitives.common.Rect(0, 0, panel.innerWidth(), panel.innerHeight());
                var position = new primitives.common.Rect(0, 0, panelSize.width / 2, panelSize.height);
                    position.offset(-2);
                    var position2 = new primitives.common.Rect(panelSize.width / 2, 0, panelSize.width / 2, panelSize.height);
                    position2.offset(-2);
                    jQuery(".contentpanel").css(position.getCSS());
                    var bodyWidth = $(window).width()
                    var bodyHeight = $(window).height() - 80
                    jQuery(".contentpanel").css({
                        "width": bodyWidth + "px",
                        "height": bodyHeight + "px",
                    });
                    jQuery(".contentpanel").addClass("set_style")
            }

            jQuery("#print").click(function(){
                window.print();
            });

            jQuery("#toogl_button").click(function (e) {
                if(jQuery("#toogl_button").text().trim("") == _t('Vertical layout')){
                    jQuery(".contentpanel").orgDiagram({
                        orientationType: primitives.common.OrientationType.Left,
                        horizontalAlignment: primitives.common.HorizontalAlignmentType.Center
                    });
                    jQuery(".contentpanel").orgDiagram("update", primitives.orgdiagram.UpdateMode.Refresh);
                    jQuery("#toogl_button").text(_t("Horizontal layout"))
                }else if(jQuery("#toogl_button").text().trim("") == _t('Horizontal layout')){
                    jQuery(".contentpanel").orgDiagram({
                        orientationType: primitives.common.OrientationType.Top,
                        horizontalAlignment: primitives.common.HorizontalAlignmentType.Center
                    });
                    jQuery(".contentpanel").orgDiagram("update", primitives.orgdiagram.UpdateMode.Refresh);
                    jQuery("#toogl_button").text(_t("Vertical layout"))
                }
            });

            jQuery("#toogl_expand").click(function (e) {
                if(jQuery("#toogl_expand").text().trim("") == _t('Expand')){
                    jQuery(".contentpanel").orgDiagram({
                        pageFitMode : primitives.common.PageFitMode.None,
                    });
                    jQuery(".contentpanel").orgDiagram("update", primitives.orgdiagram.UpdateMode.Refresh);
                    jQuery("#toogl_expand").text("Shrink")
                }else if(jQuery("#toogl_expand").text().trim("") == _t('Shrink')){
                    jQuery(".contentpanel").orgDiagram({
                        pageFitMode : primitives.common.PageFitMode.pageHeight
                    });
                    jQuery(".contentpanel").orgDiagram("update", primitives.orgdiagram.UpdateMode.Refresh);
                    jQuery("#toogl_expand").text("Expand")
                }
            })
        }
    })

    instance.web.Menu.include({
        /**
         * Opens a given menu by id, as if a user had browsed to that menu by hand
         * except does not trigger any event on the way
         *
         * @param {Number} id database id of the terminal menu to select
         */
        open_menu: function (id) {
            this.current_menu = id;
            this.session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
            }

            // Activate current main menu
            this.$el.find('.active').removeClass('active');
            $main_menu.parent().addClass('active');

            // Show current sub menu
            this.$secondary_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Hide/Show the leftbar menu depending of the presence of sub-items
            this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);

            // Activate current menu item and show parents
            this.$secondary_menus.find('.active').removeClass('active');
            if ($main_menu !== $clicked_menu) {
                $clicked_menu.parents().show();
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    $clicked_menu.parent().addClass('active');
                }
            }
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'destroy');
           });
            if($clicked_menu[0].text.trim() == _t("Employee Chart")){
                $(".oe_leftbar").hide()
            }else{
                $(".oe_leftbar").show()
            }
        },
    })
}
