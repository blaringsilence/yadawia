var formatCartData = function(products) {
	var product_id = [];
	var product_variety = [];
	var product_quantity = [];
	for(var i=0; i<products.length; i++) {
		var p = products[i]
		product_id.push(p.id);
		product_variety.push(p.variety_id);
		product_quantity.push(p.quantity);
	}
	return { pid: product_id, pvar: product_variety, pq: product_quantity };
}

var update_list = function() {
	var cart_page = Flask.url_for('cart');
	if(window.location.pathname !== cart_page) { return false; }
	var list_place = $('#cart-items-list');
	var total_price_place = $('.total-price-wrapper h3');
	var cart_btns = $('.cart-buttons button');
	$(list_place).html('');
	$(total_price_place).html('');
	$(cart_btns).hide();
	Cart.update(); // so we don't have to rely on order of functions executed.
	if(Cart.isEmpty()) {
		$(list_place).append('<li><h4>Your cart is empty.</h4></li>');
	} else {
		var data = formatCartData(Cart.products);
		$.getJSON(Flask.url_for('cart_products'), {
			product_id: data.pid,
			product_variety: data.pvar,
			product_quantity: data.pq
		}, function (d) {
			if(!d.error){
				errors = 0
				for(var i in d.items) {
					var item = d.items[i];
					var prod = Cart.products[Cart.find(item.product_id, item.variety_id)];
					if(!item.error){
						var remarks = prod.remarks ? '"' + prod.remarks + '" <br>' : '';
						$(list_place).append('<li class="cart-product-item" data-productID="' 
											+ item.product_id 
											+ '" data-varietyID="' 
											+ item.variety_id 
											+ '"><h4>' 
											+ '<a href="' 
											+ Flask.url_for('product', { productID: item.product_id }) 
											+ '" target="_blank">' 
											+ item.product_name 
											+ '</a>'
											+ ' (' + item.variety_name + ')'
											+ ' '
											+ '<small>' + item.currency + ' ' + item.price 
											+ ' X ' + prod.quantity 
											+ ' = ' + item.price * prod.quantity + '</small>'
											+'</h4>'
											+ remarks
											+ '<small class="added-when" title="' 
											+ moment(prod.date_added).format('MMMM Do YYYY, h:mm:ss a') 
											+ '">Added to cart ' 
											+ moment(prod.date_added).fromNow() 
											+ '</small>'
											+ '<small><button class="btn btn-danger remove-from-cart-btn">Remove</button>'
											+ '</li>');	
					} else {
						$(list_place).append('<li id="' + prod.id + '-' + prod.variety_id + '"></li>');
						generateMessage('error', $('#' + prod.id + '-' + prod.variety_id), item.error);
						var id_in_cart = Cart.find(item.product_id, item.variety_id);
						Cart.remove(item.product_id, item.variety_id, true);
						errors++;
					}
				}
				if(errors !== d.items.length){ // if at least 1 is not an error
					total_price = [];
					for (var property in d.total_price) {
					    if (d.total_price.hasOwnProperty(property)) {
					    	total_price.push(property + ' ' + d.total_price[property]);
					    }
					}
					$(total_price_place).html('<i class="fa fa-calculator"></i> Total: ' + total_price.join(' + '));	
					$(cart_btns).show();
					$('.remove-from-cart-btn').click(function(){
						var product_elem = $(this).parent().parent();
						var product_id = $(product_elem).data('productid');
						var variety_id = $(product_elem).data('varietyid');
						Cart.remove(product_id, variety_id);
					});
				}
			}
		});
	}
}
$(function(){
	update_list();
	window.addEventListener('storage', function(event){
		if(event.key === 'cart') {
			update_list();
		}
	}, false);
	$(window).on('cartChange', update_list);
	$('.clear-cart-btn').dblclick(function(){ Cart.clear(); });
});