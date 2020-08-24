document.addEventListener('DOMContentLoaded', function()
{
    var elements  = document.querySelectorAll('.modal');

    var instances = M.Modal.init(elements);
});

document.addEventListener('DOMContentLoaded', function()
{
    var elements  = document.querySelectorAll('select');

    var instances = M.FormSelect.init(elements);
});

function callback_change_compression_quality()
{
    if ($('#compression_quality_good_id').prop('checked'))
    {
        $('#compression_quality_good_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');

        $('#compression_quality_best_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
    else
    {
        $('#compression_quality_good_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_quality_best_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');
    }
}

function callback_change_compression_format()
{
    if ($('#compression_format_auto_id').prop('checked'))
    {
        $('#compression_format_auto_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');

        $('#compression_format_jpg_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_format_png_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
    else if ($('#compression_format_jpg_id').prop('checked'))
    {
        $('#compression_format_auto_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_format_jpg_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');

        $('#compression_format_png_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
    else
    {
        $('#compression_format_auto_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_format_jpg_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_format_png_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');
    }
}

function callback_change_compression_workers()
{
    if ($('#compression_workers_0_id').prop('checked'))
    {
        $('#compression_workers_0_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');

        $('#compression_workers_5_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_10_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_20_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
    else if ($('#compression_workers_5_id').prop('checked'))
    {
        $('#compression_workers_0_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_5_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');

        $('#compression_workers_10_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_20_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
    else if ($('#compression_workers_10_id').prop('checked'))
    {
        $('#compression_workers_0_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_5_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_10_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');

        $('#compression_workers_20_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
    else
    {
        $('#compression_workers_0_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_5_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_10_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');

        $('#compression_workers_20_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');
    }
}

function callback_change_compression_options()
{
    if ($('#compression_options_copy_id').prop('checked'))
    {
        $('#compression_options_copy_id').siblings().addClass('black-text').removeClass('grey-text text-lighten-1');
    }
    else
    {
        $('#compression_options_copy_id').siblings().addClass('grey-text text-lighten-1').removeClass('black-text');
    }
}

function callback_change_credential_host(element)
{
    if ($(element).val() == '1')
    {
        $(element).parents().eq(6).find('input[id$=json_id]').each(function()
        {
            $(this).parents().eq(1).hide();
        });

        $(element).parents().eq(6).find('input[id$=access_id]').each(function()
        {
            $(this).parents().eq(0).show();
        });

        $(element).parents().eq(6).find('input[id$=secret_id]').each(function()
        {
            $(this).parents().eq(0).show();
        });
    }
    else
    {
        $(element).parents().eq(6).find('input[id$=json_id]').each(function()
        {
            $(this).parents().eq(1).show();
        });

        $(element).parents().eq(6).find('input[id$=access_id]').each(function()
        {
            $(this).parents().eq(0).hide();
        });

        $(element).parents().eq(6).find('input[id$=secret_id]').each(function()
        {
            $(this).parents().eq(0).hide();
        });
    }
}

$(function()
{
    callback_change_compression_quality();

    $('input[name="compress_quality"]').on('change', function()
    {
        callback_change_compression_quality();
    });
});

$(function()
{
    callback_change_compression_format();

    $('input[name="compress_format"]').on('change', function()
    {
        callback_change_compression_format();
    });
});

$(function()
{
    callback_change_compression_workers();

    $('input[name="compress_workers"]').on('change', function()
    {
        callback_change_compression_workers();
    });
});

$(function()
{
    callback_change_compression_options();

    $('input[name="compress_copy"]').on('change', function()
    {
        callback_change_compression_options();
    });
});

$(function()
{
    $('select[id$=host_id]').each(function()
    {
        callback_change_credential_host(this);
    });

    $('select[id$=host_id]').on('change', function()
    {
        callback_change_credential_host(this);
    });
});

$(function()
{
    $('#prompt_success').delay(2500).hide(0);

    $('#prompt_failure').delay(2500).hide(0);
});

// var interval = setInterval(function()
// {
//     $.get('/status', function(response)
//     {
//         $('#overview_status').text(response["overview_status"]);
//         $('#overview_queued').text(response["overview_queued"]);
//         $('#overview_rate').text(response["overview_rate"]);
//         $('#overview_eta').text(response["overview_eta"]);
//         $('#overview_error').text(response["overview_eta"]);
//     });

// }, 5000);