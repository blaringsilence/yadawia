$(function(){
	if(window.location.pathname === Flask.url_for('checkout')){
		Cart.update();
		$('#finalize-order').prop('disabled', true);
		$('.checkout-invoice ul').html('');
		if(!Cart.isEmpty()){
			Cart.lock();
			$('.checkout-nonempty').show();
			$('.go-to-cart').hide();
			getCartProductInfo(function(d){
				errors = 0;
				for(var i in d.items){
					if(d.items[i].error) {
						generateMessage('danger', $('.checkout-error-place'), 
										d.items[i].error + ' This item has been removed from your cart.', true);
						Cart.unlock();
						Cart.remove(d.items[i].product_id, d.items[i].variety_id);
						Cart.lock();
						errors++;
					}
				}
				if(errors === d.items.length) {
					Cart.unlock(); 
					$('.checkout-nonempty').hide(); 
					$('.go-to-cart').show(); 
				} else {
					for(var i in d.items){
						var prod = Cart.products[Cart.find(d.items[i].product_id, d.items[i].variety_id)];
						$('.checkout-invoice ul').append('<li>'
														+ prod.quantity
														+ ' X '
														+ d.items[i].product_name
														+ ' (' + d.items[i].variety_name + ') '
														+ ' = '
														+ d.items[i].price
														+ ' X '
														+ prod.quantity
														+ ' = '
														+ d.items[i].price * prod.quantity
														+ ' ' + d.items[i].currency
														+'</li>');
						$('#checkout-form').append('<input type="hidden" name="product_id" value="'
													+ prod.id
													+ '">');
						$('#checkout-form').append('<input type="hidden" name="variety_id" value="'
													+ prod.variety_id
													+ '">');
						$('#checkout-form').append('<input type="hidden" name="price" value="'
													+ d.items[i].price
													+ '">');
						$('#checkout-form').append('<input type="hidden" name="currency" value="'
													+ d.items[i].currency
													+ '">');
						$('#checkout-form').append('<input type="hidden" name="quantity" value="'
													+ prod.quantity
													+ '">');
						$('#checkout-form').append('<input type="hidden" name="remark" value="'
													+ prod.remarks
													+ '">');
						$('#finalize-order').prop('disabled', false);
					}
				var total_arr = [];
				for(key in d.total_price){
					total_arr.push(key + ' ' + d.total_price[key]);
				}
				$('.total-before-method').text('Total before payment method fees: ' + total_arr.join(' + '));
				}
			});
			$('#cancel-checkout').click(function(){
				Cart.unlock();
				window.location.pathname = Flask.url_for('cart');
			});
		} else {
			Cart.unlock();
			$('.go-to-cart').show();
		}
	}
});