(function() {
    'use strict';

    var website = openerp.website;
    // website.openerp_website = {};
    var _t = openerp._t;

    website.add_template_file('/theme_crafito/static/src/xml/theme_crafito.xml');

    website.snippet.options.crafito_tabbing_snippet = website.snippet.Option.extend({
        start: function() {
            var self = this;
            self.$el.find(".custom_add_option").on('click', _.bind(self.custom_add_function, self));
            self.$el.find(".custom_remove_option").on('click', _.bind(self.custom_remove_function, self));
            // self.$el.find("li[role='presentation'] > a[role='tab']").css('display','block')
            self._super();
        },
        drop_and_build_snippet: function() {
            var self = this;
            var unique_id = Math.random().toString(36).substring(7);
            self.$target.find('.nav-tabs > li > a').each(function() {
                var item = $(this);
                var href = item.attr('href');
                item.attr('href', String(href) + String(unique_id));
                item.attr('data-cke-saved-href', String(item.attr('data-cke-saved-href')) + String(unique_id));
                item.attr('aria-controls', String(item.attr('aria-controls')) + String(unique_id));
                var pane = self.$target.find('.tab-content > div' + href);
                pane.attr('id', String(pane.attr('id')) + String(unique_id))
            });
        },
        custom_add_function: function() {
            var self = this;
            var tabs = self.$target.find('.nav-tabs');
            var panes = self.$target.find('.tab-content');
            var newid = Math.random().toString(36).substring(7);

            var li = $('<li/>', {
                'role': 'presentation',
                'class': 'active'
            });
            $('<a/>', {
                'href': '#' + newid,
                'aria-controls': 'tab1',
                'role': 'tab',
                'data-toggle': 'tab',
                'text': 'New'
            }).appendTo(li);
            var div = $("<div id='" + newid + "' class='oe_structure oe_empty tab-pane active' role='tabpanel'><p>A great way to catch your reader's attention is to tell astory. Everything you consider writing can be told as astory.</p><p><b>Great stories have personality.</b> Consider telling a great story that provides personality. Writing a story withpersonality for potential clients will asist with making a relationship connection. This shows up in small quirks like word choices or phrases. Write from your point of view, not from someone else's experience.</p></div>")

            li.insertBefore(tabs.find('.active').removeClass('active'));
            div.insertBefore(panes.find('.active').removeClass('active'));
        },
        custom_remove_function: function() {
            var self = this;
            var tabs = self.$target.find('.nav-tabs');
            var panes = self.$target.find('.tab-content');

            if (tabs.find('> li[role="presentation"]').size() > 1 && panes.find('> div[role="tabpanel"]').size() > 1) {
                tabs.find('.active').remove();
                panes.find('.active').remove();
                tabs.find('> li[role="presentation"]:first').addClass('active');
                panes.find('> div[role="tabpanel"]:first').addClass('active');
            }
        },
    });

    website.snippet.options.theme_crafito_blog_custom_snippet = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.crafito_blog_slider').empty();
            if (!editMode) {
                self.$el.find(".crafito_blog_slider").on("click", _.bind(self.theme_crafito_blog_slider, self));
            }
        },
        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.theme_crafito_blog_slider()) {
                this.theme_crafito_blog_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },
        clean_for_save: function() {
            $('.crafito_blog_slider').empty();
        },
        theme_crafito_blog_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#blog_slider_type"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                openerp.jsonRpc('/theme_crafito/blog_get_options', 'call', {}).done(function(res) {
                    $('#blog_slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_type.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_type.val());
                    if ($('select#blog_slider_type').find(":selected").text()) {
                        type = _t($('select#blog_slider_type').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_multi_cat_custom_snippet = website.snippet.Option.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.oe_multi_category_slider').empty();
            if (!editMode) {
                self.$el.find(".oe_multi_category_slider").on("click", _.bind(self.multi_category_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.multi_category_slider()) {
                this.multi_category_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_multi_category_slider').empty();
        },

        multi_category_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.multi_product_custom_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_type"),
                    $category_slider_cancel = self.$modal.find("#cancel"),
                    $snippnet_submit = self.$modal.find("#multi_tabs_submit");

                openerp.jsonRpc('/theme_crafito/product_multi_get_options', 'call', {}).done(function(res) {
                    $("select[id='slider_type'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_type']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    // var type = '';
                    self.$target.attr('data-multi-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl-' + $slider_type.val());
                    if ($('select#slider_type').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_type').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy"> ' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_coming_soon_mode_one = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".biztech_coming_soon_mode_one").empty();
            if (!editMode) {
                self.$el.find(".biztech_coming_soon_mode_one").on("click", _.bind(self.theme_crafito_coming_soon_mode_one_function, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.theme_crafito_coming_soon_mode_one_function()) {
                self.theme_crafito_coming_soon_mode_one_function.fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.biztech_coming_soon_mode_one').empty();
        },

        theme_crafito_coming_soon_mode_one_function: function(type, value) {
            if (type == "click" || type == undefined) {
                var self = this;
                self.$modal = $(openerp.qweb.render("theme_crafito.model_dialog_commingsoon"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $sub_data = self.$modal.find("#biztech_coumtdown_btn");
                var $can = self.$modal.find("#biz_cancle");
                $sub_data.on('click', function() {
                    if (parseInt(self.$modal.find("input#year").val()) > 0 || parseInt(self.$modal.find("input#month").val()) > 0 || parseInt(self.$modal.find("input#day").val()) > 0 || parseInt(self.$modal.find("input#minutes").val()) > 0 || parseInt(self.$modal.find("input#hours").val()) > 0 || parseInt(self.$modal.find("input#second").val()) > 0) {
                        if (parseInt(self.$modal.find("input#minutes").val()) <= 60 & parseInt(self.$modal.find("input#second").val()) <= 60) {
                            var current_date = new Date();
                            var count_year = parseInt(self.$modal.find("input#year").val()) + current_date.getFullYear();
                            var count_month = parseInt(self.$modal.find("input#month").val()) + current_date.getMonth() + 1;
                            var count_date = parseInt(self.$modal.find("input#day").val()) + current_date.getDate();
                            var count_hours = parseInt(self.$modal.find("input#hours").val()) + current_date.getHours();
                            var count_min = parseInt(self.$modal.find("input#minutes").val()) + current_date.getMinutes();
                            var count_sec = parseInt(self.$modal.find("input#second").val()) + current_date.getSeconds();
                            var total_days = parseInt(new Date(count_year, current_date.getMonth() + 1, 0).getDate())
                            while (count_sec > 60) {
                                count_min = count_min + 1
                                count_sec = count_sec - 60
                            }
                            while (count_min > 60) {
                                count_hours = count_hours + 1
                                count_min = count_min - 60
                            }
                            while (count_hours > 24) {
                                count_date = count_date + 1
                                count_hours = count_hours - 24
                            }
                            while (count_date > total_days) {
                                count_month = count_month + 1
                                count_date = count_date - total_days
                                total_days = parseInt(new Date(count_year, count_month, 0).getDate())


                            }
                            while (count_month > 12) {
                                count_year = count_year + 1
                                count_month = count_month - 12
                            }
                            var formated_date = count_month + '/' + count_date + '/' + count_year + ' ' + count_hours + ':' + count_min + ':' + count_sec;
                            self.$modal.modal('hide');
                            self.$target.attr('data-blog-updated-date-time', formated_date)

                        } else {
                            alert("Minutes and seconds should be between 0 to 60.")
                        }
                    } else {
                        alert("Please enter proper data.")
                    }
                })
                $can.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            }
        }
    });

    website.snippet.options.theme_crafito_coming_soon_mode_two = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".biztech_coming_soon_mode_two").empty();
            if (!editMode) {
                self.$el.find(".biztech_coming_soon_mode_two").on("click", _.bind(self.theme_crafito_coming_soon_mode_two_function, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.theme_crafito_coming_soon_mode_two_function()) {
                self.theme_crafito_coming_soon_mode_two_function.fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.biztech_coming_soon_mode_two').empty();
        },

        theme_crafito_coming_soon_mode_two_function: function(type, value) {
            if (type == "click" || type == undefined) {
                var self = this;
                self.$modal = $(openerp.qweb.render("theme_crafito.model_dialog_commingsoon"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $sub_data = self.$modal.find("#biztech_coumtdown_btn");
                var $mode_two_can = self.$modal.find("#biz_cancle");
                $sub_data.on('click', function() {
                    if (parseInt(self.$modal.find("input#year").val()) > 0 || parseInt(self.$modal.find("input#month").val()) > 0 || parseInt(self.$modal.find("input#day").val()) > 0 || parseInt(self.$modal.find("input#minutes").val()) > 0 || parseInt(self.$modal.find("input#hours").val()) > 0 || parseInt(self.$modal.find("input#second").val()) > 0) {
                        if (parseInt(self.$modal.find("input#minutes").val()) <= 60 & parseInt(self.$modal.find("input#second").val()) <= 60) {
                            var current_date = new Date();
                            var count_year = parseInt(self.$modal.find("input#year").val()) + current_date.getFullYear();
                            var count_month = parseInt(self.$modal.find("input#month").val()) + current_date.getMonth() + 1;
                            var count_date = parseInt(self.$modal.find("input#day").val()) + current_date.getDate();
                            var count_hours = parseInt(self.$modal.find("input#hours").val()) + current_date.getHours();
                            var count_min = parseInt(self.$modal.find("input#minutes").val()) + current_date.getMinutes();
                            var count_sec = parseInt(self.$modal.find("input#second").val()) + current_date.getSeconds();
                            var total_days = parseInt(new Date(count_year, current_date.getMonth() + 1, 0).getDate())
                            while (count_sec > 60) {
                                count_min = count_min + 1
                                count_sec = count_sec - 60
                            }
                            while (count_min > 60) {
                                count_hours = count_hours + 1
                                count_min = count_min - 60
                            }
                            while (count_hours > 24) {
                                count_date = count_date + 1
                                count_hours = count_hours - 24
                            }
                            while (count_date > total_days) {
                                count_month = count_month + 1
                                count_date = count_date - total_days
                                total_days = parseInt(new Date(count_year, count_month, 0).getDate())


                            }
                            while (count_month > 12) {
                                count_year = count_year + 1
                                count_month = count_month - 12
                            }
                            var formated_date = count_month + '/' + count_date + '/' + count_year + ' ' + count_hours + ':' + count_min + ':' + count_sec;
                            self.$modal.modal('hide');
                            self.$target.attr('data-cm2-updated-date-time', formated_date)

                        } else {
                            alert("Minutes and seconds should be between 0 to 60.")
                        }
                    } else {
                        alert("Please enter proper data.")
                    }
                })
                $mode_two_can.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            }
        }
    });

    website.snippet.options.theme_crafito_category_slider = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".oe_cat_slider").empty();
            if (!editMode) {
                self.$el.find(".oe_cat_slider").on("click", _.bind(self.cat_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_cat_slider').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_type"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");

                openerp.jsonRpc('/theme_crafito/category_get_options', 'call', {}).done(function(res) {
                    $('#slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-cat-slider-id', $slider_type.val());
                    if ($('select#slider_type').find(":selected").text()) {
                        type = _t($('select#slider_type').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_product_slider = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".oe_prod_slider").empty();
            if (!editMode) {
                self.$el.find(".oe_prod_slider").on("click", _.bind(self.prod_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.prod_slider()) {
                this.prod_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_prod_slider').empty();
        },

        prod_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_dynamic_product_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_type"),
                    $product_slider_cancel = self.$modal.find("#cancel"),
                    $pro_sub_data = self.$modal.find("#prod_sub_data");

                openerp.jsonRpc('/theme_crafito/product_get_options', 'call', {}).done(function(res) {
                    $('#slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-prod-slider-id', $slider_type.val());
                    if ($('select#slider_type').find(":selected").text()) {
                        type = _t($('select#slider_type').find(":selected").text());
                    } else {
                        type = _t("Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $product_slider_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                });
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_featured_product_slider = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".oe_featured_prod_slider").empty();
            if (!editMode) {
                self.$el.find(".oe_featured_prod_slider").on("click", _.bind(self.featured_prod_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.featured_prod_slider()) {
                this.featured_prod_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_featured_prod_slider').empty();
        },

        featured_prod_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_dynamic_featured_product_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#featured_slider_type"),
                    $featured_product_slider_cancel = self.$modal.find("#cancel"),
                    $pro_sub_data = self.$modal.find("#featured_prod_sub_data");

                openerp.jsonRpc('/theme_crafito/featured_product_get_options', 'call', {}).done(function(res) {
                    $('#slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='featured_slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-featured-prod-slider-id', $slider_type.val());
                    if ($('select#featured_slider_type').find(":selected").text()) {
                        type = _t($('select#featured_slider_type').find(":selected").text());
                    } else {
                        type = _t("Featured Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $featured_product_slider_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                });
            } else {
                return;
            }
        },
    });
    website.snippet.options.biztech_new_theme_fact_sheet_jsselector = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".theme_fact_sheet").empty();
            if (!editMode) {
                self.$el.find(".biztech_fact_sheet").on("click", _.bind(self.biztech_fact_sheet_function, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.biztech_fact_sheet_function()) {
                this.biztech_fact_sheet_function().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.biztech_fact_sheet').empty();
        },

        biztech_fact_sheet_function: function(type) {
            if (type == "click" || type == undefined) {
                var self = this;
                var factcount
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_dynami_fact_sheet"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $cancel = self.$modal.find("#biz_cancle"),
                    $fact_selection = self.$modal.find("#fact_count_selection"),
                    $sub_data = self.$modal.find("#bzitech_fact_btn");
                $fact_selection.on("change", function() {
                    factcount = parseInt($fact_selection.find(":selected").val());
                    if (factcount == 0) {
                        alert("Please enter proper data")
                    } else {
                        var i;
                        for (i = 2; i <= 4; i++) {
                            if (i <= factcount) {
                                self.$modal.find("#icon_hided_" + i).removeClass("hidden");
                                self.$modal.find("#name_hided_" + i).removeClass("hidden");
                                self.$modal.find("#number_hided_" + i).removeClass("hidden");
                            } else {
                                self.$modal.find("#icon_hided_" + i).addClass("hidden");
                                self.$modal.find("#name_hided_" + i).addClass("hidden");
                                self.$modal.find("#number_hided_" + i).addClass("hidden");
                            }
                        }

                    }
                });
                $sub_data.on('click', function() {
                    var i
                    var fact_numbers = []
                    var fact_name_error = []
                    var fact_icon_error = []
                    for (i = 1; i <= 4; i++) {
                        if (self.$modal.find("#number_hided_" + i).attr('class') == 'form-control' & (self.$modal.find("#number_hided_" + i).val() < 1 || self.$modal.find("#number_hided_" + i) > 100)) {
                            fact_numbers.push("error")
                        }
                        if (self.$modal.find("#name_hided_" + i).attr('class') == 'form-control' & self.$modal.find("#name_hided_" + i).val() == '') {
                            fact_name_error.push("error")
                        }
                        if (self.$modal.find("#icon_hided_" + i).attr('class') == 'form-control' & self.$modal.find("#icon_hided_" + i).val() == '') {
                            fact_icon_error.push("error")
                        }
                    }
                    if (fact_icon_error.length == 0) {
                        if (fact_name_error.length == 0) {
                            if (fact_numbers.length == 0) {
                                if (isNaN(parseInt(self.$modal.find("input[name='business']").val())) == false & isNaN(parseInt(self.$modal.find("input[name='client']").val())) == false & isNaN(parseInt(self.$modal.find("input[name='projects']").val())) == false & isNaN(parseInt(self.$modal.find("input[name='award']").val())) == false) {
                                    self.$target.attr('data-fact-number-1', parseInt(self.$modal.find("input[name='business']").val()))
                                    self.$target.attr('data-fact-number-2', parseInt(self.$modal.find("input[name='client']").val()))
                                    self.$target.attr('data-fact-number-3', parseInt(self.$modal.find("input[name='projects']").val()))
                                    self.$target.attr('data-fact-number-4', parseInt(self.$modal.find("input[name='award']").val()))
                                    self.$target.attr('data-fact-name-1', self.$modal.find("input[name='label_business']").val() || "In Business")
                                    self.$target.attr('data-fact-name-2', self.$modal.find("input[name='label_client']").val() || "Clients Served")
                                    self.$target.attr('data-fact-name-3', self.$modal.find("input[name='label_projects']").val() || "Projects Delivered")
                                    self.$target.attr('data-fact-name-4', self.$modal.find("input[name='label_award']").val() || "Awards Won")
                                    self.$target.attr('data-fact-icon-1', self.$modal.find("input[name='label_business_icone']").val() || "fa fa-thumbs-o-up")
                                    self.$target.attr('data-fact-icon-2', self.$modal.find("input[name='label_client_icone']").val() || "fa fa-comments")
                                    self.$target.attr('data-fact-icon-3', self.$modal.find("input[name='label_projects_icon']").val() || "fa fa-smile")
                                    self.$target.attr('data-fact-icon-4', self.$modal.find("input[name='label_award_icon']").val() || "fa fa-trophy")
                                    self.$modal.modal('hide');
                                } else {
                                    alert("Only number are allowed");
                                }
                            } else {
                                alert("Numbers should be greater than 0")
                            }
                        } else {
                            alert("Titles can not be blak")
                        }
                    } else {
                        alert("Icons can not be blank")
                    }
                });

                $cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                    self.$modal.modal('hide');
                })

            }
        }

    });
    website.snippet.options.biztech_new_theme_skill_jsselector = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".biztech_new_theme_skill").empty();
            if (!editMode) {
                self.$el.find(".biztech_new_theme_skill").on("click", _.bind(self.biztech_new_theme_skill_function, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.biztech_new_theme_skill_function()) {
                this.biztech_new_theme_skill_function().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.biztech_new_theme_skill').empty();
        },

        biztech_new_theme_skill_function: function(type) {
            if (type == "click" || type == undefined) {
                var self = this;
                var skillcount
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_dyanamic_skill"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $skill_cancel = self.$modal.find("#biz__skill_cancle"),
                    $skill_selection = self.$modal.find("#skill_count_selection"),
                    $sub_data = self.$modal.find("#bzitech_skill_btn");
                $skill_selection.on("change", function() {
                    skillcount = parseInt($skill_selection.find(":selected").val());
                    if (skillcount == 0) {
                        alert("Please enter proper data")
                    } else {
                        var i;
                        for (i = 2; i <= 4; i++) {
                            if (i <= skillcount) {
                                self.$modal.find("#name_hided_" + i).removeClass("hidden");
                                self.$modal.find("#number_hided_" + i).removeClass("hidden");
                            } else {
                                self.$modal.find("#name_hided_" + i).addClass("hidden");
                                self.$modal.find("#number_hided_" + i).addClass("hidden");
                            }
                        }

                    }
                });
                $sub_data.on('click', function() {
                    var i
                    var numbers = []
                    var name_error = []
                    for (i = 1; i <= 4; i++) {
                        if (self.$modal.find("#number_hided_" + i).attr('class') == 'form-control' & (self.$modal.find("#number_hided_" + i).val() < 1 || self.$modal.find("#number_hided_" + i) > 100)) {
                            numbers.push("error")
                        }
                        if (self.$modal.find("#name_hided_" + i).attr('class') == 'form-control' & self.$modal.find("#name_hided_" + i).val() == '') {
                            name_error.push("error")
                        }
                    }
                    if (name_error.length == 0) {
                        if (numbers.length == 0 & parseInt(self.$modal.find("input[name='wordpress']").val()) <= 100 & parseInt(self.$modal.find("input[name='html5']").val()) <= 100 & parseInt(self.$modal.find("input[name='css3']").val()) <= 100 & parseInt(self.$modal.find("input[name='photoshop']").val()) <= 100) {
                            if (isNaN(parseInt(self.$modal.find("input[name='wordpress']").val())) == false & isNaN(parseInt(self.$modal.find("input[name='html5']").val())) == false & isNaN(parseInt(self.$modal.find("input[name='css3']").val())) == false & isNaN(parseInt(self.$modal.find("input[name='photoshop']").val())) == false) {
                                self.$target.attr('data-skill-number-1', parseInt(self.$modal.find("input[name='wordpress']").val()))
                                self.$target.attr('data-skill-number-2', parseInt(self.$modal.find("input[name='html5']").val()))
                                self.$target.attr('data-skill-number-3', parseInt(self.$modal.find("input[name='css3']").val()))
                                self.$target.attr('data-skill-number-4', parseInt(self.$modal.find("input[name='photoshop']").val()))
                                self.$target.attr('data-skill-name-1', self.$modal.find("input[name='label_wordpress']").val() || "wordpress")
                                self.$target.attr('data-skill-name-2', self.$modal.find("input[name='label_html5']").val() || "html5")
                                self.$target.attr('data-skill-name-3', self.$modal.find("input[name='label_css3']").val() || "css3")
                                self.$target.attr('data-skill-name-4', self.$modal.find("input[name='label_photoshop']").val() || "photoshop")
                                self.$modal.modal('hide');
                            } else {
                                alert("Only numbers are allowed ")
                            }
                        } else {
                            alert("Values should be in range of 1 to 100")
                        }
                    } else {
                        alert("Title can not be blak")
                    }
                })
                $skill_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                    self.$modal.modal('hide');
                })

            }
        }

    });

    website.snippet.options.theme_crafito_news1_js = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.crafito_newsone_slider').empty();
            if (!editMode) {
                self.$el.find(".crafito_newsone_slider").on("click", _.bind(self.theme_crafito_newsone_slider, self));
            }
        },
        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.theme_crafito_newsone_slider()) {
                this.theme_crafito_newsone_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },
        on_remove: function() {
            this._super();
        },
        clean_for_save: function() {
            $('.crafito_newsone_slider').empty();
        },
        theme_crafito_newsone_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#blog_slider_type"),
                    $newonecancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                openerp.jsonRpc('/theme_crafito/blog_get_options', 'call', {}).done(function(res) {
                    $('#blog_slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-newsone-slider-type', $slider_type.val());
                    if ($('select#blog_slider_type').find(":selected").text()) {
                        type = _t($('select#blog_slider_type').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $newonecancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                    self.$modal.modal('hide');
                })
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_news2_js = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.crafito_newstwo_slider').empty();
            if (!editMode) {
                self.$el.find(".crafito_newstwo_slider").on("click", _.bind(self.theme_crafito_newstwo_slider, self));
            }
        },
        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.theme_crafito_newstwo_slider()) {
                this.theme_crafito_newstwo_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        on_remove: function() {
            this._super();
        },

        clean_for_save: function() {
            $('.crafito_newstwo_slider').empty();
        },

        theme_crafito_newstwo_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#blog_slider_type"),
                    $newonecancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                openerp.jsonRpc('/theme_crafito/blog_get_options', 'call', {}).done(function(res) {
                    $('#blog_slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-newstwo-slider-type', $slider_type.val());
                    if ($('select#blog_slider_type').find(":selected").text()) {
                        type = _t($('select#blog_slider_type').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $newonecancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                    self.$modal.modal('hide');
                })
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_hardware_blog_snippet = website.snippet.Option.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.theme_crafito_new_blog').empty();
            if (!editMode) {
                self.$el.find(".theme_crafito_new_blog").on("click", _.bind(self.theme_crafito_new_blog_function, self));
            }
        },
        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.theme_crafito_new_blog_function()) {
                this.theme_crafito_new_blog_function().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.theme_crafito_new_blog').empty();
        },

        theme_crafito_new_blog_function: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(openerp.qweb.render("theme_crafito.crafito_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#blog_slider_type"),
                    $blognewcancel = self.$modal.find("#cancel"),
                    $blognewsub_data = self.$modal.find("#blog_sub_data");

                openerp.jsonRpc('/theme_crafito/blog_get_options', 'call', {}).done(function(res) {
                    $('#blog_slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $blognewsub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-hardware-newblog-slider-type', $slider_type.val());
                    self.$target.attr('data-hardware-newblog-slider-id', 'blog-myowl' + $slider_type.val());
                    if ($('select#blog_slider_type').find(":selected").text()) {
                        type = _t($('select#blog_slider_type').find(":selected").text());
                    } else {
                        type = _t("Blog Post");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blognewcancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                    self.$modal.modal('hide');
                })
            } else {
                return;
            }
        },
    });

    website.snippet.options.theme_crafito_faq_three_tabing = website.snippet.Option.extend({
        start: function() {
            var self = this;
            self.$el.find(".js_faq_add").on('click', _.bind(self.add_new_tab, self));
            self.$el.find(".js_faq_remove").on("click", _.bind(self._remove_current_tab, self));
            self._super();
        },
        drop_and_build_snippet: function() {
            var self = this;
            var unique_id = Math.random().toString(36).substring(7);
            self.$target.find('.nav-tabs > li > a').each(function() {
                var item = $(this);
                var href = item.attr('href');
                item.attr('href', String(href) + String(unique_id));
                item.attr('data-cke-saved-href', String(item.attr('data-cke-saved-href')) + String(unique_id));
                item.attr('aria-controls', String(item.attr('aria-controls')) + String(unique_id));
                var pane = self.$target.find('.tab-content > div' + href);
                pane.attr('id', String(pane.attr('id')) + String(unique_id))
            });
        },
        add_new_tab: function() {
            var self = this;
            var tabs = self.$target.find('.nav-tabs');
            var panes = self.$target.find('.tab-content');
            var newid = Math.random().toString(36).substring(7);

            var li = $('<li/>', {
                'role': 'presentation',
                'class': 'active'
            });
            $('<a/>', {
                'href': '#' + newid,
                'aria-controls': 'tab1',
                'role': 'tab',
                'data-toggle': 'tab',
                'text': 'New'
            }).appendTo(li);

            var div = $("<div id='" + newid + "' class='oe_structure oe_empty tab-pane active' role='tabpanel'><section class='mb16'><div class='container'><div class='row'><div class='col-md-12 mb16 mt16'><p>A great way to catch your reader's attention is to tell astory. Everything you consider writing can be told as astory.</p></div><div class='col-md-12 mb16 mt16'><p><b>Great stories have personality.</b> Consider telling a great story that provides personality. Writing a story withpersonality for potential clients will asist with making a relationship connection. This shows up in small quirks like word choices or phrases. Write from your point of view, not from someone else's experience.</p></div></div></div></section></div>")

            li.insertBefore(tabs.find('.active').removeClass('active'));
            div.insertBefore(panes.find('.active').removeClass('active'));
        },
        remove_current_tab: function() {
            var self = this;
            var tabs = self.$target.find('.nav-tabs');
            var panes = self.$target.find('.tab-content');

            if (tabs.find('> li[role="presentation"]').size() > 1 && panes.find('> div[role="tabpanel"]').size() > 1) {
                tabs.find('.active').remove();
                panes.find('.active').remove();
                tabs.find('> li[role="presentation"]:first').addClass('active');
                panes.find('> div[role="tabpanel"]:first').addClass('active');
            }
        },
    });

    website.snippet.options.theme_crafito_faq_one_tabing = website.snippet.Option.extend({
        start: function() {
            var self = this;
            self.$el.find(".js_faq_one_add").on("click", _.bind(self.add_new_tab, self));
            self.$el.find(".js_faq_one_remove").on("click", _.bind(self.remove_current_tab, self));
            self._super();
        },
        drop_and_build_snippet: function() {
            var self = this;
            var unique_id = Math.random().toString(36).substring(7);
            self.$target.find('.nav-tabs > li > a').each(function() {
                var item = $(this);
                var href = item.attr('href');
                item.attr('href', String(href) + String(unique_id));
                item.attr('data-cke-saved-href', String(item.attr('data-cke-saved-href')) + String(unique_id));
                item.attr('aria-controls', String(item.attr('aria-controls')) + String(unique_id));
                var pane = self.$target.find('.tab-content > div' + href);
                pane.attr('id', String(pane.attr('id')) + String(unique_id))
            });
        },
        add_new_tab: function() {
            var self = this;
            var tabs = self.$target.find('.nav-tabs');
            var panes = self.$target.find('.tab-content');
            var newid = Math.random().toString(36).substring(7);

            var li = $('<li/>', {
                'role': 'presentation',
                'class': 'active'
            });
            $('<a/>', {
                'href': '#' + newid,
                'aria-controls': 'tab1',
                'role': 'tab',
                'data-toggle': 'tab',
                'text': 'New'
            }).appendTo(li);

            var div = $("<div id='" + newid + "' class='oe_structure oe_empty tab-pane active' role='tabpanel'><section class='mb16'><div class='container'><div class='row'><div class='col-md-12 mb16 mt16'><p>A great way to catch your reader's attention is to tell astory. Everything you consider writing can be told as astory.</p></div><div class='col-md-12 mb16 mt16'><p><b>Great stories have personality.</b> Consider telling a great story that provides personality. Writing a story withpersonality for potential clients will asist with making a relationship connection. This shows up in small quirks like word choices or phrases. Write from your point of view, not from someone else's experience.</p></div></div></div></section></div>")

            li.insertBefore(tabs.find('.active').removeClass('active'));
            div.insertBefore(panes.find('.active').removeClass('active'));
        },
        remove_current_tab: function() {
            var self = this;
            var tabs = self.$target.find('.nav-tabs');
            var panes = self.$target.find('.tab-content');

            if (tabs.find('> li[role="presentation"]').size() > 1 && panes.find('> div[role="tabpanel"]').size() > 1) {
                tabs.find('.active').remove();
                panes.find('.active').remove();
                tabs.find('> li[role="presentation"]:first').addClass('active');
                panes.find('> div[role="tabpanel"]:first').addClass('active');
            }
        },
    });

    website.snippet.options.collapse = website.snippet.Option.extend({
        start: function() {
            var self = this;
            this._super();
            this.$target.on('shown.bs.collapse hidden.bs.collapse', '[role="tabpanel"]', function() {
                self.buildingBlock.cover_target(self.$overlay, self.$target);
            });
        },
        create_ids: function($target) {
            var time = new Date().getTime();
            var $tab = $target.find('[data-toggle="collapse"]');

            // link to the parent group

            var $tablist = $target.closest('.panel-group');
            var tablist_id = $tablist.attr("id");
            if (!tablist_id) {
                tablist_id = "myCollapse" + time;
                $tablist.attr("id", tablist_id);
            }
            $tab.attr('data-parent', "#" + tablist_id);
            $tab.data('parent', "#" + tablist_id);

            // link to the collapse

            var $panel = $target.find('.panel-collapse');
            var panel_id = $panel.attr("id");
            if (!panel_id) {
                while ($('#' + (panel_id = "myCollapseTab" + time)).length) {
                    time++;
                }
                $panel.attr("id", panel_id);
            }
            $tab.attr('data-target', "#" + panel_id);
            $tab.data('target', "#" + panel_id);
        },
        drop_and_build_snippet: function() {
            this._super();
            this.create_ids(this.$target);
        },
        on_clone: function($clone) {
            this._super();
            this.create_ids($clone);
        },
        on_move: function() {
            this._super();
            this.create_ids(this.$target);
            var $panel = this.$target.find('.panel-collapse').removeData('bs.collapse');
            if ($panel.attr('aria-expanded') === 'true') {
                $panel.closest('.panel-group').find('.panel-collapse[aria-expanded="true"]')
                    .filter(function() {
                        return this !== $panel[0];
                    })
                    .collapse('hide')
                    .one('hidden.bs.collapse', function() {
                        $panel.trigger('shown.bs.collapse');
                    });
            }
        }
    });

})();