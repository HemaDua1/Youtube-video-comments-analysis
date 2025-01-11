let chart = null;

async function analyzeSentiment() {
    const videoUrl = document.getElementById('videoUrl').value;
    console.log('Analyzing sentiment for:', videoUrl);
    
    const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:5000'  // Development API URL
        : 'https://youtube-video-comments-analysis-t5sv.vercel.app'; // Production API URL

    // Validate input
    if (!videoUrl) {
        alert('Please paint your canvas with a YouTube URL');
        return;
    }
    
    // Show loading state
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').classList.remove('show-results');
    
    try {
        const response = await axios.post(`${apiUrl}/analyze`, 
            { videoUrl },
            {
                headers: {
                    'Content-Type': 'application/json',
                },
                withCredentials: false  // Important for CORS
            }
        );
        
        const data = response.data;
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        updateResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert(error.response?.data?.error || 'Failed to create your sentiment masterpiece. Please try again.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function updateResults(data) {
    // Update sentiment counts with animation
    animateNumber('positiveCount', data.positive);
    animateNumber('neutralCount', data.neutral);
    animateNumber('negativeCount', data.negative);
    
    // Update chart
    updateChart(data);
    
    // Show results with animation
    document.getElementById('results').style.display = 'block';
    requestAnimationFrame(() => {
        document.getElementById('results').classList.add('show-results');
    });
}

function animateNumber(elementId, final, duration = 1000) {
    const element = document.getElementById(elementId);
    const start = parseInt(element.textContent) || 0;  // Added fallback to 0
    const range = final - start;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeOutQuad = 1 - Math.pow(1 - progress, 2);
        
        const current = Math.floor(start + (range * easeOutQuad));
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function updateChart(data) {
    if (chart) {
        chart.destroy();
    }
    
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive Strokes', 'Neutral Tones', 'Dark Shades'],
            datasets: [{
                data: [data.positive, data.neutral, data.negative],
                backgroundColor: [
                    '#4ecdc4',  // Positive - matches your CSS gradient
                    '#45b7d1',  // Neutral - matches your CSS gradient
                    '#ff6b6b'   // Negative - matches your CSS gradient
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255,255,255,0.8)',
                        padding: 20,
                        font: {
                            size: 14,
                            family: "'Segoe UI', system-ui, -apple-system, sans-serif"
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}