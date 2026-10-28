
// js for Web Page Info

async function InfoMain(){

    // inner functions
    async function handleActions(){
        await getLastStatus();
        await setButtonStates();
    }
    // END inner functions


    document.title = "Info";

    handleActions()

    setInterval(async function() {
        handleActions()
    }, MonRefresh);
}

InfoMain();

