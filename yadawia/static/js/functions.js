var generateMessage = function (type, selector, message) {
	$(selector).html("<div class='alert alert-" + type + " alert-dismissable fade in' role='alert'>" 
		+ "<a class='close' data-dismiss='alert' aria-label='close'>&times;</a>"
		+ message
		+ "</div>"
	)
};

// FEEDBACK ICONS
var successful_icon = '<i class="fa fa-check success-check"></i>';
var error_icon = '<i class="fa fa-times error-check"></i>';
var loading_icon = '<i class="fa fa-circle-o-notch fa-spin loading-check"></i>';

var offline_check = function (field, check, message) {
	var field_id = '#' + $(field).attr('id');
	var feedback_elem = field_id + '-feedback';
	var error_elem = field_id + '-error-msg';
	if(check) {
		$(field).data('valid', true);
		$(feedback_elem).html(successful_icon);
		$(error_elem).html('');
	} else {
		$(field).data('valid', false);
		$(feedback_elem).html(error_icon);
		$(error_elem).html(message);
	}
}

// for layout page/footer
$(function () { $('#year', '.footer').text(new Date().getFullYear()); });