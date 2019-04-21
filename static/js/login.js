/***
 * page: login.html
 */

$('#user').focusin(function () {
    $('.error_user').empty();
    $('.error').empty();
});
$('#pwd').focusin(function () {
    $('.error_pwd').empty();
});
$('#btn').click(function () {
    if ($('#user').val() == "" || $('#user').val().length < 6) {
        $('.error_user').text("用户名不能为空,用户名大于6位")
    }
    if ($('#pwd').val() == "" || $('#pwd').val().length < 6) {
        $('.error_pwd').text("密码不能为空,密码大于6位")
    }
    if ($('#user').val().length >= 6 && $('#pwd').val().length >= 6) {
        $.post('/', {
                "user": $('#user').val(),
                "pwd": $('#pwd').val(),
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val()
            },
            function (data) {
                if (data.code == 1) {
                    location.href = data.url
                } else {
                    $('.error').text('用户名或者密码错误')
                }
            })
    }
})
/**
 *  page : index.html
 * */

$('#true_btn').click(function () {
    $.get('/delete_all/', {}, function (data) {
        if (data.code == 1) {
            location.href = data.url
        }
    })
})