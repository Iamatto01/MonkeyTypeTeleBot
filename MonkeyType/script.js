let userApiKey = "";

function setApiKey() {
    const apiKeyInput = document.getElementById("apiKey").value.trim();
    if (!apiKeyInput) {
        displayOutput("❌ Please enter a valid API key.");
        return;
    }
    userApiKey = apiKeyInput;
    displayOutput("✅ API Key has been saved!");
}

async function fetchFromApi(endpoint, params = {}) {
    if (!userApiKey) {
        displayOutput("⚠️ Please set your API key first.");
        return;
    }

    const url = new URL(`https://api.monkeytype.com${endpoint}`);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: { "Authorization": `ApeKey ${userApiKey}` }
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        displayOutput(`❌ Failed to fetch data: ${error.message}`);
        return null;
    }
}

async function fetchRecentResult() {
    const data = await fetchFromApi("/results/last");

    if (data) {
        const result = data.data;
        displayOutput(`
            <h3>📋 Most Recent Typing Test</h3>
            <p>🕹 Mode: ${result.mode}</p>
            <p>⚡ WPM: ${result.wpm}</p>
            <p>🎯 Accuracy: ${result.acc}%</p>
            <p>📏 Consistency: ${result.consistency}%</p>
            <p>⏳ Test Duration: ${result.testDuration} seconds</p>
        `);
    }
}

async function fetchPersonalBest() {
    const data = await fetchFromApi("/results", { limit: 1000 });

    if (data) {
        let results = data.data;
        let categories = {
            "15 seconds": null,
            "30 seconds": null,
            "60 seconds": null,
            "120 seconds": null,
            "10 words": null,
            "25 words": null,
            "50 words": null,
            "100 words": null,
        };

        results.forEach(result => {
            let mode = result.mode;
            let duration = result.testDuration;
            let wordCount = parseInt(result.mode2, 10) || null;
            let wpm = result.wpm;

            if (mode === "time") {
                if (duration in categories && (!categories[`${duration} seconds`] || wpm > categories[`${duration} seconds`])) {
                    categories[`${duration} seconds`] = wpm;
                }
            } else if (mode === "words" && wordCount) {
                if (wordCount in categories && (!categories[`${wordCount} words`] || wpm > categories[`${wordCount} words`])) {
                    categories[`${wordCount} words`] = wpm;
                }
            }
        });

        let pbMessage = `<h3>🏆 Personal Bests</h3>`;
        for (const [category, wpm] of Object.entries(categories)) {
            pbMessage += `<p>⭐ ${category}: ${wpm ? wpm + " WPM" : "No data available"}</p>`;
        }
        displayOutput(pbMessage);
    }
}

async function fetchNews() {
    const data = await fetchFromApi("/psa");

    if (data) {
        let newsMessage = `<h3>📰 Latest News</h3>`;
        data.data.forEach(news => {
            newsMessage += `<p>🗞 ${news.message}</p>`;
        });
        displayOutput(newsMessage);
    }
}

async function fetchHistogram() {
    const data = await fetchFromApi("/speed/histogram");

    if (data) {
        let histogramMessage = `<h3>📊 Typing Speed Distribution</h3>`;
        data.data.forEach(entry => {
            histogramMessage += `<p>⚡ ${entry.speedRange} WPM: ${entry.count} entries</p>`;
        });
        displayOutput(histogramMessage);
    }
}

function displayOutput(message) {
    document.getElementById("output").innerHTML = message;
}
