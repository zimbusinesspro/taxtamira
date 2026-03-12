class MusicPlayer {
    constructor(containerId, playlist) {
        this.container = document.getElementById(containerId);
        this.playlist = playlist;
        this.activeIndex = 0;
        this.isPlaying = false;
        this.isShuffled = false;
        this.isRepeated = false;
        this.isLiked = false;
        this.volume = 80;
        this.progress = 0;
        this.simulationInterval = null;
        
        this.init();
    }

    init() {
        this.renderPlaylist();
        this.updateActiveTrack();
        this.setupEventListeners();
        
        // Initial icon refresh
        lucide.createIcons();
    }

    renderPlaylist() {
        const playlistContainer = this.container.querySelector('.playlist-scroll');
        playlistContainer.innerHTML = '';

        this.playlist.forEach((track, index) => {
            const button = document.createElement('button');
            button.className = `track-item-btn ${index === this.activeIndex ? 'active' : ''}`;
            button.type = 'button';
            button.innerHTML = `
                <div class="track-initial-circle">${track.title.charAt(0)}</div>
                <div class="track-list-info">
                    <div>
                        <p class="track-list-title">${track.title}</p>
                        <p class="track-list-artist">${track.artist}</p>
                    </div>
                    <span class="track-list-duration">${track.duration}</span>
                </div>
            `;
            
            button.addEventListener('click', () => this.setActiveTrack(index));
            playlistContainer.appendChild(button);
        });
    }

    setActiveTrack(index) {
        if (this.activeIndex === index) return;
        
        this.activeIndex = index;
        this.progress = 0;
        
        // Update UI state
        const buttons = this.container.querySelectorAll('.track-item-btn');
        buttons.forEach((btn, i) => {
            btn.classList.toggle('active', i === index);
        });

        this.updateActiveTrack();
        
        // If it was playing, keep playing the new one visually
        if (this.isPlaying) {
            this.startProgressSimulation();
        }
    }

    updateActiveTrack() {
        const track = this.playlist[this.activeIndex];
        
        // Update Text
        this.container.querySelector('.active-track-title').textContent = track.title;
        this.container.querySelector('.active-track-meta').textContent = `${track.artist} · ${track.album}`;
        
        // Update Spotify button
        const spotifyBtn = this.container.querySelector('.btn-spotify');
        spotifyBtn.href = track.spotifyUrl;
        
        // Update embed
        const iframe = this.container.querySelector('.spotify-embed-wrap iframe');
        iframe.src = track.embedUrl;
        
        // Update Progress
        this.updateProgressUI(0, track.duration);
    }

    updateProgressUI(percent, durationStr) {
        this.container.querySelector('.progress-bar-fill').style.width = `${percent}%`;
        
        // Calculate current time placeholder
        const totalSecs = this.parseDuration(durationStr);
        const currentSecs = Math.floor((percent / 100) * totalSecs);
        this.container.querySelector('.current-time').textContent = this.formatTime(currentSecs);
        this.container.querySelector('.total-duration').textContent = durationStr;
    }

    parseDuration(str) {
        const parts = str.split(':');
        return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    }

    formatTime(secs) {
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    }

    setupEventListeners() {
        // Play/Pause
        const playBtn = this.container.querySelector('.btn-play-pause');
        playBtn.addEventListener('click', () => {
            this.isPlaying = !this.isPlaying;
            this.togglePlayUI();
        });

        // Skip Next
        this.container.querySelector('.btn-skip-forward').addEventListener('click', () => this.nextTrack());
        
        // Skip Prev
        this.container.querySelector('.btn-skip-back').addEventListener('click', () => this.prevTrack());

        // Shuffle Toggle
        const shuffleBtn = this.container.querySelector('.btn-shuffle');
        shuffleBtn.addEventListener('click', () => {
            this.isShuffled = !this.isShuffled;
            shuffleBtn.classList.toggle('active', this.isShuffled);
            this.showToast(this.isShuffled ? "Shuffle On" : "Shuffle Off");
        });

        // Repeat Toggle
        const repeatBtn = this.container.querySelector('.btn-repeat');
        repeatBtn.addEventListener('click', () => {
            this.isRepeated = !this.isRepeated;
            repeatBtn.classList.toggle('active', this.isRepeated);
            this.showToast(this.isRepeated ? "Repeat On" : "Repeat Off");
        });

        // Like Button
        const heartBtn = this.container.querySelector('.btn-heart');
        heartBtn.addEventListener('click', () => {
            this.isLiked = !this.isLiked;
            heartBtn.classList.toggle('active', this.isLiked);
            const icon = heartBtn.querySelector('i');
            icon.setAttribute('data-lucide', this.isLiked ? 'heart-off' : 'heart');
            icon.style.fill = this.isLiked ? 'var(--player-primary)' : 'none';
            lucide.createIcons();
            this.showToast(this.isLiked ? "Added to Liked Songs" : "Removed from Liked Songs");
        });

        // Volume Toggle
        const volumeBtn = this.container.querySelector('.btn-volume');
        volumeBtn.addEventListener('click', () => {
            this.volume = this.volume === 0 ? 80 : 0;
            const icon = volumeBtn.querySelector('i');
            icon.setAttribute('data-lucide', this.volume === 0 ? 'volume-x' : 'volume-2');
            volumeBtn.classList.toggle('active', this.volume === 0);
            lucide.createIcons();
            this.showToast(this.volume === 0 ? "Muted" : `Volume: ${this.volume}%`);
        });

        // Action Buttons
        this.container.querySelector('.btn-primary-player').addEventListener('click', () => {
            this.isPlaying = true;
            this.togglePlayUI();
            this.showToast("Streaming started...");
        });

        this.container.querySelector('.btn-outline-player').addEventListener('click', () => {
            this.showToast("Opening Plan Options...");
        });
    }

    togglePlayUI() {
        const playBtn = this.container.querySelector('.btn-play-pause');
        const icon = playBtn.querySelector('i');
        icon.setAttribute('data-lucide', this.isPlaying ? 'pause' : 'play');
        lucide.createIcons();
        
        if (this.isPlaying) {
            this.startProgressSimulation();
        } else {
            clearInterval(this.simulationInterval);
        }
    }

    nextTrack() {
        let index;
        if (this.isShuffled) {
            index = Math.floor(Math.random() * this.playlist.length);
        } else {
            index = (this.activeIndex + 1) % this.playlist.length;
        }
        this.setActiveTrack(index);
    }

    prevTrack() {
        let index = (this.activeIndex - 1 + this.playlist.length) % this.playlist.length;
        this.setActiveTrack(index);
    }

    startProgressSimulation() {
        clearInterval(this.simulationInterval);
        this.simulationInterval = setInterval(() => {
            if (this.progress < 100) {
                this.progress += 0.2;
                this.updateProgressUI(this.progress, this.playlist[this.activeIndex].duration);
            } else {
                if (this.isRepeated) {
                    this.progress = 0;
                } else {
                    this.nextTrack();
                }
            }
        }, 1000);
    }

    showToast(msg) {
        // Simple UI feedback
        console.log(`Player: ${msg}`);
        // We could inject a toast element here if desired
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    const musicPlaylist = [
        {
            id: "7GJSpCJglXrOTqNzQOCamv",
            title: "Harare",
            artist: "Beazy Wulf",
            album: "Harare",
            duration: "3:15",
            spotifyUrl: "https://open.spotify.com/track/7GJSpCJglXrOTqNzQOCamv",
            embedUrl: "https://open.spotify.com/embed/track/7GJSpCJglXrOTqNzQOCamv?utm_source=generator"
        },
        {
            id: "5KUcPql373AS68ZtbOoaqr",
            title: "Murenje",
            artist: "Beazy Wulf ft. Lauretta",
            album: "Murenje",
            duration: "3:30",
            spotifyUrl: "https://open.spotify.com/track/5KUcPql373AS68ZtbOoaqr",
            embedUrl: "https://open.spotify.com/embed/track/5KUcPql373AS68ZtbOoaqr?utm_source=generator"
        },
        {
            id: "1FfnhT2qzjEARSgR2bcyWM",
            title: "Conversations With God",
            artist: "Beazy Wulf",
            album: "Conversations With God",
            duration: "4:00",
            spotifyUrl: "https://open.spotify.com/track/1FfnhT2qzjEARSgR2bcyWM",
            embedUrl: "https://open.spotify.com/embed/track/1FfnhT2qzjEARSgR2bcyWM?utm_source=generator"
        },
        {
            id: "3QJfQYqwFOiDu2WfNVfpAh",
            title: "PRESSURE",
            artist: "Beazy Wulf",
            album: "PRESSURE",
            duration: "2:50",
            spotifyUrl: "https://open.spotify.com/track/3QJfQYqwFOiDu2WfNVfpAh",
            embedUrl: "https://open.spotify.com/embed/track/3QJfQYqwFOiDu2WfNVfpAh?utm_source=generator"
        },
        {
            id: "5BgCTjtJYc59vnXidyEM0Z",
            title: "Zadzisa",
            artist: "Beazy Wulf",
            album: "Zadzisa",
            duration: "3:45",
            spotifyUrl: "https://open.spotify.com/track/5BgCTjtJYc59vnXidyEM0Z",
            embedUrl: "https://open.spotify.com/embed/track/5BgCTjtJYc59vnXidyEM0Z?utm_source=generator"
        }
    ];

    if (document.getElementById('music-app-block')) {
        new MusicPlayer('music-app-block', musicPlaylist);
    }
});
