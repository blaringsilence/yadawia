$(function(){
	$('.not-confirmed-button').click(function(){
		var button = $(this);
		var csrf = $('body').data('csrf');
		var item_id = $(button).data('item');
		$(button).prop('disabled', true);
		$(button).css('cursor', 'wait');
		$.ajax({
			url: Flask.url_for('confirm_item'),
			data: { _csrf_token: csrf, item_id: item_id },
			method: 'POST',
			success: function(data){
				$(button).css('cursor', 'auto');
				if(!data.error){
					$(button).removeClass('.not-confirmed-button');
					$(button).html('<i class="fa fa-check-circle"></i> Item confirmed');
				} else {
					$(button).prop('disabled', false);
					alert('There was a problem. Try again later.');
				}
			}
		});
	});
});