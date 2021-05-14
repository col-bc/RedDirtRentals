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

    // Handle Account tab changes 
    // Hide other tabs by default
    $('#reservations_tab').hide()
    // Switch to reservations
    $('#tab_switcher_reservations').click(function () {
        $('#account_tabs_root').find('li .active').removeClass('active');
        $(this).addClass('active');
        $('#reservations_tab').show();
        $('#index_tab').hide();
    });
    $('#tab_switcher_index').click(function () {
        $('#account_tabs_root').find('li a.active').removeClass('active');
        $(this).addClass('active');
        $('#reservations_tab').hide();
        $('#index_tab').show();
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
    // Clear Implement Adder list
    $('.ia_clear').click(function () {
        $(this).parent().find('ul').empty();
    });

});

// Handle tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

// Handle password visibility
function toggle_password_visibility() {
    let field = $('.password_toggle_field');
    let icon = $('.password_toggle_indicator');
    if (field.prop('type') === "text") {
        field.prop('type', 'password');
        icon.html('visibility_off');
    } else {
        field.prop('type', 'text');
        icon.html('visibility');
    }
}