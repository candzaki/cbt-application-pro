    (function() {
        const video = document.getElementById('webcam-live-stream');
        if (!video) return;
        
        if (window.cbt_webcam_stream) {
            video.srcObject = window.cbt_webcam_stream;
            video.play().catch(err => console.error("Error playing cached stream:", err));
        } else {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    window.cbt_webcam_stream = stream;
                    video.srcObject = stream;
                    video.play().catch(err => console.error("Error playing stream:", err));
                })
                .catch(err => {
                    console.error("Camera access error:", err);
                });
            } else {
                console.error("Webcam API not supported.");
            }
        }
    })();