$(function(){
	var cw = $('.prod-edit-pic-pic').width();
	$('.prod-edit-pic-pic').css({'height':cw+'px'});

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

	$('.prod-page-date').each(function(){
		var date = $(this).data('date');
		var moment_date = momentDate(date);
		$(this).attr('title', 'Last Updated: ' + moment_date.formatted);
		$(this).text(moment_date.fromNow)
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
	$('#toggle-prod').click(function(){
		var prodID = $(this).data('prod');
		var main_error_place = $('#prod-error-place');
		$.ajax({
			url: Flask.url_for('toggle_availability', { productID: prodID }),
			type: 'POST',
			data: { _csrf_token: $('body').data('csrf') },
			success: function(data) {
				if(data.error){
					generateMessage('warning', main_error_place, data.error);
				} else {
					window.location.reload();
				}
			}
		});
	});

	if($('#variety', cart_form).find(':selected').val() && $('#quantity', cart_form).val() !== ''){
		update_total();
	}
	$(cart_form).change(update_total);

	var updatePos = function(){
		$('.positions', '.hidden-parts').remove();
		$('.prod-edit-pic-li').each(function(){
			var pos = $(this).parent().index() + 1;
			var id = $(this).data('id');
			$('.prod-edit-pic-span', this).text(pos);
			$('.prod-edit-pic-span', this).show();
			$('.hidden-parts', '#prod-pic-edit-form')
				.append('<input type="hidden" class="positions" name="pic_id" value="' + id + '">');
			$('.hidden-parts', '#prod-pic-edit-form')
				.append('<input type="hidden" class="positions rem' + id + '" name="pic_order" value="' + pos + '">')
		});
	};

	updatePos();

	$('.prod-edit-pic-remove').click(function(){
		var parent = $(this).parent();
		var grandparent = $(this).parent().parent();
		var id = $(parent).data('id');
		$('.rem' + id).val('remove');
		$(parent).remove();
		$(grandparent).remove();
	});

	$( "#sortable" ).sortable({
		update: function(event, ui) {
			updatePos();
		}
	});
    $( "#sortable" ).disableSelection();

    $('#add-to-cart').submit(function(e){
    	e.preventDefault();
    	if(window.localStorage.getItem('logged_in') === 'true') {
    		var productID = $(this).data('id');
	    	var quantity = $('#quantity', this).val();
	    	var variety_id = $('#variety', this).val();
	    	var remarks = $('#remarks', this).val();
	    	var p = new Product({ id: productID, quantity: quantity, variety_id: variety_id, remarks: remarks });
	    	try {
	    		Cart.add(p);
	    	} catch(err) {
	    		generateMessage('warning', $('#add-cart-err-place'), err);
	    	}
    	} else {
    		window.location.href = Flask.url_for('login', { next: window.location.pathname });
    	}
    });
});