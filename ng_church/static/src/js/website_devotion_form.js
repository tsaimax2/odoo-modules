odoo.define('ng_church.website_devotion_form', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    $(document).on('click',"#submit_button", function() {
        var name = $("#name").val();
        var phone = $("#phone").val();
        var email = $("#email").val();
        var amount_txt = $("#devotion_amount").val();
        var type = $('.check_box_devotion_type:checkbox:checked');
        var note = $( "#devotion_note" ).val();
        var amount = +(amount_txt);
        //alert (amount);
        
        var list_type = [];
        var number = type.length;        
    
        for (var i=0; i<(type.length); i++) {
            var k = {i : type[i].attributes['collection-id'].value};
            var type_value = type[i].attributes['collection-id'].value;
            list_type.push(k);
        }
        

        if (name == "" || phone == "" || email == "" || amount =="" || list_type.length == 0) {            
            alert("All above fields are mandatory");
        } else {
            if (list_type.length > 1) {
                alert("Select only one type, for mutliple devotions, please fill another form");
            } else {
                var devotion_record = {'name': name, 'phone': phone, 'email': email, 'amount': amount, 'type_value': type_value, 'note': note};
                    $.ajax({
                        url: "/page/devotion_details",
                        type: "POST",
                        dataType: "json",
                        data: devotion_record,
                        type: 'POST',
                        success: function( data ) {
                            window.location.href = "/page/ng_church/church_devotion_thank_you";
                        },
                        error: function (error) {
                            alert('error: ' + error);
                        }
                    });
            }
        }
    });
    
});