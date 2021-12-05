var outliers = false;
var filetext = '';
var filename = cb_obj.value;

switch (cb_obj.value) {
    case 'raw_data':
        filetext = 'car_id;date;time;certainty;section_name;track_name;\n';
        var raw_data = raw_data_source.data;
        for (var i = 0; i < raw_data['car'].length; i++) {
            var currRow = [
                raw_data['car'][i],
                toDate(raw_data['time'][i]),
                toTime(raw_data['time'][i]),
                raw_data['certainty'][i],
                raw_data['section_name'][i],
                raw_data['track_name'][i],
                '\n'
            ];

            var joined = currRow.join(';');
            filetext = filetext.concat(joined);
        }
        break;

    case 'all_routes':
    	outliers = true
    case 'filtered_routes':
        filetext = 'car_id;departure_date;departure_time;arrival_date;arrival_time;duration[s];start_section;end_section;start_track;end_track;outlier;\n';

        var routes = routes_source.data;
        for (var i = 0; i < routes['car'].length; i++) {
        	if (!routes['outlier'][i] || outliers) {
	            var currRow = [
	                routes['car'][i],
	                toDate(routes['departure'][i]),
	                toTime(routes['departure'][i]),
	                toDate(routes['arrival'][i]),
	                toTime(routes['arrival'][i]),
	                Math.round(routes['duration'][i] * 60),
	                routes['section_name_start'][i],
	                routes['section_name_end'][i],
	                routes['track_name_start'][i],
	                routes['track_name_end'][i],
	                routes['outlier'][i],
	                '\n'
	            ];
	
	            var joined = currRow.join(';');
	            filetext = filetext.concat(joined);
            }
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