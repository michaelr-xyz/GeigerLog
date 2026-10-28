// js for Web Page Widget-Demo


async function WidgetMain(){

    document.title = "GeigerLog Widget-Demo";

    await getLastStatus();
    await setButtonStates();

    setInterval(async function() {
        await getLastStatus();
        await setButtonStates();
    }, MonRefresh);
}

WidgetMain();

