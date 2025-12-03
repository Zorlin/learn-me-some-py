/*
 * LMSP Achievement System
 * =======================
 *
 * Handles achievement unlock notifications with gorgeous animations.
 * Displays celebration moments with confetti, sparkles, and XP rewards.
 *
 * Features:
 * - Achievement unlock animations
 * - Tier-based visual styling (bronze, silver, gold, platinum, diamond)
 * - Confetti/sparkle effects
 * - Sound effects (optional)
 * - Achievement progress tracking
 */

// Achievement state
let currentAchievement = null;
let achievementQueue = [];

// Achievement tiers and their colors
const ACHIEVEMENT_TIERS = {
    bronze: { color: '#CD7F32', icon: '🥉', sparkle: '✨' },
    silver: { color: '#C0C0C0', icon: '🥈', sparkle: '✨✨' },
    gold: { color: '#FFD700', icon: '🥇', sparkle: '✨✨✨' },
    platinum: { color: '#E5E4E2', icon: '🏆', sparkle: '✨✨✨✨' },
    diamond: { color: '#B9F2FF', icon: '💎', sparkle: '✨✨✨✨✨' },
};

/**
 * Show achievement unlock notification
 * @param {Object} achievement - Achievement data from API
 */
function showAchievement(achievement) {
    // Queue if another achievement is showing
    if (currentAchievement) {
        achievementQueue.push(achievement);
        return;
    }

    currentAchievement = achievement;

    // Create achievement notification
    const notification = createAchievementNotification(achievement);
    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    // Play confetti effect
    playConfettiEffect(achievement);

    // Auto-hide after delay
    setTimeout(() => {
        hideAchievement(notification);
    }, 5000);
}

/**
 * Create achievement notification element
 * @param {Object} achievement - Achievement data
 * @returns {HTMLElement} Notification element
 */
function createAchievementNotification(achievement) {
    const tier = achievement.tier || 'bronze';
    const tierData = ACHIEVEMENT_TIERS[tier] || ACHIEVEMENT_TIERS.bronze;

    const notification = document.createElement('div');
    notification.className = 'achievement-notification';
    notification.style.setProperty('--tier-color', tierData.color);

    notification.innerHTML = `
        <div class="achievement-content">
            <div class="achievement-header">
                <span class="achievement-sparkle">${tierData.sparkle}</span>
                <span class="achievement-title">Achievement Unlocked!</span>
                <span class="achievement-sparkle">${tierData.sparkle}</span>
            </div>
            <div class="achievement-body">
                <div class="achievement-icon">${achievement.icon || tierData.icon}</div>
                <div class="achievement-details">
                    <h3 class="achievement-name">${achievement.name}</h3>
                    <p class="achievement-description">${achievement.description}</p>
                    <div class="achievement-xp">+${achievement.xp_reward} XP</div>
                </div>
            </div>
        </div>
    `;

    // Click to dismiss
    notification.addEventListener('click', () => {
        hideAchievement(notification);
    });

    return notification;
}

/**
 * Hide achievement notification
 * @param {HTMLElement} notification - Notification element
 */
function hideAchievement(notification) {
    notification.classList.add('hide');

    setTimeout(() => {
        notification.remove();
        currentAchievement = null;

        // Show next achievement if any queued
        if (achievementQueue.length > 0) {
            const next = achievementQueue.shift();
            showAchievement(next);
        }
    }, 500);
}

/**
 * Play confetti effect for achievement
 * @param {Object} achievement - Achievement data
 */
function playConfettiEffect(achievement) {
    const tier = achievement.tier || 'bronze';
    const tierData = ACHIEVEMENT_TIERS[tier] || ACHIEVEMENT_TIERS.bronze;

    // Create confetti particles
    const particleCount = tier === 'diamond' ? 50 : tier === 'platinum' ? 40 : tier === 'gold' ? 30 : 20;

    for (let i = 0; i < particleCount; i++) {
        createConfettiParticle(tierData.color);
    }
}

/**
 * Create a single confetti particle
 * @param {string} color - Particle color
 */
function createConfettiParticle(color) {
    const particle = document.createElement('div');
    particle.className = 'confetti-particle';
    particle.style.setProperty('--particle-color', color);

    // Random position
    const startX = Math.random() * window.innerWidth;
    const startY = window.innerHeight / 2;

    particle.style.left = startX + 'px';
    particle.style.top = startY + 'px';

    // Random animation duration and delay
    const duration = 2 + Math.random() * 2;
    const delay = Math.random() * 0.5;

    particle.style.animationDuration = duration + 's';
    particle.style.animationDelay = delay + 's';

    // Random movement direction
    const angle = Math.random() * Math.PI * 2;
    const distance = 200 + Math.random() * 200;
    const endX = startX + Math.cos(angle) * distance;
    const endY = startY + Math.sin(angle) * distance;

    particle.style.setProperty('--end-x', (endX - startX) + 'px');
    particle.style.setProperty('--end-y', (endY - startY) + 'px');

    document.body.appendChild(particle);

    // Remove after animation
    setTimeout(() => {
        particle.remove();
    }, (duration + delay) * 1000);
}

/**
 * Update achievement progress display
 * @param {Object} progress - Achievement progress data
 */
function updateAchievementProgress(progress) {
    const container = document.getElementById('achievement-progress');
    if (!container) return;

    // Clear existing progress
    container.innerHTML = '';

    // Show in-progress achievements
    if (progress.in_progress && progress.in_progress.length > 0) {
        const progressList = document.createElement('div');
        progressList.className = 'achievement-progress-list';

        progress.in_progress.forEach(item => {
            const progressItem = createProgressItem(item);
            progressList.appendChild(progressItem);
        });

        container.appendChild(progressList);
    }
}

/**
 * Create achievement progress item
 * @param {Object} item - Progress item data
 * @returns {HTMLElement} Progress item element
 */
function createProgressItem(item) {
    const progress = item.progress || 0;
    const required = item.required || 1;
    const percent = item.percent || 0;

    const progressItem = document.createElement('div');
    progressItem.className = 'achievement-progress-item';

    progressItem.innerHTML = `
        <div class="progress-header">
            <span class="progress-name">${item.name}</span>
            <span class="progress-count">${progress}/${required}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${percent}%"></div>
        </div>
        <p class="progress-description">${item.description}</p>
    `;

    return progressItem;
}

/**
 * Fetch and display achievement progress
 * @param {string} playerId - Player ID
 */
async function fetchAchievementProgress(playerId = 'default') {
    try {
        const response = await fetch(`/api/achievements?player_id=${playerId}`);
        const data = await response.json();
        updateAchievementProgress(data);
    } catch (error) {
        console.error('Failed to fetch achievement progress:', error);
    }
}

/**
 * Handle code submission response with achievement check
 * @param {Object} response - Submission response from API
 */
function handleSubmissionResponse(response) {
    // Check for achievement unlock
    if (response.achievement_unlocked) {
        showAchievement(response.achievement_unlocked);

        // Refresh achievement progress
        setTimeout(() => {
            fetchAchievementProgress();
        }, 1000);
    }
}

// Initialize achievement system
function initAchievements() {
    // Load initial achievement progress
    fetchAchievementProgress();

    // Listen for custom achievement events
    window.addEventListener('lmsp-achievement-unlocked', (event) => {
        showAchievement(event.detail);
    });

    console.log('✨ Achievement system initialized');
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAchievements);
} else {
    initAchievements();
}

// Export for use in other scripts
window.LMSP = window.LMSP || {};
window.LMSP.achievements = {
    show: showAchievement,
    updateProgress: updateAchievementProgress,
    handleResponse: handleSubmissionResponse,
};

// Self-teaching note:
//
// This file demonstrates:
// - DOM manipulation (creating/removing elements)
// - CSS animations and transitions
// - Event handling and custom events
// - Async/await for API calls
// - Queue management for sequential animations
// - setTimeout for timing control
// - CSS custom properties (--variable)
//
// Prerequisites:
// - JavaScript basics (functions, objects, arrays)
// - DOM API (createElement, appendChild, classList)
// - Fetch API for HTTP requests
// - CSS animations and transitions
//
// This creates the CELEBRATION moments that make learning FUN.
// Every achievement unlock is a dopamine hit that keeps players engaged!
