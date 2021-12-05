var geometry = cb_data['geometry'];
to_select.value = "";
from_select.value = parseDateTime(geometry['x0']);
to_select.value = parseDateTime(geometry['x1']);

function parseDateTime(datetime) {
    var date_time = new Date(datetime);
    var date = [pad(date_time.getUTCDate()), pad(date_time.getUTCMonth() + 1), date_time.getUTCFullYear()].join('.');
    var time = [pad(date_time.getUTCHours()), pad(date_time.getUTCMinutes()), pad(date_time.getUTCSeconds())].join(':');
    return [date, time].join(' ');
}

function pad(number) {
    return ('0' + number).slice(-2);
}