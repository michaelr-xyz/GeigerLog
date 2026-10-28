
// js for d3 line: gwebj_w_line_all.js

var linedata;


async function getLineData(VarIndex, DeltaT) {

    const defname = "getLineData: "

    const strcall = "/lastrecs?var=" + String(VarIndex) + "&dt=" + String(DeltaT)
    const datalastrecs = await d3.csv(strcall);

    linedata = [];
    for (let i = 0; i < datalastrecs.length; i++){
        linedata[i] = {"DateTime": new Date(datalastrecs[i]["DateTime"]), "Value": +datalastrecs[i]["Value"]};
    };
    console.log(defname, strcall, "#recs:", datalastrecs.length, "linedata:", linedata)
};


function redrawGraph(VarName, unit){
    // dur 100 ... 150 ms with ~67000 recs

    let lastval, strval;

    document.getElementById("varvalue").style.backgroundColor = LogStatus ? '#F9F4C9' : '#C0C0C0';

    // draws the full set of data in a completely new graph
    makeLineGraph(linedata);

    // add the bottom text to graph with last val, like: 'CPM2nd : 50 CPM'
    // get the value
    try      {lastval = linedata[linedata.length - 1]["Value"];}
    catch(e) {lastval = 0;}
    // console.log("linedata[linedata.length - 1]['Value']", lastval);

    // format the value
    strval = getNumFormat(lastval);

    // write value to web page into 'd3-container'
    document.getElementById("varvalue").innerHTML = VarName + " : " + strval + unit;

    // console.log("VarName:", VarName, "Value:", strval, "Unit:", unit)
}


async function LineMain(){

    // inner functions
    async function handleActions(force){
        await getLastStatus();
        document.getElementById("linegraph").style.backgroundColor = LogStatus ? '#F9F4C9' : '#C0C0C0';

        if (LogStatus || force){
            t1 = performance.now()
                await getLineData(VarIndex, DeltaT);
            t2 = performance.now()
                d3.selectAll("svg").remove();  // why is this NOT needed? strange: needed only for the Demo page
            t3 = performance.now()
                redrawGraph(VarName, unit);
            t4 = performance.now()

            console.log(defname, "recs:", linedata.length, "getLineData:", (t2-t1).toFixed(2), "remove:", (t3-t2).toFixed(2), "redraw:", (t4-t3).toFixed(2))
        }
    }
    // END inner functions


    const defname = "LineMain: "
    let   unit    = "";
    let t1, t2, t3, t4

    document.title = "Line";

    if      (VarName.startsWith("Temp"))    {unit = " °C"}
    else if (VarName.startsWith("Press"))   {unit = " hPa"}
    else if (VarName.startsWith("Humid"))   {unit = " %"}
    else if (VarName.startsWith("Xtra"))    {unit = " Units"}
    else if (VarName.startsWith("CPM"))     {unit = " CPM"}
    else if (VarName.startsWith("CPS"))     {unit = " CPS"}
    // console.log(defname, "VarName:", VarName,  "Unit:", unit)

    handleActions(true)

    setInterval(async function() {
        handleActions()
    // }, MonRefresh );
    }, GraphRefresh);
}

LineMain();

