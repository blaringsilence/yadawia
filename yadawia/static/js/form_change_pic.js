$(function(){
	$('#photo').change(function(){
		var input = this;

		// 1. Reset everything => empty preview, no feedback element.

		$('#preview').attr('src', '');
		hide_feedback_elem(input);
		$('#little-previews', '#preview-wrapper').html('');
		// 2. If there are files..
		if (input.files && input.files[0]) {
			// 2.1 Put the other images if they pass validation in a grid below the big image,
			// 	   and display the first one in the big preview.
			for(var i=0; i<input.files.length; i++){
				var pic = input.files[i];
				var size_in_mb = pic.size * 0.000001;
				var is_bigger_than_limit = size_in_mb > 16;
				var is_image = pic.type.substr(0,6) === 'image/';
				var disable_submit = is_bigger_than_limit || !is_image;
				offline_check(input, !disable_submit, pic.name +  ' is not an image or is over 16 megabytes.');
				$('#change-pic-submit', '.change-pic-form').prop('disabled', disable_submit);

				if(!disable_submit) { // if valid
					var url = window.URL.createObjectURL(pic);
					$('#init-preview').hide(); // #init-preview is the element that says "No preview available"
					if($(input).attr('multiple')){
						$('#little-previews', '#preview-wrapper').append('<img id="preview-' + i 
																		+ '" src="' + url 
																		+ '" class="little-preview-pic">');
					}

					if(i==0) {
						$('#preview').attr('src', url);
					}
				} else {
					resetValues(input);
					$('#preview').attr('src', '');
					$('#init-preview').show();
					$('#little-previews', '#preview-wrapper').html('');
					break;
				}
			}
			$('.little-preview-pic').click(function(){
				var url = $(this).attr('src');
				$('#preview').attr('src', url);
			});
    	} else {
    		$('#init-preview').show();
    	}
	});

	var resetValues = function(field) {
		$(field).wrap('<form>').closest('form').get(0).reset();
		$(field).unwrap();
	}
});