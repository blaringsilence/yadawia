$(function(){
	$('#photo', '#change-pic-form').change(function(){
		var input = this;
		if (input.files && input.files[0]) {
	        var reader = new FileReader();
	        reader.onload = function (e) {
	            $('#preview', '#change-pic-form').attr('src', e.target.result);
	        }
	        reader.readAsDataURL(input.files[0]);
	        $('#no-preview').hide();
    	}
	});
});