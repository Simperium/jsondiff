$(function(){
    var jd = new jsondiff();
    var methodmap = {
        diff: jd.diff
    }

    $.getJSON('assertions.json', function(assertions) {
        test('jsondiff', function() {  
            for (var i=0; i<assertions.length; i++) {
                var method = methodmap[assertions[i][0]];
                var want = method.apply(jd, assertions[i][1]);
                ok(jd.equals(want, assertions[i][2]), assertions[i][3]);
            }
        });
    });
});
