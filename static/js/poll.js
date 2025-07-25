let chart;

function fetchPoll() {
    fetch('/api/poll')
        .then(res => res.json())
        .then(data => renderChart(data));
}

function renderChart(data) {
    const labels = data.options.map(opt => opt.text);
    const votes = data.options.map(opt => opt.votes);

    if (chart) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = votes;
        chart.update();
    } else {
        const ctx = document.getElementById('resultChart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Votes',
                    data: votes,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

function submitVote(option_id) {
    fetch('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option_id })
    }).then(res => res.json())
      .then(data => {
          if (data.error) {
              document.getElementById("messageArea").innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
          } else {
              document.getElementById("messageArea").innerHTML = `<div class="alert alert-success">${data.message}</div>`;
              fetchPoll();
          }
      });
}

fetchPoll();
setInterval(fetchPoll, 5000);