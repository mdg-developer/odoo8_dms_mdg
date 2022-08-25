openerp.web_iframe = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var web_iframe = session.web_iframe;

    session.web.client_actions.add('web_iframe.iframe', 'session.web_iframe.iframe');
    web_iframe.iframe = session.web.Widget.extend({
        template: 'web_iframe.iframe',

        /**
         * @param {Object} parent parent
         * @param {Object} [options]
         * @param {Array} [options.domain] domain on the Wall
         * @param {Object} [options.context] context, is an object. It should
         *      contain default_model, default_res_id, to give it to the threads.
         */
        init: function (parent, action) {
            this._super(parent, action);
            this.action = _.clone(action);
            this.action.params = _.extend({
                'link': 'https://yelizariev.github.io/',
            }, this.action.params);
        },
        start: function() {
            this._super();
            var team_data = '';
            var self = this
            openerp.jsonRpc("/user_sales_team", 'call', {
                'user_id': this.session.uid
                })
            .then(function (data) {
                if(data){
                    console.log("###########")
                    team_data = data;
                    self.$el.find('iframe').css({height: '100%', width: '100%', border: 0});
                    self.$el.find('iframe').attr({src: self.action.params.link+'&p.team='+ team_data});
                    self.$el.find('iframe').on("load", self.bind_events.bind(self));
                }
//                return this._super();
            });

        },
        bind_events: function(){
            //this.$el.find('iframe').contents().click(this.iframe_clicked.bind(this));
        },
        iframe_clicked: function(e){
        }
    });
};
