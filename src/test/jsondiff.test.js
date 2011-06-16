var jd = new jsondiff();
test('listdiff', function() {  
    var got = jd.diff([1], [1,4]);
    var want = {'o': 'L', 'v': {1: {'o':'+', 'v':4}}};
    ok(jd.equals(want, got), 'append list item');
});
