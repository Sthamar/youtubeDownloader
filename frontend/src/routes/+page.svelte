<script>
    import { onMount } from "svelte";

    let url = "";
    let format = "mp4";
    let progress = 0;
    let successMessage = "";
    let errorMessage = "";
    let socket;

    onMount(() => {
        socket = new WebSocket("ws://127.0.0.1:8000/ws");

        socket.onopen = () => {
            console.log("Connected to WebSocket server!");
        };

        socket.onmessage = (event) => {
            let message = JSON.parse(event.data);
            console.log("Received:", message);

            if (message.progress) {
                let newProgress = parseFloat(message.progress);
                if (!isNaN(newProgress)) {
                    progress = newProgress; // Svelte automatically updates UI
                }
            }
        };

        socket.onerror = (error) => {
            console.error("WebSocket Error:", error);
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed.");
        };
    });

    async function startDownload() {
        try {
            const res = await fetch("http://127.0.0.1:8000/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url, format }),
            });

            if (res.ok) {
                successMessage = "Download Completed";
            } else {
                errorMessage = "Download failed, try again later";
            }
        } catch (e) {
            console.error("Error starting download:", e);
            errorMessage = "Network Error";
        }
    }
</script>

<div class="hero min-h-screen">
    <div class="hero-content flex-col text-center">
        <div class="card-body shrink-0 shadow-x">
            <h1 class="text-5xl font-bold">YouTube Downloader</h1>

            {#if errorMessage}
                <div class="bg-error">{errorMessage}</div>
            {/if}

            {#if successMessage}
                <div class="bg-success">{successMessage}</div>
            {/if}

            <div class="card-body">
                <div class="form-control">
                    <label for="url" class="label-text">Video URL</label>
                    <input type="text" bind:value={url} class="input input-bordered">
                </div>

                <div class="form-control">
                    <label for="format" class="label-text">Format</label>
                    <select id="format" class="select select-bordered" bind:value={format}>
                        <option value="mp4">MP4</option>
                        <option value="mp3">MP3</option>
                    </select>
                </div>

                <button on:click={startDownload} class="btn btn-primary">Download</button>

                <div class="form-control">
                    <label>Download Progress:</label>
                    <progress value={progress} max="100" class="progress progress-success"></progress>
                </div>
            </div>
        </div>
    </div>
</div>
