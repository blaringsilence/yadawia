$(function(){
	var varieties = 0;

	$('#prod-cat', '#product-upload-form').change(function(){
		var arr = $(this).val();
		var disp_element = $('#prod-cat-selected');
		$(disp_element).html('');
		console.log('clicked');
		if (arr) {
			if (arr.length >= 5) {
				$('option', this).each(function(){
					arr = arr.slice(0,5);
					if(arr.indexOf($(this).val()) === -1) {
						$(this).prop('disabled', true);
						$(this).prop('selected', false);
					}
				});
			} else if (arr.length < 5) {
				$('option:not("#default-cat")', this).prop('disabled', false);
			}
			for(var i=0; i < arr.length; i++) {
				var id = arr[i];
				var name = $('option[value="' + id + '"]', this).text();
				generateCat(name, id, disp_element, this);
			}
		}
	});

	$('#prod-var-title', '#product-upload-form').bind('click keyup', function(){
		$('#prod-var-add', '#product-upload-form').prop('disabled', $(this).val() === '');
	});

	$('#prod-var-add', '#product-upload-form').click(function(){
		var title_place = $('#prod-var-title', '#product-upload-form');
		var price_place = $('#prod-var-price', '#product-upload-form');
		var title = $(title_place).val();
		var price = $(price_place).val() !== '' ? $(price_place).val() : 'Default';
		var form = $('#product-upload-form');
		var disp_element = $('#prod-var-select', form);
		var class_name = 'varieties-' + varieties;
		varieties++;

		generateHidden('variety_title', title, form, class_name);
		generateHidden('variety_price', price, form, class_name);

		generateVar(title, price, disp_element, class_name);

		$(title_place).val('');
		$(price_place).val('');

		$(this).prop('disabled', true);
	});

	var generateCat = function(name, id, disp_element, select_element) {
		$(disp_element).append('<span title="Remove" id="prod-remove-' + id 
								+ '" class="prod-cat-disp">' + name + ' <i class="fa fa-times"></i></span>');
		$('#prod-remove-' + id).click(function(){
			$('#cat-' + id).prop('selected', false);
			$(select_element).change();
		});
	}

	var generateVar = function(title, price, disp_element, class_name) {
		$(disp_element).append('<span title="Remove" id="prod-var-remove-' + class_name
								+ '" class="prod-var-disp">' + title + ', Price: ' + price 
								+ ' <i class="fa fa-times"></i></span>');
		$('#prod-var-remove-' + class_name).click(function(){
			$('.' + class_name).remove();
			$(this).remove();
		});
	}

});