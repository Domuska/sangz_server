/**
 * @fileOverview Forum administration dashboard. It utilizes the Forum API to 
                 handle user information (retrieve user list, edit user profile, 
                 as well as add and remove new users form the system). It also 
                 permits to list and remove user's messages.
 * @author <a href="mailto:ivan@ee.oulu.fi">Ivan Sanchez Milara</a>
 * @version 1.0
 * 
 * NOTE: The documentation utilizes jQuery syntax to refer to classes and ids in
         the HTML code: # is utilized to refer to HTML elements ids while . is
         utilized to refer to HTML elements classes.
**/


/**** START CONSTANTS****/

/** 
 * Set this to true to activate the debugging messages. 
 * @constant {boolean}
 * @default 
 */
var DEBUG = true,

/** 
 * Collection+JSON mime-type 
 * @constant {string}
 * @default 
 */
COLLECTIONJSON = "application/vnd.collection+json",

/** 
 * HAL mime type
 * @constant {string}
 * @default 
 */
HAL = "application/hal+json",

/** 
 * Link to Users_profile
 * @constant {string}
 * @default 
 */
FORUM_USER_PROFILE = "/profiles/users",

/** 
 * Link to Messages_profile
 * @constant {string}
 * @default 
 */
FORUM_MESSAGE_PROFILE = "/profiles/messages",

/** 
 * Default datatype to be used when processing data coming from the server.
 * Due to JQuery limitations we should use json in order to process Collection+JSON
 * and HAL responses
 * @constant {string}
 * @default 
 */
DEFAULT_DATATYPE = "json",

/** 
 * Entry point of the application
 * @constant {string}
 * @default 
 */
ENTRYPOINT = "/forum/api/users/"; //Entrypoint: Resource Users

/**** END CONSTANTS****/


/**** START RESTFUL CLIENT****/

//our stuff goes here

/**** END RESTFUL CLIENT****/

/**** UI HELPERS ****/

/**** This functions are utilized by rest of the functions to interact with the
      UI ****/
	  
// note, these are copied from the forum excercise example, not modified (yet).
// these might also not be needed, will be left here for now

/**
 * Append a new user to the #user_list. It appends a new <li> element in the #user_list 
 * using the information received in the arguments.  
 *
 * @param {string} url - The url of the User to be added to the list
 * @param {string} nickname - The nickname of the User to be added to the list
 * @returns {Object} The jQuery representation of the generated <li> elements.
**/
function appendUserToList(url, nickname) {
    var $user = $('<li>').html('<a class= "user_link" href="'+url+'">'+nickname+'</a>');
    //Add to the user list
    $("#user_list").append($user);
    return $user;
}

/**
 * Populate a form with the <input> elements contained in the <i>template</i> input parameter.
 * The action attribute is filled in with the <i>url</i> parameter. Values are filled
 * with the default values contained in the template. It supports Collection+JSON
 * required extension to mark inputs with required property. 
 *
 * @param {string} url - The url of to be added in the action attribute
 * @param {Object} template - a Collection+JSON template ({@link https://github.com/collection-json/spec#23-template}) 
 * which is utlized to append <input> elements in the form
 * @param {string} id - The id of the form is gonna be populated
**/
function createFormFromTemplate(url,template,id){
    $form=$('#'+ id);
    $form.attr("action",url);
    //Clean the forms
    $form_content=$(".form_content",$form);
    $form_content.empty();
    $("input[type='button']",$form).hide();
    if (template.data) {
        for (var i =0; i<template.data.length; i++){
            var name = template.data[i].name;
            var input_id = "new_"+name+"_id";
            var value = template.data[i].value;
            var prompt = template.data[i].prompt;
            var required = template.data[i].required;
            $input = $('<input type="text"></input>');
            $input.addClass("editable");
            $input.attr('name',name);
            $input.attr('id',input_id);
            $label_for = $('<label></label>');
            $label_for.attr("for",input_id);
            $label_for.text(name);
            $form_content.append($label_for);
            $form_content.append($input);
            if(value){
                $input.attr('value', value);
            }
            if(prompt){
                $input.attr('placeholder', prompt);
            }
            if(required){
                $input.prop('required',true);
                $label = $("label[for='"+$input.attr('id')+"']");
                $label.append(document.createTextNode("*"));
            }
            
        }
    }
}

/**
 * Populate a form with the <input> elements contained in the <i>data</i> parameter. 
 * The data.parameter name is the <input> name attribute while the data.parameter 
 * value represents the <input> value. All parameters are by default assigned as 
 * <i>readonly</i>.
 * The action attribute is filled in with the <i>url</i> parameter. 
 * If a template is provided, the <input> parameters contained in the template
 * are set editable. Required <input> fields are marked with the <i>required</i> property.
 * If a template property does not have its <input> counterpart it will create a new 
 * <input> for that property.
 * 
 * NOTE: All buttons in the form are hidden. After executing this method adequate
 *       buttons should be shown using $(#button_name).show()
 *
 * @param {string} url - The url of to be added in the action attribute
 * @param {Object} data - An associative array formatted using HAL format ({@link https://tools.ietf.org/html/draft-kelly-json-hal-07})
 * Each element in the dictionary will create an <input> element in the form. 
 * @param {string} id - The id of the form is gonna be populated
 * @param {Object} [template] - a Collection+JSON template ({@link https://github.com/collection-json/spec#23-template}) 
 * which is utlized to set the properties of the <input> elements in the form, or
 * append missing ones. 
 * @param {Array} [exclude] - A list of attributes names from the <i>data</i> parametsr
 * that are not converted in <input> elements.
**/
function fillFormWithHALData(url,data,id,template,exclude){
    $form=$('#'+ id);
    $form.attr("action",url);
    //Clean the forms
    $form_content=$(".form_content",$form);
    $form_content.empty();
    $("input[type='button']",$form).hide();

    for (var attribute_name in data){
        if ($.inArray(attribute_name, exclude) != -1 || attribute_name == "_links")
            continue;
        var $input = $('<input type="text"></input>');
        $input.attr('name',attribute_name);
        $input.attr('value', data[attribute_name]);
        $input.attr('id', attribute_name+"_id");
        $input.attr('readonly','readonly');
        $label_for = $('<label></label>');
        $label_for.attr("for", attribute_name+"_id");
        $label_for.text(attribute_name);
        $form_content.append($label_for);
        $form_content.append($input);
    }
    
    if (template && template.data){
        for (var i =0; i<template.data.length; i++){
            var t_attribute_name = template.data[i].name;
            var input_id = t_attribute_name + "_id";
            var prompt = template.data[i].prompt;
            var required = template.data[i].required;
            var value = template.data[i].value;
            var $template_input = null;
            //If the input already exists
            if ($("#" + input_id, $form).length !== 0) {
                $template_input = $("#" +input_id, $form);
            }
            //Otherwise create it.
            else {
                $template_input = $('<input type="text"></input>');
                $template_input.attr('name',t_attribute_name);
                if(value){
                    $template_input.attr('value', value);
                }
                $template_input.attr('id',input_id);
                $template_label_for = $('<label></label>');
                $template_label_for.attr("for", t_attribute_name+"_id");
                $template_label_for.text(t_attribute_name);
                $form_content.append($template_label_for);
                $form_content.append($template_input);
            }
            $template_input.addClass("editable");
            if(prompt){
                $template_input.attr('placeholder', prompt);
            }
            if(required){
                $template_input.prop('required',true);
                var $label = $("label[for='"+$template_input.attr('id')+"']");
                $label.append(document.createTextNode("*"));
            }
            $template_input.removeAttr("readonly");
        }
    }
}

/**
 * Serialize the input values from a given form (jQuer instance) into a
 * Collection+JSON template.
 * 
 * @param {Object} $form - a jQuery instance of the form to be serailized
 * @returs {Object} An associative array in which each form <input> is converted
 * into an element in the dictionary. It is encapsulate in a Collection+JSON template.
 * @see {@link https://github.com/collection-json/spec#23-template}
**/
function serializeFormTemplate($form){
    var envelope={'template':{
                                'data':[]
    }};
    // get all the inputs into an array.
    var $inputs = $form.find(".form_content input");
    $inputs.each(function(){
        var _data = {};
        _data.name = this.name;
        if (_data.name === "address"){
            _data.object = getAddress($(this).val());
        }
        else
            _data.value = $(this).val();
        envelope.template.data.push(_data);
    });
    return envelope;
}

/**
 * Add a new .message HTML element in the to the #messages_list <div> element.
 * The format of the generated HTML is the following:
 * @example
 *  //<div class='message'>
 *  //        <form action='#'>
 *  //            <div class="commands">
 *  //                <input type="button" class="editButton editMessage" value="Edit"/>
 *  //                <input type="button" class="deleteButton deleteMessage" value="Delete"/>
 *  //             </div>
 *  //             <div class="form_content">
 *  //                <input type=text class="headline">
 *  //                <input type="textarea" class="articlebody">
 *  //             </div>  
 *  //        </form>
 *  //</div>
 *
 * @param {string} url - The url of the created message
 * @param {string} headline - The title of the new message
 * @param {string} articlebody - The body of the crated message. 
**/
function appendMessageToList(url, headline, articlebody) {
        
    var $message = $("<div>").addClass('message').html(""+
                        "<form action='"+url+"'>"+
                        "   <div class='form_content'>"+
                        "       <input type=text class='headline' value='"+headline+"' readonly='readonly'/>"+
                        "       <div class='articlebody'>"+articlebody+"</div>"+
                        "   </div>"+
                        "   <div class='commands'>"+
                        "        <input type='button' class='deleteButton deleteMessage' value='Delete'/>"+
                        "   </div>" +
                        "</form>"
                    );
    //Append to list
    $("#messages_list").append($message);
}

/**
 * Helper method to be called before showing new user data information
 * It purges old user's data and hide all buttons in the user's forms (all forms
 * elements inside teh #userData)
 *
**/
function prepareUserDataVisualization() {
    
    //Remove all children from form_content
    $("#userData .form_content").empty();
    //Hide buttons
    $("#userData .commands input[type='button'").hide();
    //Reset all input in userData
    $("#userData input[type='text']").val("??");
    //Remove old messages
    $("#messages_list").empty();
    //Be sure that the newUser form is hidden
    $("#newUser").hide();
    //Be sure that user information is shown
    $("#userData").show();
    //Be sure that mainContent is shown
    $("#mainContent").show();
}

/**
 * Helper method to visualize the form to create a new user (#new_user_form)
 * It hides current user information and purge old data still in the form. It 
 * also shows the #createUser button.
**/
function showNewUserForm () {
    //Remove selected users in the sidebar
    deselectUser();

    //Hide the user data, show the newUser div and reset the form
    $("#userData").hide();
    var form =  $("#new_user_form")[0];
    form.reset();
    // Show butons
    $("input[type='button']",form).show();
    
    $("#newUser").show();
    //Be sure that #mainContent is visible.
    $("#mainContent").show();
}

/**
 * Helper method that unselects any user from the #user_list and go back to the
 * initial state by hiding the "#mainContent".
**/
function deselectUser() {
    $("#user_list li.selected").removeClass("selected");
    $("#mainContent").hide();
}

/**
 * Helper method to reload current user's data by making a new API call
 * Internally it makes click on the href of the selected user.
**/
function reloadUserData() {
    var selected = $("#user_list li.selected a");
    selected.click();
}

/**** END UI HELPERS ****/

/**** BUTTON HANDLERS ****/



/**** END BUTTON HANDLERS ****/





/*** START ON LOAD ***/
//This method is executed when the webpage is loaded.
$(function(){

    //TODO 1: Add corresponding click handler to all HTML buttons
    // The handlers are:
    // #addUserButton -> handleShowUserForm
    // #deleteUser -> handleDeleteUser
    // #editUser -> handleEditUser
    // #deleteUserRestricted -> handleDeleteUserRestricted
    // #editUserRestricted -> handleEditUserRestricted
    // #createUser -> handleCreateUser
    //
    // Check http://api.jquery.com/on/ for more help.
    /*$("#addUserButton").on("click",  handleShowUserForm);
    $("#deleteUser").on("click", handleDeleteUser);
    $("#editUser").on("click", handleEditUser);
    $("#deleteUserRestricted").on("click", handleDeleteUserRestricted);
    $("#editUserRestricted").on("click", handleEditUserRestricted);
    $("#createUser").on("click", handleCreateUser);*/
	
	
	
    
    //TODO 1: Add corresponding click handlers for .deleteMessage button and
    // #user_list li a anchors. Since these elements are generated dynamically
    // (they are not in the initial HTML code), you must use delegated events.
    // Recommend delegated elements are #messages_list for .deleteMessage buttons and
    // #user_list for "#user_list li a" anchors.
    // The handlers are:
    // .deleteMessage => handleDeleteMessage
    // #user_list li a => handleGetUser
    // More information for direct and delegated events from http://api.jquery.com/on/
    /*$("#user_list").on("click","li a",handleGetUser);
    $("#messages_list").on("click", ".deleteMessage", handleDeleteMessage);
    //Retrieve list of users from the server
    getUsers(ENTRYPOINT);*/
	
});
/*** END ON LOAD**/