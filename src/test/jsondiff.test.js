var jd = new jsondiff();
test('listdiff', function() {  
    console.log(jd.diff([1], [1,4]));
    console.log({'o': 'L', 'v': {1: {'o':'+', 'v':4}}});
    equals(jd.diff([1], [1,4]), {'o': 'L', 'v': {1: {'o':'+', 'v':4}}}, 'append list item')
});
