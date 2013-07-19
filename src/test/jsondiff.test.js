$(function(){
    var jd = new jsondiff();

    function run_assertion(method, description, args, expected) {
        var description = method + ': ' + description;
        switch(method) {
            case 'diff':
                method = jd.diff
                break;
            case 'applydiff':
                if (jd.typeOf(args[0]) == 'array')
                    method = jd.apply_list_diff;
                else if (jd.typeOf(args[0]) == 'object')
                    method = jd.apply_object_diff;
                break;
            case 'transform':
                var orig = args[0];
                var diffa = jd.diff(args[0], args[1])['v'];
                var diffb = jd.diff(args[0], args[2])['v'];
                var tdiff = jd.transform_object_diff(diffa, diffb, orig);
                ok(jd.entries(tdiff) > 0, description);

                method = jd.apply_object_diff;
                args = [jd.apply_object_diff(orig, diffb), tdiff];
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
                if (assertions[i][0] == 'diff') {
                    var original = assertions[i][2][0];
                    var target = assertions[i][2][1];
                    run_assertion('applydiff', assertions[i][1], [original, assertions[i][3]['v']], target);
                } else if (assertions[i][0] == 'transform') {
                    var original = assertions[i][2][0];

                }
            }
        });
    });
});
window.jd = new jsondiff()
window.dmp = jsondiff.dmp;
window.s = { 'a' : [1, 2, 3] };
window.a = { 'a' : [1, 2, 3, 5] };
window.b = { 'a' : [1, 2, 3, 4] };
window.atext = jd._serialize_to_text(a.a)
window.btext = jd._serialize_to_text(b.a)
window.diffa = jd.diff(s, a);
window.diffb = jd.diff(s, b);
