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
		$('.prod-edit-pic-li').each(function(){
			var pos = $(this).parent().index() + 1;
			$('span', this).text(pos);
			$('span', this).show();
		});
	};

	updatePos();

	$( "#sortable" ).sortable({
		update: function(event, ui) {
			updatePos();
		}
	});
    $( "#sortable" ).disableSelection();
});