$(document).ready(function(){
  $('.parallax').parallax();
  $('.tooltipped').tooltip();
  $('.fixed-action-btn').floatingActionButton();
  $('.sidenav').sidenav();
  $('select').formSelect();
  $('.modal').modal();
});

$('.scale-trigger').click(function(){
  $('#scale-element').toggleClass('scale-out');
});

$('.copy-trigger').click(function(){
  copyText = document.getElementById('copy-text');
  copyText.select();
  document.execCommand('copy');
  $('.copy-notif').toggleClass('scale-out');
});
