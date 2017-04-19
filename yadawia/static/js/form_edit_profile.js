$(function(){
	$('#edit-profile-form').submit(function(e){
		e.preventDefault();
		var form = this;
		var username = $('#edit-username', form).val();
		validate_and_send(form, 'edit_profile', '', Flask.url_for('profile', { 'username': username }));
	});
});