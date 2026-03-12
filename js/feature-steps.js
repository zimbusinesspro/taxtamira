/**
 * Feature Steps Component Logic
 * Synchronizes steps, progress bars, and image transitions.
 */
class FeatureSteps {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        this.features = options.features || [];
        this.autoPlayInterval = options.autoPlayInterval || 4000;
        this.currentFeature = 0;
        this.progress = 0;
        this.timer = null;

        this.init();
    }

    init() {
        this.render();
        this.startTimer();
    }

    render() {
        const stepItems = this.container.querySelectorAll('.step-item');
        const imageItems = this.container.querySelectorAll('.feature-image-item');
        const progressBars = this.container.querySelectorAll('.step-progress-bar');

        this.stepItems = stepItems;
        this.imageItems = imageItems;
        this.progressBars = progressBars;

        // Click listeners
        this.stepItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.jumpTo(index);
            });
        });
    }

    startTimer() {
        const startTime = Date.now();
        const duration = this.autoPlayInterval;

        const update = () => {
            const elapsed = Date.now() - startTime;
            this.progress = (elapsed / duration) * 100;

            if (this.progress >= 100) {
                this.next();
                this.startTimer(); // Restart for next
            } else {
                this.updateUI();
                this.timer = requestAnimationFrame(update);
            }
        };

        this.timer = requestAnimationFrame(update);
    }

    updateUI() {
        this.stepItems.forEach((item, index) => {
            if (index === this.currentFeature) {
                item.classList.add('active');
                item.classList.remove('completed');
                this.progressBars[index].style.width = `${this.progress}%`;
            } else if (index < this.currentFeature) {
                item.classList.add('completed');
                item.classList.remove('active');
                this.progressBars[index].style.width = '100%';
                const numBox = item.querySelector('.step-number-wrap');
                if (numBox) numBox.innerHTML = '✓';
            } else {
                item.classList.remove('active', 'completed');
                this.progressBars[index].style.width = '0%';
                const numBox = item.querySelector('.step-number-wrap');
                if (numBox) numBox.innerHTML = index + 1;
            }
        });

        this.imageItems.forEach((img, index) => {
            if (index === this.currentFeature) {
                img.classList.add('active');
            } else {
                img.classList.remove('active');
            }
        });
    }

    next() {
        this.currentFeature = (this.currentFeature + 1) % this.features.length;
        if (this.currentFeature === 0) {
            // Reset icons when looping back
            this.stepItems.forEach((item, index) => {
                const numBox = item.querySelector('.step-number-wrap');
                if (numBox) numBox.innerHTML = index + 1;
            });
        }
    }

    jumpTo(index) {
        cancelAnimationFrame(this.timer);
        this.currentFeature = index;
        this.progress = 0;
        this.startTimer();
    }
}

// Global reveal function for images if they are lazy loaded or need observer
document.addEventListener('DOMContentLoaded', () => {
    // Initializer will be called in the HTML for specific data
});
