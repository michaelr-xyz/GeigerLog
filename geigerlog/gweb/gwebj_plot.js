// gwebj_plot.js
// make 2 iframes holding line graphs

async function findVarIndexes(){
    // reads the settings of the drop down boxes for vars on the web page

    try         {TopVarIndex = document.getElementById("topvar").selectedIndex;}
    catch(e)    {TopVarIndex = 99;}

    try         {BottomVarIndex = document.getElementById("bottomvar").selectedIndex;}
    catch(e)    {BottomVarIndex = 99;}

    console.log("Var Indexes: Top:", TopVarIndex, "oldTop:", oldTopVarIndex, "Bottom:", BottomVarIndex, "oldBottom:", oldBottomVarIndex)
}


async function createPlots(){

    // internal function
    async function makeGraphs(init){
        // creates the graphs for top and bottom iframes

        const defname = "makeGraphs: "

        await getLastStatus();
        await setButtonStates();
        if (!init) {await findVarIndexes();}

        let refreshtop    = false
        let refreshbottom = false

        // TopVar selection has changed
        if (oldTopVarIndex != TopVarIndex){
            oldTopVarIndex = TopVarIndex;
            document.getElementById("topvar").selectedIndex = TopVarIndex;
            refreshtop     = true
        }

        // BottomVar selection has changed
        if (oldBottomVarIndex != BottomVarIndex){
            oldBottomVarIndex = BottomVarIndex;
            document.getElementById("bottomvar").selectedIndex = BottomVarIndex;
            refreshbottom     = true
        }

        // when logging
        if (LogStatus) {
            nowtime = new Date().getTime()
            // console.log(defname, "lasttime:", lasttime)
            // console.log(defname, "nowtime: ", nowtime)
            // console.log(defname, "delta  : ", nowtime - lasttime)
            // console.log(defname, "GraphRefresh: ", GraphRefresh )

            if ((nowtime - lasttime) >= (GraphRefresh)){
                lasttime = nowtime
                refreshtop    = true
                refreshbottom = true
            }
        }

        if (oldLogStatus != LogStatus){
            oldLogStatus = LogStatus;
            refreshtop    = true
            refreshbottom = true
        }
        // console.log(defname, "refreshtop", refreshtop, "refreshbottom", refreshbottom)

        // set plots into iframes if due
        if (refreshtop)   {document.getElementById("iframetop").src =    "/widget_line?var=" + String(TopVarIndex);}
        if (refreshbottom){document.getElementById("iframebottom").src = "/widget_line?var=" + String(BottomVarIndex);}
    }
    // END internal function


    const defname  = "createPlots: "
    let   lasttime = 0
    let   nowtime  = new Date().getTime();
    document.title = "Plot";

    document.getElementById("reclen").innerHTML = DeltaT + " min"
    makeGraphs(true)

    setInterval(async function() {
        makeGraphs()
    }, MonRefresh);
}

createPlots();

