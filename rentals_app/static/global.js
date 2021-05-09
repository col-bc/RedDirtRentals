$(document).ready(function () {

    // Handle Admin Tab Changes
    // Set reservations hidden by default
    $('#reservation_tab_content').hide();
    $('#customer_tab_content').hide();
    $('#inventory_tab_selector').click(function () {
        $('#tab_root').find('.active').removeClass('active')
        $('#inventory_active_elem').addClass('active');

        $('#customer_tab_content').hide();
        $('#reservations_tab_content').hide();
        $('#inventory_tab_content').show();
    });
    $('#reservations_tab_selector').click(function () {
        $('#tab_root').find('.active').removeClass('active')
        $('#reservations_tab_selector').addClass('active');

        $('#customer_tab_content').hide();
        $('#inventory_tab_content').hide();
        $('#reservation_tab_content').show();
    });
    $('#customer_tab_selector').click(function () {
        $('#tab_root').find('.active').removeClass('active')
        $('#customer_tab_selector').addClass('active')

        $('#reservation_tab_content').hide();
        $('#inventory_tab_content').hide();
        $('#customer_tab_content').show();
    });

    // Handle Implement Adder
    $('.ia_submit').click(function () {
        let field = $(this).parent().find('.ia_input');
        let list = $('.ia_target');

        if (field.val() !== '') {
            let implement = field.val();
            let html = '<li class="list-group-item">' + implement + '</li>';
            list.append(html);
            field.val('');
            field.focus();
        }
    });
    $('.ia_clear').click(function () {
        $(this).parent().find('ul').empty();
     });

    //Prevent forms from being submitted when enter is pressed
    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

});