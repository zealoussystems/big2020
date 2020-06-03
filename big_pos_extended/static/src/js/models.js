odoo.define('big_pos_extended.models', function (require) {
"use strict";

    var core = require('web.core');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    var _t = core._t;

    models.load_domains = function(model_name, domain){
       var tmodels = models.PosModel.prototype.models;
       for(var i=0;i< tmodels.length;i++){
           var tmodel = tmodels[i];
           if(tmodel.model == model_name){
               tmodel.domain = domain;
           }
       }
    }

    models.load_fields('res.partner', ['is_pos_customer','register_qty', 'remaining_qty',
    'cid_number','license_number']);
    models.load_fields('product.product', ['is_refile_lpg_product']);

    models.load_domains('res.partner', [['is_pos_customer','=',true]]);

    models.PosModel = models.PosModel.extend({
        prepare_new_partners_domain: function(){
            return [['write_date','>', this.db.get_partner_write_date()], ['is_pos_customer','=',true]];
        },
    });

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            _super_Order.initialize.apply(this, arguments);
            this.is_new_connection = false
        },
        set_is_new_connection: function(is_new_connection){
            this.is_new_connection = is_new_connection;
        },
        get_is_new_connection: function(){
            return this.is_new_connection;
        },
        export_as_JSON: function() {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            json.is_new_connection = this.get_is_new_connection();
            return json;
        }
    });

    screens.ActionpadWidget.include({
        check_connection: function(client,total_qty){
            var self = this;
            var order = self.pos.get_order();
            if(client){
                var register_qty = client.register_qty;
                if(total_qty > register_qty){
                   self.gui.show_popup('alert',{
                        'title': _t('Warning !!'),
                        'body': _t("We can't sale qty greater than register qty " + register_qty ),
                    })
                   return true;
                }
                var remaining_qty = client.remaining_qty;
                var connection_list = false;
                if(remaining_qty == 0){
                    self.gui.show_screen('payment');
                }else if((register_qty - remaining_qty) == 0){
                   connection_list = [
                       {'label': 'New Customer?','item':'new_connection'}
                   ]
                }else if((register_qty - remaining_qty) > 0){
                    connection_list = [
                       {'label': 'New Customer?','item':'new_connection'},
                       {'label': 'Existing Customer?','item':'existing_connection'}
                   ]
                }
                if (connection_list){
                    self.gui.show_popup('selection',{
                        title: _t('Select Options'),
                        list: connection_list,
                        confirm: function (connection) {
                            if(connection == 'new_connection'){
                                if(total_qty > remaining_qty){
                                   self.gui.show_popup('alert',{
                                        'title': _t('Warning !!'),
                                        'body': _t('Only ' + remaining_qty + ' qty require for new customer so please set ' + remaining_qty +' qty.'),
                                    })
                                   return true;
                                }
                                order.set_is_new_connection(true)
                            }else{
                                if(total_qty > (register_qty -remaining_qty)){
                                   self.gui.show_popup('alert',{
                                        'title': _t('Warning !!'),
                                        'body': _t('Only ' + (register_qty -remaining_qty) + ' qty require for existing customer so please set ' + (register_qty -remaining_qty) +' qty.'),
                                    })
                                   return true;
                                }
                                order.set_is_new_connection(false)
                            }
                            self.gui.show_screen('payment');
                        },
                    });
                }
            }
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').off('click').on('click',function(){
                var order = self.pos.get_order();
                var client = order.get_client();
                var total_qty = 0;
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    if(line && line.product.is_refile_lpg_product){
                        total_qty = total_qty + line.get_quantity();
                    }
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            if(client){
                                self.check_connection(client,total_qty);
                            }else{
                                self.gui.show_screen('clientlist');
                            }
                        },
                    });
                }else{
                    if(client){
                        self.check_connection(client,total_qty);
                    }else{
                        self.gui.show_screen('clientlist');
                    }
                }
            });
        }
    });

});