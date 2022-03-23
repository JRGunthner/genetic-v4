google.charts.load('current', {'packages':['gantt']});
google.charts.setOnLoadCallback(drawChart);

function minutesToMilliseconds(minutes) {
    return minutes * 60 * 1000;
}

function drawChart() {

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Task ID');
    data.addColumn('string', 'Task Name');
    data.addColumn('string', 'Resource');
    data.addColumn('date', 'Start Date');
    data.addColumn('date', 'End Date');
    data.addColumn('number', 'Duration');
    data.addColumn('number', 'Percent Complete');
    data.addColumn('string', 'Dependencies');

    data.addRows([
        ['a1', 'a1', "['1']", new Date(2019,5,1,10,20), new Date(2019,5,1,11,5), minutesToMilliseconds(30), 100, null],
        ['b1', 'b1', "['1']", new Date(2019,5,1,14,20), new Date(2019,5,1,15,30), minutesToMilliseconds(30), 100, null],
        ['d1', 'd1', "['1']", new Date(2019,5,1,9,20), new Date(2019,5,1,9,40), minutesToMilliseconds(30), 100, null],
        ['e1', 'e1', "['1']", new Date(2019,5,1,11,5), new Date(2019,5,1,11,55), minutesToMilliseconds(30), 100, null],
        ['f1', 'f1', "['1']", new Date(2019,5,1,9,0), new Date(2019,5,1,9,20), minutesToMilliseconds(30), 100, null],
        ['g1', 'g1', "['1']", new Date(2019,5,1,9,40), new Date(2019,5,1,10,0), minutesToMilliseconds(30), 100, null],
        ['h1', 'h1', "['1']", new Date(2019,5,1,10,0), new Date(2019,5,1,10,20), minutesToMilliseconds(30), 100, null],
        ['i1', 'i1', "['1']", new Date(2019,5,1,13,0), new Date(2019,5,1,13,20), minutesToMilliseconds(30), 100, null],
        ['c1', 'c1', "['1']", new Date(2019,5,1,13,20), new Date(2019,5,1,14,20), minutesToMilliseconds(30), 100, null],
        ['e5', 'e5', "['4']", new Date(2019,5,1,13,0), new Date(2019,5,1,13,35), minutesToMilliseconds(30), 100, 'e1'],
        ['e6', 'e6', "['8']", new Date(2019,5,1,14,45), new Date(2019,5,1,15,30), minutesToMilliseconds(30), 100, 'e1'],
        ['b2', 'b2', "['6']", new Date(2019,5,1,15,30), new Date(2019,5,1,16,35), minutesToMilliseconds(30), 100, 'b1'],
        ['a2', 'a2', "['6']", new Date(2019,5,1,13,20), new Date(2019,5,1,14,25), minutesToMilliseconds(30), 100, 'a1'],
        ['c7', 'c7', "['8']", new Date(2019,5,1,14,20), new Date(2019,5,1,14,45), minutesToMilliseconds(30), 100, 'c1'],
        ['d2', 'd2', "['6']", new Date(2019,5,1,9,40), new Date(2019,5,1,10,10), minutesToMilliseconds(30), 100, 'd1'],
        ['d3', 'd3', "['3']", new Date(2019,5,1,9,40), new Date(2019,5,1,9,55), minutesToMilliseconds(30), 100, 'd1'],
        ['e7', 'e7', "['5']", new Date(2019,5,1,15,30), new Date(2019,5,1,16,0), minutesToMilliseconds(30), 100, 'e5,e6'],
        ['a3', 'a3', "['3']", new Date(2019,5,1,14,25), new Date(2019,5,1,15,15), minutesToMilliseconds(30), 100, 'a2'],
        ['b6', 'b6', "['8']", new Date(2019,5,1,16,35), new Date(2019,5,1,17,30), minutesToMilliseconds(30), 100, 'b2'],
        ['b3', 'b3', "['3']", new Date(2019,5,1,16,35), new Date(2019,5,1,17,10), minutesToMilliseconds(30), 100, 'b2'],
        ['b7', 'b7', "['5']", new Date(2019,5,1,17,30), new Date(2019,5,1,17,50), minutesToMilliseconds(30), 100, 'b6'],
        ['a5', 'a5', "['4']", new Date(2019,5,1,16,35), new Date(2019,5,1,17,30), minutesToMilliseconds(30), 100, 'a3'],
        ['b4', 'b4', "['6']", new Date(2019,5,1,17,10), new Date(2019,5,1,17,50), minutesToMilliseconds(30), 100, 'b3'],
        ['a6', 'a6', "['8']", new Date(2019,5,1,17,30), new Date(2019,5,1,18,0), minutesToMilliseconds(30), 100, 'a5'],
    ]);

    var data2 = new google.visualization.DataTable();
    data2.addColumn('string', 'Task ID');
    data2.addColumn('string', 'Task Name');
    data2.addColumn('string', 'Resource');
    data2.addColumn('date', 'Start Date');
    data2.addColumn('date', 'End Date');
    data2.addColumn('number', 'Duration');
    data2.addColumn('number', 'Percent Complete');
    data2.addColumn('string', 'Dependencies');

    data2.addRows([
        ['a1', 'a1', "[u'1']", new Date(2019,5,1,9,0), new Date(2019,5,1,9,45), minutesToMilliseconds(30), 100, null],
        ['b1', 'b1', "[u'1']", new Date(2019,5,1,14,20), new Date(2019,5,1,15,30), minutesToMilliseconds(30), 100, null],
        ['d1', 'd1', "[u'1']", new Date(2019,5,1,10,5), new Date(2019,5,1,10,25), minutesToMilliseconds(30), 100, null],
        ['e1', 'e1', "[u'1']", new Date(2019,5,1,10,25), new Date(2019,5,1,11,15), minutesToMilliseconds(30), 100, null],
        ['f1', 'f1', "[u'1']", new Date(2019,5,1,11,35), new Date(2019,5,1,11,55), minutesToMilliseconds(30), 100, null],
        ['g1', 'g1', "[u'1']", new Date(2019,5,1,13,0), new Date(2019,5,1,13,20), minutesToMilliseconds(30), 100, null],
        ['h1', 'h1', "[u'1']", new Date(2019,5,1,9,45), new Date(2019,5,1,10,5), minutesToMilliseconds(30), 100, null],
        ['i1', 'i1', "[u'1']", new Date(2019,5,1,11,15), new Date(2019,5,1,11,35), minutesToMilliseconds(30), 100, null],
        ['c1', 'c1', "[u'1']", new Date(2019,5,1,13,20), new Date(2019,5,1,14,20), minutesToMilliseconds(30), 100, null],
        ['e5', 'e5', "[u'4']", new Date(2019,5,1,11,15), new Date(2019,5,1,11,50), minutesToMilliseconds(30), 100, 'e1'],
        ['e6', 'e6', "[u'8']", new Date(2019,5,1,14,45), new Date(2019,5,1,15,30), minutesToMilliseconds(30), 100, 'e1'],
        ['b2', 'b2', "[u'6']", new Date(2019,5,1,15,30), new Date(2019,5,1,16,35), minutesToMilliseconds(30), 100, 'b1'],
        ['a2', 'a2', "[u'6']", new Date(2019,5,1,13,20), new Date(2019,5,1,14,25), minutesToMilliseconds(30), 100, 'a1'],
        ['c7', 'c7', "[u'8']", new Date(2019,5,1,14,20), new Date(2019,5,1,14,45), minutesToMilliseconds(30), 100, 'c1'],
        ['d2', 'd2', "[u'6']", new Date(2019,5,1,10,25), new Date(2019,5,1,10,55), minutesToMilliseconds(30), 100, 'd1'],
        ['d3', 'd3', "[u'3']", new Date(2019,5,1,10,25), new Date(2019,5,1,10,40), minutesToMilliseconds(30), 100, 'd1'],
        ['e7', 'e7', "[u'5']", new Date(2019,5,1,15,30), new Date(2019,5,1,16,0), minutesToMilliseconds(30), 100, 'e5,e6'],
        ['a3', 'a3', "[u'3']", new Date(2019,5,1,14,25), new Date(2019,5,1,15,15), minutesToMilliseconds(30), 100, 'a2'],
        ['b6', 'b6', "[u'8']", new Date(2019,5,1,16,35), new Date(2019,5,1,17,30), minutesToMilliseconds(30), 100, 'b2'],
        ['b3', 'b3', "[u'3']", new Date(2019,5,1,16,35), new Date(2019,5,1,17,10), minutesToMilliseconds(30), 100, 'b2'],
        ['b7', 'b7', "[u'5']", new Date(2019,5,1,17,30), new Date(2019,5,1,17,50), minutesToMilliseconds(30), 100, 'b6'],
        ['a5', 'a5', "[u'4']", new Date(2019,5,1,16,35), new Date(2019,5,1,17,30), minutesToMilliseconds(30), 100, 'a3'],
        ['b4', 'b4', "[u'6']", new Date(2019,5,1,17,10), new Date(2019,5,1,17,50), minutesToMilliseconds(30), 100, 'b3'],
        ['a6', 'a6', "[u'8']", new Date(2019,5,1,17,30), new Date(2019,5,1,18,0), minutesToMilliseconds(30), 100, 'a5']
    ]);

    var options = {
        height: 1900
    };

    var chart = new google.visualization.Gantt(document.getElementById('chart_div'));
    chart.draw(data, options);

    var chart2 = new google.visualization.Gantt(document.getElementById('chart_div-2'));
    chart2.draw(data2, options);
}
