const API_KEY = "1c822032a6498dc5481bbe2810f3e0da";
const API_URL = `https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey=${API_KEY}&regions=us&markets=h2h&oddsFormat=american`;

// Allowed leagues to display
const allowedLeagues = ["NFL", "NBA", "MLB", "NHL", "NCAAF", "NCAAB"];

// Format ISO date to American-readable format
function formatDateTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
    month: "short",
    day: "numeric"
  });
}

// Format odds with "+" for positive lines
function formatOdds(price) {
  return price > 0 ? `+${price}` : `${price}`;
}

// Convert American odds to implied probability
function calculateImpliedProbability(odds) {
  if (odds > 0) {
    return (100 / (odds + 100) * 100).toFixed(2) + "%";
  } else {
    return (Math.abs(odds) / (Math.abs(odds) + 100) * 100).toFixed(2) + "%";
  }
}

// Fetch odds and populate the table
async function fetchOdds() {
  try {
    const res = await fetch(API_URL);
    const games = await res.json();

    const selectedLeague = document.getElementById("league-filter").value;
    const tableBody = document.querySelector("#vegas-odds-table tbody");
    tableBody.innerHTML = "";

    games.forEach(game => {
      const league = game.sport_title;
      if (!allowedLeagues.includes(league)) return;
      if (selectedLeague !== "all" && league !== selectedLeague) return;

      const match = `${game.home_team} vs ${game.away_team}`;
      const gameTime = formatDateTime(game.commence_time);

      game.bookmakers.forEach(bookmaker => {
        const market = bookmaker.markets.find(m => m.key === "h2h");
        if (!market) return;

        const outcomes = market.outcomes;

        const team1 = outcomes[0]?.name || "N/A";
        const rawOdds1 = outcomes[0]?.price;
        const odds1 = rawOdds1 != null ? formatOdds(rawOdds1) : "N/A";
        const prob1 = rawOdds1 != null ? calculateImpliedProbability(rawOdds1) : "N/A";

        const team2 = outcomes[1]?.name || "N/A";
        const rawOdds2 = outcomes[1]?.price;
        const odds2 = rawOdds2 != null ? formatOdds(rawOdds2) : "N/A";
        const prob2 = rawOdds2 != null ? calculateImpliedProbability(rawOdds2) : "N/A";

        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${league}</td>
          <td>${match}</td>
          <td>${gameTime}</td>
          <td>${bookmaker.title}</td>
          <td>
            ${team1} (${odds1}, ${prob1})<br>
            ${team2} (${odds2}, ${prob2})
          </td>
        `;
        tableBody.appendChild(row);
      });
    });
  } catch (err) {
    console.error("Failed to fetch odds:", err);
  }
}

// Chat icon toggle
document.getElementById("chat-circle").addEventListener("click", () => {
  document.getElementById("chat-window").classList.toggle("hidden");
});

// Filter change reloads data
document.getElementById("league-filter").addEventListener("change", fetchOdds);

// Load on page start
fetchOdds();
