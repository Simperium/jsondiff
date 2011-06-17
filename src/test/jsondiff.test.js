$(function(){
    var jd = new jsondiff();

    function run_assertion(method, description, args, expected) {
        var description = method + ': ' + description;
        switch(method) {
            case 'diff':
                var method = jd.diff
                break;
            case 'applydiff':
                if (jd.typeOf(args[0]) == 'array')
                    var method = jd.apply_list_diff;
                else if (jd.typeOf(args[0]) == 'object')
                    var method = jd.apply_object_diff;
                break;
        }

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
                    var original = assertions[i][2][0];
                    var target = assertions[i][2][1];
                    run_assertion('applydiff', assertions[i][1], [original, assertions[i][3]['v']], target);
                }
            }
        });
    });
});
