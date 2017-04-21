$(function(){
	var home = Flask.url_for('home');
	var arg_next = getURLParameter('next');
	var next = arg_next ? arg_next : home;
	$('#nextVal', '#login-form').val(next);
});