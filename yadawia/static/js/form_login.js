$(function(){
	var home = Flask.url_for('home');
	var this_page = window.location.pathname;
	var next = home === this_page ? Flask.url_for('login') : this_page;
	$('#nextVal', '#login-form').val(next);
});