$(function(){
	var pictures = $('.prod-page-pic');
	var empty_circle = '<i class="fa fa-circle-o"></i>';
	var full_circle = '<i class="fa fa-circle"></i>';

	$(pictures).each(function(){
		var pic = this;
		var circ_id = $(this).data('circle');
		$('#prod-pic-circles').append('<span class="prod-circle" data-pic="' 
									+ $(pic).attr('id') 
									+ '" id="' + circ_id 
									+ '">' + empty_circle 
									+ '</span>');
	});

	$('.prod-circle').click(function(){
		var pic = '#' + $(this).data('pic');
		$(pic).triggerHandler('show');
	});

	$(pictures).click(function(){
		var url = $(this).attr('src');
		$('#zoomed-pic', '#prod-pic').attr('src', url);
		$('#prod-pic').modal('show');
	});

	$(pictures).on('show', function(e, info){
		$(pictures).hide();
		$(this).show();
		var circ_id = '#' + $(this).data('circle');
		$('.prod-circle').html(empty_circle);
		$(circ_id).html(full_circle);
	});

	$(pictures).first().triggerHandler('show');

	var cart_form = $('#add-to-cart');

	var update_total = function(){
		$('#total-price', cart_form).show();
		var price_per_unit = $('#variety', cart_form).find(':selected').data('price');
		var quantity = $('#quantity', cart_form).val();
		var total = price_per_unit * quantity;
		$('#total-disp', cart_form).text(total);
	}

	if($('#variety', cart_form).find(':selected').val() && $('#quantity', cart_form).val() !== ''){
		update_total();
	}
	$(cart_form).change(update_total);
});