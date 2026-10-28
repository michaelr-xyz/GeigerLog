
// js for Web Page Root

async function RootMain(){

    // internal function
    async function makeRootpage(){
        await getLastStatus();
        await setButtonStates();
    }
    // END internal function

    document.title = "GeigerLog Monitor Server";

    await makeRootpage();

    setInterval(async function() {
        await makeRootpage();
    }, MonRefresh);
}

RootMain();

