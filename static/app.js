const tg = window.Telegram.WebApp;
tg.expand();

let initData = tg.initData;
let currentUser = null;

async function init() {
    const urlParams = new URLSearchParams(window.location.search);
    const startParam = urlParams.get('start_param');

    const response = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: initData, start_param: startParam })
    });

    if (response.ok) {
        const data = await response.json();
        currentUser = data.user;
        updateUI();
    }
}

function updateUI() {
    if (!currentUser) return;
    document.getElementById('username').innerText = currentUser.username;
    document.getElementById('balance').innerText = currentUser.balance;
    document.getElementById('click-level').innerText = currentUser.click_level;
    document.getElementById('upgrade-cost').innerText = currentUser.click_level * 100;
    document.getElementById('user-id').innerText = currentUser.user_id;
    document.getElementById('ref-count').innerText = currentUser.referrals_count;
}

const coinBtn = document.getElementById('coin-btn');
coinBtn.addEventListener('click', async (e) => {
    showClickAnimation(e.clientX, e.clientY);

    const response = await fetch('/api/click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: initData })
    });

    if (response.ok) {
        const data = await response.json();
        currentUser.balance = data.balance;
        document.getElementById('balance').innerText = data.balance;
    }
});

function showClickAnimation(x, y) {
    const pop = document.createElement('div');
    pop.className = 'click-pop';
    pop.innerText = `+${currentUser ? currentUser.click_level : 1}`;
    pop.style.left = `${x}px`;
    pop.style.top = `${y}px`;
    document.body.appendChild(pop);

    setTimeout(() => pop.remove(), 800);
}

document.getElementById('upgrade-btn').addEventListener('click', async () => {
    const response = await fetch('/api/upgrade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: initData })
    });

    if (response.ok) {
        const data = await response.json();
        currentUser.balance = data.balance;
        currentUser.click_level = data.level;
        updateUI();
    }
});

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
    if (tabName !== 'main') {
        const activeTab = document.getElementById(`${tabName}-tab`);
        if (activeTab) activeTab.classList.remove('hidden');
        if (tabName === 'leaderboard') fetchLeaderboard();
    }
}

async function fetchLeaderboard() {
    const res = await fetch('/api/leaderboard');
    const data = await res.json();
    const list = document.getElementById('leaderboard-list');
    list.innerHTML = '';
    data.leaderboard.forEach(item => {
        const li = document.createElement('li');
        li.innerText = `${item.username}: ${item.balance} coin`;
        list.appendChild(li);
    });
}

document.getElementById('ref-btn').addEventListener('click', () => {
    const refLink = `https://t.me/YOUR_BOT_USERNAME?start=${currentUser.user_id}`;
    navigator.clipboard.writeText(refLink);
    alert('Referral havolangiz nusxalandi!');
});

init();
