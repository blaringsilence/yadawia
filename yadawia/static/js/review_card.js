$(function(){
	$('.review-date').each(function(){
		var date = $(this).data('date');
		var moment_date = momentDate(date);
		$(this).attr('title', moment_date.formatted);
		$(this).text(moment_date.fromNow);
	});
});