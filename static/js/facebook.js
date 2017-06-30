define(['jquery','underscore','toastr','utils'],function($,_,toastr){

    var customers_carousel_template = _.template('\
                            <div class="center">\
                                <h4><%=reviewer.name%></h4>\
                                <% if (has_review) { %><p><%=review_text%></p><% } %>\
                            </div>\
                        ');
    var brands_carousel_template = _.template('\
                <div class = "center" >\
                        <img src="https://graph.facebook.com/<%=reviewer.id%>/picture" style="height:80px;width:90px;" alt="">\
                </div>\
            ')

    $.ajax({
        url:'/facebook/ratings/',
        data:{},
        cache:false,
        type:'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded' ,
            'X-CSRFToken':self.csrftoken,
        },
        error:function(){
            // ERROR
        },
        success:function(dt){
            return dt
        },
    }).done(function(dt){
        if (dt.data){
            _.each(dt.data,function(value,key){
                console.log(value)
                $('div#customers-carousel').append($(customers_carousel_template(value)))
                $('div#brands-carousel').append($(brands_carousel_template(value)))
            })
        }
    })
})