$(document).ready(function () {

    // Handle Mobile Menu Click
    $(".navbar-burger").click(function () {
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
    });

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
    
    //Handle Radio Icon State Changes
    $('.radio-icn input').change(function () {
        $('.radio-icn').css('border', '2px solid whitesmoke');
        $(this).parent().css('border', '2px solid silver');
    });

    //Handle Inventory Shade
    $('.expand-toggle').click(function () {
        let shade = $(this).parent().parent().find('.shade')
        let classes = shade.attr("class").split(/\s+/);

        if (~classes.indexOf("is-hidden")) {
            shade.removeClass('is-hidden');
            $('button.expand-toggle').css("transform", "rotate(180deg)")
        } else {
            shade.addClass('is-hidden')
            $('button.expand-toggle').css("transform", "rotate(0deg)")
        }
    });
    //Handle Individual Shade Changes
    $('.tab-item').click(function () {
        $('.tabs ul li').removeClass('is-active')
        if ($(this).hasClass('is-active')) {
            $(this).removeClass('is-active');
        } else {
            $(this).addClass('is-active');
        }
        if ($('.tab-item.is-active').children().attr('id') == "reservations_tab") {
            $('#inventory_tab_view').addClass('is-hidden');
            $('#reservations_tab_view').removeClass('is-hidden');
        } else {
            $('#reservations_tab_view').addClass('is-hidden');
            $('#inventory_tab_view').removeClass('is-hidden');
        }
    });
    //Handle All Shade Changes
    $('#collapse_all_inventory').click(function () {
        $('#inventory_tab_view').find('.shade').addClass('is-hidden');
        $('#inventory_tab_view').find('button.expand-toggle').css('transform', 'rotate(0deg)')
    });
    $('#show_all_inventory').click(function () {
        $('#inventory_tab_view').find('.shade').removeClass('is-hidden')
        $('#inventory_tab_view').find('button.expand-toggle').css('transform', 'rotate(180deg)')
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
    $('form.has-implement-adder').submit(function(){
        $('.implement_target option').prop('selected', true);
    });

    //Prevent forms from being submitted when enter is pressed
    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

});

// Handle Notification Close
document.addEventListener('DOMContentLoaded', () => {
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        const $notification = $delete.parentNode;
        $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });
});