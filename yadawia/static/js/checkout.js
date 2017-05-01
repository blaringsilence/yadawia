$(function(){
	if(window.location.pathname === Flask.url_for('checkout')){
		Cart.update();
		Cart.lock();
		$('#cancel-checkout').click(function(){
			Cart.unlock();
			window.location.pathname = Flask.url_for('cart');
		});
	}
});