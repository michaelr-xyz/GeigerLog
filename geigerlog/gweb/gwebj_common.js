
// gwebj_common.js
'use strict';

var MonRefresh    = 1000;  // ms
var GraphRefresh  = GRAPHREFRESH  // ms
var LastData      = [];
// var LastData      = {};
var LogStatus     = 0;
var oldLogStatus  = 0;
var FileStatus    = 0;
var VarNames      = ["datetime",
                     "cpm",     "cps",      "cpm1st",   "cps1st",
                     "cpm2nd",  "cps2nd",   "cpm3rd",   "cps3rd",
                     "temp",    "press",    "humid",    "xtra",
                     "sensitivityDef", "sensitivity1st", "sensitivity2nd", "sensitivity3rd",
                     "limitLo", "limitHi",
                     "logstate", "filestate",
                     "TopWidget", "BottomWidget",
                     "PlotMin", "PlotMax",
                     "PlotLength",
                     "CycleTime",
                    ];
var DeltaT        = MONSERVER_REC_LENGTH;           // min

var TopVarIndex         = 0;
var BottomVarIndex      = 1;
var oldTopVarIndex      = -1;
var oldBottomVarIndex   = -1;
var PlotLength          = 10;   // min
var CycleTime           = 1;    // sec


SUPPRESS_CONSOLE_LOG


function BusyCursor()       {document.body.style.cursor = 'wait';}
function NormalCursor()     {document.body.style.cursor = 'default';}
function isNumber(value)    {return typeof value === 'number' && isFinite(value);}


// used for 1-line record types: lastdata, lastavg, ...
async function fetchRecord(RecordType){
    let fetchDataText = "";
    try{
        const fetchData = await fetch(RecordType, {cache: "no-store"});
        fetchDataText   = await fetchData.text();
        // console.log("fetchDataText", fetchDataText);

        if (fetchDataText.startsWith("<!")) fetchDataText = "HTML";
    }
    catch(error){
        console.log("Error:", error, " -- function: fetchRecord: RecordType:", RecordType);
    }
    return fetchDataText.split(",");
}


function getNumFormat(number){
    if      (isNaN(number))   return "---";
    else if (number >= 10000) return number.toFixed(0);
    else if (number >= 900)   return number.toFixed(1); // to allow P from 900.0 to >1030.9
    else if (number >= 100)   return number.toFixed(1);
    else                      return number.toFixed(2);
}


function clamp(val, minval, maxval){
    return Math.min(Math.max(val, minval), maxval);
}


async function getLastStatus(){
    // creates 'LastData' as last record for all vars and GeigerLog status data

    const   defname = "getLastStatus:"

    // let start = performance.now()
    const StatusData = await fetchRecord('/laststatus');    // dur typ: 12 ms, range: 8...100 ms
    // let stop  = performance.now()
    // console.log(defname, `getting StatusData in: ${stop - start} ms`);

    // let start = performance.now()
    LastData[VarNames[0]] = new Date(StatusData[0]);
    for (let i = 1; i < VarNames.length; i++){
        LastData[VarNames[i]] = +StatusData[i];
    }

    LogStatus      = LastData["logstate"];
    FileStatus     = LastData["filestate"];
    TopVarIndex    = LastData["TopWidget"];
    BottomVarIndex = LastData["BottomWidget"];
    PlotLength     = LastData["PlotLength"];
    CycleTime      = LastData["CycleTime"];
    // let stop  = performance.now()
    // console.log(defname, `handling StatusData in: ${stop - start} ms`);  // dur handling w/ log: 0 ms


    console.log(defname, "StatusData:", StatusData,
                         "Log:", LogStatus, "File:", FileStatus, "TopVar:", TopVarIndex,
                         "BottomVar:", BottomVarIndex, "PlotLength:", PlotLength, "CycleTime:", CycleTime )
    // let stop  = performance.now()
    // console.log(defname, `handling StatusData in: ${stop - start} ms`);  // dur handling: 0 ... 3 ms
}


async function setButtonStates(){

    // JS has no 'enable' function ;-/

    if (LogStatus){
        document.getElementById("btnquick").disabled = true;
        document.getElementById("btnstart").disabled = true;
        document.getElementById("btnstop") .disabled = false;
    }
    else if(!LogStatus && FileStatus){
        document.getElementById("btnquick").disabled = false;
        document.getElementById("btnstart").disabled = false;
        document.getElementById("btnstop") .disabled = true;
    }
    else{
        document.getElementById("btnquick").disabled = false;
        document.getElementById("btnstart").disabled = true;
        document.getElementById("btnstop") .disabled = true;
    }
}
