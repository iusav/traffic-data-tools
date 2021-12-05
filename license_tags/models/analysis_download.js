var outliers = false;
var filetext = '';
var filename = cb_obj.value;

var selected_connections = connections_source.data['connections'];
var selection = lines.selected.indices;
selection.sort(function (a, b) { return a - b });
if (selection.length == 0) {
    selection = [];
    for (var i = 0; i < lines.data['time'].length; i++) {
        selection.push(i);
    }
}
var line_data = lines.data;
var bar_data = bars;

var currRow = ['date', 'time'];
switch (cb_obj.value) {
    case 'lines':
        currRow = currRow.concat(lineHeader());
        filetext = currRow.join(';') + '\n';

        for (var i = 0; i < selection.length; i++) {
            var index = selection[i];
            var datetime = line_data['time'][index];
            currRow = [toDate(datetime), toTime(datetime)];
            currRow = currRow.concat(lineData(index));
            filetext += currRow.join(';') + '\n';
        }
        
        break;
    case 'bars':
        currRow = currRow.concat(barHeader());
        filetext = currRow.join(';') + '\n';

        for (var i = 0; i < selection.length; i++) {
            var index = selection[i];
            var datetime = line_data['time'][index];
            currRow = [toDate(datetime), toTime(datetime)];
            currRow = currRow.concat(barData(index));
            filetext += currRow.join(';') + '\n';
        }

        break;
    case 'lines_and_bars':
        currRow = currRow.concat(lineHeader());
        currRow = currRow.concat(barHeader());
        filetext = currRow.join(';') + '\n';

        for (var i = 0; i < selection.length; i++) {
            var index = selection[i];
            var datetime = line_data['time'][index];
            currRow = [toDate(datetime), toTime(datetime)];
            currRow = currRow.concat(lineData(index));
            currRow = currRow.concat(barData(index));
            filetext += currRow.join(';') + '\n';
        }

        break;
}

var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename + ".csv");
} else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename + ".csv";
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}

function lineHeader() {
    currRow = [];
    var line_column_name_suffixes = [' (q=' + (0.5 - quantile.value).toFixed(2) + ')', ' (median)', ' (q=' + (0.5 + quantile.value).toFixed(2) + ')'];
    for (var k = 0; k < line_column_name_suffixes.length; ++k) {
        for (var j = 0; j < selected_connections.length; j++) {
            currRow = currRow.concat(selected_connections[j] + line_column_name_suffixes[k]);
        }
    }
    return currRow;
}

function lineData(index) {
    var currRow = [];
    for (var k = 0; k < line_name_suffixes.length; ++k) {
        for (var j = 0; j < selected_connections.length; j++) {
            var line_name = selected_connections[j] + line_name_suffixes[k];
            var value = Math.round(line_data[line_name][index] * 60);
            currRow = currRow.concat(value);
        }
    }
    return currRow;
}

function barHeader() {
    currRow = [];
    for (var k = 0; k < bar_mode_names.length; ++k) {
        for (var j = 0; j < selected_connections.length; j++) {
            currRow = currRow.concat(selected_connections[j] + " (" + bar_mode_names[k] + ")");
        }
    }
    return currRow;
}

function barData(index) {
    var currRow = [];
    for (var k = 0; k < bar_mode_names.length; ++k) {
        var bar_mode = bar_mode_names[k];
        var mode_bar_data = bar_data[bar_mode].data;
        for (var j = 0; j < selected_connections.length; j++) {
            var line_name = selected_connections[j];
            var value = mode_bar_data[line_name][index].toLocaleString();
            currRow = currRow.concat(value);
        }
    }
    return currRow;
}

function toTime(datetime) {
	var date_time = new Date(datetime);
    return [pad(date_time.getUTCHours()), pad(date_time.getUTCMinutes()), pad(date_time.getUTCSeconds())].join(':');
}

function toDate(datetime) {
	var date_time = new Date(datetime);
    return [pad(date_time.getUTCDate()), pad(date_time.getUTCMonth() + 1), date_time.getUTCFullYear()].join('.');
}

function pad(number) {
    return ('0' + number).slice(-2);
}