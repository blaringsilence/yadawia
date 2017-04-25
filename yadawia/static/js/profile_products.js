$(function(){
	$('.prod-card-date', '.product-card').each(function(){
		var date = $(this).data('date');
		var moment_date = momentDate(date);
		$(this).attr('title', 'Last Updated: ' + moment_date.formatted);
		$(this).text(moment_date.fromNow)
	});
});