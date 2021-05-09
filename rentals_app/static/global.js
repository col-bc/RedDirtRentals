$(document).ready(function () {



    // TODO: Change to Bootstrap.
    //Handle Developer Modal
    $('#developer_option').click(function () {
        $('#fast_add_inventory').addClass('is-active');
    });

    //Handle Modal Close
    $('.modal-close').click(function () {
        $(this).parent().removeClass('is-active');
    });
    $('.modal-background').click(function () {
        $(this).parent().removeClass('is-active')
    });

    //Handle Implement Adder to select
    $('.implement_adder_submit').click(function () {
        let text = $('.implement_adder')
        let list = $('.implement_target');
        if (text.val() !== "") {
            option = new Option(text.val(), text.val());
            list.append(option);
            text.val('');
        }
        $('.implement_target option').prop('selected', true);
    });
    //Handle Implement clear list
    $('.implement_clear').click(function () {
        $('.implement_target')
            .find('option')
            .remove()
            .end()
    });
    //Ensure Implement options are selected on submit
    $('form.has-implement-adder').submit(function () {
        $('.implement_target option').prop('selected', true);
    });

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

    //Prevent forms from being submitted when enter is pressed
    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

});