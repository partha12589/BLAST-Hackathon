// Initial Payload demonstration logic
document.addEventListener('DOMContentLoaded', () => {
    console.log("Command Center initialized. Awaiting API payload...");

    // Mock Payload injection for UI presentation
    setTimeout(() => {
        simulatePayloadIngestion({
            "transaction_hash": "0x4f8a...9c21",
            "overall_risk_score": 98,
            "status": "BLOCKED",
            "flagged_entities": ["Lazarus Group", "Tornado Cash"],
            "taint_distance_hops": 3,
            "matched_heuristics": ["Peeling Chain", "Sanctioned Entity Tie"],
            "target_wallet": "0x1234abcd5678ef90..."
        });
    }, 2500);
});

function simulatePayloadIngestion(payload) {
    // 1. Top Metrics 
    const riskElem = document.getElementById('risk-score');
    riskElem.innerText = payload.overall_risk_score;
    document.getElementById('risk-trend').innerText = 'Critical Risk Detected';
    
    // color code risk
    if(payload.overall_risk_score > 80) riskElem.style.color = 'var(--danger)';
    
    document.getElementById('taint-volume').innerText = '$4,250,000'; // Mock taint vol payload expansion
    document.getElementById('network-hops').innerText = payload.taint_distance_hops;
    
    // 2. Command Center
    document.querySelector('.wallet-address').innerText = payload.target_wallet;
    
    const badge = document.getElementById('status-badge');
    badge.innerText = payload.status;
    badge.className = 'status-badge ' + payload.status.toLowerCase();
    
    const btn = document.getElementById('freeze-btn');
    if(payload.status === 'BLOCKED') {
        btn.classList.remove('disabled');
        btn.style.animation = 'pulse-danger 2s infinite';
    }
    
    // 3. Graph area update
    const graphArea = document.querySelector('.graph-placeholder');
    graphArea.innerHTML = `
        <div style="text-align:center; color: var(--danger); animation: fadeIn 0.5s ease;">
            <div style="font-size: 48px; margin-bottom: 20px;">🕸️</div>
            <h4 style="margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">Malicious Provenance Detected</h4>
            <p style="font-size: 0.9em; color: var(--text-secondary)">
                ${payload.matched_heuristics.join(' • ')}
            </p>
            <div style="margin-top:20px; padding: 10px; background: rgba(255,42,67,0.1); border: 1px solid var(--danger); border-radius: 8px;">
                Identified Entities: ${payload.flagged_entities.join(', ')}
            </div>
        </div>
    `;
}
