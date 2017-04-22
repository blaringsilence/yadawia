$(function(){
	var classes = $('#preview').attr('class');
	$('#photo').change(function(){
		var input = this;
		var preview = 0;
		$('.not-init').remove();
		if (input.files && input.files[0]) {
			for(var i=0; i<input.files.length; i++){
				var pic = input.files[i];
				var size_in_mb = pic.size * 0.000001;
				var is_bigger_than_limit = size_in_mb > 16;
				var is_image = pic.type.substr(0,6) === 'image/';
				var disable_submit = is_bigger_than_limit || !is_image;
				offline_check(input, !disable_submit, pic.name +  ' is not an image or is over 16 megabytes.');
				$('#change-pic-submit', '.change-pic-form').prop('disabled', disable_submit);

				if(!disable_submit) {
					$('#init-preview').hide();
					$('#preview-wrapper').append('<img id="preview-' + preview + '" class="not-init ' + classes + '">');
					var url = window.URL.createObjectURL(pic);
			        $('#preview-' + preview).attr('src', url);
			        preview++;
				} else {
					resetValues(input);
					$('#init-preview').show();
					$('.not-init').remove();
					break;
				}
			}
    	} else {
    		$('#init-preview').show();
    		$('.not-init').remove();
    		hide_feedback_elem(input);
    	}
	});

	var resetValues = function(field) {
		$(field).wrap('<form>').closest('form').get(0).reset();
		$(field).unwrap();
	}
});