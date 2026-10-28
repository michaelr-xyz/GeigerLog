
// avg

var chunk         = 0;       // DeltaT in min
var AvgVarNames   = ["datetime",                                                                    // 1    1   0
                     "cpm", "cps", "cpm1st", "cps1st", "cpm2nd", "cps2nd", "cpm3rd", "cps3rd",      // 8    9   8
                     "temp", "press", "humid", "xtra",                                              // 4    13  12
                     "DeltaT",                                                                      // 1    14  13
                     "sensitivityDef", "sensitivity1st", "sensitivity2nd", "sensitivity3rd",        // 4    18  17
                     "usvDef", "usv1st", "usv2nd", "usv3rd"                                         // 4    22  21
                    ];
var LastAvgData   = [];


async function getDataAvgList(DeltaT){
    // get Avg data for last records over DeltaT minutes

    // let i, DataSource, DataRecords;

    let DataSource  = "/lastavgdata?chunk=" + DeltaT;
    let DataRecords = await fetchRecord(DataSource);
    console.log("DataRecords:", DataRecords);

    LastAvgData[AvgVarNames[0]] = new Date(DataRecords[0]);
    for (let i = 1; i <= 17; i++){LastAvgData[AvgVarNames[i]] = +DataRecords[i];}

    LastAvgData["usvDef"] = LastAvgData["cpm"]    / LastAvgData["sensitivityDef"];
    LastAvgData["usv1st"] = LastAvgData["cpm1st"] / LastAvgData["sensitivity1st"];
    LastAvgData["usv2nd"] = LastAvgData["cpm2nd"] / LastAvgData["sensitivity2nd"];
    LastAvgData["usv3rd"] = LastAvgData["cpm3rd"] / LastAvgData["sensitivity3rd"];
    // console.log("LastAvgData: \n", LastAvgData)

    return LastAvgData;
};


async function insertDataAvgToTable(type, DeltaT){
    // type is: "A", "B", or "C" for 1st, 2nd, 3rd column

    let data, i;

    // console.log("insertDataAvgToTable: type:", type, "DeltaT:", DeltaT);

    data = await getDataAvgList(DeltaT);
    for (i of [1,2,3,4,5,6,7,8,9,10,11,12,   18,19,20,21]){
        document.getElementById(AvgVarNames[i] + type).innerHTML = getNumFormat(data[AvgVarNames[i]]);
    }

    document.getElementById("recs" + type).innerHTML = data["DeltaT"] + " min";
}


async function insertAllValues(){

    await insertDataAvgToTable("A", MONSERVERDATACONFIGA);
    await insertDataAvgToTable("B", MONSERVERDATACONFIGB);
    await insertDataAvgToTable("C", MONSERVERDATACONFIGC);
}


async function DataMain(){

    document.title = "Data";

    await getLastStatus();
    await setButtonStates();
    // console.log("DataMain: Interval LogStatus: ", LogStatus, "oldLogStatus: ", oldLogStatus)

    await insertAllValues();

    setInterval(async function() {
        await getLastStatus();
        await setButtonStates();
        // console.log("MonMain: Interval LogStatus: ", LogStatus, "oldLogStatus: ", oldLogStatus)
        if (LogStatus) {
            await insertAllValues();
        }
    }, MonRefresh);
}

DataMain();

