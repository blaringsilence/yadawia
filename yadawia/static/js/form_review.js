$(function(){
	var form = $('#review-item-form');
	var init_pos = $('#rating', form).val();
	if(init_pos){
		colorUntil(init_pos);
	}
	$(form).submit(function(e){
		e.preventDefault();
		var error_place = $('.main-error-msg', form);
		if($('#rating', form).val() && $('#rating', form).val() !== ''){
			validate_and_send(form, $(form).data('endpoint'), null, null, { productID: $(form).data('product') });
		} else {
			generateMessage('warning', error_place, 'Rating cannot be empty.');
		}
	});

	$('#rate-area i', form).hover(function(){
		var pos = $(this).data('num');
		colorUntil(pos);
	}, function(){
		if($('#rating', form).val() == ''){
			$('#rate-area i').removeClass('fa-star').addClass('fa-star-o');
		} else {
			var pos = $('#rating', form).val();
			colorUntil(pos);
		}
	});

	$('#rate-area i', form).click(function(){
		var pos = $(this).data('num');
		colorUntil(pos);
		$('#rating', form).val(pos);
	});
});