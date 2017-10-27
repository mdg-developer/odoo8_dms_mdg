(function() {
    'use strict';
    
    // $("li[role='presentation'] > a[role='tab']").css('display','block')
    // $("ul[role='tablist'] > li > a[data-toggle='tab']").css('display','block')

    var $filter_defult = $('#filterOptions li span')
    $filter_defult.removeClass('o_default_snippet_text')
    var $filterType_defult = $('#filterOptions li.active span').attr('class');
    var $holder_defult = $('ul.ourHolder');

    var $data_defult = $holder_defult.clone();
  
    $(document).on('click','#filterOptions li span',function() {
    
        $('#filterOptions li').removeClass('active');
        var $filterType_defult = $(this).attr('class');
        
        $(this).parent().addClass('active');
        
        if ($filterType_defult == 'all') {
            var $filteredData_defult = $data_defult.find('li');
        } 
        else {
            var $filteredData_defult = $data_defult.find('li[data-type=' + $filterType_defult + ']');
        }
        $holder_defult.quicksand($filteredData_defult, {
            duration: 800,
            easing: 'easeInOutQuad'
        });
        return false;
    });
/* 2 column portfolio */
    var $filter_one = $('#filterOptions1 li span')
    $filter_one.removeClass('o_default_snippet_text')
    var $filterType_one = $('#filterOptions1 li.active span').attr('class');
    var $holder_one = $('ul.ourHolder1');

    var $data_one = $holder_one.clone();
  
    $(document).on('click','#filterOptions1 li span',function() {
        $('#filterOptions1 li').removeClass('active');
        var $filterType_one = $(this).attr('class');
        
        $(this).parent().addClass('active');
        
        if ($filterType_one == 'all') {
            var $filteredData_one = $data_one.find('li');
        } 
        else {
            var $filteredData_one = $data_one.find('li[data-type=' + $filterType_one + ']');
        }
        $holder_one.quicksand($filteredData_one, {
            duration: 800,
            easing: 'easeInOutQuad'
        });
        return false;
    });


/* 4 column portfolio */

    var $filter_two = $('#filterOptions2 li span')
    $filter_two.removeClass('o_default_snippet_text')
    var $filterType_two = $('#filterOptions2 li.active span').attr('class');
    var $holder_two = $('ul.ourHolder2');

    var $data_two = $holder_two.clone();
  
    $(document).on('click','#filterOptions2 li span',function() {
        
        $('#filterOptions2 li').removeClass('active');
        var $filterType_two = $(this).attr('class');
        
        $(this).parent().addClass('active');
        
        if ($filterType_two == 'all') {
            var $filteredData_two = $data_two.find('li');
        } 
        else {
            var $filteredData_two = $data_two.find('li[data-type=' + $filterType_two + ']');
        }
        $holder_two.quicksand($filteredData_two, {
            duration: 800,
            easing: 'easeInOutQuad'
        });
        return false;
    });

    
})();

