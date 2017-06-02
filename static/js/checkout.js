require(['backbone','underscore','toastr','xml2json','payment_ui','stripe'],function(Backbone,_,toastr,X2JS){
    $(function(){
        Checkout = {
            Models : {},
            Views : {},
            Events:{},
        }
        $(document).ready(function(){
            var order_total = $("td#order_total");
            var shipping_total = $("td#shipping_total");
            var csrftoken = getCookie('csrftoken');
            var payment_box = $("div#payment_box");
            var left_side = $("div#left_side");
            var address_defaults = {
                    'name':'',
                    'street':'',
                    'is_company':false,
                    'street2':'',
                    'country_id':false,
                    'zip':'',
                    'state':'',
                    'email':''
            }
            Checkout.Events.Checkout = _.extend({},Backbone.Events)
            Checkout.Models.Address = Backbone.Model.extend({
                defaults:address_defaults,
            })
            var signin_box = 
            _.template('\
                    <div class="card card-container">\
                        <!-- <img class="profile-img-card" src="//lh3.googleusercontent.com/-6V8xOA6M7BA/AAAAAAAAAAI/AAAAAAAAAAA/rzlHcD0KYwo/photo.jpg?sz=120" alt="" /> -->\
                        <img id="profile-img" class="profile-img-card" src="//ssl.gstatic.com/accounts/ui/avatar_2x.png" />\
                        <p id="profile-name" class="profile-name-card"></p>\
                        <form class="form-signin">\
                            <span id="reauth-email" class="reauth-email"></span>\
                            <input type="email" name="username" id="inputEmail" class="form-control" placeholder="Email address" required autofocus>\
                            <input type="password" id="inputPassword" class="form-control" name="password" placeholder="Password" required>\
                            <div id="remember" class="checkbox">\
                                <label>\
                                    <input type="checkbox" value="remember-me"> Remember me\
                                </label>\
                            </div>\
                            <button class="btn btn-lg btn-primary btn-block btn-signin" type="submit">Sign in</button>\
                        </form><!-- /form -->\
                        <button class="btn btn-lg btn-success btn-block btn-signin" id = "checkout_as_guest" type="submit">Checkout as Guest</button>\
                        <button href="#forgot-password-popup" class="forgot-password btn-link">\
                            Forgot password?\
                        </button>\
                    </div><!-- /card-container -->\
            ')
            var checkout_box =
            _.template('\
            <div class="board" style = "height:100%;">\
                <!-- <h2>Welcome to IGHALO!<sup>™</sup></h2>-->\
                    <div class="board-inner">\
	                    <ul class="nav nav-tabs" id="myTab">\
		                    <div class="liner"></div>\
		                    <li class="active">\
		                    	<a href="#shipping" data-toggle="tab" title="Shipping Information">\
				                    <span class="round-tabs two">\
				                        <i class="glyphicon glyphicon-user"></i>\
				                    </span>\
					           </a>\
		                	</li>\
		                 	<li>\
			                 	<a href="#billing" data-toggle="tab" title="Billing Information">\
				                    <span class="round-tabs three">\
				                          <i class="glyphicon glyphicon-credit-card"></i>\
				                    </span>\
			                    </a>\
		                     </li>\
		                    <li><a href="#doner" data-toggle="tab" title="completed">\
		                        <span class="round-tabs five">\
		                              <i class="glyphicon glyphicon-ok"></i>\
		                        </span></a>\
		                    </li>\
	                    </ul>\
                    </div>\
                    <div class="tab-content">\
                    	<div class="tab-pane fade in active" id="shipping">\
                        </div>\
	                    <div class="tab-pane fade" id="billing">\
	                    </div>\
	                    <div class="tab-pane fade" id="doner">\
					  		<div class="text-center">\
					    		<i class="img-intro icon-checkmark-circle"></i>\
							</div>\
						</div>\
						<div class="clearfix"></div>\
					</div>\
				</div>\
            ')
            var form_address_template =
            _.template('\
                <% if (adr_key == "billing_address") { %>\
                    <div class="form-group">\
                        <label class="checkbox-inline">\
                            <input type="checkbox" name="shipping_billing_same">\
                            <span>Billing Address is same as Shipping Address</span>\
                        </label>\
                    </div>\
                <% } %>\
                <div class = "row" style="border: 1px solid black;padding: 11px;">\
                    <form action="." method = "POST" id = "<%= adr_key %>">\
                        <div class="form-group">\
                            <label for="name">Name <sup>*</sup></label>\
                            <input type="text" class="form-control dark" name="name" required id="name" value="<%=address.name%>" placeholder="Name">\
                        </div><!-- /.form-group -->   \
                        <% if (adr_key == "billing_address") { %>\
                            <div class="form-group">\
                                <label for="name">Email <sup>*</sup></label>\
                                <input type="email" class="form-control dark" name="email" required id="email" value="<%=address.email%>" placeholder="Email">\
                            </div><!-- /.form-group -->   \
                            <div class="form-group">\
                                <label for="name">Contact No. <sup>*</sup></label>\
                                <input type="text" class="form-control dark" name="phone"  id="phone" value="<%=address.phone%>" placeholder="Contact Number.">\
                            </div><!-- /.form-group -->   \
                        <% } %>\
                        <div class="form-group">\
                            <label for="street">Address*</label>\
                            <input type="text" class="form-control dark" value="<%=address.street%>" required id="street" placeholder="Street Address" name="street">\
                        </div><!-- /.form-group -->\
                        <div class="form-group">\
                            <label for="street2" class="sr-only"></label>\
                            <input type="text" class="form-control dark" value="<%=address.street2%>" id="street2" placeholder="Apartment, suite, unit etc. (Optional)" name="street2">\
                        </div><!-- /.form-group -->\
                        <div class="row">\
                            <div class= "col-md-4">\
                                <div class="form-group">\
                                    <label for="city" class="sr-only">City <sup>*</sup></label>\
                                    <input type="text" required class="form-control dark" name="city" value="<%=address.city%>" id="city" placeholder="City" />\
                                </div><!-- /.form-group -->\
                            </div>\
                            <div class= "col-md-4">\
                                <div class="form-group">\
                                    <label for="state_id" class="sr-only">State <sup>*</sup></label>\
                                    <select name="state_id" required placeholder="Select State" id="state_id" class="form-control dark">\
                                        <option disabled selected value> -- select a state -- </option>\
                                        <% _.each(state_ids[address.country_id],function(val,key) { %>\
                                            <% if (parseInt(key) == address.state_id) { %>\
                                                <option selected value="<%=key%>"><%=val%></option>\
                                            <% } else { %>\
                                                <option value="<%=key%>"><%=val%></option>\
                                            <% } %>\
                                        <% }) %>\
                                    </select>\
                                </div><!-- /.form-group -->\
                            </div>\
                            <div class= "col-md-4">\
                                <div class="form-group">\
                                    <label for="zip" class="sr-only">Zip <sup>*</sup></label>\
                                    <input type="text" class="form-control dark" required name="zip" value="<%=address.zip%>" id="zip" placeholder="Zip" />\
                                </div><!-- /.form-group -->\
                            </div>\
                        </div>\
                        <input value="<%=adr_key%>" type="hidden" name="adr_key" />\
                        <input value="<%=csrftoken%>" type="hidden" name="csrfmiddlewaretoken" />\
                        <div class="form-group">\
                            <label for="country">Country <sup>*</sup></label>\
                            <select <% if ((!is_allowed_shipping) && (adr_key == "shipping_address" )) { %> style="color:red!important" <% } %> required name="country_id" id="country" class="form-control dark">\
                                <option disabled selected value> -- select a country -- </option>\
                                <% _.each(country_ids,function(val,key) { %>\
                                    <% if (address.country_id) { %>\
                                        <% if (address.country_id == parseInt(key)) { %>\
                                            <option selected value="<%=key%>"><%=val.name%></option>\
                                        <% } else { %>\
                                            <option value="<%=key%>"><%=val.name%></option>\
                                        <% } %>\
                                    <% } else { %>\
                                        <% if (key == "United States") { %>\
                                            <option selected value="<%=key %>"><%=val.name %></option>\
                                        <% } else { %>\
                                            <option value="<%=key%>"><%=val.name%></option>\
                                        <% } %>\
                                    <% } %>\
                                <% }) %>\
                            </select>\
                        </div><!-- /.form-group -->\
                        <% if (adr_key == "billing_address") { %>\
                            <div class = "form-group">\
                                <label for="note">Order Notes</label>\
                                <textarea class="form-control" name = "note" id = "note"></textarea>\
                            </div>\
                        <% } %>\
                        <p class="text-right" >\
                            <% if (adr_key == "billing_address") { %>\
                                <button type="button" id = "go_to_shipping" class="btn btn-primary"><i class="fa fa-arrow-left" aria-hidden="true"></i>    Go Back to Shipping</a></button>\
                            <% } %>\
                            <% if (adr_key == "shipping_address") { %>\
                                <button type="button" id = "calculate_shipping" class="btn btn-primary">Calculate Shipping</button>\
                                <button type="button" id = "go_to_billing" class="btn btn-success">Next    <i class="fa fa-arrow-right" aria-hidden="true"></i></a></button>\
                            <% } %>\
                        </p>\
                    </form>\
                </div>\
            ')
            var saved_address_template =
            _.template('\
                    <h3><%=name%></h3>\
                    <% if (user && address) { %>\
                            <% if (!is_allowed_shipping) { %>\
                                <div class="row text-center alert alert-danger">\
                                    <i class="fa fa-exclamation-triangle"></i>\
                                    <strong>Sorry!</strong><span> We currently only ship to 48 states of United States of America. Please <a href="/misc/contactus"><strong style="text-decoration: underline;">CONTACT US</strong></a> for further assistance. Your cart data is saved with us.</span>\
                                </div>\
                            <% } %>\
                            <div class = "row" style="padding: 11px;">\
                                <div class="col-sm-12">\
                                    <div class="card" >\
                                        <div class="card-block" id = "saved_shipping_details">\
                                            <h4 class="card-title text-center">Saved Address</h4>\
                                            <p class="card-text" name="name"><%= address.name %></p>\
                                            <% if (address.street) { %>\
                                            <p class="card-text" name="street" ><%= address.street %></p>\
                                            <% } %>\
                                            <% if (address.street2) { %>\
                                            <p class="card-text" name="street2" ><%= address.street2 %></p>\
                                            <% } %>\
                                            <p class="card-text">\
                                            <% if (address.city) { %>\
                                            <%= address.city %>\
                                            <% } %>\
                                            <% if (address.state_id && address.country_id) { %>\
                                                , <%= state_ids[address.country_id][address.state_id] %>\
                                            <% } %>\
                                            <%  if (address.zip) { %>\
                                             - <%= address.zip %>\
                                            <% } %>\
                                            </p>\
                                            <% if (address.country_id) { %>\
                                                <p <% if (!is_allowed_shipping && adr_key == "shipping_address") { %> style="color:red!important" <% } %> class="card-text"><%= country_ids[address.country_id].name %></p>\
                                            <% } %>\
                                            <% if (adr_key == "billing_address") { %>\
                                                <p  class="card-text"><%= address.email %></p>\
                                            <% } %>\
                                            <% if (adr_key == "billing_address") { %>\
                                                <p  class="card-text"><%= address.phone %></p>\
                                            <% } %>\
                                            <p class= "text-center" ><a id="use_this_address" class="btn btn-link">Use this Address</a></p>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>\
                        <% } %>\
                    ')
            Checkout.Models.Tab = Backbone.Model.extend({
                defaults:{
                    next:false,
                    shipping_cost:0.00,
                    order_total:0.00,
                },
            })
            Checkout.Views.SavedBillingAddress = Backbone.View.extend({
                initialize:function(data,selector,name,adr_key){
                    var self = this;
                    this.selector = selector
                    this.data = data;
                    this.adr_key = adr_key
                    this.name = name;
                    this.model = new Checkout.Models.Tab;
                    if (data.user){
                        this.address = new Checkout.Models.Address(self.data['user'][adr_key]);
                    }else{
                        this.address = new Checkout.Models.Address();
                    }
                    this.render();
                },
                render:function(){
                    var self = this;
                    this.$el = $(this.selector);
                    this.saved_address =$(saved_address_template({
                        'user':self.data['user'],
                        'address':self.address.attributes,
                        'state_ids':self.data['state_ids'],
                        'country_ids':self.data['country_ids'],
                        'is_allowed_shipping':self.data['is_allowed_shipping'],
                        'name':self.name,
                        'adr_key':self.adr_key,
                    }))
                    if (self.address.get("name")){
                        this.$el.append(this.saved_address)
                    }
                    this.form_address = $(form_address_template({
                        'user':self.data['user'],
                        'address':self.address.attributes,
                        'is_allowed_shipping':self.data['is_allowed_shipping'],
                        'name':self.name,
                        'state_ids':data['state_ids'],
                        'country_ids':data['country_ids'],
                        'adr_key':self.adr_key,
                        'csrftoken':csrftoken,
                    }))
                    this.$el.append(this.form_address)
                    this.start()
                    this.$el.append(this.form_address);
                    self.start();
                },
                validate_billing:function(country_id){
                    var self = this;
                    var valid = self.form_address.find('form').valid();
                    self.form_address.find('form').validate({
                        rules:{
                            name:{
                                required:true
                            },
                            email:{
                                required:true,
                                email:true
                            },
                            street:{
                                required:true
                            },
                            zip:{
                                required:true
                            },
                            city:{
                                required:true
                            },
                            country_id:{
                                required:true
                            },
                            state_id:{
                                required:true
                            },
                        },
                        messages:{
                            name:{
                                required:"*Name is required",
                            },
                            email:{
                                required:"*Email is required",
                                email:"Please enter valid Email ID"
                            },
                            street:{
                                required:"*Adress is required",
                            },
                            zip:{
                                required:"*Zip code is required",
                            },
                            city:{
                                required:"*City is required",
                            },
                            country_id:{
                                required:"*Country is required. We only to United States as of now."
                            },
                            state_id:{
                                required:"*State is required"
                            },
                        }
                    })
                    return valid;
                },
                update_address:function(loud){
                    var self = this;
                    return $.ajax({
                        url:'/checkout/get_data/',
                        data:_.extend(self.address.attributes,{adr_key:self.adr_key}),
                        cache:false,
                        headers:{
                            'X-CSRFToken':csrftoken,
                        },
                        type:'POST',
                        error:function(){
                            toastr.error("We faced error saving your address")
                            self.model.set({'next':false})
                            return false
                        },
                        success:function(dt){
                            if (loud){
                                toastr.success("Address Updated Successully",'Success')
                            }
                            self.$el.empty()
                            self.render();
                            return true
                        },
                        complete:function(){
                        },
                    })
                },
                start:function(){
                    var self = this;
                    self.form_address.find("button#go_to_shipping").on('click',function(){
                        $("a[href='#billing']").removeAttr('data-toggle');
                        $("a[href='#shipping']").attr('data-toggle','tab');
                        $("a[href='#shipping']").trigger('click')
                        payment_box.hide();
                    })
                    self.form_address.find("form").on('change',function(e){
                        var data = {};
                        e.stopImmediatePropagation();
                        self.model.set({'next':false});
                        data[$(e.target).attr('name')] = $(e.target).val()
                        self.address.set(data)
                    })
                    self.form_address.find("input[name='shipping_billing_same']").on('click',function(){
                        event.stopImmediatePropagation();
                        var checked = $(this).is(":checked");
                        if (checked){
                            var form = self.form_address.find("form");
                            Checkout.Events.Checkout.trigger('same_address_billing',form)
                        }
                    })
                    self.saved_address.find('a#use_this_address').on('click',function(){
                        self.$el.empty()
                        self.render();
                    })
                    self.form_address.find("select#country").on("change",function(e){
                        var country_id = $(this).val();
                        function _onchange_country_id(states){
                            self.form_address.find('select#state_id').empty();
                            var template = _.template('<option value="<%=name%>" ><%=value%></option>')
                            self.form_address.find('select#state_id').append($("<option disabled selected value> -- select a state -- </option>"))
                            _.each(states,function(key,val){
                                self.form_address.find('select#state_id').append($(template({'name':val,'value':key})))
                            });
                        }
                        if (_.has(self.data['state_ids'],country_id)){
                            _onchange_country_id(self.data.state_ids[country_id])
                            return $.Deferred().resolve()
                        }else{
                            var country_id = $(this).val();
                            return $.ajax({
                                url:'/checkout/get_data/',
                                data:{'states_list':$(this).val()}, // Send the country_id for the states_list
                                cache:false,
                                type:'GET',
                                headers: {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/x-www-form-urlencoded' ,
                                },
                                success:function(dt){
                                    $.extend(self.data['state_ids'],dt);
                                    _onchange_country_id(dt[country_id])
                                },
                            })
                        }
                    })
                },
            })
            Checkout.Views.SavedAddress = Backbone.View.extend({
                initialize:function(data,selector,name,adr_key){
                    var self = this;
                    this.selector = selector
                    this.data = data;
                    this.adr_key = adr_key
                    this.name = name;
                    this.is_allowed_shipping = self.data['is_allowed_shipping'],
                    this.model = new Checkout.Models.Tab;
                    if (data.user){
                        this.address = new Checkout.Models.Address(self.data['user'][adr_key]);
                    }else{
                        this.address = new Checkout.Models.Address();
                    }
                    this.render();

                },
                render:function(){
                    var self = this;
                    this.$el = $(this.selector)
                    this.saved_address =$(saved_address_template({
                        'user':self.data['user'],
                        'address':self.address.attributes,
                        'state_ids':data['state_ids'],
                        'country_ids':data['country_ids'],
                        'is_allowed_shipping':self.data['is_allowed_shipping'],
                        'name':self.name,
                        'adr_key':self.adr_key,
                    }))
                    this.$el.append(this.saved_address)
                    this.form_address = $(form_address_template({
                        'user':self.data['user'],
                        'address':self.address.attributes,
                        'is_allowed_shipping':self.data['is_allowed_shipping'],
                        'name':self.name,
                        'state_ids':data['state_ids'],
                        'country_ids':data['country_ids'],
                        'adr_key':self.adr_key,
                        'csrftoken':csrftoken,
                    }))
                    this.$el.append(this.form_address)
                    this.start()
                },
                validate_shipping:function(country_id){
                    var self = this;
                    var valid = self.form_address.find('form').valid();
                    var is_allowed_shipping=false;
                    self.form_address.find('form').validate({
                        rules:{
                            name:{
                                required:true
                            },
                            street:{
                                required:true
                            },
                            zip:{
                                required:true
                            },
                            city:{
                                required:true
                            },
                            country_id:{
                                required:true
                            },
                            state_id:{
                                required:true
                            },
                        },
                        messages:{
                            name:{
                                required:"*Name is required",
                            },
                            street:{
                                required:"*Adress is required",
                            },
                            zip:{
                                required:"*Zip code is required",
                            },
                            city:{
                                required:"*City is required",
                            },
                            country_id:{
                                required:"*Country is required. We only to United States as of now."
                            },
                            state_id:{
                                required:"*State is required"
                            },
                        }
                    })
                    if (!valid){
                        self.model.set({'next':false})
                        return;
                    }
                    _.each(self.data['country_allowed_shipping'],function(i){
                        if (i[0] == country_id){
                            self.is_allowed_shipping = true;
                        }else{
                            self.is_allowed_shipping = false;
                        }
                    })
                    if (!self.is_allowed_shipping){
                        valid=false
                        self.model.set({'next':false})
                        toastr.error("We only ship to 48 states of United States. Please contact us for further support. Your cart is saved with us")
                    }
                    return valid
                },
                calculate_total:function(){
                    var self=this;
                    var total = 0.00;
                    total = this.data['gross_total'] + self.model.get('shipping_cost');
                    total = total.toFixed(2);
                    self.model.set({'order_total':total})
                    order_total.find('span').text('$'+self.model.get('order_total'));
                    Checkout.Events.Checkout.trigger('order_total_changed',total)
                },
                update_address:function(loud){
                    var self = this;
                    if (!self.data.user){
                        return $.Deferred().resolve();
                    }
                    return $.ajax({
                        url:'/checkout/get_data/',
                        data:_.extend(self.address.attributes,{adr_key:self.adr_key}),
                        cache:false,
                        headers:{
                            'X-CSRFToken':csrftoken,
                        },
                        type:'POST',
                        error:function(){
                            toastr.error("We faced error saving your address")
                            self.model.set({'next':false})
                            return false
                        },
                        success:function(dt){
                            if (loud){
                                toastr.success("Address Updated Successully",'success')
                            }
                            self.$el.empty()
                            self.render();
                            self.render_next_button();
                            return true
                        },
                        complete:function(){
                        },
                    })
                },
                render_next_button:function(){
                    var self= this;
                    var n = self.model.get('next');
                    if (n){
                        self.form_address.find("button#go_to_billing").show()
                    }else{
                        self.form_address.find("button#go_to_billing").hide()
                    }
                },
                start:function(){
                    var self = this;
                    $("a[href='#doner']").removeAttr('data-toggle'); // Initially it will not be clickabe
                    $("a[href='#billing']").removeAttr('data-toggle'); // Initially it will not be clickabe
                    self.form_address.find("button#go_to_billing").hide();
                    self.form_address.find('form').submit(function(event){
                        event.preventDefault();
                        self.update_address(true);
                    })
                    self.form_address.find("form").on('change',function(e){
                        var data = {};
                        self.model.set({'next':false});
                        data[$(e.target).attr('name')] = $(e.target).val()
                        self.address.set(data)
                    })
                    self.form_address.find("button#go_to_billing").on('click',function(){
                        var country_id = self.form_address.find('form').find('select#country')
                        var valid = self.validate_shipping(parseInt(country_id.val()))
                        self.update_address(false).done(function(done){
                            if (self.model.get('next')){
                                $("a[href='#shipping']").removeAttr('data-toggle');
                                $("a[href='#billing']").attr('data-toggle','tab'); // Initially it will not be clickabe
                                $("a[href='#billing']").trigger('click')
                                payment_box.show();
                            }else{
                                toastr.warning("Please calculate the shipping cost first and then proceed to Billing Details")
                            }
                        })
                    })
                    self.saved_address.find('a#use_this_address').on('click',function(){
                        self.$el.empty()
                        self.render();
                    })
                    self.model.on("change:next",function(e){
                        self.render_next_button();
                    })
                    this.listenTo(Checkout.Events.Checkout,'same_address_billing',function(form){
                        event.stopImmediatePropagation();
                        form.find('input[name="name"]').val(self.address.get('name') || '').change();
                        form.find('input[name="street"]').val(self.address.get('street') || '').change();
                        form.find('input[name="street2"]').val(self.address.get('street2') || '').change();
                        form.find('input[name="city"]').val(self.address.get('city') || '').change();
                        form.find('input[name="zip"]').val(self.address.get('zip') || '').change();
                        if (self.address.get('country_id')){
                            form.find('select[name="country_id"]').val(self.address.get('country_id')).change();
                        }
                        $.when(form.find("select#country").triggerHandler("change")).done(function(def){
                            $.when(def).done(function(){
                                if (self.address.get('state_id')){
                                    form.find('select[name="state_id"]').val(self.address.get('state_id')).change();
                                }
                            })
                        })
                    })
                    self.form_address.find("button#calculate_shipping").on('click',function(){
                        var country_id = self.form_address.find('form').find('select#country')
                        var is_allowed_shipping = false
                        var valid = self.validate_shipping(parseInt(country_id.val()));
                        if (!valid){
                            return
                        }
                        if (!getCookie("ac_custom_verified")){
                            toastr.error("Please refresh page and try again without bypassing age test")
                            return
                        }
                        var zip = self.form_address.find('form').find('input#zip')
                        $.ajax({
                            url:'/checkout/get_shipping_rates/',
                            data:self.form_address.find('form').serialize(), // Send the country_id for the states_list
                            cache:false,
                            type:'GET',
                            headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/x-www-form-urlencoded' ,
                            },
                            beforeSend:function(){
                                toastr.info("Request for Shipping Rates Sent.Please Wait .....")
                            },
                            success:function(dt){
                                if (dt.error){
                                    toastr.warning(dt.msg);
                                    self.model.set({'next':false});
                                    return
                                }else{
                                    if (dt.msg){
                                        toastr.success(dt.msg);
                                    }
                                    self.model.set({'next':true});
                                    self.model.set({'shipping_cost':dt.rate});
                                    shipping_total.text("$"+dt.rate);
                                    self.calculate_total();
                                }
                            },
                            complete:function(){
                                toastr.success("Received Shipping Rates Info.")
                            },
                        })
                    })
                    self.form_address.find("select#country").on("change",function(e){
                        var country_id = $(this).val();
                        function _onchange_country_id(states){
                            self.form_address.find('select#state_id').empty();
                            var template = _.template('<option value="<%=name%>" ><%=value%></option>')
                            self.form_address.find('select#state_id').append($("<option disabled selected value> -- select a state -- </option>"))
                            _.each(states,function(key,val){
                                self.form_address.find('select#state_id').append($(template({'name':val,'value':key})))
                            });
                        }
                        if (_.has(self.data['state_ids'],country_id)){
                            _onchange_country_id(self.data.state_ids[country_id])
                            return $.Deferred().resolve()
                        }else{
                            var country_id = $(this).val();
                            return $.ajax({
                                url:'/checkout/get_data/',
                                data:{'states_list':$(this).val()}, // Send the country_id for the states_list
                                cache:false,
                                type:'GET',
                                headers: {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/x-www-form-urlencoded' ,
                                },
                                success:function(dt){
                                    $.extend(self.data['state_ids'],dt);
                                    _onchange_country_id(dt[country_id])
                                },
                            })
                        }
                    })
                }
            })
            Checkout.Views.PaymentForm = Backbone.View.extend({
                initialize:function(shipping_address,billing_address,data){
                    this.model = new Backbone.Model;
                    this.billing_tab = billing_address;
                    this.shipping_tab = shipping_address;
                    this.data = data;
                    this.render();
                },
                paymentFormReady:function() {
                    if (this.$el.find('[name=billing-cc-number]').hasClass("success") &&
                        this.$el.find('[name=billing-cc-exp]').hasClass("success") &&
                        this.$el.find('[name=billing-cvv]').val().length > 1) {
                        return true;
                    } else {
                        return false;
                    }
                },
                render:function(){
                    var self = this;
                    this.$el = $('#payment-form');
                    this.model.set({'step':'step1','order_total':0.00})
                    /* Fancy restrictive input formatting via jQuery.payment library*/
                    $('input[name=billing-cc-number]').payment('formatCardNumber');
                    $('input[name=billing-cvv]').payment('formatCardCVC');
    //				$('input[name=billing-cc-exp]').payment('formatCardExpiry');
                    /* Form validation using Stripe client-side validation helpers */
                    jQuery.validator.addMethod("cardNumber", function(value, element) {
                        return this.optional(element) || Stripe.card.validateCardNumber(value);
                    }, "Please specify a valid credit card number.");
                    jQuery.validator.addMethod("cardExpiry", function(value, element) {
                        /* Parsing month/year uses jQuery.payment library */
                        value = $.payment.cardExpiryVal(value);
                        return this.optional(element) || Stripe.card.validateExpiry(value.month, value.year);
                    }, "Invalid expiration date.");
                    jQuery.validator.addMethod("cardCVC", function(value, element) {
                        return this.optional(element) || Stripe.card.validateCVC(value);
                    }, "Invalid CVC.");
                    validator = this.$el.validate({
                        rules: {
                            'billing-cc-number': {
                                required: true,
                                cardNumber: true
                            },
                            'billing-cc-exp': {
                                required: true,
                                cardExpiry: true
                            },
                            'billing-cvv': {
                                required: true,
                                cardCVC: true
                            }
                        },
                        highlight: function(element) {
                            $(element).closest('.form-control').removeClass('success').addClass('error');
                        },
                        unhighlight: function(element) {
                            $(element).closest('.form-control').removeClass('error').addClass('success');
                        },
                        errorPlacement: function(error, element) {
                            $(element).closest('.form-group').append(error);
                        }
                    });
                    this.$el.find('.subscribe').prop('disabled', true);
                    this.readyInterval = setInterval(function() {
                        if (self.paymentFormReady()) {
                            self.$el.find('.subscribe').prop('disabled', false);
                            clearInterval(this.readyInterval);
                        }
                    }, 250);
                    self.start();
                },
                start:function(){
                    var self = this;
                    self.listenTo(Checkout.Events.Checkout,'order_total_changed',function(total){
                        self.model.set({'order_total':total});
                    });
                    self.model.on('change:order_total',function(){
                        self.$el.find("button#make_payment").text("Make Payment - $"+self.model.get('order_total'));
                    })
                    self.$el.find("button#make_payment").on('click',function(event){
                        event.preventDefault();
                        event.stopImmediatePropagation();
                        var valid = self.billing_tab.validate_billing()
                        if (!valid){
                            return
                        }
                        clearInterval(self.readyInterval);
                        self.$el.find('.subscribe').prop('disabled', true);
                        if (self.data.user){
                            self.billing_tab.update_address(true);
                        }
                        switch(self.model.get('step')){
                            case 'step1':
                                console.log("Billing Address:",self.billing_tab.address)
                                console.log("Shipping  Address:",self.shipping_tab.address)
                                self.execute_step1();
                                break;
                        }
                    })
                },
                execute_step2:function(){
                    var self = this;
                    if (self.paymentFormReady()){
                        self.$el.attr("action",self.model.get('form-url'))
                        self.$el.submit();
                    }
                },
                execute_step1:function(){
                    var self = this;
                    $.ajax({
                        url:data['payment_redirect_url'],
                        contentType:"application/json; charset=utf-8",
                        data:JSON.stringify({
                            'step':self.model.get('step'),
                            'total':self.model.get('order_total'),
                            'note':self.billing_tab.address.get('note') || '',
                            'shipping_cost':parseFloat(self.shipping_tab.model.get('shipping_cost')) || 0.00,
                            'shipping_address':self.shipping_tab.address.attributes,
                            'billing_address':self.billing_tab.address.attributes,
                        }),
                        type:'POST',
                        headers:{
                            'X-CSRFToken':csrftoken,
                        },
                        error:function(dt){
                            //error
                            toastr.error("Sorry we were unable to process the request")
                        },
                        success:function(dt){
                            //success
                            // result-code 100 means successfull transaction
                            var x2js = new X2JS();
                            var jsonObj = x2js.xml_str2json( dt.xml_string );
                            var response = jsonObj.response;
                            if (response['result-code'] == "100"){
                                self.model.set({
                                    'step':dt.next_step,
                                    'form-url':response['form-url'],
                                    'transaction-id':response['transaction-id'],
                                });
                                self.execute_step2();
                            }else{
                                toastr.error(response['result-text'])
                                return;
                            }
                        },
                    })
                },
            })
            var data= {};
            $.ajax({
                url:'/checkout/get_data/',
                data:{},
                cache:false,
                type:'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded' ,
                },
                success:function(dt){
                    data = dt;
                },
            }).done(function(){
                payment_box.hide();
                if (data.user){
                    left_side.append($(checkout_box({})))
                    var saved_shipping_address = new Checkout.Views.SavedAddress(data,'div#shipping.tab-pane','Shipping Details','shipping_address')
                    var saved_billing_address = new Checkout.Views.SavedBillingAddress(data,'div#billing.tab-pane','Billing Details','billing_address')
                    var payment_form = new Checkout.Views.PaymentForm(saved_shipping_address,saved_billing_address,data);
                }else{
                    var signin_form = left_side.append($(signin_box({})))
                    signin_form.find("button#checkout_as_guest").on('click',function(){
                        event.preventDefault();
                        left_side.empty();
                        left_side.append($(checkout_box({})))
                        var saved_shipping_address = new Checkout.Views.SavedAddress(data,'div#shipping.tab-pane','Shipping Details','shipping_address')
                        var saved_billing_address = new Checkout.Views.SavedBillingAddress(data,'div#billing.tab-pane','Billing Details','billing_address')
                        var payment_form = new Checkout.Views.PaymentForm(saved_shipping_address,saved_billing_address,data);
                    })
                    signin_form.find('form').on('submit',function(){
                        event.preventDefault();
                        var form = this;
                        var url = $(form).attr('action');
                        $.ajax({
                            type: "POST",
                            url: data.signin_login,
                            beforeSend:function(){
                                $(form).find("button[type='submit']").addClass('active')
                            },
                            headers:{
                                'X-CSRFToken':csrftoken,
                            },                            
                            data: $(form).serializeArray(),
                            error:function(data){
                                console.log("error",data)
                            },
                            complete:function(){
                                $(form).find("button[type='submit']").removeClass('active')
                            },
                            success:function(data){
                                if (data['auth'] == true){
                                    toastr.success("Login Successful")
                                    $(form).find('div#auth_failed').addClass('hidden');
                                    location.reload();
                                }else{
                                    console.log($(form).find('div#auth_failed'))
                                    $(form).find('div#auth_failed').removeClass('hidden')
                                    toastr.error("Login Failed")
                                }

                            },
                        });
                    })
                    $('button[href="#forgot-password-popup"]').magnificPopup({
                        type:'inline',
                        midClick: false,
                        closeOnBgClick: false
                    });
                    loadProfile();
                    function getLocalProfile(callback){
                        var profileImgSrc      = localStorage.getItem("PROFILE_IMG_SRC");
                        var profileName        = localStorage.getItem("PROFILE_NAME");
                        var profileReAuthEmail = localStorage.getItem("PROFILE_REAUTH_EMAIL");

                        if(profileName !== null
                                && profileReAuthEmail !== null
                                && profileImgSrc !== null) {
                            callback(profileImgSrc, profileName, profileReAuthEmail);
                        }
                    }

                    /**
                     * Main function that load the profile if exists
                     * in localstorage
                     */
                    function loadProfile() {
                        if(!supportsHTML5Storage()) { return false; }
                        // we have to provide to the callback the basic
                        // information to set the profile
                        getLocalProfile(function(profileImgSrc, profileName, profileReAuthEmail) {
                            //changes in the UI
                            $("#profile-img").attr("src",profileImgSrc);
                            $("#profile-name").html(profileName);
                            $("#reauth-email").html(profileReAuthEmail);
                            $("#inputEmail").hide();
                            $("#remember").hide();
                        });
                    }

                    /**
                     * function that checks if the browser supports HTML5
                     * local storage
                     *
                     * @returns {boolean}
                     */
                    function supportsHTML5Storage() {
                        try {
                            return 'localStorage' in window && window['localStorage'] !== null;
                        } catch (e) {
                            return false;
                        }
                    }

                    /**
                     * Test data. This data will be safe by the web app
                     * in the first successful login of a auth user.
                     * To Test the scripts, delete the localstorage data
                     * and comment this call.
                     *
                     * @returns {boolean}
                     */
                    function testLocalStorageData() {
                        if(!supportsHTML5Storage()) { return false; }
                        localStorage.setItem("PROFILE_IMG_SRC", "//lh3.googleusercontent.com/-6V8xOA6M7BA/AAAAAAAAAAI/AAAAAAAAAAA/rzlHcD0KYwo/photo.jpg?sz=120" );
                        localStorage.setItem("PROFILE_NAME", "César Izquierdo Tello");
                        localStorage.setItem("PROFILE_REAUTH_EMAIL", "oneaccount@gmail.com");
                    }                    
                }
            })
        })
    })
})
