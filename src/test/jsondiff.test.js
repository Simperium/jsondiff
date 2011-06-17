$(function(){
    var jd = new jsondiff();
    var methodmap = {
        diff: jd.diff,
        applydiff: jd.apply_object_diff
    }

    function run_assertion(method, args, expected, description) {
        var description = method + ': ' + description;
        var method = methodmap[method];
        var want = method.apply(jd, args);
        ok(jd.equals(want, expected), description);
    }

    $.getJSON('assertions.json', function(assertions) {
        test('jsondiff', function() {  
            for (var i=0; i<assertions.length; i++) {
                run_assertion(assertions[i][0], assertions[i][1], assertions[i][2], assertions[i][3]);
                //
                // generate applydiff tests from diff tests
                if(assertions[i][0] == 'diff') {
                    var original = assertions[i][1][0];
                    var target = assertions[i][1][1];
                    run_assertion('applydiff', [original, assertions[i][2]['v']], target, assertions[i][3]);
                }
            }
        });
    });
});
