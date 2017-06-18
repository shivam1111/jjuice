require(['toastr','recaptcha'],function(toastr){
        var registration_form = $('form#registration_form');
        var states_list = {};
        var csrftoken = getCookie('csrftoken');
        var is_wholesale = registration_form.find('input#is_wholesale')
        var is_wholesale_fieldset = registration_form.find('fieldset#is_wholesale')
        is_wholesale_fieldset.hide();
        is_wholesale.on("change",function(){
            if (this.checked){
                is_wholesale_fieldset.show();
            }else{
                is_wholesale_fieldset.hide();
            }
        })

        jQuery.validator.addMethod("wholesale", function(value, element) {
            if (registration_form.find('input#is_wholesale').is(":checked")){
                if (value){
                    return true
                }else{
                    return false
                }
            }
        }, "Required");
        registration_form.validate({
            rules:{
                name:{
                    required:true
                },
                email:{
                    required:true,
                    email:true,
                    remote:"/accounts/validate_username/",
                },
                phone:{
                    required:true,
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
                'register-password':{
                    required:true,
                },
                'register-confirm-password':{
                    required:true,
                    equalTo: "#register-password"
                },
                vat:{
                    wholesale:true,
                },
                type_account:{
                    wholesale:true,
                },
                company_name:{
                    wholesale:true,
                }
            },
            messages:{
                name:{
                    required:"*Name is required",
                },
                email:{
                    required:"*Email is required",
                    email:"Please enter valid Email ID",
                    remote:jQuery.validator.format("{0} is already taken.")
                },
                phone:{
                    required:"*Phone is required",
                },
                street:{
                    required:"*Address is required",
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
                'register-password':{
                    required:"*Password is required"
                },
                'register-confirm-password':{
                    equalTo: "Passwords Mismatch"
                },
                vat:{
                    wholesale:"State Issued Resale Number is required"
                },
                type_account:{
                    wholesale:"Account Type is Required",
                },
                company_name:{
                    wholesale:"Company Name Required",
                },
            }
        })
        registration_form.find("select#country_id").on("change",function(e){
            var country_id = $(this).val();
            var code = $(this).find('option:selected').attr('name');
//            if (code != 'US'){
//                registration_form.find("select#state_id").replaceWith('<input type="text" class="form-control dark" required name="state_id"\
//                                                                       id="state_id" placeholder="State" />')
//                return
//            }else{
//                registration_form.find("input#state_id").replaceWith('<select name="state_id" required placeholder="Select State" id="state_id" class="form-control dark">\
//                                                                        <option disabled selected value> -- select a state -- </option>\
//                                                                     </select>')
//            }
            function _onchange_country_id(states){
                registration_form.find('select#state_id').empty();
                var template = _.template('<option value="<%=name%>" ><%=value%></option>')
                registration_form.find('select#state_id').append($("<option disabled selected value> -- select a state -- </option>"))
                _.each(states,function(key,val){
                    registration_form.find('select#state_id').append($(template({'name':val,'value':key})))
                });
            }
            console.log(states_list)
            if (_.has(states_list,country_id)){
                _onchange_country_id(states_list[country_id])
                return $.Deferred().resolve()
            }else{
                $.ajax({
                    url:'/checkout/get_data/',
                    data:{'states_list':$(this).val()}, // Send the country_id for the states_list
                    cache:false,
                    type:'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/x-www-form-urlencoded' ,
                    },
                    success:function(dt){
                        $.extend(states_list,dt);
                        _onchange_country_id(dt[country_id])
                    },
                })
            }
        })
        registration_form.submit(function(event){
            event.preventDefault();
            if (registration_form.valid()){
                var arr = $(this).serializeArray()
                var captcha = arr.filter(function(set){
                    if (set.name == "g-recaptcha-response"){
                        return true
                    }
                })
                if (captcha[0].value){
                    registration_form.find("button[type='submit']").addClass("active")
                    registration_form.find("button[type='submit']").prop("disabled",true)
                    $.ajax({
                        url:'/accounts/captcha/',
                        data:{
                            'g-recaptcha-response':captcha[0].value
                        },
                        type:'POST',
                        headers:{
                            'X-CSRFToken':csrftoken,
                        },
                        error:function(dt){
                            //error
                            toastr.error("Sorry we were unable to process the request")
                            registration_form.find("button[type='submit']").removeClass("active")
                            registration_form.find("button[type='submit']").removeAttr("disabled")
                            grecaptcha.reset();
                            return false
                        },
                        success:function(dt){
                            //success
                            // result-code 100 means successfull transaction
                            return dt
                        },
                    }).done(function(dt){
                        if (!_.isEmpty(dt)){
                            if (dt.success){
                                $.ajax({
                                    url:'/accounts/registration/',
                                    data:registration_form.serialize(),
                                    type:'POST',
                                    headers:{
                                        'X-CSRFToken':csrftoken,
                                    },
                                    error:function(dt){
                                        //error
                                        toastr.error("Sorry we were unable to process the request")
                                        registration_form.find("button[type='submit']").removeAttr("disabled")
                                        grecaptcha.reset();
                                        return false
                                    },
                                    complete:function(){
                                        registration_form.find("button[type='submit']").removeClass("active")
                                    },
                                    success:function(dt){
                                        registration_form.find("button[type='submit']").removeAttr("disabled")
                                        if (dt.error){
                                            toastr.error(dt.msg)
                                            return
                                        }else{
                                            toastr.success("Registration Successfull")
                                            if (dt.is_wholesale){
                                                registration_form.empty();
                                                msg_html = '<div class = "row">\
                                                                <div class = "col-md-8 col-md-offset-2">\
                                                                    <div class="alert alert-info">\
                                                                        <strong class="upper">Registration Successfull!</strong><hr>\
                                                                        <p>Since it is a wholesale account, It will take upto 24 hours for the account to get activated</p>\
                                                                        <p>To activate it sooner, Please contact JJuice directly. Phone: 801-331-8919</p>\
                                                                    </div>\
                                                                </div>\
                                                            </div>'
                                                registration_form.append($(msg_html))
                                            }else{
                                                $.magnificPopup.close()
                                                $.magnificPopup.open({items: {
                                                    src: '#login-popup',type:'inline',
                                                },})
                                            }
                                        }
                                    },
                                })
                        }else{
                            toastr.error("Could not verify as Human")
                            registration_form.find("button[type='submit']").removeClass("active")
                            registration_form.find("button[type='submit']").removeAttr("disabled")
                            grecaptcha.reset();
                        }
                    }
                    else{
                        toastr.error("Please confirm you are a human!",'warning')
                        registration_form.find("button[type='submit']").removeClass("active")
                        registration_form.find("button[type='submit']").removeAttr("disabled")
                        grecaptcha.reset();
                    }
                });
            }
        }
    });
})
