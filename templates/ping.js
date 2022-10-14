$(document).ready(function(){
    $('#sample_form').on('submit', function(event){
      event.preventDefault();
      var count_error = 0;
     
      if($('#ip').val() == '')
      {
       $('#first_name_error').text('User Name is required');
       count_error++;
      }
     
      if(count_error == 0)
      {
       $.ajax({
      url:"/ajaxprogressbar",
      method:"POST",
      data:$(this).serialize(),
      beforeSend:function()
      {
       $('#save').attr('disabled', 'disabled');
       $('#process').css('display', 'block');
      },
      success:function(data)
      { 
       var percentage = 0;
     
       var timer = setInterval(function(){
        percentage = percentage + 20;
        progress_bar_process(percentage, timer,data);
       }, 1000);
      }
     })
      }
      else
      {
       return false;
      }
        
     });
       
     function progress_bar_process(percentage, timer,data)
     {
    $('.progress-bar').css('width', percentage + '%');
    if(percentage > 100)
    {
     clearInterval(timer);
     $('#sample_form')[0].reset();
     $('#process').css('display', 'none');
     $('.progress-bar').css('width', '0%');
     $('#save').attr('disabled', false);
     $('#success_message').html(data);
     setTimeout(function(){
      $('#success_message').html('');
     }, 5000);
    }
     }
       
    });