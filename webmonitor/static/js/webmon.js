/**
 * Created with PyCharm.
 * User: fccoelho
 * Date: 04/06/12
 * Time: 09:30
 *
 */

function create_table(data) {
    //data should be an array of JSON objetcs: [{...},{...},...]
    var table = '';
    table += '<table id="procTable" class="table-condensed table-striped">';
    table +=  "<thead>";
    table +=   "<tr>";
    for (var v in data[0]){
        table += "<th>" + v.toString() + "</th>";
    }
    table +=   "</tr>" ;
    table +=  "</thead>" ;
    table +=  "<tbody>" ;
    // Adding rows
    for (var i = 0; i < data.length; i++) {
        table +=   "<tr>";
        for (var d in data[i]) {
            var cnt = data[i][d];
            if (d == "started at") {
                cnt = new Date(data[i][d]*1000);
                cnt = cnt.toDateString();
            }
            table += "<td>" + cnt + "</td>";
        }
        table +=   "</tr>";
    }
    table +=  "</tbody>" ;
    table +=  "</table>" ;
    return table;
}

var webmon = {};

webmon.monitor = function(){};

webmon.monitor.prototype.get_ts_data = function (nnodes, nnames) {
                var options = {
                    series: { shadowSize:1 }, // drawing is faster without shadows
                    lines: { show: true },
                    points: { show: true },
                    yaxis: { min: 0, max: 100 },
                    xaxis: { show: true, mode: "time", timeformat: "%h:%M"},
        };
                $.getJSON($SCRIPT_ROOT+'/_get_stats', {}, function (data) {
                    for (var i = 0; i < nnodes ; i++) {
                        $.plot($("#placeholder" + i.toString()), data[nnames[i]], options);//[nnames[i]]
                    }
                });
                return "passed";
            };

webmon.monitor.prototype.update_logs = function () {
                var Logs;
                $.getJSON($SCRIPT_ROOT+'/_get_logs', {}, function (logs) {
                    Logs = logs
                    $('#loglist').html(' ');
                    for (var i = 0; i < logs.length; i++) {
                        var l = logs[i];
                        var logbot = '</div>';
                        if (l.level.indexOf("INFO") >= 0) {
                            var logtop = '<div class="alert alert-info"><a class="close" data-dismiss="alert" href="#">×</a>';
                            $('#loglist').append(logtop + '<h4 class="alert-info">' + l.loggerName + '-' + l.level + '-' + l.timest + '</h4>' + l.message + logbot);
                        }

                        else if (l.level.indexOf('WARNING') >= 0) {
                            var logtop = '<div class="alert alert-warning"><a class="close" data-dismiss="alert" href="#">×</a>';
                            $('#loglist').append(logtop + '<h4 class="alert-warning">' + l.loggerName + '-' + l.level + '-' + l.timest + '</h4>' + l.message + logbot);
                        }
                        else if (l.level.indexOf('ERROR') >= 0) {
                            var logtop = '<div class="alert alert-error"><a class="close" data-dismiss="alert" href="#">×</a>';
                            $('#loglist').append(logtop + '<h4 class="alert-error">' + l.loggerName + '-' + l.level + '-' + l.timest + '</h4>' + l.message + logbot);
                        }

                        else if (l.level.indexOf('DEBUG') >= 0) {
                            var logtop = '<div class="alert alert-success"><a class="close" data-dismiss="alert" href="#">×</a>';
                            $('#loglist').append(logtop + '<h4 class="alert-success">'+ l.loggerName + '-' + l.level + '-' + l.timest + '</h4>' + l.message + logbot);
                        }

                    }
                });

    return Logs;
            };

webmon.monitor.prototype.update_jobs = function () {
                var Jobs;
                $.getJSON($SCRIPT_ROOT+'/_get_active_jobs', {}, function (jobs) {
                    Jobs = jobs;
                    $('#joblist').html(' ');
                    for (ip in Jobs) {
                        tbl = create_table(Jobs[ip]);
                        $('#joblist').append('<div class="label label-success">' + ip.toString() + '</div><div id="jobs" class="collapse in">'+tbl+'</div>');
                    }
//                    $('#jobs').collapse()
                });
                return Jobs;
        };


webmon.monitor.prototype.update = function (numbnodes,nodenames, updateInterval) {
                this.update_logs();
                this.get_ts_data(numbnodes,nodenames);
                this.update_jobs();
                //setTimeout(this.update, 1000);
            };


