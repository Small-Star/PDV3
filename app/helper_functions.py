MA_SLIDER_CODE = ("""

var wd = w.data
var sd = s.data
var ma = cb_obj.value
var r = 0

cn = w.column_names
for (h = 0; h < cn.length; h++) {
    if (cn[h] != 'date'){
        working = wd[cn[h]]
        static = sd[cn[h]]
    }
    for (i = 0;  i < working.length; i++){
        working[i] = 0
        r = Math.min(ma,i)
        for (j = 0; j < r; j++){
            working[i] += static[i-j]
        }
        working[i] = working[i]/r
    }
}
w.change.emit();

""")
