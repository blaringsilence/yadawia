$(function(){
	$('#photo').change(function(){
		var input = this;

		// 1. Reset everything => empty preview, no feedback element.

		$('#preview').attr('src', '');
		hide_feedback_elem(input);
		$('#little-previews', '#preview-wrapper').html('');
		$('#photo-urls').html('');
		$('#complete-upload').val('false').trigger('change');

		// 2. If there are files..
		if (input.files && input.files[0]) {
			// 2.1 Put the other images if they pass validation in a grid below the big image,
			// 	   and display the first one in the big preview.
			var i;
			for(i=0; i<input.files.length; i++){
				var pic = input.files[i];
				var size_in_mb = pic.size * 0.000001;
				var is_bigger_than_limit = size_in_mb > 10;
				var is_image = pic.type.substr(0,6) === 'image/';
				var disable_submit = is_bigger_than_limit || !is_image;
				offline_check(input, !disable_submit, pic.name +  ' is not an image or is over 16 megabytes.');

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
			if(i===input.files.length) {
				$('.little-preview-pic').click(function(){
					var url = $(this).attr('src');
					$('#preview').attr('src', url);
				});
				$('#photo-urls').data('number', input.files.length);
				uploadPicsToS3(input.files, $('#photo-urls'), $('#complete-upload'));
			}
    	} else {
    		$('#init-preview').show();
    	}
	});

	$('#complete-upload', '.change-pic-form').change(function(){
		$('#change-pic-submit', '.change-pic-form').prop('disabled', $(this).val() !== 'true');
	});

	var resetValues = function(field) {
		$(field).wrap('<form>').closest('form').get(0).reset();
		$(field).unwrap();
	}
});