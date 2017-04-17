var generateMessage = function (type, selector, message) {
	$(selector).html("<div class='alert alert-" + type + " alert-dismissable fade in' role='alert'>" 
		+ "<a class='close' data-dismiss='alert' aria-label='close'>&times;</a>"
		+ message
		+ "</div>"
	)
};