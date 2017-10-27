(function() {
    'use strict';


    var website = openerp.website;
    website.openerp_website = {};
    var _t = openerp._t;

    function getTimeRemaining(formated_date) {
        var t = Date.parse(formated_date) - Date.parse(new Date());
        var seconds = Math.floor((t / 1000) % 60);
        var minutes = Math.floor((t / 1000 / 60) % 60);
        var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
        var days = Math.floor(t / (1000 * 60 * 60 * 24));
        return {
            'total': t,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        };
    }

    function initializeClock(id, endtime) {
        var clock = $(id)
        var test = getTimeRemaining(endtime);
        if (test.total > 0) {
            var timeinterval = setInterval(function() {
                var t = getTimeRemaining(endtime);
                clock.find('.days').text(t.days);
                clock.find('.hours').text(t.hours);
                clock.find('.minutes').text(t.minutes);
                clock.find('.seconds').text(t.seconds);
                if (t.total <= 0) {
                    clearInterval(timeinterval);
                }
            }, 1000);

        }
    }

    website.snippet.animationRegistry.theme_crafito_blog_custom_snippet = website.snippet.Animation.extend({
        selector: ".crafito_blog_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_blog_snippet').empty();
                var blog_name = _t("Blog Slider")
                $('#theme_crafito_custom_blog_snippet').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + blog_name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-blog-slider-type');
                $.get("/theme_crafito/blog_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-blog-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".crafito_blog_slider").removeClass('hidden');
                        openerp.jsonRpc('/theme_crafito/blog_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {
                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: res.counts,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    }
                                },
                            });
                        });
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.s_theme_crafito_client_slider_snippet = website.snippet.Animation.extend({
        selector: ".our-client-slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_client_slider').empty();
                var client_name = _t("Client Slider")
                $('#theme_crafito_custom_client_slider').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + client_name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                $.get("/theme_crafito/get_clients_dynamically_slider", {}).done(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $('div#crafito-client-slider').owlCarousel({
                            loop: false,
                            margin: 10,
                            responsiveClass: true,
                            nav: false,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 2,
                                },
                                768: {
                                    items: 4,
                                },
                                1000: {
                                    items: 6,
                                },
                                1500: {
                                    items: 6,
                                }
                            }
                        });
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_multi_cat_custom_snippet = website.snippet.Animation.extend({
        selector: ".oe_multi_category_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_multi_product_tab_slider').empty();
                var name = _t("Multi Product Tabs Slider")
                $('#theme_crafito_custom_multi_product_tab_slider').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-multi-cat-slider-type');
                $.get("/theme_crafito/product_multi_get_dynamic_slider", {
                    'slider-type': slider_type || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_multi_category_slider").removeClass('hidden');
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_coming_soon_mode_one = website.snippet.Animation.extend({
        selector: ".biztech_coming_soon_mode_one",
        start: function(editable_mode) {
            var self = this;
            if (!editable_mode) {
                var formated_date
                var exit_date = self.$target.attr('data-blog-updated-date-time')
                $.get("/biztech_comming_soon/soon_data", {}).then(function(data) {
                    self.$target.empty().append(data);
                })

                var $divcount = self.$target
                var x = initializeClock($divcount, exit_date)

            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_coming_soon_mode_two = website.snippet.Animation.extend({
        selector: ".biztech_coming_soon_mode_two",
        start: function(editable_mode) {
            var self = this;
            if (!editable_mode) {
                var formated_date
                var maintwo_date = self.$target.attr('data-cm2-updated-date-time')
                $.get("/biztech_comming_soon_two/two_soon_data", {}).then(function(data) {
                    self.$target.empty().append(data);
                })


                var $divcount_maintwo = self.$target
                var main2 = initializeClock($divcount_maintwo, maintwo_date)

            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_category_slider = website.snippet.Animation.extend({
        selector: ".oe_cat_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_category_slider').empty();
                var cat_name = _t("Category Slider")
                $('#theme_crafito_custom_category_slider').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + cat_name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_id = self.$target.attr('data-cat-slider-id');
                $.get("/theme_crafito/category_get_dynamic_slider", {
                    'slider-id': self.$target.attr('data-cat-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_cat_slider").removeClass('hidden');

                        openerp.jsonRpc('/theme_crafito/category_image_effect_config', 'call', {
                            'slider_id': slider_id
                        }).done(function(res) {
                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    },
                                },
                            });
                        });
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_product_slider = website.snippet.Animation.extend({

        selector: ".oe_prod_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_product_slider').empty();
                var prod_name = _t("Products Slider")
                $('#theme_crafito_custom_product_slider').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + prod_name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_id = self.$target.attr('data-prod-slider-id');
                $.get("/theme_crafito/product_get_dynamic_slider", {
                    'slider-id': self.$target.attr('data-prod-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_prod_slider").removeClass('hidden');

                        openerp.jsonRpc('/theme_crafito/product_image_effect_config', 'call', {
                            'slider_id': slider_id
                        }).done(function(res) {
                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    },
                                },
                            });
                        });
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_featured_product_slider = website.snippet.Animation.extend({

        selector: ".oe_featured_prod_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_carfito_custom_featured_product_theme').empty();
                var fea_prod_name = _t("Featured Products Slider")
                $('#theme_carfito_custom_featured_product_theme').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + fea_prod_name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_id = self.$target.attr('data-featured_prod-slider-id');
                $.get("/theme_crafito/featured_product_get_dynamic_slider", {
                    'slider-id': self.$target.attr('data-featured-prod-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_featured_prod_slider").removeClass('hidden');
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.biztech_new_theme_fact_sheet_jsselector = website.snippet.Animation.extend({
        selector: ".biztech_fact_sheet",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                self.$target.find('.counter-container').empty();
            }
            if (!editable_mode) {
                var years = self.$target.attr('data-fact-number-1')
                var clients = self.$target.attr('data-fact-number-2')
                var projects = self.$target.attr('data-fact-number-3')
                var awords = self.$target.attr('data-fact-number-4')
                var total = 0;
                var i;
                for (i = 1; i <= 4; i++) {
                    if (parseInt(self.$target.attr('data-fact-number-' + i)) > 0) {
                        total = total + 1
                    }
                }
                $.get('/biztech_fact_model_data/fact_data', {}).then(function(data) {
                    self.$target.empty().append(data);
                    if (parseInt(years) > 0) {
                        self.$target.find("span#custom_business").html(years)
                        self.$target.find("p#custom_label_business").html(self.$target.attr('data-fact-name-1'))
                        self.$target.find("i#business_icon").attr('class', self.$target.attr('data-fact-icon-1'))
                    }
                    if (parseInt(clients) > 0) {
                        self.$target.find("span#custom_Clients").html(clients)
                        self.$target.find("p#custom_label_Clients").html(self.$target.attr('data-fact-name-2'))
                        self.$target.find("i#client_icon").attr('class', self.$target.attr('data-fact-icon-2'))
                    }
                    if (parseInt(projects) > 0) {
                        self.$target.find("span#custom_Projects").html(projects)
                        self.$target.find("p#custom_label_Projects").html(self.$target.attr('data-fact-name-3'))
                        self.$target.find("i#project_icon").attr('class', self.$target.attr('data-fact-icon-3'))
                    }
                    if (parseInt(awords) > 0) {
                        self.$target.find("span#custom_Awards").html(awords)
                        self.$target.find("p#custom_label_Awards").html(self.$target.attr('data-fact-name-4'))
                        self.$target.find("i#awards_icon").attr('class', self.$target.attr('data-fact-icon-4'))
                    }

                    for (i = 1; i <= 4; i++) {
                        if (total == 1 & parseInt(self.$target.find("div#counter-inner-content-" + i + " span").html()) > 0) {
                            self.$target.find("div#counter-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#counter-inner-content-" + i).attr('class', "col-sm-12 counter-inner-content")
                        }
                        if (total == 2 & parseInt(self.$target.find("div#counter-inner-content-" + i + " span").html()) > 0) {
                            self.$target.find("div#counter-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#counter-inner-content-" + i).attr('class', "col-sm-6 counter-inner-content")
                        }
                        if (total == 3 & parseInt(self.$target.find("div#counter-inner-content-" + i + " span").html()) > 0) {
                            self.$target.find("div#counter-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#counter-inner-content-" + i).attr('class', "col-sm-4 counter-inner-content")
                        }
                        if (total == 4 & parseInt(self.$target.find("div#counter-inner-content-" + i + " span").html()) > 0) {
                            self.$target.find("div#counter-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#counter-inner-content-" + i).attr('class', "col-sm-3 counter-inner-content")
                        }
                    }
                    var $counter = $(self.$target.find('.counter'))
                    $counter.counterUp({
                        delay: 10,
                        time: 1000
                    });
                });
            }
        }
    });

    website.snippet.animationRegistry.biztech_new_theme_skill_jsselector = website.snippet.Animation.extend({
        selector: ".biztech_new_theme_skill",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                self.$target.find('.skill-counter').empty();
            }
            if (!editable_mode) {
                var total = 0;
                var i;
                for (i = 1; i <= 4; i++) {
                    if (parseInt(self.$target.attr('data-skill-number-' + i)) > 0) {
                        total = total + 1
                    }
                }
                $.get('/biztech_skill_model_data/skill_data', {}).then(function(data) {
                    self.$target.empty().append(data);
                    if (parseInt(self.$target.attr('data-skill-number-1')) > 0) {
                        self.$target.find("div.skill_graph_1").html(self.$target.attr('data-skill-number-1'))
                        self.$target.find("span#skill1").html("<h4>" + self.$target.attr('data-skill-name-1') + "</h4>")
                    }
                    if (parseInt(self.$target.attr('data-skill-number-2')) > 0) {
                        self.$target.find("div.skill_graph_2").html(self.$target.attr('data-skill-number-2'))
                        self.$target.find("span#skill2").html("<h4>" + self.$target.attr('data-skill-name-2') + "</h4>")
                    }
                    if (parseInt(self.$target.attr('data-skill-number-3')) > 0) {

                        self.$target.find("div.skill_graph_3").html(self.$target.attr('data-skill-number-3'))
                        self.$target.find("span#skill3").html("<h4>" + self.$target.attr('data-skill-name-3') + "</h4>")

                    }
                    if (parseInt(self.$target.attr('data-skill-number-4')) > 0) {

                        self.$target.find("div.skill_graph_4").html(self.$target.attr('data-skill-number-4'))
                        self.$target.find("span#skill4").html("<h4>" + self.$target.attr('data-skill-name-4') + "</h4>")
                    }

                    for (i = 1; i <= 4; i++) {
                        if (total == 1 & parseInt(self.$target.find("div#skill-inner-content-" + i + " div.custom_percentage").html()) > 0) {
                            self.$target.find("div#skill-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#skill-inner-content-" + i).attr('class', "col-md-12 counter-inner-content")
                        }
                        if (total == 2 & parseInt(self.$target.find("div#skill-inner-content-" + i + " div.custom_percentage").html()) > 0) {
                            self.$target.find("div#skill-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#skill-inner-content-" + i).attr('class', "col-md-6 counter-inner-content")
                        }
                        if (total == 3 & parseInt(self.$target.find("div#skill-inner-content-" + i + " div.custom_percentage").html()) > 0) {
                            self.$target.find("div#skill-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#skill-inner-content-" + i).attr('class', "col-md-4 counter-inner-content")
                        }
                        if (total == 4 & parseInt(self.$target.find("div#skill-inner-content-" + i + " div.custom_percentage").html()) > 0) {
                            self.$target.find("div#skill-inner-content-" + i).removeClass("hidden")
                            self.$target.find("div#skill-inner-content-" + i).attr('class', "col-md-3 counter-inner-content")
                        }
                    }

                    var waypoints = self.$target.find('#skill-counter').waypoint({
                        offset: '75%',
                        triggerOnce: true,
                        handler: function(direction) {
                            self.$target.find('#skill_graph_1').circleGraphic({
                                'color': '#3a424c'
                            });
                            self.$target.find('#skill_graph_2').circleGraphic({
                                'color': '#3a424c'
                            });
                            self.$target.find('#skill_graph_3').circleGraphic({
                                'color': '#3a424c'
                            });
                            self.$target.find('#skill_graph_4').circleGraphic({
                                'color': '#3a424c'
                            });
                        },
                    })
                });
            }
        }
    });

    website.snippet.animationRegistry.s_biztech_new_theme_team_two = website.snippet.Animation.extend({
        selector: ".team",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_second_team').empty();
                $('#theme_crafito_custom_second_team').empty().append('<div class="block-title" contentEditable="false">\
                    <h3 class="fancy">Team 2</h3>\
                </div>');
            }
            if (!editable_mode) {
                $.get("/biztech_emp_data/employee_data", {}).then(function(data) {
                    self.$target.empty();
                    self.$target.append(data);
                })
            }
        }
    });

    website.snippet.animationRegistry.s_biztech_new_theme_team_one = website.snippet.Animation.extend({
        selector: ".column-3-team",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_colthree_team').empty();
                $('#theme_crafito_custom_colthree_team').empty().append('<div class="block-title" contentEditable="false">\
                    <h3 class="fancy">Team 1</h3>\
                </div>');
            }
            if (!editable_mode) {
                $.get("/biztech_emp_data_one/employee_data", {}).then(function(data) {
                    self.$target.empty();
                    self.$target.append(data);
                })
            }
        }
    });

    website.snippet.animationRegistry.s_biztech_new_theme_team_three = website.snippet.Animation.extend({
        selector: ".new-1-column-team",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_three_custom_team').empty();
                $('#theme_crafito_three_custom_team').empty().append('<div class="block-title" contentEditable="false">\
                    <h3 class="fancy" style="color:white;">Team 3</h3>\
                </div>');
            }
            if (!editable_mode) {
                $.get("/biztech_emp_data_three/employee_data", {}).then(function(data) {
                    self.$target.empty();
                    self.$target.append(data);
                    $('div#our_team_3').owlCarousel({
                        center: true,
                        items: 2,
                        loop: true,
                        margin: 10,
                        responsive: {
                            0: {
                                items: 1,
                            },
                            1000: {
                                items: 2,
                            }
                        }
                    });

                })
            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_news1_js = website.snippet.Animation.extend({
        selector: ".crafito_newsone_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_news1').empty();
                $('#theme_crafito_custom_news1').empty().append('<div class="block-title" contentEditable="false">\
                    <h3 class="fancy">News1</h3>\
                </div>');
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-newsone-slider-type');
                $.get("/theme_crafito/newsone_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-newsone-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".crafito_newsone_slider").removeClass('hidden');
                    }
                });
            }
        }
    });


    website.snippet.animationRegistry.theme_crafito_news2_js = website.snippet.Animation.extend({
        selector: ".crafito_newstwo_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_second_news').empty();
                var news_two_name = _t("News 2")
                $('#theme_crafito_custom_second_news').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + news_two_name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-newstwo-slider-type');
                $.get("/theme_crafito/newstwo_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-newstwo-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".crafito_newstwo_slider").removeClass('hidden');
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.theme_crafito_hardware_blog_snippet = website.snippet.Animation.extend({
        selector: ".theme_crafito_new_blog",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_hardware_blog_inner_containt').empty();
                $('#theme_crafito_hardware_blog_inner_containt').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">News3</h3>\
                                                    </div>\
                                                </div>')

            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-hardware-newblog-slider-type');
                $.get("/theme_crafito/theme_new_hardware_blog", {
                    'slider-type': self.$target.attr('data-hardware-newblog-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".theme_crafito_new_blog").removeClass('hidden');
                    }
                });
            }
        }
    });

    website.snippet.animationRegistry.s_theme_crafito_events = website.snippet.Animation.extend({
        selector: ".event_category",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_crafito_custom_event_category').empty();
                $('#theme_crafito_custom_event_category').empty().append('<div class="block-title" contentEditable="false">' +
                    '<h3>Events</h3>' +
                    '</div>');

            }
            if (!editable_mode) {
                $.get("/theme_crafito/event_slider/get_data", {}).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                    }
                });
                var tabs = self.$target.find('.nav-tabs');
                var panes = self.$target.find('.tab-content');
                tabs.find('> li[role="presentation"]').first().addClass('active');
                panes.find('> div[role="tabpanel"]:first').addClass('active');

            }
        }
    });



})();