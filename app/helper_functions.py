MA_SLIDER_CODE = ("""

var wd = w.data
var sd = s.data
var ma = cb_obj.value
var r = 0
cn = w.column_names
for (h = 0; h < cn.length; h++) {
    working = wd[cn[h]]
    static = sd[cn[h]]
    if ((cn[h] == 'date') || (cn[h] == 'date_str')){
        working = Object.assign({},static)
        continue;
    }
    for (i = 0;  i < working.length; i++){
        working[i] = 0
        r = Math.min(ma,i)

        for (k = 0; k < r; k++){
        //Change moving average window when previous data isn't all present
            if(isNaN(static[i-k])){
            r=k;
            break;
            }
        }

        for (j = 0; j < r; j++){
            working[i] += static[i-j]
        }
        working[i] = (working[i]/r)
    }
}
w.change.emit();
""")


DIET_STATS_CODE = ("""

var s_d = s.data
var culled_vals = Object.assign({},s.data)

//var div_end_range = d_e_r;

var div_days = d_d;
var div_avg_intake = d_a_i;
var div_tdee = d_t;
var div_avg_net = d_a_n;
var div_avg_protein = d_a_p;
var div_avg_fat = d_a_f;
var div_avg_carb_all = d_a_c_a;
var div_avg_carb_net = d_a_c_n;
var div_avg_carb_fiber = d_a_c_f;
var div_problem_days = d_p_d;
var div_volatility = d_v;

//Beginning and end of currently selected x_range
var end = new Date(Number(cb_obj.end.toString()));
var beg = new Date(Number(cb_obj.start.toString()));

//var ind = []
//culled_vals = s_d['date'].filter(function(d_comp){return(d_comp >= beg && d_comp <= end)});
//culled_vals = s_d['date'].filter(function(d_comp,idx){if(d_comp >= beg && d_comp <= end){ind.push(idx);return true;}});

//Clear values
cn = s.column_names
for (h = 0; h < cn.length; h++) {
    culled_vals[cn[h]] = []
    }

//Read in values of the dates in the currently selected x_range
//***TODO: Probably some efficiency gains here...
for (i = 0; i < s_d['date'].length; i++) {
    if(s_d['date'][i] >= beg && s_d['date'][i] <= end){
        for (j = 0; j < cn.length; j++) {
            //if (!isNaN(s_d[cn[j]][i])){
                culled_vals[cn[j]].push(s_d[cn[j]][i])
            //}

        }
    }
}

function array_sum(a){
var s = 0
    for (h = 0; h < a.length; h++) {
    s += a[h]
    }
    return s
}

function array_avg(a){
    return array_sum(a)/a.length
}

div_days.text = culled_vals['date'].length.toString();
div_avg_intake.text = array_avg(culled_vals['kcal_intake']).toFixed(0).toString();
div_tdee.text = array_avg(culled_vals['tdee']).toFixed(0).toString();
div_avg_net.text = array_avg(culled_vals['net_intake']).toFixed(0).toString();
div_avg_protein.text = array_avg(culled_vals['protein_g']).toFixed(1).toString();
div_avg_fat.text = array_avg(culled_vals['fat_g']).toFixed(1).toString();
div_avg_carb_all.text = array_avg(culled_vals['carb_g']).toFixed(1).toString();
div_avg_carb_net.text = array_avg(culled_vals['net_carb_g']).toFixed(1).toString();
div_avg_carb_fiber.text = array_avg(culled_vals['fiber_g']).toFixed(1).toString();
div_problem_days.text = culled_vals['kcal_intake'].filter(function(kci){return(kci > 4000)}).length.toString();

//TODO: Implememt
div_volatility.text = "TODO";

div_days.change.emit();
div_avg_intake.change.emit();
div_tdee.change.emit();
div_avg_net.change.emit();
div_avg_protein.change.emit();
div_avg_fat.change.emit();
div_avg_carb_all.change.emit();
div_avg_carb_net.change.emit();
div_avg_carb_fiber.change.emit();
div_problem_days.change.emit();
div_volatility.change.emit();

//div_end_range.text = end.toString() + beg.toString() + culled_vals['date'].length + " " + avg_intake.toString() + " " + tdee.toString();//+ " " + b_idx.toString() + " " + e_idx.toString() + " " + ind.length;
//div_end_range.change.emit();
""")

MOOD_STATS_CODE = ("""

var s_d = s.data
var culled_vals = Object.assign({},s.data)

var div_days = d_d;
var div_avg_a = d_avg_a;
var div_avg_v = d_avg_v;
var div_good_days = d_g_d;
var div_poor_days = d_p_d;
var div_caution_days = d_c_d;
var div_warning_days = d_w_d;

//Beginning and end of currently selected x_range
var end = new Date(Number(cb_obj.end.toString()));
var beg = new Date(Number(cb_obj.start.toString()));

//Clear values
cn = s.column_names
for (h = 0; h < cn.length; h++) {
    culled_vals[cn[h]] = []
    }

//Read in values of the dates in the currently selected x_range
//***TODO: Probably some efficiency gains here...
for (i = 0; i < s_d['date'].length; i++) {
    if(s_d['date'][i] >= beg && s_d['date'][i] <= end){
        for (j = 0; j < cn.length; j++) {
            //if (!isNaN(s_d[cn[j]][i])){
                culled_vals[cn[j]].push(s_d[cn[j]][i])
            //}
        }
    }
}

function array_sum(a){
var s = 0
    for (h = 0; h < a.length; h++) {
    s += a[h]
    }
    return s
}

function array_avg(a){
    return array_sum(a)/a.length
}

div_days.text = culled_vals['date'].length.toString();
div_avg_a.text = array_avg(culled_vals['a_be']).toFixed(2).toString();
div_avg_v.text = array_avg(culled_vals['v_be']).toFixed(2).toString();
div_good_days.text = culled_vals['v_be'].filter(function(val){return(val >= 6)}).length.toString();
div_poor_days.text = culled_vals['v_be'].filter(function(val){return(val <= 4)}).length.toString();
div_caution_days.text = culled_vals['v_be'].filter(function(val){return(val <= 3.5)}).length.toString();
div_warning_days.text = culled_vals['v_l'].filter(function(val){return(val <= 2)}).length.toString();

div_days.change.emit();
div_avg_a.change.emit();
div_avg_v.change.emit();
div_good_days.change.emit();
div_poor_days.change.emit();
div_caution_days.change.emit();
div_warning_days.change.emit();

""")

BODY_STATS_CODE = ("""

var s_d = s.data
var culled_vals = Object.assign({},s.data)

var div_days = d_d;
var div_avg_bg = d_a_bg;
var div_avg_rhr = d_a_r;
var div_avg_slp_dur = d_a_s_d;
var div_avg_slp_q = d_a_s_q;

//Beginning and end of currently selected x_range
var end = new Date(Number(cb_obj.end.toString()));
var beg = new Date(Number(cb_obj.start.toString()));

//Clear values
cn = s.column_names
for (h = 0; h < cn.length; h++) {
    culled_vals[cn[h]] = []
    }

//Read in values of the dates in the currently selected x_range
//***TODO: Probably some efficiency gains here...
for (i = 0; i < s_d['date'].length; i++) {
    if(s_d['date'][i] >= beg && s_d['date'][i] <= end){
        for (j = 0; j < cn.length; j++) {
            if (!isNaN(s_d[cn[j]][i])){
                culled_vals[cn[j]].push(s_d[cn[j]][i])
            }
        }
    }
}

function array_sum(a){
var s = 0
    for (h = 0; h < a.length; h++) {
    s += a[h]
    }
    return s
}

function array_avg(a){
    return array_sum(a)/a.length
}

div_days.text = culled_vals['date'].length.toString();
div_avg_bg.text = array_avg(culled_vals['glucose']).toFixed(0).toString();
div_avg_rhr.text = array_avg(culled_vals['bpm']).toFixed(0).toString();
div_avg_slp_dur.text = array_avg(culled_vals['sleep_duration']).toFixed(2).toString();
div_avg_slp_q.text = array_avg(culled_vals['sleep_overall_q']).toFixed(0).toString();

div_days.change.emit();
div_avg_bg.change.emit();
div_avg_rhr.change.emit();
div_avg_slp_dur.change.emit();
div_avg_slp_q.change.emit();

""")

BODY_COMP_STATS_CODE = ("""

var s_d = s.data
var culled_vals = Object.assign({},s.data)

var div_days_bc = d_d_bc;
var div_avg_wt = d_a_wt;
var div_avg_bf = d_a_bf;

//Beginning and end of currently selected x_range
var end = new Date(Number(cb_obj.end.toString()));
var beg = new Date(Number(cb_obj.start.toString()));

//Clear values
cn = s.column_names
for (h = 0; h < cn.length; h++) {
    culled_vals[cn[h]] = []
    }

//Read in values of the dates in the currently selected x_range
//***TODO: Probably some efficiency gains here...
for (i = 0; i < s_d['date'].length; i++) {
    if(s_d['date'][i] >= beg && s_d['date'][i] <= end){
        for (j = 0; j < cn.length; j++) {
            if (!isNaN(s_d[cn[j]][i])){
                culled_vals[cn[j]].push(s_d[cn[j]][i])
            }
        }
    }
}

function array_sum(a){
var s = 0
    for (h = 0; h < a.length; h++) {
    s += a[h]
    }
    return s
}

function array_avg(a){
    return array_sum(a)/a.length
}

div_days_bc.text = culled_vals['date'].length.toString();
div_avg_wt.text = array_avg(culled_vals['weight']).toFixed(1).toString();
div_avg_bf.text = array_avg(culled_vals['bodyfat']).toFixed(2).toString();

div_days_bc.change.emit();
div_avg_wt.change.emit();
div_avg_bf.change.emit();

""")

LIFTS_STATS_CODE = ("""

var s_d = s.data

var culled_vals = Object.assign({},s.data)

var div_squat_max = d_s_m;
var div_deadlift_max = d_d_m;
var div_bench_max = d_b_m;
var div_ohp_max = d_o_m;

var div_squat_max_vol_per_set = d_s_mvps;
var div_deadlift_max_vol_per_set = d_d_mvps;
var div_bench_max_vol_per_set = d_b_mvps;
var div_ohp_max_vol_per_set = d_o_mvps;

var div_squat_total_vol = d_s_tv;
var div_deadlift_total_vol = d_d_tv;
var div_bench_total_vol = d_b_tv;
var div_ohp_total_vol = d_o_tv;

//Beginning and end of currently selected x_range
var end = new Date(Number(cb_obj.end.toString()));
var beg = new Date(Number(cb_obj.start.toString()));

//Clear values
cn = s.column_names
for (h = 0; h < cn.length; h++) {
    culled_vals[cn[h]] = []
    }

//Read in values of the dates in the currently selected x_range
//***TODO: Probably some efficiency gains here...
for (i = 0; i < s_d['date'].length; i++) {
    if(s_d['date'][i] >= beg && s_d['date'][i] <= end){
        for (j = 0; j < cn.length; j++) {
               if (!isNaN(s_d[cn[j]][i])){
                culled_vals[cn[j]].push(s_d[cn[j]][i])
            }             
        }
    }
}

function array_sum(a){
var s = 0
    for (h = 0; h < a.length; h++) {
    s += a[h]
    }
    return s
}

function array_max(a){
var s = 0
    for (h = 0; h < a.length; h++) {
        if (a[h] > s){
            s = a[h]
        }
    }
    return s
}


function array_avg(a){
    return array_sum(a)/a.length
}

div_squat_max.text = array_max(culled_vals['squat_max']).toFixed(0).toString();
div_deadlift_max.text = array_max(culled_vals['deadlift_max']).toFixed(0).toString();
div_bench_max.text = array_max(culled_vals['bench_max']).toFixed(0).toString();
div_ohp_max.text = array_max(culled_vals['ohp_max']).toFixed(0).toString();

div_squat_max_vol_per_set.text = array_max(culled_vals['squat_max_vol_per_set']).toFixed(0).toString();
div_deadlift_max_vol_per_set.text = array_max(culled_vals['deadlift_max_vol_per_set']).toFixed(0).toString();
div_bench_max_vol_per_set.text = array_max(culled_vals['bench_max_vol_per_set']).toFixed(0).toString();
div_ohp_max_vol_per_set.text = array_max(culled_vals['ohp_max_vol_per_set']).toFixed(0).toString();

div_squat_total_vol.text = array_sum(culled_vals['squat_total_vol']).toFixed(0).toString();
div_deadlift_total_vol.text = array_sum(culled_vals['deadlift_total_vol']).toFixed(0).toString();
div_bench_total_vol.text = array_sum(culled_vals['bench_total_vol']).toFixed(0).toString();
div_ohp_total_vol.text = array_sum(culled_vals['ohp_total_vol']).toFixed(0).toString();

div_squat_max.change.emit();
div_deadlift_max.change.emit();
div_bench_max.change.emit();
div_ohp_max.change.emit();

div_squat_max_vol_per_set.change.emit();
div_deadlift_max_vol_per_set.change.emit();
div_bench_max_vol_per_set.change.emit();
div_ohp_max_vol_per_set.change.emit();

div_squat_total_vol.change.emit();
div_deadlift_total_vol.change.emit();
div_bench_total_vol.change.emit();
div_ohp_total_vol.change.emit();

""")
