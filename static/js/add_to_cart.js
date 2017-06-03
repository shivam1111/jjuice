define(['jquery','underscore','backbone','toastr','utils'],function($,_,Backbone,toastr){
    var AddToCart = {
        Views:{},
    }
    var cart_menubar_template = 
    _.template('\
        <% if (cart_item_count == 0) { %>\
        <li>\
            <div class="container-fluid">\
                <span class="text-muted">Cart is empty</span>\
            </div>\
        </li>\
        <% } %>\
        <% if (cart_item_count != 0) { %>\
        <li>\
            <div class="container-fluid">\
                <ul class="whishlist">\
                    <% _.each(cart_items,function(val,key) { %>\
                    <li>\
                        <div class="whishlist-item">\
                            <div class="product-image">\
                                <a href="<%=val.flavor_url%>" title="">\
                                    <img src="<%=val.image_url%>" alt="">\
                                </a>\
                            </div>\
                            <div class="product-body">\
                                <div class="whishlist-name">\
                                    <h3><a href="<%=val.flavor_url%>" title=""><%=val.name%></a></h3>\
                                </div>\
                                <div class="whishlist-price">\
                                    <span>Price:</span>\
                                    <strong><%= val.price %></strong>\
                                </div>\
                                <div class="whishlist-quantity">\
                                    <span>Quantity:</span>\
                                    <% if (val.quantity > val.qty.virtual_available) { %><span style="color:red"><strong><%=val.quantity%></strong></span><% } %>\
                                    <% if (val.quantity <= val.qty.virtual_available) { %><span ><%=val.quantity%></span><% } %>\
                                </div>\
                                <div class="whishlist-quantity">\
                                    <% if (val.quantity > val.qty.virtual_available) { %><span style="color:red"><strong>OUT OF STOCK</strong></span> <% } %>\
                                </div>\
                            </div>\
                        </div>\
                    </li>\
                    <% }) %>\
                </ul>\
                <div class="menu-cart-total" style = "border-bottom:none;">\
                    <span>Gross Total</span>\
                    <span class="price">$<%=cart_total%></span>\
                </div>\
                <div class="menu-cart-total" style = "border-bottom:none;">\
                    <span >Discount (%) <i data-toggle="tooltip" data-original-title="3+1=4" class="fa fa-question-circle" aria-hidden="true"></i></span>\
                    <span class="price"><%=discount_percentage%></span>\
                </div>\
                <div class="menu-cart-total">\
                    <span data-toggle="tooltip" data-original-title="3+1=4" >Grand Total </span>\
                    <span class="price">$<%=net_total%></span>\
                </div>\
                <div class="cart-action">\
                    <a href="<%=cart_url%>" title="Checkout" class="btn btn-lg btn-dark btn-outline btn-block">View cart</a>\
                    <% if (authenticated) { %>\
                        <a href="<%=checkout_url%>" id = "proceed_to_checkout" title="Proceed to Checkout" class="btn btn-lg btn-primary btn-block">Proceed To Checkout</a>\
                    <% } %>\
                </div>\
            </div>\
        </li>\
        <%  } %>\
    ');

    AddToCart.Views.Main = Backbone.View.extend({
        initialize:function(form){
            var self = this;
            self.form = form;
            self.csrftoken = getCookie('csrftoken');
            self.menubar_cart = $("li.menubar-cart");
            self.data = {};
            this.start();
        },
        render_template:function(){
            var self = this;
            var data = self.data
            self.menubar_cart.find('span.cart-number').remove()
            self.menubar_cart.find('a.awemenu-icon.menu-shopping-cart').append($(_.template('<span class="cart-number"><%= cart_item_count %></span>')({'cart_item_count':data.cart_item_count})))
            self.menubar_cart.find("ul.submenu.megamenu").empty().append($(cart_menubar_template(data)))
        },
        start:function(){
            var self = this;
            self.form.on("submit",function(){
                event.preventDefault()
                $.ajax({
                    url:'/cart/add_to_cart/',
                    data:self.form.serialize(),
                    cache:false,
                    type:'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/x-www-form-urlencoded' ,
                        'X-CSRFToken':self.csrftoken,
                    },
                    error:function(){
                        toastr.error("We faced error updating the cart. We apologize for the inconvinience caused")
                    },
                    success:function(dt){
                        self.data = dt.data
                        if (dt.error){
                            toastr.error(dt.msg)
                        }else{
                            var qty = self.form.find('input[name="quantity"]').val()
                            console.log(dt)
                            if (dt.available_qty.virtual_available <= 0 ){
                                toastr.warning("Sorry! this product is currently out of stock!");
                            }else if (dt.available_qty.virtual_available < dt.cart_qty ){
                                toastr.warning("Sorry! only "+dt.available_qty.virtual_available+" units are availbale and order quantity is "+dt.cart_qty);
                            }else{
                                toastr.success("Product added to cart. Please continue shopping!")
                                self.form.find('input[name="quantity"]').val('');
                            }
                            self.render_template()
                        }
                    },
                })
            })
        },
    })
    return AddToCart
});