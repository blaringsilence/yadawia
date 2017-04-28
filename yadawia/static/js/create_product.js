var generateCat = function(name, id, disp_element, select_element) {
		$(disp_element).append('<span title="Remove" id="prod-remove-' + id 
								+ '" class="prod-cat-disp-create">' + name + ' <i class="fa fa-times"></i></span>');
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

$(function(){
	var varieties = 0;

	var edit_form = $('#edit-product-form');
	var is_edit = edit_form.length > 0;
	var populate_edit_vars = function (form) {
		var titles = [];
		var prices = [];
		$('.already-var-title').each(function() {
		    titles.push($(this).val());
		});
		$('.already-var-price').each(function() {
		    prices.push($(this).val());
		});

		var disp_element = $('#prod-var-select', form);

		for(var i=0; i<titles.length; i++){
			var class_name = 'varieties-' + varieties;
			generateHidden('variety_title', titles[i], form, class_name);
			generateHidden('variety_price', prices[i], form, class_name);
			generateVar(titles[i], prices[i], disp_element, class_name);
			varieties++;
		}
	};

	if (is_edit) populate_edit_vars(edit_form);

	var cat = function(this_elem) {
		var arr = $(this_elem).val();
		var disp_element = $('#prod-cat-selected');
		$(disp_element).html('');
		if (arr) {
			if (arr.length >= 5) {
				$('option', this_elem).each(function(){
					arr = arr.slice(0,5);
					if(arr.indexOf($(this_elem).val()) === -1) {
						$(this_elem).prop('disabled', true);
						$(this_elem).prop('selected', false);
					}
				});
			} else if (arr.length < 5) {
				$('option:not("#default-cat")', this_elem).prop('disabled', false);
			}
			for(var i=0; i < arr.length; i++) {
				var id = arr[i];
				var name = $('option[value="' + id + '"]', this_elem).text();
				generateCat(name, id, disp_element, this_elem);
			}
		}
	};

	cat($('#prod-cat'));

	$('#prod-cat').change(function(){
		cat(this);
	});

	$('#prod-var-title').bind('click keyup', function(){
		$('#prod-var-add').prop('disabled', $(this).val() === '');
	});

	$('#prod-var-add').click(function(){
		var title_place = $('#prod-var-title');
		var price_place = $('#prod-var-price');
		var title = $(title_place).val();
		var price = $(price_place).val() !== '' ? $(price_place).val() : 'Default';
		var form = is_edit ? $('#edit-product-form') : $('#product-upload-form');
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

	$('#complete-upload').change(function(){
		$('#submit-form').prop('disabled', $(this).val() !== 'true');
		if($(this).val() === 'true'){
			$('#loading').hide();
		}
		else{
			$('#loading').show();
		}
	});
});