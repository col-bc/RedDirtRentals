$(document).ready(function () {

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