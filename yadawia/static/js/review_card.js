$(function(){
	$('.review-date').each(function(){
		var date = $(this).data('date');
		var moment_date = moment.utc(date).local();
		$(this).attr('title', moment_date.format('MMMM Do YYYY, h:mm:ss a'));
		$(this).text(moment_date.fromNow());
	});
});