$(function(){
	$('#photo', '#change-pic-form').change(function(){
		var input = this;
		if (input.files && input.files[0]) {
			var pic = input.files[0];
			var size_in_mb = pic.size * 0.000001;
			var is_bigger_than_limit = size_in_mb > 16;
			var is_image = pic.type.substr(0,6) === 'image/';
			var disable_submit = is_bigger_than_limit || !is_image;
			offline_check(input, !disable_submit, 'Must be an image under 16 megabytes.');
			$('#change-pic-submit', '#change-pic-form').prop('disabled', disable_submit);

			if(!disable_submit) {
				var reader = new FileReader();
		        reader.onload = function (e) {
		            $('#preview', '#change-pic-form').attr('src', e.target.result);
		        }
		        reader.readAsDataURL(pic); 
		        $('#no-preview').hide();
			}
    	}
	});
});